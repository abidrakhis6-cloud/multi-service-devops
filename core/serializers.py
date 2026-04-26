from rest_framework import serializers
from .models import Store, Product, Cart, CartItem, Order, Payment, Driver, Message

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'name', 'phone', 'vehicle', 'rating', 'is_available', 'latitude', 'longitude']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'category', 'image']

class StoreSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True, source='product_set')
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'category', 'description', 'rating', 'image', 'products']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total']
    
    def get_total(self, obj):
        return obj.get_total()

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'method', 'status', 'transaction_id', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    driver = DriverSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'store', 'driver', 'status', 'total_price', 'delivery_address', 'items', 'payment', 'created_at']
    
    def get_items(self, obj):
        return CartItemSerializer(obj.cart.items.all(), many=True).data

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp']
