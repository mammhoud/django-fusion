"""AppConfig for the shared ``applications.www.core`` package.

The label ``shared_www_core`` is intentionally distinct from the per-site
``www.core`` label (``www_core``) so adding both packages to
``INSTALLED_APPS`` does not produce "Conflicting models" errors during
Django's system-checks.
"""

from __future__ import annotations

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Canonical AppConfig for the consolidated www.core code."""

    name = "applications.www.core"
    label = "shared_www_core"
    verbose_name = "Shared WWW Core"
    default_auto_field = "django.db.models.BigAutoField"
