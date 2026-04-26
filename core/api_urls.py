from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import StoreViewSet, ProductViewSet, CartViewSet, OrderViewSet, DriverViewSet

router = DefaultRouter()
router.register(r'stores', StoreViewSet)
router.register(r'products', ProductViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'drivers', DriverViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
