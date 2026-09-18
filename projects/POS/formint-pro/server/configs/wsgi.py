"""
POS Full — WSGI configuration.

The WSGI entry point for hosting the Django stack behind a WSGI server
(e.g. gunicorn). For WebSocket support use ``asgi:application`` instead.

Usage::

    gunicorn configs.wsgi:application
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs")
application = get_wsgi_application()
