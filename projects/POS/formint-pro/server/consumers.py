"""
POS Full — Django Channels WebSocket consumers.

Replaces the Robyn ``@app.websocket()`` endpoints:

  * ``/ws/nodes``    — Node event stream (register, heartbeat, status changes)
  * ``/ws/entities`` — Entity change events (CRUD notifications for Redux)
  * ``/ws/config``   — Config change events (device/master/cloud-link updates)

Each consumer has its own in-memory client set; signals from route handlers
broadcast to connected clients via ``async_to_sync(channel_layer.group_send)``.
"""

import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.urls import re_path

logger = logging.getLogger("pos.consumers")

# ── Group names for Channels layer routing ──
GROUP_NODES = "pos_nodes"
GROUP_ENTITIES = "pos_entities"
GROUP_CONFIG = "pos_config"


# ═══════════════════════════════════════════════════════════════════════
# Node Event Consumer (/ws/nodes)
# ═══════════════════════════════════════════════════════════════════════

class NodeConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for node lifecycle events.

    Replaces ``routes/nodes.py`` ``@app.websocket("/ws/nodes")``.
    Clients connect to receive real-time notifications when nodes
    register, send heartbeats, or change status.
    """

    async def connect(self):
        await self.channel_layer.group_add(GROUP_NODES, self.channel_name)
        await self.accept()
        await self.send_json({
            "type": "connected",
            "message": "Connected to node event stream",
            "group": GROUP_NODES,
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(GROUP_NODES, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # Clients can ping — just echo back
        if content.get("type") == "ping":
            await self.send_json({"type": "pong", "ts": content.get("ts")})

    async def node_event(self, event):
        """Handler for ``type: node_event`` messages."""
        await self.send_json(event["data"])


# ═══════════════════════════════════════════════════════════════════════
# Entity Event Consumer (/ws/entities)
# ═══════════════════════════════════════════════════════════════════════

class EntityConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for entity CRUD change events.

    Replaces ``server.py`` ``@app.websocket("/ws/entities")``.
    The Redux middleware subscribes here to invalidate RTK Query caches
    when any entity (Product, Customer, Sale, etc.) is created, updated,
    or deleted.
    """

    async def connect(self):
        await self.channel_layer.group_add(GROUP_ENTITIES, self.channel_name)
        await self.accept()
        await self.send_json({
            "type": "connected",
            "message": "Connected to entity event stream",
            "group": GROUP_ENTITIES,
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(GROUP_ENTITIES, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "ping":
            await self.send_json({"type": "pong", "ts": content.get("ts")})

    async def entity_event(self, event):
        """Handler for ``type: entity_event`` messages."""
        await self.send_json(event["data"])


# ═══════════════════════════════════════════════════════════════════════
# Config Event Consumer (/ws/config)
# ═══════════════════════════════════════════════════════════════════════

class ConfigConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for configuration change events.

    Replaces ``routes/config.py`` ``@app.websocket("/ws/config")``.
    Broadcasts device config, master device, and cloud-link updates.
    """

    async def connect(self):
        await self.channel_layer.group_add(GROUP_CONFIG, self.channel_name)
        await self.accept()
        await self.send_json({
            "type": "connected",
            "message": "Connected to config event stream",
            "group": GROUP_CONFIG,
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(GROUP_CONFIG, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "ping":
            await self.send_json({"type": "pong", "ts": content.get("ts")})

    async def config_event(self, event):
        """Handler for ``type: config_event`` messages."""
        await self.send_json(event["data"])


# ═══════════════════════════════════════════════════════════════════════
# URL patterns for Channels routing
# ═══════════════════════════════════════════════════════════════════════

websocket_urlpatterns = [
    re_path(r"^ws/nodes$", NodeConsumer.as_asgi()),
    re_path(r"^ws/entities$", EntityConsumer.as_asgi()),
    re_path(r"^ws/config$", ConfigConsumer.as_asgi()),
]


# ═══════════════════════════════════════════════════════════════════════
# Broadcast helpers — drop-in replacements for the Robyn stream sets
# ═══════════════════════════════════════════════════════════════════════

def broadcast_nodes(data: dict) -> None:
    """Send a node event to all connected WS clients."""
    try:
        layer = get_channel_layer()
        if layer:
            async_to_sync(layer.group_send)(
                GROUP_NODES,
                {"type": "node_event", "data": data},
            )
    except Exception as exc:
        logger.debug("broadcast_nodes failed: %s", exc)


def broadcast_entities(data: dict) -> None:
    """Send an entity change event to all connected WS clients."""
    try:
        layer = get_channel_layer()
        if layer:
            async_to_sync(layer.group_send)(
                GROUP_ENTITIES,
                {"type": "entity_event", "data": data},
            )
    except Exception as exc:
        logger.debug("broadcast_entities failed: %s", exc)


def broadcast_config(data: dict) -> None:
    """Send a config change event to all connected WS clients."""
    try:
        layer = get_channel_layer()
        if layer:
            async_to_sync(layer.group_send)(
                GROUP_CONFIG,
                {"type": "config_event", "data": data},
            )
    except Exception as exc:
        logger.debug("broadcast_config failed: %s", exc)
