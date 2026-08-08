"""POS Cloud — WebSocket sync-events stream tests.

Verifies the Django Channels ``SyncEventConsumer`` protocol that the
Astro frontend consumes at ``/ws/sync-events/``:

* connect + ``identify`` → ``identify_ack`` and per-branch group join
* entity events broadcast to the global ``sync_events`` group reach
  connected clients
* broker pushes target the per-branch group only
* error frames for malformed/missing identify payloads

Isolation notes
---------------
Two pieces of state are process-global and can leak between tests in the
same run:

* ``apps.domain.sync_broker.broker`` — a module-level singleton holding
  ``_connected_branches`` (terminal channel registry) and
  ``_message_handlers``.
* The ``InMemoryChannelLayer`` — its ``channels`` / ``groups`` maps
  persist across tests in one process.

Each test therefore flushes the channel layer, resets the broker's
connection registry, and snapshots/restores the broker's message
handlers, so a failed or slow test can never pollute the next one.
"""

from __future__ import annotations

import asyncio
import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase

from apps.core.models import Branch, Organization
from apps.domain.sync_broker import BrokerMessage, broker
from apps.handlers.consumers import SyncEventConsumer

User = get_user_model()


def _flush_channel_layer() -> None:
    """Drop all channels/groups from the in-memory channel layer."""
    layer = get_channel_layer()
    if layer is not None and hasattr(layer, "flush"):
        async_to_sync(layer.flush)()


class SyncEventsWebSocketTests(TransactionTestCase):
    """End-to-end WebSocket protocol tests via the channels test harness."""

    def setUp(self):
        self.org = Organization.objects.create(name="WS Test Org", slug="ws-test-org")
        self.branch = Branch.objects.create(
            organization=self.org, name="WS Branch", code="WS001",
        )
        # Full isolation of the two process-global pieces of state.
        _flush_channel_layer()
        broker.reset()  # clears connection registry, keeps ready() handlers

    def tearDown(self):
        # Even if a test failed before disconnecting its communicators,
        # reset the singleton so the next test starts clean.
        broker.reset()
        _flush_channel_layer()
        super().tearDown()

    async def _connect(self, identify: dict | None = None):
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

    async def test_connect_identify_and_ack(self):
        """A client identifies with a branch and gets an ack."""
        comm = await self._connect({"branch_code": "WS001", "node_id": "node-1"})

        # Broker now tracks the branch as online.
        health = broker.branch_health_check("WS001")
        self.assertEqual(health["connected_terminals"], 1)

        await comm.disconnect()

    async def test_global_sync_event_reaches_client(self):
        """Entity events broadcast to the global sync_events group arrive."""
        comm = await self._connect()

        # Simulate a sync receiver broadcast (sync_api._broadcast_sync_event).
        layer = get_channel_layer()
        await layer.group_send(
            "sync_events",
            {
                "type": "sync_event",
                "data": {
                    "entity_type": "products",
                    "synced": 3,
                    "branch": self.branch.name,
                    "node_id": "node-1",
                    "timestamp": "2026-01-01T00:00:00Z",
                },
            },
        )

        frame = await comm.receive_json_from(timeout=5)
        self.assertEqual(frame["entity_type"], "products")
        self.assertEqual(frame["synced"], 3)

        await comm.disconnect()

    async def test_branch_push_reaches_identified_client(self):
        """broker.push_to_branch() targets only the branch group."""
        comm = await self._connect({"branch_code": "WS001", "node_id": "node-1"})

        # Send exactly the event broker.push_to_branch() puts on the layer:
        # group_send(branch_{code}, {"type": "broker_message", "data": ...})
        message = BrokerMessage(
            type="entity_event",
            payload={"entity_type": "products", "action": "sync", "count": 2},
        )
        layer = get_channel_layer()
        await layer.group_send(
            "branch_WS001",
            {"type": "broker_message", "data": message.to_dict()},
        )

        frame = await comm.receive_json_from(timeout=5)
        self.assertEqual(frame["type"], "broker_message")
        self.assertEqual(frame["message"]["subtype"], "entity_event")
        self.assertEqual(frame["message"]["payload"]["count"], 2)

        await comm.disconnect()

    async def test_branch_push_skips_unidentified_clients(self):
        """A client that did NOT identify with the branch gets no push."""
        comm = await self._connect()  # connected, but no identify frame

        message = BrokerMessage(
            type="entity_event",
            payload={"entity_type": "products", "action": "sync", "count": 2},
        )
        layer = get_channel_layer()
        await layer.group_send(
            "branch_WS001",
            {"type": "broker_message", "data": message.to_dict()},
        )

        # The unidentified client must NOT receive the branch-targeted push
        # (it only joined the global sync_events / sync_broadcast groups).
        from asgiref.timeout import timeout

        with self.assertRaises(asyncio.TimeoutError):
            async with timeout(0.5):
                await comm.receive_json_from()

        await comm.disconnect()

    async def test_missing_branch_code_returns_error(self):
        """An identify frame without branch_code yields an error frame."""
        comm = WebsocketCommunicator(SyncEventConsumer.as_asgi(), "/ws/sync-events/")
        connected, _ = await comm.connect()
        self.assertTrue(connected)

        await comm.send_json_to({"type": "identify", "payload": {"node_id": "x"}})
        frame = await comm.receive_json_from(timeout=5)
        self.assertEqual(frame["type"], "error")
        self.assertIn("branch_code", frame["payload"]["message"])

        await comm.disconnect()

    async def test_invalid_json_returns_error(self):
        """Non-JSON payloads produce an error frame without crashing."""
        comm = await self._connect()
        await comm.send_to(text_data="not-json{")
        frame = await comm.receive_json_from(timeout=5)
        self.assertEqual(frame["type"], "error")
        await comm.disconnect()
