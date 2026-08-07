"""ASGI/WSGI entrypoints for the customizer."""

import os

from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = get_wsgi_application()
asgi_application = get_asgi_application()
