from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('restaurants/', views.restaurants, name='restaurants'),
    path('restaurants/<str:name>/', views.restaurant_detail, name='restaurant_detail'),
    path('courses/', views.courses, name='courses'),
    path('courses/<str:name>/', views.courses_detail, name='courses_detail'),
    path('boutiques/', views.boutiques, name='boutiques'),
    path('boutiques/<str:name>/', views.boutique_detail, name='boutique_detail'),
    path('pharmacie/', views.pharmacie, name='pharmacie'),
    path('pharmacie/<str:name>/', views.pharmacie_detail, name='pharmacie_detail'),
    path('livraison/', views.livraison, name='livraison'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    # API endpoints
    path('api/send-sms/', views.send_sms_api, name='send_sms'),
    path('api/send-verification-sms/', views.send_verification_sms, name='send_verification_sms'),
    path('api/make-call/', views.make_call_api, name='make_call'),
    path('api/health/', views.health_check, name='health'),
]