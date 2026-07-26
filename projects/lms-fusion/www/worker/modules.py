"""Integration points for ceptor-ai background tasks.

The installed ceptor-ai distribution may expose its own Celery task modules.
This module lists the task modules we expect the shared worker to autodiscover
when ceptor-ai is installed; importing is deliberately deferred to the worker
runtime so local/minimal environments can still boot.

``TASK_MODULES`` is consumed by ``www.worker.__init__.py`` and used by
Dramatiq's autodiscovery to register actor modules at worker startup.

Adding a new task module:

1. Create the module (e.g. ``www/worker/my_tasks.py``).
2. Add its dotted path to ``TASK_MODULES``.
3. The shared-worker will discover it on next deploy.

Example::

    # www/worker/my_tasks.py
    import dramatiq

    @dramatiq.actor(queue_name="my-queue")
    def my_task():
        ...
"""

TASK_MODULES = [
    "ceptor_ai.tasks",
    "ceptor_ai.workflows.tasks",
    "ceptor_ai.services.communication.tasks",
]
