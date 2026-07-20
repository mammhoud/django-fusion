#!/usr/bin/env python3
"""Django management CLI for POS Full sidecar (master manager).

Supports: migrate, makemigrations, showmigrations, createsuperuser, runserver

Usage:
    python manage.py migrate              # Apply migrations
    python manage.py createsuperuser      # Create admin superuser
    python manage.py runserver 0.0.0.0:8000  # Start admin panel

The server.py also supports --migrate flag for auto-migration at startup.
"""

import os
import sys
from pathlib import Path

_PATH = Path(__file__).resolve().parent

# Add sidecar/ and projects/pos/ to Python path so `import configs` and `import models` work
sys.path.insert(0, str(_PATH))                     # sidecar/ (configs, models, handlers, routes)
sys.path.insert(0, str(_PATH.parent.parent))       # pos-full/ (project root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manage_settings")

import django
from django.conf import settings

if not settings.configured:
    # Use centralized configs module (same as server.py)
    from configs import (
        DEBUG, DATABASES, INSTALLED_APPS, MIDDLEWARE,
        TEMPLATES, ROOT_URLCONF, SECRET_KEY,
        DEFAULT_AUTO_FIELD, USE_TZ, STATIC_URL, STATIC_ROOT,
    )
    settings.configure(
        DEBUG=DEBUG,
        DATABASES=DATABASES,
        INSTALLED_APPS=INSTALLED_APPS,
        MIDDLEWARE=MIDDLEWARE,
        TEMPLATES=TEMPLATES,
        ROOT_URLCONF=ROOT_URLCONF,
        SECRET_KEY=SECRET_KEY,
        DEFAULT_AUTO_FIELD=DEFAULT_AUTO_FIELD,
        USE_TZ=USE_TZ,
        STATIC_URL=STATIC_URL,
        STATIC_ROOT=STATIC_ROOT,
    )
    # Register admin models
    import configs.admin  # noqa: F401

django.setup()

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
