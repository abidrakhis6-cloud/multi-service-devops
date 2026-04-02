from django.urls import path
from .views import home, store_detail

urlpatterns = [
    path('', home),
    path('store/<int:store_id>/', store_detail),
]