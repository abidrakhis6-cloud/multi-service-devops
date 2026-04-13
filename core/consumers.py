import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Order, Message, Driver

class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket pour le chat en temps réel entre client et livreur
    Usage Django Channels pour les messages en temps réel
    """
    
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'chat_{self.order_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message')
        user = self.scope['user']
        
        # Save message to database
        await self.save_message(user, int(self.order_id), message_content)
        
        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'user': user.username,
                'timestamp': str(Message.objects.latest('timestamp').timestamp) if Message.objects.exists() else ''
            }
        )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user'],
            'timestamp': event['timestamp']
        }))
    
    @sync_to_async
    def save_message(self, user, order_id, content):
        order = Order.objects.get(id=order_id)
        Message.objects.create(
            order=order,
            user=user,
            content=content
        )

class DriverLocationConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket pour la localisation en temps réel du livreur
    """
    
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'location_{self.order_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Update driver location
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        driver_id = data.get('driver_id')
        
        await self.update_driver_location(driver_id, latitude, longitude)
        
        # Broadcast location to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'location_update',
                'latitude': latitude,
                'longitude': longitude,
                'driver_id': driver_id,
                'timestamp': str(__import__('datetime').datetime.now())
            }
        )
    
    async def location_update(self, event):
        # Send location to WebSocket
        await self.send(text_data=json.dumps({
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'driver_id': event['driver_id'],
            'timestamp': event['timestamp'],
            'type': 'location'
        }))
    
    @sync_to_async
    def update_driver_location(self, driver_id, latitude, longitude):
        driver = Driver.objects.get(id=driver_id)
        driver.latitude = latitude
        driver.longitude = longitude
        driver.save()

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket pour les notifications en temps réel
    Notifie le client sur les changements de statut
    """
    
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'notifications_{self.order_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def status_update(self, event):
        # Send status notification
        await self.send(text_data=json.dumps({
            'type': 'status',
            'status': event['status'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
    async def driver_assigned(self, event):
        # Send driver assignment notification
        await self.send(text_data=json.dumps({
            'type': 'driver_assigned',
            'driver': event['driver'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
