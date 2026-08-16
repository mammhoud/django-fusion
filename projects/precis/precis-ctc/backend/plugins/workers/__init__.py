"""Precis background workers.

All product work is registered with django-fusion's Dramatiq backend. This
package is intentionally separate from ``apps.tasks``, which owns the local
TaskExecution audit model and migrations.
"""

TASK_MODULES = (
    "plugins.workers.shared_email",
    "plugins.workers.shared_content",
    "plugins.workers.heartbeat",
    "plugins.workers.email_tasks",
    "plugins.workers.course_tasks",
    "plugins.workers.content_tasks",
    "plugins.workers.legacy_email_tasks",
    "plugins.workers.campaign_tasks",
)
