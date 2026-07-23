"""Infrastructure utilities — health endpoints, middleware, locale, management command base, and scripts.

Sub-packages
------------
infrastructure.health            Lightweight health-check endpoints.
infrastructure.locale           Translation catalogue for django-fusion strings.
infrastructure.middlewares       Request/response middleware (language, error tracking, etc.).
infrastructure.templatetags     ``django_fusion_tags`` — low-level template tag library.

Management commands and scripts now live under ``django_fusion.management``
(``django_fusion.management.commands.base`` and ``django_fusion.management.scripts``).

Usage::

    from django_fusion.management.commands.base import BaseCommand
    from django_fusion.management.scripts.superuser import create_superuser
"""
