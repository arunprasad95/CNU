from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class Cuisine(models.Model):
    name = models.CharField(default="", max_length=50)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    cuisines = models.ManyToManyField(Cuisine)
    city = models.CharField(max_length=50)
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    is_open = models.BooleanField()
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Item(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    price = models.FloatField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return self.name