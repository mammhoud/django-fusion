"""Celery tasks for the shared worker.

Auto-discovered by `core/ctc-research/www/worker/celery.py` via
`app.autodiscover_tasks(lambda: ["www.worker"])`. The heartbeat task
is wired into celery-beat via the data migration at
`www/migrations/0007_add_celery_beat_heartbeat.py` so this module's
addition ships with a reproducible schedule.

Heartbeat task
--------------
A 30-second periodic task. Two writes per fire so log-volume rise
is provable from EITHER channel:
  1. INFO log line ("celery beat heartbeat fired at <UTC>") via
     standard structlog/Django logger.
  2. Marker file at /app/logs/celery_beat_heartbeat.txt — APPENDED
     per fire (one line per beat), so `wc -l` equals the count of
     beats since container start. The marker survives container log
     buffering / logrotate, so absence == "beat is broken".


Heartbeat routing
-----------------
Celery beat (in `shared-scheduler`) sends this task to the broker
keyed on the `queue` field of the PeriodicTask row in the
`django_celery_beat` table (currently `ctc-research`, set by the
data migration at `www/core/content/migrations/0004_add_celery_beat_
heartbeat.py`). shared-worker is Dramatiq-only and ignores Celery
tasks; the per-site Celery workers (ctc-worker, lms-worker,
vresume-worker) consume their site-named queue.

Run `make logs-tasks` after `make deploy-tasks` to watch the timeline.
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
    queue="ctc-research",
    bind=True,
    max_retries=0,
    acks_late=False,
)
def heartbeat(self):  # noqa: D401 — Celery `bind=True` signature
    """Beat-driven heartbeat. Returns the UTC ISO-8601 timestamp string.

    Returns:
        ISO-8601 UTC timestamp string. Celery records this in the
        django_celery_results table when CELERY_RESULT_BACKEND is set.
    """
    now = datetime.now(timezone.utc)
    ts = now.isoformat()

    logger.info("celery beat heartbeat fired at %s", ts)

    try:
        # Append (not truncate) so the file grows into a fire-history
        # log; `wc -l /app/logs/celery_beat_heartbeat.txt` then equals
        # the number of beats since container start.
        with open(HEARTBEAT_MARKER, "a", encoding="utf-8") as fh:
            fh.write(f"{ts}\n")
    except OSError as exc:
        # Don't raise — the log line is enough proof; a flakey disk
        # shouldn't take the worker out of the schedule. Just warn.
        logger.warning("heartbeat could not write marker: %s", exc)

    return ts
