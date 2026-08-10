"""POS Cloud — ASGI application with WebSocket support for real-time sync events.

Uses Django Channels ProtocolTypeRouter to route HTTP traffic to Django's
ASGI handler and WebSocket connections to the SyncEventConsumer.

Usage:
    daphne configs.asgi:application
    uvicorn configs.asgi:application
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs")

# Initialize Django ASGI application before importing channels so
# Django apps are fully loaded when the consumers need them.
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.auth import AuthMiddlewareStack  # noqa: E402
from django.urls import path  # noqa: E402

from apps.handlers.consumers import SyncEventConsumer  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/sync-events/", SyncEventConsumer.as_asgi()),
                ]
            )
        ),
    }
)
