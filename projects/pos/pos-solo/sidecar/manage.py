#!/usr/bin/env python3
"""Django management CLI for POS Solo sidecar.

Supports: migrate, makemigrations, showmigrations

Usage:
    python manage.py migrate          # Apply migrations
    python manage.py makemigrations   # Create migration files
    python manage.py showmigrations   # List migration status

The server.py also supports --migrate flag for auto-migration at startup.
"""

import os
import sys
from pathlib import Path

_BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(_BASE.parent.parent))  # shared module

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manage_settings")

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(_BASE.parent / "restaurant.db"),
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "models.PosSoloConfig",  # Managed models (pos_unified)
            "models.posapp_app.PosappConfig",  # Rust-mirror models (posapp, managed=True)
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
        SECRET_KEY=os.environ.get("DJANGO_SECRET_KEY", "pos-solo-mgmt-key"),
    )

django.setup()

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
