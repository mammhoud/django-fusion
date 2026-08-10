"""Django AppConfig for the Precis task worker.

Registers Dramatiq actor modules (email, content) with the broker when
Django finishes loading, ensuring background tasks are discoverable at
runtime across all tenant websites (fusion-cms, lms, VResume).

The worker app is registered globally via
the Precis base app registry so it activates for the backend.
every site without per-site configuration.
"""

from django.apps import AppConfig


class WorkerConfig(AppConfig):
    """Django app configuration for the shared task worker package.

    Attributes:
        default_auto_field: Primary key field type for auto-generated models.
        name: Python dotted path to the worker package.
        label: Short unique label used by Django for app references.
        verbose_name: Human-readable name displayed in Django admin.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "configs.tools.worker"
    label = "worker"
    verbose_name = "Task Worker"

    def ready(self) -> None:
        """Import actor modules so django-dramatiq registers them with the broker.

        Called once per Django process at startup. The imported modules
        register their ``@dramatiq.actor`` decorated functions with the
        configured message broker (Redis) so the shared-worker container
        can consume tasks from the ``email`` and ``default`` queues.

        Import order is intentionally explicit rather than relying on
        ``__init__.py`` imports to make the registration dependency clear.
        """
        # Import actor modules so django-dramatiq registers them with the broker.
        from . import email, content  # noqa: F401
