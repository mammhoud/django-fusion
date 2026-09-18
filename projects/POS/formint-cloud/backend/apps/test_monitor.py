"""Tests for the /monitor/status endpoint (Cloud Task C3)."""

import json

from django.test import TestCase
from django.urls import reverse

from apps.core.models import BackupRun, Branch, Organization, SyncQueueItem


class MonitorStatusTest(TestCase):
    """GET /monitor/status — health summary for the cloud master."""

    def setUp(self):
        # SyncQueueItem requires a Branch, which requires an Organization.
        self.org = Organization.objects.create(name="Test Org")
        self.branch = Branch.objects.create(
            name="Test Branch",
            code="TST01",
            organization=self.org,
            pos_type="standard",
        )

    def test_healthy_with_no_backups(self):
        """Fresh deployment: DB is ok, no backups recorded, queue empty."""
        resp = self.client.get(reverse("monitor-status"))
        assert resp.status_code == 200
        payload = json.loads(resp.content)
        assert payload["database"] == "ok"
        assert payload["last_backup"] is None
        assert payload["sync_queue_depth"] == 0

    def test_reports_latest_backup(self):
        """The latest BackupRun is surfaced with filename, status, size, timestamp."""
        BackupRun.objects.create(
            filename="pos_cloud-20260809-120000.db",
            status="success",
            size_bytes=128,
        )
        BackupRun.objects.create(
            filename="pos_cloud-20260809-130000.db",
            status="failed",
            error_message="disk full",
        )
        resp = self.client.get(reverse("monitor-status"))
        payload = json.loads(resp.content)
        assert payload["database"] == "ok"
        backup = payload["last_backup"]
        assert backup is not None
        assert backup["status"] == "failed"
        assert backup["filename"] == "pos_cloud-20260809-130000.db"
        assert backup["size_bytes"] is None
        assert "started_at" in backup

    def test_reports_queue_depth(self):
        """Pending sync queue items are counted."""
        SyncQueueItem.objects.create(
            branch=self.branch,
            node_id="node-1",
            entity_type="products",
            payload={},
            status="pending",
        )
        SyncQueueItem.objects.create(
            branch=self.branch,
            node_id="node-2",
            entity_type="sales",
            payload={},
            status="pending",
        )
        resp = self.client.get(reverse("monitor-status"))
        payload = json.loads(resp.content)
        assert payload["database"] == "ok"
        assert payload["sync_queue_depth"] == 2


class MonitorFragmentTest(TestCase):
    """GET /fusion/monitor — django-fusion monitor tile fragment (Cloud C5)."""

    def setUp(self):
        self.org = Organization.objects.create(name="Test Org")
        self.branch = Branch.objects.create(
            name="Test Branch",
            code="TST01",
            organization=self.org,
            pos_type="standard",
        )

    def test_monitor_fragment_renders(self):
        """The monitor fragment renders the latest backup filename."""
        BackupRun.objects.create(
            filename="pos_cloud-20260809-120000.db",
            status="success",
            size_bytes=128,
        )
        resp = self.client.get("/fusion/monitor")
        assert resp.status_code == 200
        assert "pos_cloud-20260809-120000.db" in resp.content.decode()

    def test_monitor_fragment_reports_queue_depth(self):
        """The monitor fragment surfaces pending sync queue depth."""
        SyncQueueItem.objects.create(
            branch=self.branch,
            node_id="node-1",
            entity_type="products",
            payload={},
            status="pending",
        )
        resp = self.client.get("/fusion/monitor")
        assert resp.status_code == 200
        body = resp.content.decode()
        assert "Sync queue depth" in body
        assert 'fusion-monitor-tile__queue">1<' in body

    def test_monitor_fragment_empty_state(self):
        """No backups recorded yet — fragment still renders 200."""
        resp = self.client.get("/fusion/monitor")
        assert resp.status_code == 200
        assert "No backups recorded yet" in resp.content.decode()
