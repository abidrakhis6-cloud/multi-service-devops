from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<order_id>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/location/(?P<order_id>[^/]+)/$', consumers.DriverLocationConsumer.as_asgi()),
]
