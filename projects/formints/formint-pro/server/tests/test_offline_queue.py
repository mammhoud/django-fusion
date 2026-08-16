"""
Offline Queue (P1) — OutboxQueue enqueue/flush/backoff/dead-letter tests.

Covers ``services.outbox.OfflineQueueService``: durable enqueue, offline
flush (failed + backoff), backoff gating, dead-letter at max retries,
successful flush, and re-queue of dead entries.
"""

from __future__ import annotations

import pytest


def _svc(base_url=""):
    import services.outbox as ob

    return ob.OfflineQueueService(base_url=base_url)


@pytest.fixture(autouse=True)
def _clean_outbox(django_bootstrap):
    from models.outbox import OutboxQueue

    OutboxQueue.objects.all().delete()
    yield
    OutboxQueue.objects.all().delete()


class TestEnqueue:
    def test_enqueue_creates_pending_entry(self):
        item = _svc().enqueue("sale", entity_id="42", payload={"total": 9.5})
        assert item.status == "pending"
        assert item.entity_type == "sale"
        assert item.payload == {"total": 9.5}

    def test_stats_counts(self):
        svc = _svc()
        svc.enqueue("sale", entity_id="1")
        svc.enqueue("product", entity_id="2")
        stats = svc.stats()
        assert stats["pending"] == 2
        assert stats["total"] == 2


class TestFlushOffline:
    def test_offline_flush_marks_failed_with_backoff(self):
        from models.outbox import OutboxQueue

        svc = _svc(base_url="")  # offline
        item = svc.enqueue("sale", entity_id="42")
        result = svc.flush()
        assert result["pushed"] == 0
        assert result["failed"] == 1

        item.refresh_from_db()
        assert item.status == "failed"
        assert item.retry_count == 1
        assert item.last_error == "offline"
        assert item.available_at is not None

    def test_backoff_gates_not_due_entries(self):
        from models.outbox import OutboxQueue

        svc = _svc(base_url="")
        item = svc.enqueue("sale", entity_id="42")
        svc.flush()  # fails once, sets available_at in the future
        result = svc.flush()  # should skip (not due yet)
        assert result["failed"] == 0
        assert result["pushed"] == 0

        # Once the backoff window elapses, it becomes due again.
        from django.utils import timezone
        from datetime import timedelta

        OutboxQueue.objects.filter(id=item.id).update(
            available_at=timezone.now() - timedelta(seconds=1)
        )
        result = svc.flush()
        assert result["failed"] == 1

    def test_dead_letter_after_max_retries(self):
        from models.outbox import OutboxQueue

        svc = _svc(base_url="")
        item = svc.enqueue("sale", entity_id="42", max_retries=1)
        result = svc.flush()
        assert result["dead_lettered"] == 1

        item.refresh_from_db()
        assert item.status == "dead"
        assert item.retry_count == 1


class TestFlushSuccess:
    def test_successful_flush_marks_done(self, monkeypatch):
        from models.outbox import OutboxQueue

        svc = _svc(base_url="http://cloud.example")
        item = svc.enqueue("sale", entity_id="42")
        monkeypatch.setattr(svc, "push_one", lambda i: (True, ""))
        result = svc.flush()
        assert result["pushed"] == 1

        item.refresh_from_db()
        assert item.status == "done"
        assert item.last_error == ""


class TestRequeue:
    def test_requeue_dead(self):
        from models.outbox import OutboxQueue

        svc = _svc(base_url="")
        item = svc.enqueue("sale", entity_id="42", max_retries=1)
        svc.flush()
        item.refresh_from_db()
        assert item.status == "dead"

        count = svc.requeue_dead()
        assert count == 1
        item.refresh_from_db()
        assert item.status == "pending"
        assert item.retry_count == 0
