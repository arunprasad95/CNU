from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from mile1 import tasks
# Create your models here.
from django.db.models.signals import post_save, pre_save, m2m_changed, post_delete, pre_delete
from django.dispatch import receiver


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'categories'

    name = models.CharField(max_length=200)
    count_businesses = models.IntegerField(default=0, editable=False)
    def dec_counter(self):
        self.count_businesses-=1
        self.save()
    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    neighbourhood = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    postal_code = models.IntegerField(default=0)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    is_open = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False, editable=False)
    stars = models.FloatField(default=0, editable=False)
    review_count = models.IntegerField(default=0, editable=False)
    categories = models.ManyToManyField(Category)
    images_added = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        for category in self.categories.all():
            category.dec_counter()
        self.save()

    def _categories(self):
        x= ""
        for i in self.categories.filter():
            x+=(i.name + "\n")
        return x


class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    stars = models.PositiveIntegerField(default=5, validators=[MaxValueValidator(10), MinValueValidator(0)])
    date = models.DateField(auto_now_add=True, blank=True)
    text = models.TextField()
    list_display = 'rest_id'

    def __str__(self):
        return "Review for restaurant: " + str(self.restaurant.name)

    def rest_id(self):
        return getattr(self.restaurant, 'id')

    rest_id.short_description = 'Restaurant Id'

class Image(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    url = models.CharField(max_length=200)
@receiver(post_save, sender = Restaurant)
def imagespart(sender, instance, **kwargs):
    if kwargs['created']:
        tasks.download.s(instance.name,instance.id).delay()
@receiver(m2m_changed, sender=Restaurant.categories.through)
def update_categories_restaurant_create(sender, instance, **kwargs):
    if kwargs['action'] == 'pre_remove':
        change = -1
    elif kwargs['action'] == 'post_add':
        change = 1
    else:
        change = 0
    categories = instance.categories.all()
    for category in categories:
        category.count_businesses += change
        category.save()


@receiver(post_save, sender=Review)
def update_restaurant_review_create(sender, instance, **kwargs):
    restaurant = instance.restaurant
    old_review_count = restaurant.review_count
    old_stars = restaurant.stars
    restaurant.review_count += 1
    restaurant.stars = ((old_stars * old_review_count) + instance.stars) / restaurant.review_count
    restaurant.save()