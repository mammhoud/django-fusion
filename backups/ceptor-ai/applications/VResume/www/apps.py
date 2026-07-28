"""VResume website application configuration."""
from django.apps import AppConfig


class WwwConfig(AppConfig):
    """Configuration for the VResume website application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "www"
    verbose_name = "VResume Website"
