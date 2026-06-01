"""
Unified ASGI/WSGI server for all websites.

This server handles both HTTP and WebSocket requests and can run in either
ASGI or WSGI mode based on the SERVER_TYPE environment variable.

Environment variables:
- SERVER_TYPE: "asgi" (default) or "wsgi"
- DJANGO_SETTINGS_MODULE: Django settings module (default: "configs.settings")
- DJANGO_SITE: Website identifier (ctc-research, lms-demo, vresume)
"""

import os
import sys
from pathlib import Path

# Add workspace root to path for shared configs
workspace_root = Path(__file__).resolve().parents[1]
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")

# Import Django after path is set
from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application

# Choose server mode: "asgi" (default) or "wsgi"
SERVER_TYPE = os.environ.get("SERVER_TYPE", "asgi").lower()

if SERVER_TYPE == "wsgi":
    # --- WSGI application (synchronous, no websocket support) ---
    application = get_wsgi_application()

else:
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

    async def application(scope, receive, send):
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