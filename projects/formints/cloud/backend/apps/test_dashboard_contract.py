"""POS Cloud — dashboard API contract tests.

Pins the exact JSON shapes of every ``/api/dashboard/*`` endpoint so
monitoring tools and the frontend can rely on a stable contract,
interchangeable across the surfaces that serve it (the :8767 API layer
and the :8082 admin layer share the same ``apps.handlers.sync_dashboard``
views, so this is the single source of truth for both).

Endpoints covered::

    GET  /api/dashboard/branches/health
    GET  /api/dashboard/branches/{code}/health
    GET  /api/dashboard/queue/summary
    GET  /api/dashboard/queue/by-branch
    GET  /api/dashboard/queue/list/{status}
    POST /api/dashboard/queue/retry/{id}
    POST /api/dashboard/queue/cancel/{id}
    GET  /api/dashboard/conflicts
    GET  /api/dashboard/conflicts/stats
    POST /api/dashboard/conflicts/{id}/resolve
    POST /api/dashboard/conflicts/{id}/dismiss
    GET  /api/dashboard/activity
"""

from __future__ import annotations

from django.test import TestCase
from django.urls import reverse

from apps.core.models import (
    Branch, BranchSyncLog, Organization, SyncConflict, SyncQueueItem,
)


class DashboardContractTests(TestCase):
    """Every dashboard endpoint returns its documented JSON shape."""

    def setUp(self):
        self.org = Organization.objects.create(name="Contract Org", slug="contract-org")
        self.branch = Branch.objects.create(
            organization=self.org, name="Downtown", code="BR001",
            node_id="node-1", pos_type="formint-pos",
        )

        self.queue_item = SyncQueueItem.objects.create(
            branch=self.branch, node_id="node-1",
            entity_type="products", operation="update",
            status=SyncQueueItem.QueueStatus.PENDING,
            attempt_count=0, max_attempts=5, last_error="",
        )
        self.conflict = SyncConflict.objects.create(
            branch=self.branch, node_id="node-1",
            entity_type="products", entity_id="p1",
            resolver_used="auto", reason="price mismatch",
            conflict_fields=[{"field": "price", "local_value": 10, "remote_value": 12}],
            local_data={"price": 10}, remote_data={"price": 12},
            status=SyncConflict.ResolutionStatus.PENDING,
        )
        self.log = BranchSyncLog.objects.create(
            branch=self.branch, node_id="node-1",
            entity_type="products", entity_count=3, status="processed",
        )

    # ── Health ────────────────────────────────────────────────────────

    def test_all_branches_health_shape(self):
        r = self.client.get("/api/dashboard/branches/health")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(set(data), {"branches", "total"})
        self.assertEqual(data["total"], 1)
        branch = data["branches"][0]
        self.assertEqual(set(branch), {
            "id", "name", "code", "node_id", "pos_type",
            "sync_enabled", "online", "connected_terminals",
        })
        self.assertEqual(branch["code"], "BR001")
        self.assertIn(branch["online"], (True, False))
        self.assertIsInstance(branch["connected_terminals"], int)

    def test_single_branch_health_shape(self):
        r = self.client.get("/api/dashboard/branches/BR001/health")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(set(data), {"branch", "websocket"})
        branch = data["branch"]
        self.assertEqual(set(branch), {
            "id", "name", "code", "node_id", "pos_type",
            "is_active", "sync_enabled", "sync_interval",
        })
        ws = data["websocket"]
        self.assertEqual(set(ws), {"online", "connected_terminals", "branch_code"})
        self.assertEqual(ws["branch_code"], "BR001")

    def test_single_branch_health_404(self):
        r = self.client.get("/api/dashboard/branches/NOPE/health")
        self.assertEqual(r.status_code, 404)

    # ── Queue ─────────────────────────────────────────────────────────

    def test_queue_summary_shape(self):
        r = self.client.get("/api/dashboard/queue/summary")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(set(data), {
            "pending", "failed", "total", "estimated_backlog_seconds",
        })
        self.assertEqual(data["pending"], 1)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["estimated_backlog_seconds"], 2)  # pending * 2

    def test_queue_by_branch_shape(self):
        r = self.client.get("/api/dashboard/queue/by-branch")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(set(data), {"branches"})
        entry = data["branches"][0]
        self.assertEqual(set(entry), {"branch", "code", "pending", "failed"})
        self.assertEqual(entry["code"], "BR001")
        self.assertEqual(entry["pending"], 1)

    def test_queue_list_shape(self):
        r = self.client.get("/api/dashboard/queue/list/pending")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(set(data), {"items", "count"})
        self.assertEqual(data["count"], 1)
        item = data["items"][0]
        self.assertEqual(set(item), {
            "id", "branch", "branch_code", "entity_type", "operation",
            "status", "attempt_count", "max_attempts", "last_error",
            "created_at", "next_retry_at",
        })
        self.assertEqual(item["entity_type"], "products")
        self.assertEqual(item["status"], "pending")

    def test_queue_list_unknown_status_falls_back_to_pending(self):
        r = self.client.get("/api/dashboard/queue/list/bogus")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["items"][0]["status"], "pending")

    def test_queue_retry_missing_404(self):
        r = self.client.post("/api/dashboard/queue/retry/99999")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(set(r.json()), {"error"})

    def test_queue_cancel_missing_404(self):
        r = self.client.post("/api/dashboard/queue/cancel/99999")
        self.assertEqual(r.status_code, 404)

    # ── Conflicts ─────────────────────────────────────────────────────

    def test_conflict_list_shape(self):
        r = self.client.get("/api/dashboard/conflicts")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(set(data), {"conflicts", "count"})
        self.assertEqual(data["count"], 1)
        conflict = data["conflicts"][0]
        self.assertEqual(set(conflict), {
            "id", "branch", "branch_code", "node_id", "entity_type",
            "entity_id", "resolver_used", "reason", "conflict_fields",
            "local_data", "remote_data", "created_at",
        })
        self.assertEqual(conflict["entity_type"], "products")
        self.assertEqual(conflict["resolver_used"], "auto")

    def test_conflict_stats_shape(self):
        r = self.client.get("/api/dashboard/conflicts/stats")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(set(data), {
            "pending", "resolved", "dismissed", "total", "by_entity_type",
        })
        self.assertEqual(data["pending"], 1)
        self.assertEqual(data["by_entity_type"], {"products": 1})

    def test_conflict_resolve_shape(self):
        r = self.client.post(
            f"/api/dashboard/conflicts/{self.conflict.id}/resolve",
            data='{"resolution": "use_remote", "notes": "contract"}',
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {
            "status": "resolved",
            "conflict_id": self.conflict.id,
            "resolution": "use_remote",
        })

    def test_conflict_resolve_invalid_resolution_400(self):
        r = self.client.post(
            f"/api/dashboard/conflicts/{self.conflict.id}/resolve",
            data='{"resolution": "nuke"}',
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("error", r.json())

    def test_conflict_dismiss_shape(self):
        r = self.client.post(f"/api/dashboard/conflicts/{self.conflict.id}/dismiss")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {
            "status": "dismissed",
            "conflict_id": self.conflict.id,
        })

    def test_conflict_missing_404(self):
        r = self.client.post("/api/dashboard/conflicts/99999/dismiss")
        self.assertEqual(r.status_code, 404)

    # ── Activity ──────────────────────────────────────────────────────

    def test_activity_shape(self):
        r = self.client.get("/api/dashboard/activity")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(set(data), {"entries"})
        entry = data["entries"][0]
        self.assertEqual(set(entry), {
            "id", "branch", "branch_code", "node_id", "entity_type",
            "entity_count", "status", "error_message", "received_at",
        })
        self.assertEqual(entry["entity_type"], "products")
        self.assertEqual(entry["entity_count"], 3)

    def test_activity_limit_param(self):
        r = self.client.get("/api/dashboard/activity?limit=1")
        self.assertEqual(r.status_code, 200)
        self.assertLessEqual(len(r.json()["entries"]), 1)
