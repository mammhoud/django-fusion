import os

from django.core.asgi import get_asgi_application

from configs.settings import settings

# If DJANGO_SETTINGS_MODULE is unset, default to the local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings.get("DJANGO_SETTINGS_MODULE"))

# This application object is used by any ASGI server configured to use this file.
django_application = get_asgi_application()

# Import websocket application here, so apps from django_application are loaded first
from core.websocket import websocket_application  # noqa: E402


async def application(scope, receive, send):
    if scope["type"] == "http":
        await django_application(scope, receive, send)
    elif scope["type"] == "websocket":
        await websocket_application(scope, receive, send)
    else:
        msg = f"Unknown scope type {scope['type']}"
        raise NotImplementedError(msg)
