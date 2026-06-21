"""Integration points for crafts-ai background tasks.

The installed crafts-ai distribution may expose its own Celery task modules.
This module lists the task modules we expect the shared worker to autodiscover
when crafts-ai is installed; importing is deliberately deferred to the worker
runtime so local/minimal environments can still boot.
"""

DJANGO_RSEAL_TASK_MODULES = [
    "crafts_ai.rseal.tasks",
    "crafts_ai.rseal.workflows.tasks",
    "crafts_ai.rseal.workflows.pipelines.tasks",
    "crafts_ai.rseal.services.communication.tasks",
]
