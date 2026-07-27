#!/usr/bin/env python3
"""Unified ASGI/WSGI server for cms-fusion website.

Supports both ASGI (async, WebSocket) and WSGI (sync) modes via DJANGO_SERVER_TYPE env var.
"""
import os

from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ.get("DJANGO_SETTINGS_MODULE", "settings"))
os.environ.setdefault("DJANGO_SITE", "cms-fusion")
os.environ.setdefault("WEBSITE", "cms-fusion")

# Choose server mode: "asgi" (default) or "wsgi"
SERVER_TYPE = os.environ.get("DJANGO_SERVER_TYPE", "asgi").lower()

# --- WSGI application (synchronous, no websocket support) ---
# Always exported as `application` so `runserver` and WSGI servers work.
application = get_wsgi_application()

if SERVER_TYPE == "asgi":
    # --- ASGI application (HTTP + WebSocket) ---
    django_asgi_app = get_asgi_application()

    async def websocket_application(scope, receive, send):
        """Simple WebSocket handler: accepts connection, replies 'pong' to 'ping'."""
        while True:
            event = await receive()

            if event["type"] == "websocket.connect":
                await send({"type": "websocket.accept"})

            if event["type"] == "websocket.disconnect":
                break

            if event["type"] == "websocket.receive":
                if event.get("text") == "ping":
                    await send({"type": "websocket.send", "text": "pong!"})

    async def asgi_application(scope, receive, send):
        """
        ASGI dispatcher:
        - HTTP → Django
        - WebSocket → custom websocket handler
        """
        if scope["type"] == "http":
            await django_asgi_app(scope, receive, send)
        elif scope["type"] == "websocket":
            await websocket_application(scope, receive, send)
        else:
            raise NotImplementedError(f"Unknown scope type: {scope['type']}")

else:
    # WSGI-only mode — fallback asgi_application for settings compatibility
    from django.core.asgi import get_asgi_application as _get_asgi
    asgi_application = _get_asgi()
