from django.http import JsonResponse
from .models import Product

def products(request):
    data = list(Product.objects.values())
    return JsonResponse(data, safe=False)