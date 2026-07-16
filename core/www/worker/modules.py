"""Integration points for ceptor-ai background tasks.

The installed ceptor-ai distribution may expose its own Celery task modules.
This module lists the task modules we expect the shared worker to autodiscover
when ceptor-ai is installed; importing is deliberately deferred to the worker
runtime so local/minimal environments can still boot.
"""

TASK_MODULES = [
    "ceptor_ai.tasks",
    "ceptor_ai.workflows.tasks",
    "ceptor_ai.services.communication.tasks",
]
