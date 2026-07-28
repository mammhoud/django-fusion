"""ASGI/WSGI entry point for the CRM site."""
import sys
import os
from pathlib import Path

_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent

for _path in (str(_SITE_DIR / "www"), str(_SITE_DIR), str(_WORKSPACE_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")

# WSGI
from django.core.wsgi import get_wsgi_application as _get_wsgi
_wsgi_app = _get_wsgi()

# ASGI
try:
    from django.core.asgi import get_asgi_application as _get_asgi
    application = _get_asgi()
except ImportError:
    application = _wsgi_app
