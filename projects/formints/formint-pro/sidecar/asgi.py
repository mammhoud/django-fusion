"""
POS Full — ASGI configuration (Daphne / uvicorn entry point).

Replaces the Robyn server with a Django-native ASGI stack:

  * HTTP        → Django's ASGI handler (asgi_application)
  * WebSocket   → Django Channels (ProtocolTypeRouter → URLRouter → consumers)

Usage::

    daphne -b 0.0.0.0 -p 8766 asgi:application
    uvicorn asgi:application --host 0.0.0.0 --port 8766
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs")

import django
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from consumers import websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})
