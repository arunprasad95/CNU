from django.shortcuts import render
from rest_framework import viewsets

from .serializers import RestaurantSerializer, ItemSerializer
from .models import Restaurant, Item


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
