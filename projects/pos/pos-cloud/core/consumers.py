"""POS Cloud — WebSocket consumer for real-time sync event broadcasting.

Connected clients (e.g., the bolt analytics dashboard) receive live
notifications whenever a branch pushes products, sales, inventory, or
a heartbeat to the cloud sync receivers.
"""

from __future__ import annotations

import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger("pos.sync_events")


class SyncEventConsumer(AsyncWebsocketConsumer):
    """Broadcasts sync events to all connected WebSocket clients.

    Joins the ``sync_events`` channel group on connect.  When a sync
    receiver (products, sales, inventory, heartbeat) finishes processing
    a push, it calls ``group_send`` on this group so every open dashboard
    gets the event in real time.
    """

    # ── Channel group name ──
    group_name = "sync_events"

    async def connect(self) -> None:
        """Accept the WebSocket and join the broadcast group."""
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.debug("WebSocket client connected to sync_events group")

    async def disconnect(self, close_code: int) -> None:
        """Leave the broadcast group on disconnect."""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.debug("WebSocket client disconnected (code=%s)", close_code)

    # ── Event handlers ──
    # Each handler matches the ``type`` key in the event dict sent by
    # ``channel_layer.group_send`` and forwards the payload to the client.

    async def sync_event(self, event: dict) -> None:
        """Forward a ``sync_event`` to the WebSocket client."""
        try:
            await self.send(text_data=json.dumps(event["data"]))
        except (TypeError, ValueError) as exc:
            logger.warning("Failed to serialize sync event for WS client: %s", exc)
