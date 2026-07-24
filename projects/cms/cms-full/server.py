#!/usr/bin/env python3
"""Unified ASGI/WSGI server for cms-full (merged CTC Research + LMS)."""
import os

from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ.setdefault("DJANGO_SITE", "cms-full")
os.environ.setdefault("WEBSITE", "cms-full")

SERVER_TYPE = os.environ.get("DJANGO_SERVER_TYPE", "asgi").lower()

if SERVER_TYPE == "wsgi":
    application = get_wsgi_application()
else:
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

    async def application(scope, receive, send):
        if scope["type"] == "http":
            await django_asgi_app(scope, receive, send)
        elif scope["type"] == "websocket":
            await websocket_application(scope, receive, send)
        else:
            raise NotImplementedError(f"Unknown scope type: {scope['type']}")
