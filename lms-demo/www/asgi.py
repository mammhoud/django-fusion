import os
import sys
from pathlib import Path

# Ensure workspace root is importable (shared `configs/`, `plugins/`)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Set DJANGO_SETTINGS_MODULE before loading the app
# Use local settings module instead of workspace-level configs.settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.core.asgi import get_asgi_application

# This application object is used by any ASGI server configured to use this file.
django_application = get_asgi_application()

# Import websocket application here, so apps from django_application are loaded first
from www.websocket import websocket_application  # noqa: E402


async def application(scope, receive, send):
    if scope["type"] == "http":
        await django_application(scope, receive, send)
    elif scope["type"] == "websocket":
        await websocket_application(scope, receive, send)
    else:
        msg = f"Unknown scope type {scope['type']}"
        raise NotImplementedError(msg)
