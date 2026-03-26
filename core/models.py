from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

class Store(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)