from django.urls import path
from . import views
from . import stripe_views

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
    # Invoice & Bank Setup
    path('invoice/<int:invoice_id>/', stripe_views.get_invoice_pdf, name='invoice_pdf'),
    path('bank-setup/', views.bank_setup, name='bank_setup'),
    # API endpoints
    path('api/send-sms/', views.send_sms_api, name='send_sms'),
    path('api/send-verification-sms/', views.send_verification_sms, name='send_verification_sms'),
    path('api/make-call/', views.make_call_api, name='make_call'),
    path('api/health/', views.health_check, name='health'),
    # Stripe Payment endpoints
    path('api/payment/create-intent/', stripe_views.create_payment_intent, name='create_payment_intent'),
    path('api/payment/confirm/', stripe_views.confirm_payment, name='confirm_payment'),
    path('api/payment/webhook/', stripe_views.webhook, name='stripe_webhook'),
    # Stripe Connect (for receiving payments)
    path('api/stripe/create-account/', stripe_views.create_connected_account, name='create_stripe_account'),
    path('api/stripe/add-bank/', stripe_views.add_bank_account, name='add_bank_account'),
    path('api/stripe/transfer/', stripe_views.transfer_to_account, name='transfer_to_account'),
]