from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter
from foodapp import views
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='FoodApp API')

class OptionalSlashRouter(SimpleRouter):
    def __init__(self):
        self.trailing_slash = '/?'
        super(SimpleRouter, self).__init__()

router = OptionalSlashRouter()
router.register(r'api/restaurants', views.RestaurantViewSet)
router.register(r'api/items', views.ItemViewSet)
router.register(r'api/users', views.UserViewSet)
router.register(r'api/cart', views.CartViewSet)
router.register(r'api/orders', views.OrderViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^swagger/$', schema_view),
]
