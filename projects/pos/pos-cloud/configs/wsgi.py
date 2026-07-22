"""POS Cloud — WSGI application for gunicorn deployment."""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs")
application = get_wsgi_application()
