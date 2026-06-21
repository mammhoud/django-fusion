"""
Django app configuration for django_rseal core module.
"""

from django.apps import AppConfig


class PipelinesConfig(AppConfig):
    """Configuration for the django_rseal core Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_rseal.core"
    label = "core"
    verbose_name = "Core"

    def ready(self):
        """Import signal handlers when app is ready."""
        try:
            from django_rseal import signals  # noqa: F401
        except ImportError:
            pass
