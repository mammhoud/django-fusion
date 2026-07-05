"""Infrastructure utilities — locale, management command base, and scripts.

Sub-packages
------------
infrastructure.locale           Translation catalogue for django-fusion strings.
infrastructure.management       Base class for django-fusion management commands.
infrastructure.scripts          Utility scripts: superuser creation helper.
infrastructure.templatetags     ``django_fusion_tags`` — low-level template tag library.

Usage::

    from django_fusion.infrastructure.management import OsoulBaseCommand
    from django_fusion.infrastructure.scripts.superuser import ensure_superuser
"""
