"""Infrastructure utilities — locale, management command base, and scripts.

Sub-packages
------------
infrastructure.locale           Translation catalogue for django-osoul strings.
infrastructure.management       Base class for django-osoul management commands.
infrastructure.scripts          Utility scripts: superuser creation helper.
infrastructure.templatetags     ``django_osoul_tags`` — low-level template tag library.

Usage::

    from django_osoul.infrastructure.management import OsoulBaseCommand
    from django_osoul.infrastructure.scripts.superuser import ensure_superuser
"""
