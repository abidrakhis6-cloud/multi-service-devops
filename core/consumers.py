import json
import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer


DRIVER_REPLIES = {
    ('bonjour', 'bjr', 'salut', 'hello', 'coucou'): 'Oui bonjour ! Je suis en route 😊',
    ('merci', 'thanks'): "De rien, j'arrive bientôt !",
    ('où', 'ou es', 'arrivez', 'arrives', 'viens', 'venez'): "J'arrive dans quelques minutes ! 🚴",
    ('combien', 'temps', 'longtemps', 'minutes', 'attendre'): 'Environ 5 minutes encore ⏱️',
    ('porte', 'code', 'digicode', 'badge', 'interphone'): 'Noté, merci pour l\'info ! 📝',
    ('étage', 'escalier', 'ascenseur', 'batiment'): 'Parfait, je monte ! 🏢',
    ('ok', 'parfait', 'super', 'bien', 'd\'accord', 'dac'): 'Super, à tout de suite ! 👍',
    ('lent', 'vite', 'rapide', 'pressé'): "Je fais de mon mieux, j'arrive !",
    ('problème', 'souci', 'erreur'): "Pas de souci, je m'en occupe !",
}


def _get_auto_response(message: str) -> str:
    m = message.lower()
    for keywords, reply in DRIVER_REPLIES.items():
        if any(kw in m for kw in keywords):
            return reply
    return '👍 Reçu !'


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'chat_{self.order_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send welcome message from driver on first connect
        await asyncio.sleep(0.5)
        ts = datetime.now().strftime('%H:%M')
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': "Bonjour ! J'ai récupéré votre commande. Je serai chez vous dans environ 8 minutes ! 🚴",
            'sender_type': 'driver',
            'sender_name': 'Ahmed',
            'timestamp': ts,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        sender_type = data.get('sender_type', 'customer')
        sender_name = data.get('sender_name', 'Vous')

        if not message:
            return

        ts = datetime.now().strftime('%H:%M')

        # Broadcast the customer message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_type': sender_type,
                'sender_name': sender_name,
                'timestamp': ts,
            }
        )

        # Schedule driver auto-response for customer messages
        if sender_type == 'customer':
            asyncio.ensure_future(self._driver_respond(message))

    async def _driver_respond(self, customer_message: str):
        try:
            await asyncio.sleep(1.5)
            reply = _get_auto_response(customer_message)
            ts = datetime.now().strftime('%H:%M')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': reply,
                    'sender_type': 'driver',
                    'sender_name': 'Ahmed',
                    'timestamp': ts,
                }
            )
        except Exception:
            pass

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_type': event['sender_type'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
        }))


class DriverLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'location_{self.order_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude is None or longitude is None:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'location_update',
                'latitude': latitude,
                'longitude': longitude,
            }
        )

    async def location_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'location',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
        }))
