"""Celery tasks for the shared worker.

This module defines Celery tasks that run in the ``shared-scheduler``
container and are consumed by per-site Celery workers (``ctc-worker``,
``lms-worker``, ``vresume-worker``). The primary task is a periodic
heartbeat that verifies the Celery beat scheduler is alive and
functioning.

Auto-discovered by ``www.worker.celery`` via
``app.autodiscover_tasks(lambda: ["www.worker"])``.

The heartbeat task is wired into celery-beat via a data migration
so it ships with a reproducible schedule and survives container
restarts.

Heartbeat task
--------------
A 30-second periodic task. Two writes per fire so log-volume rise
is provable from EITHER channel:

  1. **INFO log line** ("celery beat heartbeat fired at <UTC>") via
     standard Python logger (captured by Docker logs / log aggregator).

  2. **Marker file** at ``/app/logs/celery_beat_heartbeat.txt`` —
     APPENDED per fire (one line per beat), so ``wc -l`` equals the
     count of beats since container start. The marker survives
     container log buffering / logrotate, so absence == "beat is broken".

Heartbeat routing
-----------------
Celery beat (in ``shared-scheduler``) sends this task to the broker
keyed on the ``queue`` field of the PeriodicTask row in the
``django_celery_beat`` table (currently ``fusion-cms``).

- ``shared-worker`` is Dramatiq-only and ignores Celery tasks.
- Per-site Celery workers (``ctc-worker``, ``lms-worker``,
  ``vresume-worker``) consume their site-named queue.

Run ``make logs-tasks`` after ``make deploy-tasks`` to verify the
heartbeat is firing correctly.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from celery import shared_task

logger = logging.getLogger(__name__)

HEARTBEAT_MARKER = "/app/logs/celery_beat_heartbeat.txt"


@shared_task(
    name="www.worker.tasks.heartbeat",
    # Matches the queue field on the PeriodicTask row so this is
    # consistent on inspection. Beat will route by the row's queue
    # anyway, but this decorator default is documentation-as-code.
    queue="fusion-cms",
    bind=True,
    max_retries=0,
    acks_late=False,
)
def heartbeat(self):  # noqa: D401 — Celery ``bind=True`` signature
    """Celery beat periodic heartbeat task.

    Fires every 30 seconds (configured via django-celery-beat
    PeriodicTask). Produces two evidence channels so operators can
    verify the beat scheduler is alive:

    1. An ``INFO`` log line with the current UTC timestamp.
    2. A marker file at ``HEARTBEAT_MARKER`` appended per fire.

    The heartbeat runs on the ``fusion-cms`` queue and is consumed
    by the per-site Celery workers. The ``shared-worker`` Dramatiq
    container ignores this task entirely.

    Args:
        self: Celery task instance (injected via ``bind=True``).

    Returns:
        ISO-8601 UTC timestamp string (e.g.
        ``"2026-07-18T12:34:56.789000+00:00"``). Celery records
        this in ``django_celery_results`` when
        ``CELERY_RESULT_BACKEND`` is configured.

    Note:
        If the marker file cannot be written, the ``OSError`` is
        caught and logged as a warning — a transient disk issue
        should not take the worker out of the schedule. The task
        still returns the timestamp successfully.
    """
    now = datetime.now(timezone.utc)
    ts = now.isoformat()

    logger.info("celery beat heartbeat fired at %s", ts)

    try:
        # Append (not truncate) so the file grows into a fire-history
        # log; ``wc -l /app/logs/celery_beat_heartbeat.txt`` then equals
        # the number of beats since container start.
        with open(HEARTBEAT_MARKER, "a", encoding="utf-8") as fh:
            fh.write(f"{ts}\n")
    except OSError as exc:
        # Don't raise — the log line is enough proof; a flakey disk
        # shouldn't take the worker out of the schedule. Just warn.
        logger.warning("heartbeat could not write marker: %s", exc)

    return ts
