from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers, status
from models import *
from django.forms import model_to_dict
from rest_framework.fields import ListField
from django.core.exceptions import SuspiciousOperation

class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ('name')

# Serializers define the API representation.
class RestaurantSerializer(serializers.ModelSerializer):
    cuisines = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Cuisine.objects.all())

    def validate(self, data):
        absent_fields = set(self.fields.keys()) - set(self.initial_data.keys()) - set(['id'])
        if absent_fields:
            raise serializers.ValidationError("Fields absent: {}".format(absent_fields))

        latitude = data['latitude']
        longitude = data['longitude']
        rating = data['rating']
        if not (0 <= rating < 100):
            raise serializers.ValidationError('Rating should be between 0 and 100')
        if not (-90 <= latitude < 90):
            raise serializers.ValidationError('latitude should be between -90 and 90')
        if not (-180 <= longitude < 180):
            raise serializers.ValidationError('longitude should be between -180 and 180')
        return data

    def to_internal_value(self, data):
        tmp_lst = []
        for x in data['cuisines']:
            try :
                c = Cuisine.objects.get(name=x)
            except ObjectDoesNotExist:
                c = Cuisine(name=x)
                c.save()
                c = Cuisine.objects.get(name=x)
            except Exception as e:
                print(e)
            tmp_lst.append(c.name)

        data['cuisines'] = tmp_lst
        return data

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'city', 'latitude', 'cuisines', 'longitude', 'rating', 'is_open')

class ItemSerializer(serializers.ModelSerializer):
    restaurant_id = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all())

    def to_representation(self, instance):
        c = [cuisine.name for cuisine in Cuisine.objects.filter(restaurant_id=instance.restaurant_id)]
        rest = model_to_dict(instance.restaurant_id)
        rest['cuisines'] = c
        return {
            "name": instance.name,
            "price": '$' + str(float(instance.price)),
            "id": instance.id,
            "restaurant": rest
        }

    def validate(self, data):
        absent_fields = set(self.fields.keys()) - set(self.initial_data.keys()) - set(['id'])
        if absent_fields:
            raise serializers.ValidationError("Fields absent: {}".format(absent_fields))
        price = data['price']
        if not (0 < price):
            raise serializers.ValidationError('Price should be positive')
        return data

    def delete(self, request, pk, format=None):
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    class Meta:
        model = Item
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="username")
    def to_representation(self, instance):
        return {
            "id": instance.profile.id,
            "name": instance.username,
            "email": instance.email,
            }

    class Meta:
        model = User
        fields = ('name', 'email', 'password')

class CartSerializer(serializers.ModelSerializer):
    item_id = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())

    def to_representation(self, instance):
        item = model_to_dict(instance.item_id)
        item_name = item["name"]
        item_price = '$' + str(float(item["price"]))
        return {
            "item": {
                "name": item_name,
                "price": item_price,
            },
            "quantity": instance.quantity,
        }

    def validate(self, data):
        quantity = data['quantity']
        print("Quantity: " + str(quantity))
        if quantity < 0:
            raise serializers.ValidationError('Quantity should be positive')
        return data

    def to_internal_value(self, data):
        post = data.copy()
        post['order'] = Order.objects.get(pk=1)
        return post

    class Meta:
        model = Cart
        fields = ('item_id', 'quantity')

class OrderSerializer(serializers.ModelSerializer):
    items = CartSerializer(many=True, read_only=True)
    def to_representation(self, instance):
        data = super(OrderSerializer, self).to_representation(instance)
        data["total_price"] = '$' + str(float(instance.total_price))
        return data

    class Meta:
        model = Order
        fields = ('total_price', 'items')
        read_only_fields = ('total_price', )
