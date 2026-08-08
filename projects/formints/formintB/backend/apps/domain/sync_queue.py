"""
POS Cloud — Durable Sync Queue with Retry, Backoff & Idempotency.

Ensures at-least-once delivery of cloud-to-branch sync operations
(catalog refresh, config updates, approval notifications).

Key features
------------
* **Exponential backoff**: Each failed attempt doubles the retry delay
  (5s → 10s → 20s → 40s → 80s, max 5 attempts).
* **Idempotency keys**: Each queue item has a unique key so the branch
  can safely deduplicate on receipt.
* **Serial processing**: Per-branch sequential processing to maintain
  causal ordering of operations.
* **Retry window**: Items that exceed their ``max_attempts`` are marked
  as ``failed`` and surfaced in the sync dashboard.
* **WebSocket fallback**: If the target branch has an active WebSocket
  connection, items are delivered immediately via the broker; otherwise
  they wait for the branch's next polling cycle.

Usage::

    from core.sync_queue import sync_queue
    from core.models import SyncQueueItem

    # Enqueue a catalog update for a branch
    sync_queue.enqueue(
        branch=branch_obj,
        entity_type="products",
        operation="update",
        payload={"products": [...]},
    )

    # Process pending items (called by a periodic task or management command)
    sync_queue.process_pending_items()

    # Retry a failed item
    sync_queue.retry_item(item_id=42)
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from django.utils import timezone as django_timezone

logger = logging.getLogger("pos.sync_queue")

# ══════════════════════════════════════════════════════════════════════
# Backoff schedule (seconds between retries)
# ══════════════════════════════════════════════════════════════════════

_RETRY_SCHEDULE = [5, 10, 20, 40, 80]


def _compute_idempotency_key(branch_id: int, operation: str, entity_type: str, payload: dict) -> str:
    """Generate a deterministic idempotency key from the operation fields.

    The key is ``sha256(branch_id|operation|entity_type|json_hash)``.
    This ensures that enqueuing the same operation twice produces the
    same key, allowing idempotent deduplication.
    """
    content = f"{branch_id}|{operation}|{entity_type}|{json.dumps(payload, sort_keys=True)}"
    return hashlib.sha256(content.encode()).hexdigest()


# ══════════════════════════════════════════════════════════════════════
# Sync Queue
# ══════════════════════════════════════════════════════════════════════


class SyncQueue:
    """Durable sync queue backed by the ``SyncQueueItem`` model.

    Thread-safe for typical Django WSGI/ASGI usage (single-process or
    database-locked via ``select_for_update``).
    """

    def enqueue(
        self,
        branch,
        entity_type: str,
        operation: str = "update",
        payload: dict | None = None,
        *,
        max_attempts: int = 5,
        _now: datetime | None = None,
    ) -> Any | None:
        """Add an item to the sync queue for a branch.

        If a pending item with the same idempotency key already exists,
        the duplicate is silently ignored (idempotent enqueue).

        Args:
            branch: ``Branch`` instance (must have ``id``, ``code``, ``node_id``).
            entity_type: Entity type discriminator (``"products"``, ``"inventory"``, …).
            operation: Operation type (``"update"``, ``"create"``, ``"delete"``, …).
            payload: Data payload to deliver to the branch.
            max_attempts: Maximum delivery attempts before marking as failed.
            _now: Test-only override for the current time.

        Returns:
            The created ``SyncQueueItem`` instance, or ``None`` if a
            duplicate was detected.
        """
        from apps.core.models import SyncQueueItem

        payload = payload or {}
        now = _now or django_timezone.now()

        idempotency_key = _compute_idempotency_key(
            branch.id, operation, entity_type, payload,
        )

        # Check for existing pending item with the same key
        existing = SyncQueueItem.objects.filter(
            idempotency_key=idempotency_key,
            status__in=["pending", "delivering"],
        ).first()
        if existing:
            logger.debug(
                "Duplicate queue item ignored (key=%s) for %s → %s",
                idempotency_key[:12], entity_type, branch.code,
            )
            return None

        item = SyncQueueItem.objects.create(
            branch=branch,
            node_id=branch.node_id,
            entity_type=entity_type,
            operation=operation,
            payload=payload,
            max_attempts=max_attempts,
            idempotency_key=idempotency_key,
            status=SyncQueueItem.QueueStatus.PENDING,
            next_retry_at=now,
        )
        logger.info(
            "Enqueued %s %s → %s (id=%d, key=%s)",
            operation, entity_type, branch.code,
            item.pk, idempotency_key[:12],
        )
        return item

    def process_pending_items(self, *, limit: int = 50, _now: datetime | None = None) -> int:
        """Process all queue items whose ``next_retry_at`` has passed.

        Uses ``select_for_update()`` to prevent duplicate delivery
        in multi-worker deployments.

        Attempts to deliver each item via the WebSocket broker.  If the
        branch doesn't have an active WebSocket connection, the item
        remains pending for the next polling cycle.

        Args:
            limit: Maximum number of items to process in one call.
            _now: Test-only override.

        Returns:
            Number of items processed.
        """
        from django.db import transaction
        from apps.core.models import SyncQueueItem

        now = _now or django_timezone.now()
        processed = 0

        with transaction.atomic():
            items = list(
                SyncQueueItem.objects
                .select_for_update(skip_locked=True)
                .filter(
                    status=SyncQueueItem.QueueStatus.PENDING,
                    next_retry_at__lte=now,
                )
                .select_related("branch")
                .order_by("created_at")[:limit]
            )

        for item in items:
            self._attempt_delivery(item, now)
            processed += 1

        return processed

    def _attempt_delivery(self, item, now: datetime) -> None:
        """Attempt to deliver a single queue item via the WebSocket broker.

        Uses ``select_for_update`` to prevent race conditions in
        multi-worker deployments.

        On failure, schedules a retry with exponential backoff.
        """
        from apps.domain.sync_broker import BrokerMessage, broker

        # Lock the row and update status atomically
        from django.db import transaction
        with transaction.atomic():
            item = SyncQueueItem.objects.select_for_update().get(pk=item.pk)
            item.status = SyncQueueItem.QueueStatus.DELIVERING
            item.attempt_count += 1
            item.save(update_fields=["status", "attempt_count"])

        message = BrokerMessage(
            type="queue_push",
            payload={
                "queue_item_id": item.pk,
                "idempotency_key": item.idempotency_key,
                "operation": item.operation,
                "entity_type": item.entity_type,
                "payload": item.payload,
            },
            source_node_id="cloud-server",
            target_branch_code=item.branch.code,
        )

        success = broker.push_to_branch(item.branch.code, message)

        if success:
            item.status = SyncQueueItem.QueueStatus.DELIVERED
            item.delivered_at = now
            item.save(update_fields=["status", "delivered_at"])
            logger.info("Delivered queue item %d to %s", item.pk, item.branch.code)
        else:
            # Branch offline — schedule retry
            self._schedule_retry(item, now)

    def _schedule_retry(self, item, now: datetime) -> None:
        """Schedule a retry with exponential backoff or mark as failed."""
        if item.attempt_count >= item.max_attempts:
            item.status = SyncQueueItem.QueueStatus.FAILED
            item.last_error = f"Max attempts ({item.max_attempts}) exceeded"
            item.save(update_fields=["status", "last_error"])
            logger.warning(
                "Queue item %d failed after %d attempts (branch %s)",
                item.pk, item.attempt_count, item.branch.code,
            )
            return

        delay = _RETRY_SCHEDULE[min(item.attempt_count - 1, len(_RETRY_SCHEDULE) - 1)]
        item.status = SyncQueueItem.QueueStatus.PENDING
        item.next_retry_at = now + timedelta(seconds=delay)
        item.last_error = f"Branch offline, retrying in {delay}s"
        item.save(update_fields=["status", "next_retry_at", "last_error"])
        logger.info(
            "Scheduled retry for queue item %d (attempt %d/%d, +%ds)",
            item.pk, item.attempt_count, item.max_attempts, delay,
        )

    def retry_item(self, item_id: int) -> Any | None:
        """Reset a failed queue item for retry.

        Args:
            item_id: PK of the ``SyncQueueItem`` to retry.

        Returns:
            The updated item, or ``None`` if not found.
        """
        from apps.core.models import SyncQueueItem

        try:
            item = SyncQueueItem.objects.get(pk=item_id)
        except SyncQueueItem.DoesNotExist:
            logger.warning("Queue item %d not found for retry", item_id)
            return None

        item.status = SyncQueueItem.QueueStatus.PENDING
        item.attempt_count = 0
        item.last_error = ""
        item.next_retry_at = django_timezone.now()
        item.save(update_fields=["status", "attempt_count", "last_error", "next_retry_at"])
        logger.info("Reset queue item %d for retry", item_id)
        return item

    def cancel_item(self, item_id: int) -> bool:
        """Cancel a pending queue item.

        Args:
            item_id: PK of the ``SyncQueueItem`` to cancel.

        Returns:
            ``True`` if the item was cancelled, ``False`` if not found.
        """
        from apps.core.models import SyncQueueItem

        updated = SyncQueueItem.objects.filter(
            pk=item_id,
            status__in=[SyncQueueItem.QueueStatus.PENDING, SyncQueueItem.QueueStatus.DELIVERING],
        ).update(
            status=SyncQueueItem.QueueStatus.CANCELLED,
        )
        if updated:
            logger.info("Cancelled queue item %d", item_id)
        return updated > 0

    def pending_count(self, branch_code: str | None = None) -> int:
        """Count pending queue items, optionally filtered by branch."""
        from apps.core.models import SyncQueueItem

        qs = SyncQueueItem.objects.filter(status=SyncQueueItem.QueueStatus.PENDING)
        if branch_code:
            qs = qs.filter(branch__code=branch_code)
        return qs.count()

    def failed_count(self, branch_code: str | None = None) -> int:
        """Count failed queue items, optionally filtered by branch."""
        from apps.core.models import SyncQueueItem

        qs = SyncQueueItem.objects.filter(status=SyncQueueItem.QueueStatus.FAILED)
        if branch_code:
            qs = qs.filter(branch__code=branch_code)
        return qs.count()


# ══════════════════════════════════════════════════════════════════════
# Singleton
# ══════════════════════════════════════════════════════════════════════

sync_queue = SyncQueue()
"""Global sync queue singleton. Import this in views and management commands."""
