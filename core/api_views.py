from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Store, Product, Cart, CartItem, Order, Driver, Message
from .serializers import StoreSerializer, ProductSerializer, CartSerializer, OrderSerializer, DriverSerializer, MessageSerializer

class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour les magasins"""
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    
    def get_queryset(self):
        category = self.request.query_params.get('category')
        if category:
            return Store.objects.filter(category=category)
        return Store.objects.all()
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Récupérer les produits d'un magasin"""
        store = self.get_object()
        products = store.product_set.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour les produits"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        store_id = self.request.query_params.get('store_id')
        if store_id:
            return Product.objects.filter(store_id=store_id)
        return Product.objects.all()

class CartViewSet(viewsets.ViewSet):
    """API pour le panier"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Récupérer le panier"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Ajouter un produit au panier"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        product = Product.objects.get(id=product_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Retirer un produit du panier"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item_id = request.data.get('item_id')
        
        CartItem.objects.filter(id=item_id, cart=cart).delete()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Vider le panier"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class OrderViewSet(viewsets.ViewSet):
    """API pour les commandes"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Récupérer toutes les commandes de l'utilisateur"""
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Récupérer une commande spécifique"""
        try:
            order = Order.objects.get(id=pk, user=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'detail': 'Commande non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def driver_location(self, request, pk=None):
        """Récupérer la localisation du livreur"""
        try:
            order = Order.objects.get(id=pk, user=request.user)
            if order.driver:
                driver_data = {
                    'name': order.driver.name,
                    'latitude': order.driver.latitude,
                    'longitude': order.driver.longitude,
                    'vehicle': order.driver.vehicle,
                    'phone': order.driver.phone,
                    'rating': order.driver.rating
                }
                return Response(driver_data)
            return Response({'detail': 'Pas de livreur assigné'}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({'detail': 'Commande non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Récupérer les messages d'une commande"""
        try:
            order = Order.objects.get(id=pk, user=request.user)
            messages = order.messages.all()
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'detail': 'Commande non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Envoyer un message"""
        try:
            order = Order.objects.get(id=pk, user=request.user)
            content = request.data.get('content')
            
            message = Message.objects.create(
                order=order,
                user=request.user,
                content=content
            )
            
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Order.DoesNotExist:
            return Response({'detail': 'Commande non trouvée'}, status=status.HTTP_404_NOT_FOUND)

class DriverViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour les livreurs"""
    queryset = Driver.objects.filter(is_available=True)
    serializer_class = DriverSerializer
    
    @action(detail=True, methods=['patch'])
    def update_location(self, request, pk=None):
        """Mettre à jour la localisation du livreur"""
        driver = self.get_object()
        driver.latitude = request.data.get('latitude', driver.latitude)
        driver.longitude = request.data.get('longitude', driver.longitude)
        driver.save()
        
        serializer = DriverSerializer(driver)
        return Response(serializer.data)
