from django.db import models
from django.contrib.auth.models import User
import string
import random
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=16)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        while True:
            randomStr = ''.join(random.choice(string.ascii_uppercase) for _ in range(16))
            if not Profile.objects.filter(token=randomStr).exists():
                break
        profile = Profile.objects.create(user=instance, token=randomStr)
        Order.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    pending = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(default=0.0, max_digits=20, decimal_places=10)

class Cart(models.Model):
    order = models.ForeignKey('Order', related_name='items', on_delete=models.CASCADE)
    item_id = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity = models.IntegerField()

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=20, decimal_places=10)
    restaurant_id = models.ForeignKey('Restaurant', on_delete=models.CASCADE)

    def __unicode__(self):
        return self.name

class Restaurant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=20, decimal_places=10)
    longitude = models.DecimalField(max_digits=20, decimal_places=10)
    rating = models.DecimalField(max_digits=20, decimal_places=10)
    is_open = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

class Cuisine(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    restaurant_id = models.ManyToManyField(Restaurant, related_name="cuisines")
    def __unicode__(self):
        return self.name
