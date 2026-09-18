"""Formint Cloud — scheduled database backup task.

Uses ``@task`` from ``django_fusion.tasks`` with a cron schedule so the
backup runs nightly without an external cron/systemd timer dependency.

When APScheduler is installed, the django-fusion task scheduler picks up
the ``schedule`` parameter and registers the job automatically.  When
APScheduler is not available, the management command ``backup_db`` can
still be invoked directly or via an external cron trigger.

Task C2 from docs/plans/editions/04-cloud.md.
"""

from __future__ import annotations

import logging

from django.core.management import call_command
from django_fusion.tasks import task

logger = logging.getLogger(__name__)


@task(queue="system", schedule="0 2 * * *", max_retries=1)
def run_backup():
    """Run the database backup command.

    Scheduled nightly at 02:00 UTC.  Uses ``call_command`` so the full
    ``backup_db`` codepath executes — online SQLite backup + BackupRun
    audit row.  Failing the task is safe: the next night's run will
    create a fresh backup.
    """
    try:
        call_command("backup_db")
        logger.info("Nightly backup completed successfully.")
    except Exception:
        logger.exception("Nightly backup failed.")
        raise
