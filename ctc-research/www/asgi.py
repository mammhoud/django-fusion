import asyncio
import os
import sys
from pathlib import Path

# Ensure the site `www` directory is on the Python path so packages like
# `core` (which live under `www/core`) can be imported as top-level modules.
# In container layout `www` is copied to `/app/www`, so add that directory.

# Ensure workspace root is importable (shared `configs/`, `plugins/`)
_root_dir = str(Path(__file__).resolve().parents[1])
_www_dir = str(Path(__file__).resolve().parents[0])
# Prefer the project root so shared packages (e.g. /app/core) take precedence,
# but also ensure the site `www` directory is available for site-local packages.
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
if _www_dir not in sys.path:
    # Insert after root so /app/core is preferred over /app/www/core
    sys.path.insert(1, _www_dir)

# Force the Django settings module to the unified `configs.settings` entrypoint
# to ensure dynamic configuration (site selection, ROOT_URLCONF) is applied.
os.environ["DJANGO_SETTINGS_MODULE"] = "configs.settings"

django_application = None
websocket_application = None
_startup_lock = None


def _is_health_path(scope):
    return scope.get("type") == "http" and scope.get("path", "").rstrip("/") == "/health"


async def _ensure_django_app():
    """Lazily import and initialize Django ASGI application.

    This avoids importing Django at module-import time so the module can
    respond to a simple healthcheck even when Django URLConf or templates
    are misconfigured.
    """
    global django_application, websocket_application, _startup_lock
    if django_application is None:
        # Ensure only one coroutine performs Django setup to avoid
        # concurrent calls to `django.setup()` which raise
        # "populate() isn't reentrant" when run in parallel.
        if _startup_lock is None:
            _startup_lock = asyncio.Lock()
        async with _startup_lock:
            if django_application is not None:
                return
        # Ensure the runtime config singleton is imported so dynamic
        # settings (site selection, ROOT_URLCONF, etc.) are applied
        try:
            from configs.settings.conf import settings as _cfg_settings  # noqa: F401
        except Exception:
            _cfg_settings = None

            from django.core.asgi import get_asgi_application

            django_application = get_asgi_application()
        # Import websocket application after Django apps are loaded
        try:
            from www.websocket import websocket_application as _ws  # noqa: E402

            websocket_application = _ws
        except Exception:
            websocket_application = None


async def application(scope, receive, send):
    # Short-circuit health endpoint without initializing Django.
    if _is_health_path(scope):
        headers = [(b"content-type", b"application/json")]
        await send({"type": "http.response.start", "status": 200, "headers": headers})
        await send({"type": "http.response.body", "body": b'{"status":"ok"}', "more_body": False})
        return

    # Ensure Django app is ready for non-health requests
    await _ensure_django_app()

    if scope["type"] == "http":
        await django_application(scope, receive, send)
    elif scope["type"] == "websocket":
        if websocket_application:
            await websocket_application(scope, receive, send)
        else:
            msg = f"No websocket application available"
            raise NotImplementedError(msg)
    else:
        msg = f"Unknown scope type {scope['type']}"
        raise NotImplementedError(msg)
