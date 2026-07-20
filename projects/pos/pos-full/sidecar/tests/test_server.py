"""
Test suite for POS Full Server — models, CRUD, node registry, and sync.

Covers:
  - Node registry models (Node, Heartbeat, NodeEvent, SyncLog)
  - CRUD operations via sync_to_async helpers
  - Serialization helpers
  - Edge cases & constraints

Usage:
    cd pos-full/sidecar
    DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/test_server.py -v --tb=short
"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path

# Ensure Django settings module is empty so our bootstrap runs
os.environ.pop("DJANGO_SETTINGS_MODULE", None)

# Ensure we're in the sidecar directory
_SIDECAR_DIR = Path(__file__).resolve().parent.parent  # sidecar/
if str(_SIDECAR_DIR) not in sys.path:
    sys.path.insert(0, str(_SIDECAR_DIR))

# Add projects/pos/ to path for shared module
_POS = _SIDECAR_DIR.parent.parent  # pos/
if str(_POS) not in sys.path:
    sys.path.insert(0, str(_POS))

# ---------------------------------------------------------------------------
# Django ORM bootstrap (in-memory database — independent of other test files)
# ---------------------------------------------------------------------------

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
        SECRET_KEY="test-secret-key",
    )
    django.setup()

from django.db import connection
from asgiref.sync import async_to_sync
from django.test import TestCase
from models.node import Node, Heartbeat, NodeEvent
from models.config import DeviceConfig, MasterDevice, CloudLink
from models.sync import SyncLog
from shared.models.audit import SignalEvent
from shared.models.token import DeviceToken
from shared.models.approval import SyncApproval
from models.inventory import Supplier, PurchaseOrder, PurchaseOrderItem
from models.ops import KitchenTicket, SupportTicket
from shared.__about__ import __version__

# Create tables for all managed=True models
_TABLES = [
    Node, Heartbeat, NodeEvent, SyncLog,
    DeviceConfig, MasterDevice, CloudLink,
    SyncApproval, DeviceToken, SignalEvent,
    Supplier, PurchaseOrder, PurchaseOrderItem,
    KitchenTicket, SupportTicket,
]
existing_tables = []
try:
    existing_tables = connection.introspection.table_names()
except Exception:
    pass
with connection.schema_editor() as schema_editor:
    for model in _TABLES:
        if model._meta.db_table in existing_tables:
            continue
        try:
            schema_editor.create_model(model)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Inline serialization helpers (avoid importing server.py which has its own
# settings.configure() that would conflict with our in-memory test DB)
# ---------------------------------------------------------------------------


def _ser(obj):
    """Serialize a Django model instance to a plain dict."""
    data = {}
    for field in obj._meta.fields:
        val = getattr(obj, field.attname, None)
        if isinstance(val, Decimal):
            val = float(val)
        elif isinstance(val, datetime):
            val = val.isoformat() if val else None
        data[field.attname] = val
    return data


def _ser_node(node):
    """Serialize a Node with all fields."""
    return {
        "node_id": node.node_id,
        "hostname": node.hostname,
        "node_type": node.node_type,
        "version": node.version,
        "api_version": node.api_version,
        "status": node.status,
        "status_message": node.status_message,
        "is_active": node.is_active,
        "product_count": node.product_count,
        "transaction_count": node.transaction_count,
        "customer_count": node.customer_count,
        "ip_address": str(node.ip_address) if node.ip_address else None,
        "port": node.port,
        "capabilities": node.capabilities,
        "metadata": node.metadata,
        "first_seen": node.first_seen.isoformat() if node.first_seen else None,
        "last_seen": node.last_seen.isoformat() if node.last_seen else None,
        "last_synced_at": node.last_synced_at.isoformat() if node.last_synced_at else None,
    }


# ===========================================================================
# Node Registry Tests
# ===========================================================================


class TestNodeModel(TestCase):
    """Tests for the Node registry model."""

    def test_node_creation(self):
        n = Node.objects.create(node_id="NODE-001", hostname="test-host", version="1.0")
        assert n.node_id == "NODE-001"
        assert n.hostname == "test-host"
        assert n.version == "1.0"
        assert n.status == "online"
        assert n.is_active is True
        assert n.first_seen is not None
        assert n.last_seen is not None

    def test_node_unique_node_id(self):
        Node.objects.create(node_id="UNIQUE-NODE")
        with self.assertRaises(Exception):
            Node.objects.create(node_id="UNIQUE-NODE")

    def test_node_defaults(self):
        n = Node.objects.create(node_id="DEF-NODE")
        assert n.version == "unknown"
        assert n.api_version == "1.0"
        assert n.status == "online"
        assert n.node_type == "pos-minimal"
        assert n.product_count == 0
        assert n.transaction_count == 0
        assert n.capabilities == {}
        assert n.metadata == {}

    def test_node_status_choices(self):
        for status, _ in Node.STATUS_CHOICES:
            n = Node.objects.create(node_id=f"STATUS-{status}", status=status)
            n.refresh_from_db()
            assert n.status == status

    def test_node_type_choices(self):
        for nt, _ in Node.NODE_TYPES:
            n = Node.objects.create(node_id=f"TYPE-{nt}", node_type=nt)
            n.refresh_from_db()
            assert n.node_type == nt

    def test_node_mark_offline(self):
        n = Node.objects.create(node_id="OFFLINE-NODE", status="online")
        n.mark_offline("Connection lost")
        n.refresh_from_db()
        assert n.status == "offline"
        assert n.status_message == "Connection lost"

    def test_node_mark_online(self):
        n = Node.objects.create(node_id="ONLINE-NODE", status="offline")
        n.mark_online("Back online")
        n.refresh_from_db()
        assert n.status == "online"
        assert n.status_message == "Back online"

    def test_node_str(self):
        n = Node.objects.create(node_id="STR-NODE", status="online")
        assert str(n) == "STR-NODE (online)"

    def test_node_ip_address(self):
        n = Node.objects.create(node_id="IP-NODE", ip_address="192.168.1.100")
        n.refresh_from_db()
        assert str(n.ip_address) == "192.168.1.100"

    def test_node_port(self):
        n = Node.objects.create(node_id="PORT-NODE", port=8766)
        n.refresh_from_db()
        assert n.port == 8766

    def test_node_capabilities_json(self):
        caps = {"websocket": True, "sync": True, "max_products": 1000}
        n = Node.objects.create(node_id="CAPS-NODE", capabilities=caps)
        n.refresh_from_db()
        assert n.capabilities == caps

    def test_node_metadata_json(self):
        meta = {"location": "kitchen", "version_added": "2.0"}
        n = Node.objects.create(node_id="META-NODE", metadata=meta)
        n.refresh_from_db()
        assert n.metadata == meta

    def test_node_counters(self):
        n = Node.objects.create(
            node_id="CNT-NODE", product_count=42, transaction_count=100, customer_count=25,
        )
        n.refresh_from_db()
        assert n.product_count == 42
        assert n.transaction_count == 100
        assert n.customer_count == 25


class TestHeartbeatModel(TestCase):
    """Tests for the Heartbeat model."""

    def test_heartbeat_creation(self):
        h = Heartbeat.objects.create(node_id="NODE-HB", status="online")
        assert h.node_id == "NODE-HB"
        assert h.status == "online"
        assert h.received_at is not None

    def test_heartbeat_payload(self):
        payload = {"version": "1.0", "product_count": 42}
        h = Heartbeat.objects.create(node_id="NODE-PAYLOAD", payload=payload)
        h.refresh_from_db()
        assert h.payload == payload

    def test_heartbeat_latency(self):
        h = Heartbeat.objects.create(node_id="NODE-LAT", latency_ms=12.5)
        h.refresh_from_db()
        assert h.latency_ms == 12.5

    def test_heartbeat_str(self):
        h = Heartbeat.objects.create(node_id="NODE-STR")
        assert "NODE-STR" in str(h)

    def test_heartbeat_multiple_same_node(self):
        for i in range(5):
            Heartbeat.objects.create(node_id="MULTI-HB", status="online")
        assert Heartbeat.objects.filter(node_id="MULTI-HB").count() == 5

    def test_heartbeat_ordering(self):
        h1 = Heartbeat.objects.create(node_id="ORD-HB")
        time.sleep(0.01)
        h2 = Heartbeat.objects.create(node_id="ORD-HB")
        latest = Heartbeat.objects.first()
        assert latest.id == h2.id


class TestNodeEventModel(TestCase):
    """Tests for the NodeEvent model."""

    def test_event_creation(self):
        e = NodeEvent.objects.create(
            node_id="NODE-EVT", event_type="registered",
            description="Node NODE-EVT registered",
        )
        assert e.node_id == "NODE-EVT"
        assert e.event_type == "registered"
        assert e.created_at is not None

    def test_event_types(self):
        for etype, _ in NodeEvent.EVENT_TYPES:
            e = NodeEvent.objects.create(
                node_id=f"TYPE-{etype}", event_type=etype,
                description=f"Test {etype}",
            )
            e.refresh_from_db()
            assert e.event_type == etype

    def test_event_metadata(self):
        meta = {"hostname": "test-host", "version": "1.0"}
        e = NodeEvent.objects.create(
            node_id="META-EVT", event_type="registered", metadata=meta,
        )
        e.refresh_from_db()
        assert e.metadata == meta

    def test_event_str(self):
        e = NodeEvent.objects.create(
            node_id="STR-EVT", event_type="registered",
        )
        assert "[registered]" in str(e)

    def test_event_ordering(self):
        e1 = NodeEvent.objects.create(node_id="ORD-EVT", event_type="registered")
        time.sleep(0.01)
        e2 = NodeEvent.objects.create(node_id="ORD-EVT", event_type="heartbeat")
        latest = NodeEvent.objects.first()
        assert latest.id == e2.id

    def test_event_filtering(self):
        nid = "FILTER-NODE"
        NodeEvent.objects.create(node_id=nid, event_type="registered")
        NodeEvent.objects.create(node_id=nid, event_type="heartbeat")
        NodeEvent.objects.create(node_id=nid, event_type="status_change")
        assert NodeEvent.objects.filter(event_type="registered").count() == 1
        assert NodeEvent.objects.filter(event_type="heartbeat").count() == 1
        assert NodeEvent.objects.filter(node_id=nid).count() == 3


class TestSyncLogModel(TestCase):
    """Tests for the SyncLog model."""

    def test_sync_log_creation(self):
        s = SyncLog.objects.create(
            node_id="NODE-SYNC", entity_type="product",
            entity_id="PROD-001", status="success",
        )
        assert s.node_id == "NODE-SYNC"
        assert s.entity_type == "product"
        assert s.entity_id == "PROD-001"
        assert s.status == "success"
        assert s.created_at is not None

    def test_sync_log_direction(self):
        for d, _ in SyncLog.SYNC_DIRECTION_CHOICES:
            s = SyncLog.objects.create(
                node_id="DIR-NODE", entity_type="sale",
                entity_id="SALE-001", direction=d, status="success",
            )
            s.refresh_from_db()
            assert s.direction == d

    def test_sync_log_status_choices(self):
        for st, _ in SyncLog.SYNC_STATUS_CHOICES:
            s = SyncLog.objects.create(
                node_id="STS-NODE", entity_type="node",
                entity_id="NODE-001", status=st,
            )
            s.refresh_from_db()
            assert s.status == st

    def test_sync_log_error_message(self):
        s = SyncLog.objects.create(
            node_id="ERR-NODE", entity_type="node",
            entity_id="NODE-001", status="failed",
            error_message="Connection refused",
        )
        s.refresh_from_db()
        assert s.error_message == "Connection refused"

    def test_sync_log_payload_size(self):
        s = SyncLog.objects.create(
            node_id="SIZE-NODE", entity_type="product",
            entity_id="PROD-001", status="success", payload_size=1024,
        )
        s.refresh_from_db()
        assert s.payload_size == 1024

    def test_sync_log_duration_ms(self):
        s = SyncLog.objects.create(
            node_id="DUR-NODE", entity_type="product",
            entity_id="PROD-001", status="success", duration_ms=150,
        )
        s.refresh_from_db()
        assert s.duration_ms == 150

    def test_sync_log_retry_count(self):
        s = SyncLog.objects.create(
            node_id="RET-NODE", entity_type="product",
            entity_id="PROD-001", status="failed", retry_count=3,
        )
        s.refresh_from_db()
        assert s.retry_count == 3


# ===========================================================================
# Cross-model Integration Tests
# ===========================================================================


class TestRegistryIntegration(TestCase):
    """Tests that exercise the full node lifecycle."""

    def test_node_lifecycle(self):
        """Node registered → heartbeat → status change → deleted."""
        n = Node.objects.create(node_id="LIFE-NODE", hostname="life-test", version="1.0")
        assert n.is_active is True

        Heartbeat.objects.create(node_id="LIFE-NODE", status="online")
        assert Heartbeat.objects.filter(node_id="LIFE-NODE").count() == 1

        n.status = "offline"
        n.save()
        NodeEvent.objects.create(
            node_id="LIFE-NODE", event_type="status_change",
            description="Node went offline",
        )

        n.status = "online"
        n.save()
        NodeEvent.objects.create(
            node_id="LIFE-NODE", event_type="heartbeat_restored",
            description="Node restored to online",
        )

        assert NodeEvent.objects.filter(node_id="LIFE-NODE").count() == 2
        n.delete()
        assert Node.objects.filter(node_id="LIFE-NODE").count() == 0

    def test_node_sync_log_association(self):
        """Create a node, push multiple sync events, verify audit trail."""
        Node.objects.create(node_id="SYNC-NODE", hostname="sync-test")

        SyncLog.objects.create(
            node_id="SYNC-NODE", entity_type="product",
            entity_id="P001", status="success",
        )
        SyncLog.objects.create(
            node_id="SYNC-NODE", entity_type="sale",
            entity_id="S001", status="failed",
            error_message="Timeout",
        )

        assert SyncLog.objects.filter(node_id="SYNC-NODE").count() == 2
        assert SyncLog.objects.filter(status="success").count() == 1
        assert SyncLog.objects.filter(status="failed").count() == 1

    def test_heartbeat_events_propagation(self):
        """Heartbeat recorded properly for offline node."""
        Node.objects.create(node_id="HB-NODE", status="offline")
        hb = Heartbeat.objects.create(node_id="HB-NODE", status="online")
        assert hb.node_id == "HB-NODE"


class TestSerializationHelpers(TestCase):
    """Tests for the serialization logic used by CRUD routes."""

    def test_ser_model(self):
        """Verify _ser creates correct dict from model instance."""
        n = Node.objects.create(node_id="SER-NODE", hostname="ser-test", version="2.0")
        data = _ser(n)
        assert data["node_id"] == "SER-NODE"
        assert data["hostname"] == "ser-test"
        assert data["version"] == "2.0"
        assert "first_seen" in data
        assert "last_seen" in data
        assert "created_at" in data

    def test_ser_node_formatted(self):
        """Verify _ser_node returns the rich node dict."""
        n = Node.objects.create(
            node_id="RICH-NODE", hostname="rich-test", version="1.5",
            product_count=42, transaction_count=100,
            ip_address="10.0.0.1", port=8766,
        )
        data = _ser_node(n)
        assert data["node_id"] == "RICH-NODE"
        assert data["hostname"] == "rich-test"
        assert data["version"] == "1.5"
        assert data["product_count"] == 42
        assert data["transaction_count"] == 100
        assert data["ip_address"] == "10.0.0.1"
        assert data["port"] == 8766

    def test_ser_node_render(self):
        """Verify _ser_node works for rendering."""
        n = Node.objects.create(node_id="REND-NODE")
        data = _ser_node(n)
        assert isinstance(data, dict)
        assert data["node_id"] == "REND-NODE"


class TestEdgeCases(TestCase):
    """Edge cases and constraints."""

    def test_long_node_id(self):
        long_id = "NODE-" + "x" * 90
        n = Node.objects.create(node_id=long_id)
        n.refresh_from_db()
        assert len(n.node_id) <= 100
        assert n.node_id == long_id

    def test_empty_heartbeat_payload(self):
        h = Heartbeat.objects.create(node_id="EMPTY-HB", payload={})
        h.refresh_from_db()
        assert h.payload == {}

    def test_event_blank_description_allowed(self):
        e = NodeEvent.objects.create(node_id="BLANK-DESC", event_type="registered")
        e.refresh_from_db()
        assert e.description == ""

    def test_sync_log_retry_max(self):
        s = SyncLog.objects.create(
            node_id="MAX-RET", entity_type="node",
            entity_id="N001", status="failed", retry_count=999,
        )
        s.refresh_from_db()
        assert s.retry_count == 999

    def test_multiple_nodes(self):
        for i in range(10):
            Node.objects.create(
                node_id=f"BULK-NODE-{i:03d}",
                hostname=f"host-{i}",
                status="online" if i % 2 == 0 else "offline",
            )
        assert Node.objects.count() == 10
        assert Node.objects.filter(status="online").count() == 5
        assert Node.objects.filter(status="offline").count() == 5

    def test_node_event_deduplication_same_type(self):
        nid = "DEDUP-NODE"
        for i in range(5):
            NodeEvent.objects.create(
                node_id=nid, event_type="heartbeat",
                description=f"Heartbeat {i}",
            )
        assert NodeEvent.objects.filter(node_id=nid, event_type="heartbeat").count() == 5

    def test_sync_log_empty_error(self):
        s = SyncLog.objects.create(
            node_id="NO-ERR", entity_type="product",
            entity_id="P001", status="success",
        )
        s.refresh_from_db()
        assert s.error_message == ""


# ===========================================================================
# Standalone WebSocket broadcast test helpers (mirrors server.py logic)
# ===========================================================================


class _WSBroadcastState:
    """Container for broadcast test state to avoid module-level scope issues."""
    clients: set = set()
    filters: dict[int, dict] = {}


class MockWebSocket:
    """Minimal mock for testing broadcast logic."""

    def __init__(self, name: str = "mock"):
        self.name = name
        self.sent_messages: list[str] = []
        self.should_fail: bool = False

    async def send_text(self, data: str) -> None:
        if self.should_fail:
            raise ConnectionError(f"{self.name} disconnected")
        self.sent_messages.append(data)

    def __repr__(self) -> str:
        return f"<MockWS {self.name}>"


async def _test_broadcast(event_type: str, node_id: str, data: dict) -> None:
    """Broadcast helper mirroring server.py's _broadcast_node_event for testing."""
    if not _WSBroadcastState.clients:
        return

    payload = json.dumps({
        "type": "node_event",
        "event": event_type,
        "node_id": node_id,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    disconnected: set = set()
    for ws in _WSBroadcastState.clients:
        cid = id(ws)
        f = _WSBroadcastState.filters.get(cid, {})
        if f.get("node_id") and f["node_id"] != node_id:
            continue
        if f.get("event_type") and f["event_type"] != event_type:
            continue
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.add(ws)

    _WSBroadcastState.clients -= disconnected
    for ws in disconnected:
        _WSBroadcastState.filters.pop(id(ws), None)


class TestWebSocketBroadcast(TestCase):
    """Tests for the broadcast helper and client filtering.

    Uses _WSBroadcastState class-level container instead of module-level
    variables to avoid UnboundLocalError in async closures, and
    sync_to_async for Django model access.
    """

    def setUp(self):
        _WSBroadcastState.clients.clear()
        _WSBroadcastState.filters.clear()

    def tearDown(self):
        _WSBroadcastState.clients.clear()
        _WSBroadcastState.filters.clear()

    def _make_event(self, event_type: str, node_id: str) -> dict:
        return {
            "node_id": node_id,
            "hostname": f"{node_id.lower()}.pos.local",
            "status": "online",
            "version": __version__,
            "product_count": 42,
            "node_type": "pos-full",
        }

    # ── Tests ──

    def test_broadcast_sends_to_all_clients(self):
        async def _run():
            ws1 = MockWebSocket("c1")
            ws2 = MockWebSocket("c2")
            _WSBroadcastState.clients.add(ws1)
            _WSBroadcastState.clients.add(ws2)
            _WSBroadcastState.filters[id(ws1)] = {}
            _WSBroadcastState.filters[id(ws2)] = {}

            await _test_broadcast("registered", "NODE-ALL",
                                  self._make_event("registered", "NODE-ALL"))

            assert len(ws1.sent_messages) == 1
            assert len(ws2.sent_messages) == 1
            assert json.loads(ws1.sent_messages[0])["event"] == "registered"
            assert json.loads(ws2.sent_messages[0])["event"] == "registered"
        async_to_sync(_run)()

    def test_broadcast_filter_by_node_id(self):
        async def _run():
            filtered = MockWebSocket("filtered")
            unfiltered = MockWebSocket("all")
            _WSBroadcastState.clients.add(filtered)
            _WSBroadcastState.clients.add(unfiltered)
            _WSBroadcastState.filters[id(filtered)] = {"node_id": "NODE-A"}
            _WSBroadcastState.filters[id(unfiltered)] = {}

            await _test_broadcast("heartbeat", "NODE-B",
                                  self._make_event("heartbeat", "NODE-B"))
            assert len(filtered.sent_messages) == 0
            assert len(unfiltered.sent_messages) == 1

            await _test_broadcast("heartbeat", "NODE-A",
                                  self._make_event("heartbeat", "NODE-A"))
            assert len(filtered.sent_messages) == 1
            assert json.loads(filtered.sent_messages[0])["node_id"] == "NODE-A"
        async_to_sync(_run)()

    def test_broadcast_filter_by_event_type(self):
        async def _run():
            ws = MockWebSocket("evt")
            _WSBroadcastState.clients.add(ws)
            _WSBroadcastState.filters[id(ws)] = {"event_type": "registered"}

            await _test_broadcast("heartbeat", "NODE-EVT", {})
            assert len(ws.sent_messages) == 0

            await _test_broadcast("registered", "NODE-EVT", {"node_id": "NODE-EVT"})
            assert len(ws.sent_messages) == 1
            assert json.loads(ws.sent_messages[0])["event"] == "registered"
        async_to_sync(_run)()

    def test_broadcast_reset_filter(self):
        async def _run():
            ws = MockWebSocket("reset")
            _WSBroadcastState.clients.add(ws)
            _WSBroadcastState.filters[id(ws)] = {"node_id": "NODE-X"}

            await _test_broadcast("heartbeat", "NODE-Y", {})
            assert len(ws.sent_messages) == 0

            _WSBroadcastState.filters[id(ws)] = {}
            await _test_broadcast("heartbeat", "NODE-Y", {"node_id": "NODE-Y"})
            assert len(ws.sent_messages) == 1

            _WSBroadcastState.filters[id(ws)] = {}
            await _test_broadcast("registered", "NODE-Z", {"node_id": "NODE-Z"})
            assert len(ws.sent_messages) == 2
            assert json.loads(ws.sent_messages[1])["event"] == "registered"
        async_to_sync(_run)()

    def test_broadcast_removes_disconnected_clients(self):
        async def _run():
            ok = MockWebSocket("ok")
            bad = MockWebSocket("failing")
            bad.should_fail = True
            _WSBroadcastState.clients.add(ok)
            _WSBroadcastState.clients.add(bad)
            _WSBroadcastState.filters[id(ok)] = {}
            _WSBroadcastState.filters[id(bad)] = {}

            assert len(_WSBroadcastState.clients) == 2
            await _test_broadcast("heartbeat", "NODE-DISC", {})

            assert bad not in _WSBroadcastState.clients
            assert id(bad) not in _WSBroadcastState.filters
            assert ok in _WSBroadcastState.clients
            assert len(ok.sent_messages) == 1
        async_to_sync(_run)()

    def test_broadcast_empty_clients_noop(self):
        async def _run():
            _WSBroadcastState.clients.clear()
            await _test_broadcast("registered", "NODE-NOPE", {})
        async_to_sync(_run)()

    def test_broadcast_payload_structure(self):
        async def _run():
            ws = MockWebSocket("payload")
            _WSBroadcastState.clients.add(ws)
            _WSBroadcastState.filters[id(ws)] = {}

            data = self._make_event("registered", "NODE-PAYLOAD")
            await _test_broadcast("registered", "NODE-PAYLOAD", data)

            assert len(ws.sent_messages) == 1
            p = json.loads(ws.sent_messages[0])
            assert p["type"] == "node_event"
            assert p["event"] == "registered"
            assert p["node_id"] == "NODE-PAYLOAD"
            assert p["data"]["product_count"] == 42
            assert "timestamp" in p
        async_to_sync(_run)()

    def test_broadcast_with_actual_node(self):
        """End-to-end: broadcast a real Node model instance."""
        node = Node.objects.create(
            node_id="E2E-NODE", hostname="e2e-test",
            node_type="pos-full", version=__version__, status="online",
        )
        node_data = _ser_node(node)

        async def _run():
            ws = MockWebSocket("e2e")
            _WSBroadcastState.clients.add(ws)
            _WSBroadcastState.filters[id(ws)] = {}

            await _test_broadcast("registered", node.node_id, node_data)

            assert len(ws.sent_messages) == 1
            p = json.loads(ws.sent_messages[0])
            assert p["event"] == "registered"
            assert p["node_id"] == "E2E-NODE"
            assert p["data"]["hostname"] == "e2e-test"
            assert p["type"] == "node_event"
        async_to_sync(_run)()
