"""Integration points for django-rseal background tasks.

The installed django-rseal distribution may expose its own Celery task modules.
This module lists the task modules we expect the shared worker to autodiscover
when django-rseal is installed; importing is deliberately deferred to the worker
runtime so local/minimal environments can still boot.
"""

DJANGO_RSEAL_TASK_MODULES = [
    "django_rseal.tasks",
    "django_rseal.workflows.tasks",
    "django_rseal.workflows.pipelines.tasks",
    "django_rseal.services.communication.tasks",
]
