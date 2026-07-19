"""
ASGI/WSGI server entry point for minimal POS Portal.

@tested pos-portal/minimal - Server entry point
"""

from __future__ import annotations

import os

from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ.setdefault("WEBSITE", "minimal-portal")

SERVER_TYPE = os.environ.get("DJANGO_SERVER_TYPE", "asgi").lower()

if SERVER_TYPE == "wsgi":
    application = get_wsgi_application()
else:
    application = get_asgi_application()
