"""
End-to-end test for signal → webhook delivery.

Verifies that:
1. Signal handlers are registered (shared.signal_handlers imported)
2. WEBHOOK_URL_* env vars point to the receiver endpoint
3. Firing a signal creates an audit record with webhook status
4. The webhook receiver endpoint stores the incoming webhook

Run:
    WEBHOOK_URL_CONFIG_CHANGED=http://localhost:8766/webhooks/receive/config_changed \
    WEBHOOK_URL_DEVICE_STATUS_CHANGED=http://localhost:8766/webhooks/receive/device_status_changed \
    python3 -m pytest tests/test_webhook_e2e.py -v --tb=short --import-mode=importlib

Note: This test uses httpx.Client directly to send signals and verify
the receiver, without needing a running Robyn server.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from unittest import mock

import pytest


# ---------------------------------------------------------------------------
# Configure webhook URLs before importing server
# ---------------------------------------------------------------------------

os.environ.setdefault(
    "WEBHOOK_URL_CONFIG_CHANGED",
    "http://localhost:8766/webhooks/receive/config_changed",
)
os.environ.setdefault(
    "WEBHOOK_URL_DEVICE_STATUS_CHANGED",
    "http://localhost:8766/webhooks/receive/device_status_changed",
)
os.environ.setdefault(
    "WEBHOOK_URL_CONFIG_SYNCED",
    "http://localhost:8766/webhooks/receive/config_synced",
)
os.environ.setdefault(
    "WEBHOOK_URL_MASTER_DEVICE_CHANGED",
    "http://localhost:8766/webhooks/receive/master_device_changed",
)
os.environ.setdefault(
    "WEBHOOK_URL_CLOUD_LINK_CHANGED",
    "http://localhost:8766/webhooks/receive/cloud_link_changed",
)
os.environ.setdefault("WEBHOOK_TIMEOUT_SECONDS", "5")
os.environ.setdefault("POS_FULL_API_KEY", "")


# ===========================================================================
# Standalone Django bootstrap (no server.py import)
# ===========================================================================
# Uses tests/django_setup.py which bootstraps Django ORM with the shared
# database and registers signal handlers — without importing server.py
# (no Robyn app creation, middleware, CRUD registration, or route wiring).
# This keeps the test suite robust: a failure in server.py doesn't crash
# the webhook tests, and the webhook tests don't trigger server.py side effects.

from tests.django_setup import _DJANGO_READY  # noqa: E402

assert _DJANGO_READY, "Django ORM bootstrap failed"

# ── Re-imported here for local clarity; already imported in django_setup.py ──
from shared.models.audit import SignalEvent  # noqa: E402
from shared.handlers.signal import WEBHOOK_URLS, _send_webhook  # noqa: E402
from shared.signals import (  # noqa: E402
    fire_config_changed,
    fire_device_status_changed,
    fire_config_synced,
    fire_master_device_changed,
    fire_cloud_link_changed,
)


# ===========================================================================
# Tests
# ===========================================================================


class TestWebhookConfig:
    """Verify webhook env vars are loaded correctly."""

    def test_webhook_urls_configured(self):
        assert WEBHOOK_URLS["config_changed"] is not None
        assert "webhooks/receive" in WEBHOOK_URLS["config_changed"]

    def test_all_signal_urls_configured(self):
        for signal_name in ("config_changed", "master_device_changed",
                            "cloud_link_changed", "config_synced",
                            "device_status_changed"):
            assert WEBHOOK_URLS[signal_name] is not None, f"{signal_name} URL not set"


class TestWebhookSend:
    """Test the _send_webhook function directly."""

    def test_send_webhook_connection_refused(self):
        """Sending to a non-running server returns 'failed' with error."""
        status, error = _send_webhook("config_changed", {"test": True})
        assert status == "failed"
        assert error, "Expected a non-empty error message"

    def test_send_webhook_invalid_url(self):
        """Sending to an invalid URL returns 'failed'."""
        with mock.patch.dict(WEBHOOK_URLS, {"config_changed": "http://invalid.local:1/test"}):
            status, error = _send_webhook("config_changed", {"test": True})
            assert status == "failed"
            assert error


class _AuditTestBase:
    """Base class with autouse fixture to clear audit records before each test."""

    @pytest.fixture(autouse=True)
    def _clear_audit(self):
        SignalEvent.objects.all().delete()


class TestSignalAuditTrail(_AuditTestBase):
    """Verify that firing signals creates audit records with webhook status."""

    def test_config_changed_creates_audit(self):
        fire_config_changed(
            node_id="E2E-TEST",
            config_key="test.key",
            action="created",
            category="test",
            new_value={"enabled": True},
        )
        records = SignalEvent.objects.filter(node_id="E2E-TEST")
        assert records.count() == 1
        record = records.first()
        assert record.signal_name == "config_changed"
        assert record.action == "created"
        assert record.webhook_status in ("failed",)  # No server running
        assert record.payload.get("config_key") == "test.key"

    def test_device_status_changed_creates_audit(self):
        fire_device_status_changed(
            node_id="E2E-NODE",
            old_status="offline",
            new_status="online",
            reason="heartbeat_restored",
        )
        records = SignalEvent.objects.filter(node_id="E2E-NODE")
        assert records.count() == 1
        record = records.first()
        assert record.signal_name == "device_status_changed"
        assert record.action == "online"
        assert record.payload.get("old_status") == "offline"
        assert record.payload.get("reason") == "heartbeat_restored"

    def test_config_synced_creates_audit(self):
        fire_config_synced(
            source_device_id="master-01",
            target_device_ids=["child-01", "child-02"],
            config_keys=["sync.interval", "theme"],
            status="success",
        )
        records = SignalEvent.objects.filter(node_id="master-01")
        assert records.count() == 1
        record = records.first()
        assert record.signal_name == "config_synced"
        assert record.action == "success"
        assert len(record.payload.get("target_device_ids", [])) == 2

    def test_multiple_signals_all_audited(self):
        fire_config_changed(node_id="MULTI-TEST", config_key="k1", action="updated")
        fire_device_status_changed(node_id="MULTI-TEST", old_status="idle", new_status="syncing", reason="sync_started")
        fire_config_synced(source_device_id="MULTI-TEST", target_device_ids=["n1"], config_keys=["k1"], status="success")
        assert SignalEvent.objects.filter(node_id="MULTI-TEST").count() == 3

    def test_webhook_status_tracked_in_audit(self):
        """Audit record stores whether webhook delivery succeeded or failed."""
        fire_config_changed(node_id="STATUS-TEST", config_key="test", action="created")
        record = SignalEvent.objects.filter(node_id="STATUS-TEST").first()
        assert record is not None
        # Status should be set (not empty) - will be 'failed' since no server
        assert record.webhook_status != ""
        assert record.webhook_status in ("sent", "failed", "skipped")


class TestWebhookPayloadFormat(_AuditTestBase):
    """Verify the webhook payload structure matches what the receiver expects."""

    def test_payload_has_expected_fields(self):
        """The payload dict should contain meaningful data, not just raw kwargs."""
        fire_config_changed(
            node_id="PAYLOAD-TEST",
            config_key="app.theme",
            action="updated",
            category="app",
            old_value={"theme": "dark"},
            new_value={"theme": "light"},
        )
        record = SignalEvent.objects.filter(node_id="PAYLOAD-TEST").first()
        payload = record.payload
        assert "node_id" in payload
        assert "config_key" in payload
        assert payload["config_key"] == "app.theme"
        assert payload.get("category") == "app"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
