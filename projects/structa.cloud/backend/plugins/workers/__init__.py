"""Precis Landing Dramatiq workers.

Worker implementations live under ``plugins.workers`` so the product task
boundary is independent from the ``apps.tasks`` TaskExecution model app.
"""

TASK_MODULES = (
    "plugins.workers.email_tasks",
    "plugins.workers.legacy_email_tasks",
    "plugins.workers.content_tasks",
)
