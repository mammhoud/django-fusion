"""Django app configuration for the canonical shared Dramatiq workers."""

from django.apps import AppConfig


class WorkerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.workers"
    label = "fusion_workers"
    verbose_name = "Dramatiq Workers"

    def ready(self) -> None:
        """Import infrastructure actors before configured product modules."""
        from . import heartbeat, shared_content, shared_email  # noqa: F401
