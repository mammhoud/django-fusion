"""
BranchSyncScheduler → OutboxQueue handoff tests.

Covers the failure-path wiring: when a scheduled cloud push fails, the
scheduler persists the payload into the durable ``OutboxQueue`` so the
offline queue's flush/backoff machinery retries it once the cloud master is
reachable again.

The sync ``_enqueue_failed_push_sync`` method is exercised directly (no
threadpool) because the async ``_enqueue_failed_push`` wraps it with
``sync_to_async`` — which runs in a separate thread and therefore cannot see
the in-memory SQLite database these tests use.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clean_outbox(django_bootstrap):
    from models.outbox import OutboxQueue

    OutboxQueue.objects.all().delete()
    yield


def _scheduler(node_id: str = "test-node"):
    from services.scheduler import BranchSyncScheduler

    return BranchSyncScheduler(enabled=False, node_id=node_id)


class TestEnqueueFailedPush:
    def test_creates_pending_outbox_entry(self):
        from models.outbox import OutboxQueue

        payload = {"node_id": "test-node", "products": [{"id": 1, "name": "Latte"}]}
        assert _scheduler()._enqueue_failed_push_sync("products", payload) is True

        entry = OutboxQueue.objects.get(node_id="test-node", entity_type="products")
        assert entry.status == "pending"
        assert entry.action == "push"
        assert entry.payload == payload

    def test_dedupes_existing_pending_entry(self):
        from models.outbox import OutboxQueue

        scheduler = _scheduler()
        payload = {"node_id": "test-node", "products": [{"id": 1}]}

        assert scheduler._enqueue_failed_push_sync("products", payload) is True
        # A second failure for the same entity_type is not re-enqueued.
        assert scheduler._enqueue_failed_push_sync("products", payload) is False
        assert OutboxQueue.objects.filter(
            node_id="test-node", entity_type="products"
        ).count() == 1

    def test_dedup_scoped_per_entity_type(self):
        from models.outbox import OutboxQueue

        scheduler = _scheduler()
        scheduler._enqueue_failed_push_sync("products", {"products": []})
        scheduler._enqueue_failed_push_sync("sales", {"sales": []})

        assert OutboxQueue.objects.filter(entity_type="products").count() == 1
        assert OutboxQueue.objects.filter(entity_type="sales").count() == 1

    def test_reenqueues_after_entry_is_done(self):
        from models.outbox import OutboxQueue

        scheduler = _scheduler()
        scheduler._enqueue_failed_push_sync("products", {"products": []})
        # Once the entry is flushed, a later failure re-enqueues fresh.
        OutboxQueue.objects.update(status="done")

        assert scheduler._enqueue_failed_push_sync("products", {"products": []}) is True
        assert OutboxQueue.objects.filter(
            entity_type="products", status="pending"
        ).count() == 1


class TestAsyncWrapper:
    def test_delegates_to_sync_method(self, monkeypatch):
        import asyncio

        scheduler = _scheduler()
        calls: list = []
        scheduler._enqueue_failed_push_sync = lambda et, p: calls.append((et, p)) or True

        asyncio.run(scheduler._enqueue_failed_push("sales", {"sales": [{"id": 2}]}))

        assert calls == [("sales", {"sales": [{"id": 2}]})]
