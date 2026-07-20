"""
POS Server (Solo) — WebSocket stream state and broadcast functions.

Extracted from routes/state.py. Imported by routes/state.py which re-exports
for route modules.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("pos_server")

_ws_clients: set[Any] = set()
_ws_filters: dict[int, dict] = {}

_entity_ws_clients: set[Any] = set()

async def _broadcast_entity_event(entity_name: str, action: str, data: dict):
    """Broadcast entity CRUD events to all connected entity WebSocket clients."""
    if not _entity_ws_clients:
        return
    payload = json.dumps({
        "type": "entity_event",
        "entity": entity_name,
        "action": action,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    disconnected = set()
    for ws in _entity_ws_clients:
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.add(ws)
    _entity_ws_clients.difference_update(disconnected)


async def _broadcast_node_event(event_type, node_id, data):
    if not _ws_clients:
        return
    payload = json.dumps({"type": "node_event", "event": event_type, "node_id": node_id, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()})
    disconnected = set()
    for ws in _ws_clients:
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.add(ws)
    _ws_clients.difference_update(disconnected)

_config_ws_clients: set[Any] = set()
_config_ws_filters: dict[int, dict] = {}

async def _broadcast_config_event(event_type, node_id, data):
    if not _config_ws_clients:
        return
    payload = json.dumps({"type": "config_event", "event": event_type, "node_id": node_id, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()})
    disconnected = set()
    for ws in _config_ws_clients:
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.add(ws)
    _config_ws_clients.difference_update(disconnected)
