"""
POS Full Server — WebSocket stream state and broadcast functions.

Extracted from routes/state.py. Imported by routes/state.py which re-exports
for route modules (state.py maintains the global references).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("pos_full_server")

# ── Node event WebSocket clients ──

_ws_clients: set[Any] = set()
_ws_filters: dict[int, dict] = {}


async def _broadcast_node_event(event_type: str, node_id: str, data: dict) -> None:
    """Broadcast a node event to all connected WebSocket clients matching their filters."""
    if not _ws_clients:
        return

    payload = json.dumps({
        "type": "node_event",
        "event": event_type,
        "node_id": node_id,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    disconnected: set[Any] = set()
    node_type = data.get("node_type", "") if isinstance(data, dict) else ""

    for ws in _ws_clients:
        cid = id(ws)
        f = _ws_filters.get(cid, {})
        if f.get("node_id") and f["node_id"] != node_id:
            continue
        if f.get("event_type") and f["event_type"] != event_type:
            continue
        if f.get("node_types") and node_type and node_type not in f["node_types"]:
            continue
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.add(ws)

    _ws_clients.difference_update(disconnected)
    for ws in disconnected:
        _ws_filters.pop(id(ws), None)


# ── Config WebSocket clients ──

_config_ws_clients: set[Any] = set()
_config_ws_filters: dict[int, dict] = {}


async def _broadcast_config_event(event_type: str, node_id: str, data: dict) -> None:
    """Broadcast a configuration event to all connected config WS clients."""
    if not _config_ws_clients:
        return
    payload = json.dumps({
        "type": "config_event", "event": event_type, "node_id": node_id,
        "data": data, "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    disconnected: set[Any] = set()
    for ws in _config_ws_clients:
        cid = id(ws)
        f = _config_ws_filters.get(cid, {})
        if f.get("node_id") and f["node_id"] != node_id:
            continue
        if f.get("event_type") and f["event_type"] != event_type:
            continue
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.add(ws)
    _config_ws_clients.difference_update(disconnected)
    for ws in disconnected:
        _config_ws_filters.pop(id(ws), None)
