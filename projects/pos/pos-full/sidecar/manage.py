#!/usr/bin/env python3
"""Django management CLI for POS Full sidecar (master manager).

Supports: migrate, makemigrations, showmigrations, createsuperuser, runserver

Usage:
    python manage.py migrate                          # Apply migrations
    python manage.py createsuperuser                  # Create admin superuser (interactive)
    python manage.py --ensure-superuser               # Auto-create superuser from env vars
    python manage.py runserver 0.0.0.0:8000           # Start admin panel

The server.py also supports --migrate flag for auto-migration at startup.

Environment Variables (for --ensure-superuser):
    POS_FULL_ADMIN_EMAIL       Default: admin@pos-full.local
    POS_FULL_ADMIN_PASSWORD    Default: admin123
    POS_FULL_ADMIN_NAME        Default: POS Full Admin
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

# ── Custom bootstrap flags ───────────────────────────────────────────────────


def _ensure_superuser() -> None:
    """Auto-create admin superuser from environment variables.

    Reads:
        POS_FULL_ADMIN_EMAIL    (default: admin@pos-full.local)
        POS_FULL_ADMIN_PASSWORD (default: admin123)
        POS_FULL_ADMIN_NAME     (default: POS Full Admin)

    Idempotent — if the user already exists, prints a message and does nothing.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    email = os.environ.get("POS_FULL_ADMIN_EMAIL", "admin@pos-full.local")
    password = os.environ.get("POS_FULL_ADMIN_PASSWORD", "admin123")
    name = os.environ.get("POS_FULL_ADMIN_NAME", "POS Full Admin")

    existing = User.objects.filter(email=email).first()
    if existing:
        print(f"✔ Superuser already exists: {email} (id={existing.id})")
        return

    username = email.split("@")[0]
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    user.first_name = name.split()[0] if name else username
    if " " in name:
        user.last_name = " ".join(name.split()[1:])
    user.save(update_fields=["first_name", "last_name"])

    print(f"✔ Superuser created: {email} (password: {password})")
    print(f"  → Login at http://localhost:8000/admin/")


if __name__ == "__main__":
    # Handle --ensure-superuser flag: remove it before handing off to Django
    # so it doesn't confuse execute_from_command_line.
    if "--ensure-superuser" in sys.argv:
        sys.argv.remove("--ensure-superuser")
        _ensure_superuser()
        if len(sys.argv) <= 1:
            sys.exit(0)

    execute_from_command_line(sys.argv)
