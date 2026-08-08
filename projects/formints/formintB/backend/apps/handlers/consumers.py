"""
POS Cloud — WebSocket consumer for bidirectional real-time sync.

Connected POS terminals (and dashboard clients) receive live sync event
broadcasts and can send messages back to the cloud.  The consumer:

1. Joins the per-branch channel group for targeted cloud→branch pushes.
2. Joins the global ``sync_broadcast`` group for system-wide messages.
3. Registers the connection with the ``SyncBroker`` for health tracking.
4. Routes incoming messages to the broker's registered handlers.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from channels.generic.websocket import AsyncWebsocketConsumer

from apps.domain.sync_broker import BrokerMessage, broker

logger = logging.getLogger("pos.sync_events")


class SyncEventConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time sync events.

    On connect, the client should send an initial message to identify
    itself::

        {
            "type": "identify",
            "branch_code": "BR001",
            "node_id": "pos-full-node-abc-123"
        }

    The consumer then joins the appropriate channel groups.
    """

    # ── Channel group names ──
    group_name = "sync_events"
    broadcast_group = "sync_broadcast"

    # ── Client identity (set during connect/identify) ──
    _branch_code: str = ""
    _node_id: str = ""
    _channel_name: str = ""

    async def connect(self) -> None:
        """Accept the WebSocket and join the global broadcast group."""
        self._channel_name = self.channel_name
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add(self.broadcast_group, self.channel_name)
        await self.accept()
        # Tell connected dashboards (e.g. the sync monitor) that a terminal
        # joined — they refetch branch health on this signal.
        await self._broadcast_link_change("terminal_connected")
        logger.debug("WebSocket client connected (channel=%s)", self.channel_name)

    async def disconnect(self, close_code: int) -> None:
        """Leave all groups and unregister from the broker."""
        await self._broadcast_link_change("terminal_disconnected")
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard(self.broadcast_group, self.channel_name)

        if self._branch_code:
            await self.channel_layer.group_discard(
                f"branch_{self._branch_code}",
                self.channel_name,
            )
            broker.unregister_connection(self._branch_code, self._channel_name)

        logger.debug(
            "WebSocket client disconnected (channel=%s, code=%s)",
            self.channel_name, close_code,
        )

    # ── Incoming message handler ─────────────────────────────────────

    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        """Handle an incoming message from the WebSocket client.

        Routes to handlers based on the ``type`` field::

            - ``identify``: Register client with its branch
            - ``sync_push``: Forward to broker's sync_push handlers
            - ``heartbeat``: Forward to broker's heartbeat handlers
            - ``ack``: Forward to broker's ack handlers
            - ``custom:...``: Forward to broker's custom message handlers
        """
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            logger.warning("Invalid WebSocket message (channel=%s): %s", self.channel_name, exc)
            await self._send_error(f"Invalid JSON: {exc}")
            return

        msg_type = data.get("type", "")
        payload = data.get("payload", data)

        if msg_type == "identify":
            await self._handle_identify(payload)
        elif msg_type.startswith("custom:"):
            await self._handle_custom(msg_type.removeprefix("custom:"), payload)
        else:
            # Forward to broker's registered handlers
            self._dispatch_to_broker(msg_type, payload)

    # ── Internal handlers ────────────────────────────────────────────

    async def _handle_identify(self, payload: dict) -> None:
        """Register the client with its branch code.

        Joins the per-branch channel group so the cloud can push
        targeted updates.
        """
        branch_code = (payload.get("branch_code") or "").strip()
        node_id = (payload.get("node_id") or "").strip()

        if not branch_code:
            await self._send_error("Missing branch_code in identify message")
            return

        self._branch_code = branch_code
        self._node_id = node_id

        # Join the per-branch group for targeted pushes
        await self.channel_layer.group_add(
            f"branch_{branch_code}",
            self.channel_name,
        )

        # Register with the broker for health tracking
        broker.register_connection(branch_code, self.channel_name)

        # Confirm to the client
        await self.send(text_data=json.dumps({
            "type": "identify_ack",
            "branch_code": branch_code,
            "node_id": node_id,
            "status": "registered",
        }))

        logger.info(
            "Client identified: branch=%s, node=%s (channel=%s)",
            branch_code, node_id, self.channel_name,
        )

    async def _handle_custom(self, namespace: str, payload: dict) -> None:
        """Handle a custom-namespace message from the client."""
        message = BrokerMessage(
            type=f"custom:{namespace}",
            payload=payload,
            source_node_id=self._node_id,
            target_branch_code=self._branch_code,
        )
        broker.dispatch(self._branch_code, message)

    def _dispatch_to_broker(self, msg_type: str, payload: dict) -> None:
        """Create a BrokerMessage and dispatch to registered handlers."""
        message = BrokerMessage(
            type=msg_type,
            payload=payload,
            source_node_id=self._node_id,
            target_branch_code=self._branch_code,
        )
        broker.dispatch(self._branch_code, message)

    async def _send_error(self, message: str) -> None:
        """Send an error message back to the client."""
        await self.send(text_data=json.dumps({
            "type": "error",
            "payload": {"message": message},
        }))

    async def _broadcast_link_change(self, event_type: str) -> None:
        """Broadcast a terminal connect/disconnect to the sync_events group.

        Connected dashboards (e.g. the sync monitor) use this signal to
        refetch branch health in real time. The wire payload keeps the
        documented ``sync_event`` shape
        ``{entity_type, synced, branch, node_id, timestamp}``; the origin
        channel travels on the envelope only so the originating connection
        does not receive its own link-change frame.
        """
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "sync_event",
                "origin_channel": self.channel_name,
                "data": {
                    "entity_type": event_type,
                    "synced": 1,
                    "branch": self._branch_code,
                    "node_id": self._node_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            },
        )

    # ── Event handlers (called by channel_layer.group_send) ──────────

    async def sync_event(self, event: dict) -> None:
        """Forward a ``sync_event`` to the WebSocket client.

        Matches the ``type`` key in the event dict sent by
        ``channel_layer.group_send``. Link-change frames a connection
        originated itself are skipped (``origin_channel`` travels on the
        envelope, never on the wire payload).
        """
        if event.get("origin_channel") == self.channel_name:
            return
        try:
            await self.send(text_data=json.dumps(event["data"]))
        except (TypeError, ValueError) as exc:
            logger.warning("Failed to serialize sync event: %s", exc)

    async def broker_message(self, event: dict) -> None:
        """Forward a broker message to the WebSocket client.

        This is the handler for ``broker.push_to_branch()`` and
        ``broker.broadcast()``.
        """
        try:
            data = event["data"]
            await self.send(text_data=json.dumps({
                "type": "broker_message",
                "message": data,
            }))
        except (TypeError, ValueError) as exc:
            logger.warning("Failed to serialize broker message: %s", exc)
