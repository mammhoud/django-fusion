"""Scheduled task-history sync for the website ``TaskExecution`` record.

The Task Center page mirrors the shared ``BackgroundTaskLog`` audit trail into
the product-local ``TaskExecution`` website record on every page view.  This
module registers the same mirror as a *scheduled* task so the website record
stays fresh even when nobody visits the Task Center — the task backend (or the
django-fusion APScheduler integration) fires it on a cron cadence instead of
relying on traffic.
"""

from __future__ import annotations

import logging

from django_fusion.tasks.decorators import task

logger = logging.getLogger(__name__)


@task(queue="system", schedule="*/10 * * * *", max_retries=1)
def sync_task_history() -> int:
    """Mirror shared ``BackgroundTaskLog`` rows into the website record.

    Scheduled every 10 minutes by default.  ``resolve_default_site()`` uses the
    same chain as the task backend (``FUSION_TASK_SITE_NAME`` → ``WEBSITE_NAME``
    → ``WEBSITE`` → env), so the sync filters on exactly the site the worker
    stamps into each shared log.  Returns the number of records written.

    The ``views`` import is deferred: it pulls in ``django.contrib.auth``, which
    must not be imported before Django apps are ready (``django_fusion.tasks``
    is imported during app loading / autodiscovery).
    """
    from django_fusion.tasks.views import (  # noqa: PLC0415
        resolve_default_site,
        sync_website_record,
    )

    site_name = resolve_default_site()
    written = sync_website_record(site_name)
    logger.info(
        "Task history sync wrote %d record(s) for site %r.",
        written,
        site_name or "(all)",
    )
    return written


__all__ = ["sync_task_history"]
