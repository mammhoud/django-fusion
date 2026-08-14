"""Shared Dramatiq scheduler heartbeat."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from django_fusion.tasks import task

logger = logging.getLogger(__name__)
HEARTBEAT_MARKER = "/app/logs/dramatiq_scheduler_heartbeat.txt"


@task(
    queue="system",
    schedule="*/1 * * * *",
    max_retries=0,
    actor_name="shared.scheduler.heartbeat",
)
def heartbeat() -> str:
    """Write one observable heartbeat per scheduler minute."""
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info("dramatiq scheduler heartbeat fired at %s", timestamp)
    try:
        with open(HEARTBEAT_MARKER, "a", encoding="utf-8") as marker:
            marker.write(f"{timestamp}\n")
    except OSError as exc:
        logger.warning("Dramatiq heartbeat marker unavailable: %s", exc)
    return timestamp
