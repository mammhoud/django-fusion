"""POS Cloud — WebSocket sync-events parity contract tests.

Pins the exact JSON shapes of the ``/ws/sync-events/`` protocol — the
WebSocket counterpart of ``test_dashboard_contract.py`` — so the Astro
frontend client (``frontend/src/api/sync-events.ts``) and any terminal
client can rely on a stable wire format.

The frames below are the *documented* contract (README, "WebSocket
sync-events stream") and must stay byte-for-byte compatible::

    → {"type": "identify", "payload": {"branch_code": "BR001", "node_id": "n-1"}}
    ← {"type": "identify_ack", "branch_code": "BR001", "node_id": "n-1", "status": "registered"}
    ← {"entity_type": "products", "synced": 3, "branch": "…", "node_id": "…", "timestamp": "…"}  // sync_event (all clients)
    ← {"type": "broker_message", "message": {"subtype": "entity_event", "payload": {…}}}         // branch group only

Frames covered::

    identify → identify_ack          (exact keys + echo of identity)
    sync_event (global group)        (raw payload — NO envelope)
    broker_message (branch group)    (envelope: {type, message})
    error frame                      (malformed identify / invalid JSON)

Isolation notes
---------------
Two pieces of state are process-global and can leak between tests in the
same run: the ``apps.domain.sync_broker.broker`` singleton and the
``InMemoryChannelLayer``. Each test flushes the channel layer and resets
the broker's connection registry (see ``test_ws_sync_events.py`` for the
same pattern).
"""

from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase

from apps.core.models import Branch, Organization
from apps.domain.sync_broker import BrokerMessage, broker
from apps.handlers.consumers import SyncEventConsumer


def _flush_channel_layer() -> None:
    """Drop all channels/groups from the in-memory channel layer."""
    layer = get_channel_layer()
    if layer is not None and hasattr(layer, "flush"):
        async_to_sync(layer.flush)()


class SyncEventsParityContractTests(TransactionTestCase):
    """Every sync-events frame matches its documented README shape."""

    def setUp(self):
        self.org = Organization.objects.create(name="Parity Org", slug="parity-org")
        self.branch = Branch.objects.create(
            organization=self.org, name="Parity Branch", code="PR001",
            node_id="node-1", pos_type="formint-pos",
        )
        _flush_channel_layer()
        broker.reset()  # clears connection registry, keeps ready() handlers

    def tearDown(self):
        broker.reset()
        _flush_channel_layer()
        super().tearDown()

    async def _connect(self, identify: dict | None = None) -> WebsocketCommunicator:
        communicator = WebsocketCommunicator(
            SyncEventConsumer.as_asgi(), "/ws/sync-events/"
        )
        connected, _subprotocol = await communicator.connect()
        self.assertTrue(connected, "WebSocket connect should succeed")
        if identify is not None:
            await communicator.send_json_to({"type": "identify", "payload": identify})
            ack = await communicator.receive_json_from(timeout=5)
            self.assertEqual(ack["type"], "identify_ack")
        return communicator

    # ── identify → identify_ack ──────────────────────────────────────────

    async def test_identify_ack_matches_readme(self):
        """identify yields the exact ack documented in the README."""
        comm = await self._connect()  # raw connect — we assert the ack below
        try:
            await comm.send_json_to({
                "type": "identify",
                "payload": {"branch_code": "PR001", "node_id": "node-1"},
            })
            frame = await comm.receive_json_from(timeout=5)
            # The ack is fully deterministic → exact equality, mirroring the
            # REST contract's conflict-resolve assertion.
            self.assertEqual(frame, {
                "type": "identify_ack",
                "branch_code": "PR001",
                "node_id": "node-1",
                "status": "registered",
            })
            self.assertEqual(set(frame), {
                "type", "branch_code", "node_id", "status",
            })
        finally:
            await comm.disconnect()

    async def test_identify_ack_always_carries_node_id(self):
        """An identify without node_id still yields node_id in the ack."""
        comm = await self._connect()
        try:
            await comm.send_json_to({
                "type": "identify",
                "payload": {"branch_code": "PR001"},
            })
            frame = await comm.receive_json_from(timeout=5)
            self.assertEqual(frame, {
                "type": "identify_ack",
                "branch_code": "PR001",
                "node_id": "",
                "status": "registered",
            })
        finally:
            await comm.disconnect()

    # ── sync_event — global group, raw payload (no envelope) ──────────────

    async def test_sync_event_payload_matches_readme(self):
        """Global broadcasts arrive as the raw payload — no envelope keys.

        The README documents the sync_event frame as the bare
        ``{entity_type, synced, branch, node_id, timestamp}`` object;
        this is what ``sync_api._broadcast_sync_event`` puts on the
        ``sync_events`` group and what the consumer forwards verbatim.
        """
        comm = await self._connect()  # connected, no identify needed
        try:
            data = {
                "entity_type": "products",
                "synced": 3,
                "branch": self.branch.name,
                "node_id": "node-1",
                "timestamp": "2026-01-01T00:00:00Z",
            }
            layer = get_channel_layer()
            await layer.group_send(
                "sync_events",
                {"type": "sync_event", "data": data},
            )

            frame = await comm.receive_json_from(timeout=5)
            # Exact shape — the payload must pass through untouched.
            self.assertEqual(frame, data)
            # And it must NOT be wrapped in a {type, ...} envelope.
            self.assertEqual(set(frame), {
                "entity_type", "synced", "branch", "node_id", "timestamp",
            })
            self.assertEqual(frame["entity_type"], "products")
            self.assertEqual(frame["synced"], 3)
        finally:
            await comm.disconnect()

    # ── broker_message — branch group, enveloped ─────────────────────────

    async def test_broker_message_envelope_matches_readme(self):
        """Branch-group pushes arrive wrapped in {type, message}.

        ``broker.push_to_branch()`` sends ``BrokerMessage.to_dict()`` as
        the event data; the consumer re-wraps it as
        ``{"type": "broker_message", "message": <to_dict>}`` — the
        envelope documented in the README.
        """
        comm = await self._connect({"branch_code": "PR001", "node_id": "node-1"})
        try:
            message = BrokerMessage(
                type="entity_event",
                payload={"entity_type": "products", "action": "sync", "count": 2},
            )
            layer = get_channel_layer()
            # Exactly the event broker.push_to_branch() puts on the layer.
            await layer.group_send(
                "branch_PR001",
                {"type": "broker_message", "data": message.to_dict()},
            )

            frame = await comm.receive_json_from(timeout=5)
            # Outer envelope — exactly two keys.
            self.assertEqual(set(frame), {"type", "message"})
            self.assertEqual(frame["type"], "broker_message")

            # Inner message — the full BrokerMessage.to_dict() shape.
            inner = frame["message"]
            self.assertEqual(set(inner), {
                "type", "subtype", "payload", "source_node_id",
                "target_branch_code", "message_id", "timestamp",
            })
            self.assertEqual(inner["type"], "broker_message")
            self.assertEqual(inner["subtype"], "entity_event")
            self.assertEqual(inner["payload"], {
                "entity_type": "products", "action": "sync", "count": 2,
            })
            self.assertEqual(inner["source_node_id"], "")
            self.assertEqual(inner["target_branch_code"], "")
            self.assertIsInstance(inner["message_id"], str)
            self.assertTrue(inner["message_id"])
            self.assertIsInstance(inner["timestamp"], str)
            self.assertTrue(inner["timestamp"])
        finally:
            await comm.disconnect()

    # ── error frame ───────────────────────────────────────────────────────

    async def test_error_frame_shape_missing_branch_code(self):
        """A malformed identify yields the documented error frame."""
        comm = await self._connect()
        try:
            await comm.send_json_to({"type": "identify", "payload": {"node_id": "x"}})
            frame = await comm.receive_json_from(timeout=5)
            self.assertEqual(set(frame), {"type", "payload"})
            self.assertEqual(frame["type"], "error")
            self.assertEqual(set(frame["payload"]), {"message"})
            self.assertIn("branch_code", frame["payload"]["message"])
        finally:
            await comm.disconnect()

    async def test_error_frame_shape_invalid_json(self):
        """Non-JSON input yields the same error envelope."""
        comm = await self._connect()
        try:
            await comm.send_to(text_data="not-json{")
            frame = await comm.receive_json_from(timeout=5)
            self.assertEqual(set(frame), {"type", "payload"})
            self.assertEqual(frame["type"], "error")
            self.assertEqual(set(frame["payload"]), {"message"})
        finally:
            await comm.disconnect()
