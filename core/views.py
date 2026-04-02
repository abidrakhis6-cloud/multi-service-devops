from django.shortcuts import render
from .models import Store, Product

def home(request):
    category = request.GET.get('category')
    stores = Store.objects.filter(category=category) if category else Store.objects.all()
    return render(request, 'home.html', {'stores': stores})


def store_detail(request, store_id):
    store = Store.objects.get(id=store_id)
    products = Product.objects.filter(store=store)
    return render(request, 'store.html', {'store': store, 'products': products})