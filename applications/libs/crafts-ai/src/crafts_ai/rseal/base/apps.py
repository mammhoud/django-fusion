"""
Django app configuration for crafts_ai core module.
"""

from django.apps import AppConfig


class PipelinesConfig(AppConfig):
    """Configuration for the crafts_ai core Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "crafts_ai.core"
    label = "core"
    verbose_name = "Core"

    def ready(self):
        """Import signal handlers when app is ready."""
        try:
            from crafts_ai import signals  # noqa: F401
        except ImportError:
            pass
