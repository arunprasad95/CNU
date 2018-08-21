from rest_framework import serializers

from .models import Restaurant, Item, Cuisine


class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ('name',)


class CuisineField(serializers.Field):
    def to_representation(self, cuisines):
        return list(str(cuisine) for cuisine in cuisines.all())

    def to_internal_value(self, data):
        cl = list(map(lambda x:str(x) ,Cuisine.objects.all()))
        not_there = list(filter(lambda x: x not in cl , data))
        for cuisine in not_there:
            new_cuisine_object = Cuisine(name=cuisine)
            new_cuisine_object.save()
        result = []
        for item in data:
            for cuisine_object in Cuisine.objects.all():
                if cuisine_object.name == item:
                    result+=[cuisine_object.id]
        return result
class RestaurantSerializer(serializers.ModelSerializer):
    cuisines = CuisineField()

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'cuisines', 'city', 'latitude', 'longitude', 'rating', 'is_open')


class ItemSerializer(serializers.ModelSerializer):
    restaurant_id = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), source='restaurant')
    restaurant = RestaurantSerializer(read_only=True)

    class Meta:
        model = Item
        fields = ('id', 'name', 'price', 'restaurant_id', 'restaurant')
