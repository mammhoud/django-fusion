"""
Django app configuration for ceptor_ai core module.
"""

from django.apps import AppConfig


class PipelinesConfig(AppConfig):
    """Configuration for the ceptor_ai core Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ceptor_ai.core"
    label = "core"
    verbose_name = "Core"

    def ready(self):
        """Import signal handlers when app is ready."""
        try:
            from ceptor_ai import signals  # noqa: F401
        except ImportError:
            pass
