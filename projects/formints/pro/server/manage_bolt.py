#!/usr/bin/env python3
"""
POS Full — Django manage command wrapper (post-Robyn migration).

This replaces ``python server.py`` as the canonical entry point.  The
application is now served via ASGI::

    daphne -b 0.0.0.0 -p 8766 asgi:application
    uvicorn asgi:application --host 0.0.0.0 --port 8766

For management commands (migrate, createsuperuser, etc.)::

    python manage_bolt.py migrate
    python manage_bolt.py --ensure-superuser

This is a thin wrapper around ``manage.py`` that also handles the
--ensure-superuser and --ensure-api-key convenience flags.
"""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs")

    # ── Convenience: --ensure-superuser  ──
    if "--ensure-superuser" in sys.argv:
        sys.argv.remove("--ensure-superuser")
        import django
        from django.conf import settings
        if not settings.configured:
            from configs import (
                DEBUG, DATABASES, INSTALLED_APPS, MIDDLEWARE,
                TEMPLATES, ROOT_URLCONF, SECRET_KEY,
                DEFAULT_AUTO_FIELD, USE_TZ, STATIC_URL, STATIC_ROOT,
                UNFOLD,
            )
            settings.configure(
                DEBUG=DEBUG, DATABASES=DATABASES,
                INSTALLED_APPS=INSTALLED_APPS, MIDDLEWARE=MIDDLEWARE,
                TEMPLATES=TEMPLATES, ROOT_URLCONF=ROOT_URLCONF,
                SECRET_KEY=SECRET_KEY, DEFAULT_AUTO_FIELD=DEFAULT_AUTO_FIELD,
                USE_TZ=USE_TZ, STATIC_URL=STATIC_URL, STATIC_ROOT=STATIC_ROOT,
                UNFOLD=UNFOLD,
            )
        django.setup()
        from django.contrib.auth.models import User
        email = os.environ.get("FORMINT_ADMIN_EMAIL", "admin@formint.local")
        password = os.environ.get("FORMINT_ADMIN_PASSWORD", "admin123")
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                username=email.split("@")[0],
                email=email,
                password=password,
            )
            print(f"Superuser created: {email}")
        else:
            print(f"Superuser already exists: {email}")

    # ── Convenience: --ensure-api-key ──
    if "--ensure-api-key" in sys.argv:
        sys.argv.remove("--ensure-api-key")
        import django
        from django.conf import settings
        if not settings.configured:
            from configs import (
                DEBUG, DATABASES, INSTALLED_APPS, MIDDLEWARE,
                TEMPLATES, ROOT_URLCONF, SECRET_KEY,
                DEFAULT_AUTO_FIELD, USE_TZ, STATIC_URL, STATIC_ROOT,
                UNFOLD,
            )
            settings.configure(
                DEBUG=DEBUG, DATABASES=DATABASES,
                INSTALLED_APPS=INSTALLED_APPS, MIDDLEWARE=MIDDLEWARE,
                TEMPLATES=TEMPLATES, ROOT_URLCONF=ROOT_URLCONF,
                SECRET_KEY=SECRET_KEY, DEFAULT_AUTO_FIELD=DEFAULT_AUTO_FIELD,
                USE_TZ=USE_TZ, STATIC_URL=STATIC_URL, STATIC_ROOT=STATIC_ROOT,
                UNFOLD=UNFOLD,
            )
        django.setup()
        from middleware.apikey_scoped import ensure_default_api_key
        key = ensure_default_api_key()
        if key:
            print(f"Default API key: {key}")

    # ── Delegate to Django management ──
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
