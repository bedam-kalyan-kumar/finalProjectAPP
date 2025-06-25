"""
ASGI config for finalproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

# asgi.py
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from kitchatapp import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finalproject.settings')

# Define WebSocket URL patterns here if you don't have a separate routing.py
websocket_urlpatterns = [
    re_path(r'ws/call/(?P<user_id>\d+)/$', consumers.CallConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

