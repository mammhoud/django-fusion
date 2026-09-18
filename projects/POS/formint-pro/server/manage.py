#!/usr/bin/env python3
"""Django management CLI for the merged Formint server (master manager).

Merged from the original POS Full server manage.py and the formint backend
manage.py (loyalty + settings admin, superuser seeding).

Supports: migrate, makemigrations, showmigrations, createsuperuser, runserver

Usage:
    python manage.py migrate                          # Apply migrations
    python manage.py createsuperuser                  # Create admin superuser (interactive)
    python manage.py --ensure-superuser               # Auto-create superuser from env vars
    python manage.py runserver 0.0.0.0:8000           # Start admin panel

The server.py also supports --migrate flag for auto-migration at startup.

Environment Variables (for --ensure-superuser):
    FORMINT_ADMIN_EMAIL        Default: admin@formint.local
    FORMINT_ADMIN_PASSWORD     Default: admin123
    FORMINT_ADMIN_NAME         Default: Formint Admin
"""

import os
import sys
from pathlib import Path

_PATH = Path(__file__).resolve().parent

# Add server/ and the project root to Python path so `import configs` and `import models` work
sys.path.insert(0, str(_PATH))                     # server/ (configs, models, handlers, routes)
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
        UNFOLD, FUSION_RENDER_FIRST_DEFAULT,
        COMPONENTS_DIR_NAMES, COMPONENTS_ENABLE_BLOCK_ATTRS,
        COMPONENTS_INCLUDE_PATH_ROOTS,
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
        # Unfold admin theme config (sidebar, dashboard callback, login, colors)
        UNFOLD=UNFOLD,
        # django-fusion dual-mode + component registry settings (§12)
        FUSION_RENDER_FIRST_DEFAULT=FUSION_RENDER_FIRST_DEFAULT,
        COMPONENTS_DIR_NAMES=COMPONENTS_DIR_NAMES,
        COMPONENTS_ENABLE_BLOCK_ATTRS=COMPONENTS_ENABLE_BLOCK_ATTRS,
        COMPONENTS_INCLUDE_PATH_ROOTS=COMPONENTS_INCLUDE_PATH_ROOTS,
    )

django.setup()

# Register admin models (must happen AFTER django.setup() or models won't be ready)
import formint.admin  # noqa: F401 — autodiscovery registration (canonical, covers all pos_full + formint models)

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
    from django.conf import settings

    from django.contrib.auth import get_user_model

    User = get_user_model()

    email = getattr(settings, "FORMINT_ADMIN_EMAIL", os.environ.get("FORMINT_ADMIN_EMAIL", "admin@formint.local"))
    password = getattr(settings, "FORMINT_ADMIN_PASSWORD", os.environ.get("FORMINT_ADMIN_PASSWORD", "admin123"))
    name = getattr(settings, "FORMINT_ADMIN_NAME", os.environ.get("FORMINT_ADMIN_NAME", "Formint Admin"))

    # Security guard: never create an admin with the default password when
    # DEBUG is off (production). Deployment must set FORMINT_ADMIN_PASSWORD.
    if not getattr(settings, "DEBUG", True) and password == "admin123":
        raise SystemExit(
            "Refusing to create superuser with the default password while "
            "DEBUG=False. Set FORMINT_ADMIN_PASSWORD to a strong value first."
        )

    existing = User.objects.filter(email=email).first()
    if existing:
        print(f"✔ Superuser already exists: {email} (id={existing.id})")
        user = existing
    else:
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

    # Seed UserSettings for the superuser so the Settings admin has a row.
    try:
        from formint.models import UserSettings as FormintUserSettings
    except ImportError:
        FormintUserSettings = None
    if FormintUserSettings is not None:
        if not FormintUserSettings.objects.filter(user=user).exists():
            FormintUserSettings.objects.create(
                user=user,
                restaurant_name=name if name else "Formint POS",
            )
            print(f"✔ UserSettings seeded for {email}")
        else:
            print(f"✔ UserSettings already exists for {email}")

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
