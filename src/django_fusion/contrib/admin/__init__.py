"""
Admin integration for django_fusion.

Provides Django admin customizations and hooks for django-fusion powered applications.

Modules:
    admin_site: Custom admin site configuration.
    email_admin: Email-related admin customizations.
    wagtail_hooks: Wagtail admin hooks (when Wagtail is available).

Usage in Django settings::

    INSTALLED_APPS = [
        ...
        "django_fusion.contrib.admin",
    ]
"""

from .admin_site import *  # noqa: F401, F403
from .email_admin import *  # noqa: F401, F403
from .wagtail_hooks import *  # noqa: F401, F403

__all__ = []
