"""APScheduler integration for django-fusion scheduled tasks.

Replaces Celery Beat.  Runs inside the Dramatiq worker process (or
standalone via ``python -m django_fusion.tasks.scheduler``).

Usage from the command line::

    DJANGO_SETTINGS_MODULE=myapp.settings \\
        python -m django_fusion.tasks.scheduler
"""

from __future__ import annotations

import logging
import signal
import sys

logger = logging.getLogger(__name__)


def _build_scheduler():
    """Return a configured BackgroundScheduler, or None if APScheduler is
    not installed."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.info("APScheduler not installed — scheduled tasks disabled.")
        return None

    scheduler = BackgroundScheduler(
        timezone="UTC",
        daemon=True,
    )
    return scheduler


def register_scheduled_tasks(scheduler) -> int:
    """Register all tasks that carry a ``schedule`` from the registry.

    Returns the number of jobs registered.
    """
    from apscheduler.triggers.cron import CronTrigger
    from django_fusion.tasks.registry import task_registry

    count = 0
    for entry in task_registry.scheduled_tasks():
        if not entry.schedule:
            continue
        try:
            scheduler.add_job(
                entry.func,
                trigger=CronTrigger.from_crontab(entry.schedule),
                id=entry.name,
                name=entry.name,
                replace_existing=True,
            )
            logger.info(
                "Registered scheduled task %r (cron=%s)", entry.name, entry.schedule
            )
            count += 1
        except Exception:
            logger.exception("Failed to register scheduled task %r", entry.name)
    return count


def _django_setup():
    """Initialise Django — safe to call multiple times."""
    try:
        import django
        django.setup()
    except Exception:
        pass


def start_scheduler():
    """Block and run the APScheduler loop.

    Called when the module is executed as ``__main__``.
    """
    _django_setup()

    from django_fusion.tasks.registry import task_registry
    task_registry.autodiscover()

    scheduler = _build_scheduler()
    if scheduler is None:
        logger.error("Cannot start scheduler — APScheduler not available.")
        sys.exit(1)

    registered = register_scheduled_tasks(scheduler)
    if registered == 0:
        logger.warning("No scheduled tasks discovered.")

    scheduler.start()
    logger.info("Scheduler started with %d task(s).", registered)

    def _shutdown(_signum, _frame):
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        # Keep the main thread alive while the scheduler runs in the
        # background.
        import time
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    start_scheduler()
