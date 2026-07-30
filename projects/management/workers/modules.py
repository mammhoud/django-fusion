"""Worker task module discovery for shared management.

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

TASK_MODULES: list[str] = []
