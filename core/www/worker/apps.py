from django.apps import AppConfig


class WorkerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "www.worker"
    label = "worker"
    verbose_name = "Task Worker"

    def ready(self):
        # Import actor modules so django-dramatiq registers them with the broker.
        from . import email, content  # noqa: F401
