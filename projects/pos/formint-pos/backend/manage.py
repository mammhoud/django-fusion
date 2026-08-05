#!/usr/bin/env python3
"""Formint — Django management CLI.

Supports: migrate, makemigrations, createsuperuser, runserver, …

Usage:
    python manage.py migrate                          # Apply migrations
    python manage.py createsuperuser                  # Create admin superuser (interactive)
    python manage.py --ensure-superuser               # Auto-create superuser from env vars
    python manage.py runserver 127.0.0.1:8000         # Start admin panel

Environment Variables (for --ensure-superuser):
    FORMINT_ADMIN_EMAIL       Default: admin@formint.local
    FORMINT_ADMIN_PASSWORD    Default: admin123
    FORMINT_ADMIN_NAME        Default: Formint Admin
"""

import os
import sys


def main() -> None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    from django.core.management import execute_from_command_line

    # ── Custom bootstrap flags ─────────────────────────────────────────────
    if '--ensure-superuser' in sys.argv:
        sys.argv.remove('--ensure-superuser')
        _ensure_superuser()
        if len(sys.argv) <= 1:
            sys.exit(0)

    execute_from_command_line(sys.argv)


def _ensure_superuser() -> None:
    """Auto-create the admin superuser (idempotent) from env vars.

    Reads FORMINT_ADMIN_EMAIL / FORMINT_ADMIN_PASSWORD / FORMINT_ADMIN_NAME
    (defaults from config.settings) and also seeds a UserSettings row so the
    Settings page in the admin has data for the logged-in user.
    """
    import django

    from django.conf import settings

    if not settings.configured:
        django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()

    email = settings.FORMINT_ADMIN_EMAIL
    password = settings.FORMINT_ADMIN_PASSWORD
    name = settings.FORMINT_ADMIN_NAME

    # Security guard: never create an admin with the default password when
    # DEBUG is off (production). Deployment must set FORMINT_ADMIN_PASSWORD.
    if not getattr(settings, 'DEBUG', True) and password == 'admin123':
        raise SystemExit(
            'Refusing to create superuser with the default password while '
            'DEBUG=False. Set FORMINT_ADMIN_PASSWORD to a strong value first.'
        )

    existing = User.objects.filter(email=email).first()
    if existing:
        print(f"✔ Superuser already exists: {email} (id={existing.id})")
        user = existing
    else:
        username = email.split('@')[0]
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        user.first_name = name.split()[0] if name else username
        if ' ' in name:
            user.last_name = ' '.join(name.split()[1:])
        user.save(update_fields=['first_name', 'last_name'])
        print(f"✔ Superuser created: {email}")

    # Seed UserSettings for the superuser so the Settings admin has a row.
    from formint.models import UserSettings

    if not UserSettings.objects.filter(user=user).exists():
        UserSettings.objects.create(
            user=user,
            restaurant_name=name if name else 'Formint POS',
        )
        print(f"✔ UserSettings seeded for {email}")
    else:
        print(f"✔ UserSettings already exists for {email}")

    print(f"  → Login at http://localhost:8000/admin/")


if __name__ == '__main__':
    main()
