import json
from models import *
from serializers import *
from django_filters import rest_framework as filters
from rest_framework import viewsets, mixins, pagination, response
from django.http import HttpResponse, HttpResponseBadRequest
from django.forms import model_to_dict

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size=2

    def get_paginated_response(self, data):
        return response.Response(data)

class RestaurantFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    cuisine = filters.ModelMultipleChoiceFilter(field_name="cuisines",queryset=Cuisine.objects.all(),)
    city = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Restaurant
        fields = ['name', 'city', 'cuisine']

class ItemFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    minPrice = filters.NumberFilter(field_name="price", lookup_expr='gte')
    maxPrice = filters.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = Item
        fields = ['name', 'minPrice', 'maxPrice']

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = RestaurantFilter

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ItemFilter

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        username = request.data["name"]
        email = request.data["email"]
        password = request.data["password"]
        user = User.objects.create(
            username=username,
            email=email,
            password=password
        )
        res = {
            "id": user.profile.id,
            "name": user.username,
            "email": user.email,
            "token": user.profile.token
            }
        return HttpResponse(json.dumps(res), content_type="application/json", status=201)

class CartViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        request = self.request
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Cart.objects.none()
        try:
            user = User.objects.get(profile__token=request.META['HTTP_AUTHORIZATION'])
            current_orders = Order.objects.filter(user=user, pending=True)
            if current_orders.count() == 1:
                order = current_orders.first()
                return Cart.objects.filter(order=order)
        except User.DoesNotExist:
            pass
        return Cart.objects.none()

    def list(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return HttpResponse('HTTP_AUTHORIZATION not present', status=401)
        try:
            user = User.objects.get(profile__token=request.META['HTTP_AUTHORIZATION'])
        except User.DoesNotExist:
            return HttpResponse('Unauthorized token', status=401)

        queryset = self.get_queryset()
        serializer = CartSerializer(queryset, many=True)
        return response.Response(serializer.data)

    def put(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return HttpResponse('HTTP_AUTHORIZATION not present', status=401)

        try:
            user = User.objects.get(profile__token=request.META['HTTP_AUTHORIZATION'])
        except User.DoesNotExist:
            return HttpResponse('Unauthorized token', status=401)
        current_orders = Order.objects.filter(user=user, pending=True)
        if current_orders.count() == 1:
            order = current_orders.first()
        else:
            return HttpResponseBadRequest("There are {} orders for {} user".format(current_orders.count(), user.username))

        item_id = request.data["item_id"]
        quantity = request.data["quantity"]
        other_cart_items = Cart.objects.filter(order=order, item_id=item_id)
        if other_cart_items.count() > 0:
            cart_item = other_cart_items.first()
            if quantity < 0:
                return HttpResponseBadRequest("Quantity should be non-negative")
            elif quantity==0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            return HttpResponse("Success")

        return HttpResponse(status=404)

    def create(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return HttpResponse('HTTP_AUTHORIZATION not present', status=401)

        print(json.dumps(request.data))
        item_id = request.data["item_id"]
        quantity = request.data["quantity"]

        if quantity <= 0:
            return HttpResponseBadRequest("Quantity should be positive")

        try:
            user = User.objects.get(profile__token=request.META['HTTP_AUTHORIZATION'])
        except User.DoesNotExist:
            return HttpResponse('Unauthorized token', status=401)

        current_orders = Order.objects.filter(user=user, pending=True)
        if current_orders.count() == 1:
            order = current_orders.first()
        else:
            return HttpResponseBadRequest("There are {} orders for {} user".format(current_orders.count(), user.username))


        print(str(item_id) + " &&&  " + str(quantity))
        other_cart_items = Cart.objects.filter(order=order)
        if other_cart_items.count() > 0:
            if other_cart_items.filter(item_id=item_id).count() > 0:
                return HttpResponseBadRequest("Item already exists in cart")
            other_cart_items_restaurant_id = other_cart_items.first().item_id.restaurant_id
            restaurant_id = Item.objects.get(pk=item_id).restaurant_id
            if other_cart_items_restaurant_id != restaurant_id:
                return HttpResponseBadRequest("Only same restaurant items allowed")
        Cart.objects.create(
            item_id=Item.objects.get(pk=item_id),
            order=order,
            quantity=quantity
        )

        return HttpResponse("Success", status=201)

class OrderViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        request = self.request
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Order.objects.none()
        try:
            user = User.objects.get(profile__token=request.META['HTTP_AUTHORIZATION'])
            return Order.objects.filter(user=user, pending=False)
        except User.DoesNotExist:
            return Order.objects.none()

    def list(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return HttpResponse('HTTP_AUTHORIZATION not present', status=401)
        try:
            user = User.objects.get(profile__token=request.META['HTTP_AUTHORIZATION'])
        except User.DoesNotExist:
            return HttpResponse('Unauthorized token', status=401)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return HttpResponse('HTTP_AUTHORIZATION not present', status=401)

        try:
            user = User.objects.get(profile__token=request.META['HTTP_AUTHORIZATION'])
        except User.DoesNotExist:
            return HttpResponse('Unauthorized token', status=401)

        current_orders = Order.objects.filter(user=user, pending=True)
        if current_orders.count() == 1:
            order = current_orders.first()
            cart_list = Cart.objects.filter(order=order)
            if cart_list.count() == 0:
                return HttpResponseBadRequest("No items in cart?")

            total_price = 0.0
            for cart in cart_list:
                total_price += float(cart.item_id.price*cart.quantity)
            order.total_price = total_price
            order.pending = False
            order.save()
        else:
            return HttpResponseBadRequest("There are {} orders for {} user".format(current_orders.count(), user.username))

        Order.objects.create(user=user)

        res = OrderSerializer(order).data
        return HttpResponse(json.dumps(res), content_type="application/json", status=201)
