"""POS Full — offline queue service (Offline Queue P1).

Drains the ``OutboxQueue`` outbound operations when the cloud master is
reachable, and holds them (with exponential backoff) when it isn't.

* ``enqueue`` — durably record an outbound operation.
* ``flush`` — attempt every due, non-dead entry; mark ``done`` on success,
  ``failed`` + backoff on failure, ``dead`` once ``max_retries`` is exhausted.
* ``stats`` — queue health by status.

The cloud receiver URL is resolved from ``sync_state.json`` then the
``CLOUD_CRM_URL`` environment variable; an empty URL models the offline case
(entries stay pending/failed and retry with backoff).
"""

from __future__ import annotations

import json
import logging
import os
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from models.outbox import OutboxQueue

logger = logging.getLogger("pos.outbox")

_BACKOFF_BASE_SECONDS = 2
_BACKOFF_MAX_SECONDS = 3600


def _backoff_seconds(retry_count: int) -> int:
    return min(_BACKOFF_BASE_SECONDS ** retry_count, _BACKOFF_MAX_SECONDS)


def _cloud_url() -> str:
    """Resolve the cloud receiver URL (sync_state.json > env > empty)."""
    try:
        from pathlib import Path

        state_path = Path(__file__).resolve().parent.parent / "sync_state.json"
        if state_path.exists():
            state = json.loads(state_path.read_text())
            url = state.get("cloud_url") or state.get("api_key")
            if url and not url.startswith("sk_"):
                return str(url).rstrip("/")
    except Exception:
        pass
    return os.environ.get("CLOUD_CRM_URL", "").rstrip("/")


class OfflineQueueService:
    """Durable outbound queue with retry/backoff/dead-letter semantics."""

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url if base_url is not None else _cloud_url())

    # ── Enqueue ──────────────────────────────────────────────────────
    def enqueue(
        self,
        entity_type: str,
        entity_id: str = "",
        action: str = "push",
        payload: dict | None = None,
        node_id: str = "",
        max_retries: int = 10,
    ) -> OutboxQueue:
        return OutboxQueue.objects.create(
            node_id=node_id,
            entity_type=entity_type,
            entity_id=str(entity_id),
            action=action,
            payload=payload or {},
            max_retries=max_retries,
        )

    # ── Flush ────────────────────────────────────────────────────────
    def flush(self, limit: int = 100, node_id: str | None = None) -> dict:
        """Attempt to push due entries; apply backoff/dead-letter on failure."""
        now = timezone.now()
        qs = OutboxQueue.objects.filter(status__in=["pending", "failed"])
        if node_id:
            qs = qs.filter(node_id=node_id)
        # Due = never-attempted (available_at null) OR backoff elapsed.
        due = qs.filter(Q(available_at__isnull=True) | Q(available_at__lte=now))
        due = due.order_by("created_at")[:limit]

        pushed = failed = dead = 0
        for item in due:
            ok, error = self.push_one(item)
            if ok:
                item.status = "done"
                item.retry_count = item.retry_count
                item.last_error = ""
                pushed += 1
            else:
                item.retry_count += 1
                item.last_error = error or "push failed"
                item.last_attempt_at = now
                if item.retry_count >= item.max_retries:
                    item.status = "dead"
                    dead += 1
                else:
                    item.status = "failed"
                    item.available_at = now + timedelta(
                        seconds=_backoff_seconds(item.retry_count)
                    )
                    failed += 1
            item.save(
                update_fields=[
                    "status", "retry_count", "last_error", "last_attempt_at", "available_at",
                ]
            )
        return {"pushed": pushed, "failed": failed, "dead_lettered": dead}

    def push_one(self, item: OutboxQueue) -> tuple[bool, str]:
        """Push one entry to the cloud receiver. Returns ``(ok, error)``.

        Override/monkeypatch in tests. An empty ``base_url`` models the
        offline case (returns ``(False, "offline")``).
        """
        if not self.base_url:
            return False, "offline"
        try:
            import httpx

            url = f"{self.base_url}/api/sync/push/{item.entity_type}"
            resp = httpx.post(
                url,
                json={
                    "node_id": item.node_id,
                    "entity_type": item.entity_type,
                    "entity_id": item.entity_id,
                    "payload": item.payload,
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            return True, ""
        except Exception as exc:  # network / HTTP error = offline
            return False, str(exc)

    # ── Introspection ────────────────────────────────────────────────
    def stats(self) -> dict:
        counts = {}
        for status, _ in OutboxQueue.STATUS_CHOICES:
            counts[status] = OutboxQueue.objects.filter(status=status).count()
        counts["total"] = sum(counts.values())
        counts["cloud_url"] = self.base_url or None
        return counts

    def requeue_dead(self, limit: int = 100) -> int:
        """Re-arm dead-lettered entries (back to pending, reset retries)."""
        dead = list(OutboxQueue.objects.filter(status="dead")[:limit])
        if not dead:
            return 0
        OutboxQueue.objects.filter(id__in=[d.id for d in dead]).update(
            status="pending", retry_count=0, last_error="", available_at=None,
        )
        return len(dead)
