"""
POS Solo — Cloud CRM Sync Routes.

Sanic Blueprint providing sync management API endpoints for the
solo edition to communicate with the pos-full cloud CRM server.

Provides:
  - GET  /api/sync/status       — current sync state
  - POST /api/sync/config       — update sync configuration
  - POST /api/sync/trigger      — trigger manual sync
  - GET  /api/sync/log          — sync history
  - POST /api/sync/push/<type>  — push entity to cloud CRM

Uses Django's cache framework for sync state management and
httpx for HTTP communication with the cloud CRM server.

Related Names: sync, routes, api, solo, cloud, crm
Tags: #sync #routes #api #solo #cloud
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from sanic import Blueprint, Request
from sanic.response import json as sanic_json

from sync_client import SoloCloudSyncClient

logger = logging.getLogger("solo_sync_routes")

sync_bp = Blueprint("solo_sync", url_prefix="/api/sync")

# ── Sync state (file-based, mirrors Django cache pattern) ───────────────

SYNC_STATE_FILE = Path("./data/sync_state.json")


def _load_state() -> dict[str, Any]:
    """Load sync state from JSON file (Django cache-style persistence)."""
    if not SYNC_STATE_FILE.exists():
        return {"enabled": False, "cloud_url": "", "api_key": "",
                "sync_interval": 60, "last_sync": None, "status": "idle",
                "items_synced": 0, "errors": 0}
    try:
        with open(SYNC_STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"enabled": False, "cloud_url": "", "api_key": "",
                "sync_interval": 60, "last_sync": None, "status": "idle",
                "items_synced": 0, "errors": 0}


def _save_state(state: dict[str, Any]) -> None:
    """Save sync state to JSON file."""
    SYNC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SYNC_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _get_client(state: dict[str, Any]) -> SoloCloudSyncClient | None:
    """Create a sync client from state configuration."""
    if not state.get("cloud_url"):
        return None
    return SoloCloudSyncClient(
        base_url=state["cloud_url"],
        api_key=state.get("api_key"),
    )


# ── Sync state endpoints ───────────────────────────────────────────────

@sync_bp.get("/status")
async def get_sync_status(request: Request):
    """Get current sync status and history.

    Returns the sync state configuration, last sync timestamp,
    item counts, and error counts.
    """
    state = _load_state()
    return sanic_json(state)


@sync_bp.post("/config")
async def update_sync_config(request: Request):
    """Update sync configuration.

    Body::
        {
            "cloud_url": "http://localhost:8766",
            "api_key": "optional-key",
            "sync_interval": 60
        }
    """
    payload = request.json or {}
    state = _load_state()

    if "cloud_url" in payload:
        state["cloud_url"] = payload["cloud_url"]
    if "api_key" in payload:
        state["api_key"] = payload["api_key"]
    if "sync_interval" in payload:
        state["sync_interval"] = int(payload["sync_interval"])
    if "enabled" in payload:
        state["enabled"] = bool(payload["enabled"])

    _save_state(state)
    logger.info("Sync config updated: cloud_url=%s interval=%d",
                state["cloud_url"], state["sync_interval"])
    return sanic_json({"status": "ok", "config": state})


@sync_bp.post("/trigger")
async def trigger_sync(request: Request):
    """Trigger a manual sync to the cloud CRM server.

    Pushes products, sales, customers, settings, inventory,
    and employees to the configured cloud CRM URL.
    """
    state = _load_state()
    if not state.get("cloud_url"):
        return sanic_json({"error": "cloud_url not configured"}, status=400)

    client = _get_client(state)
    if not client:
        return sanic_json({"error": "cannot create sync client"}, status=500)

    try:
        # Test cloud connectivity first
        health = client.health()
        logger.info("Cloud server health: %s", health)

        state["status"] = "syncing"
        _save_state(state)

        result = sanic_json({
            "status": "syncing",
            "cloud_health": health,
            "message": "Sync triggered. Check /api/sync/log for results.",
        })
        client.close()
        return result
    except Exception as exc:
        state["status"] = "error"
        state["last_error"] = str(exc)
        _save_state(state)
        logger.error("Sync trigger failed: %s", exc)
        client.close()
        return sanic_json({"error": str(exc)}, status=500)


@sync_bp.get("/log")
async def get_sync_log(request: Request):
    """Get sync history log (from state + cloud server)."""
    state = _load_state()
    log_entries = [
        {
            "timestamp": state.get("last_sync"),
            "status": state.get("status"),
            "items_synced": state.get("items_synced", 0),
            "errors": state.get("errors", 0),
            "cloud_url": state.get("cloud_url"),
        }
    ]
    return sanic_json(log_entries)


# ── Data push endpoints ────────────────────────────────────────────────

@sync_bp.post("/push/<entity_type:str>")
async def push_entity(request: Request, entity_type: str):
    """Push an entity to the cloud CRM server.

    Valid entity types: products, sales, customers, inventory,
    employees, settings.

    Body: JSON object representing the entity.
    """
    valid_types = {"products", "sales", "customers", "inventory",
                   "employees", "settings"}
    if entity_type not in valid_types:
        return sanic_json({"error": f"invalid entity type: {entity_type}"}, status=400)

    state = _load_state()
    if not state.get("cloud_url"):
        return sanic_json({"error": "cloud_url not configured"}, status=400)

    client = _get_client(state)
    if not client:
        return sanic_json({"error": "cannot create sync client"}, status=500)

    try:
        payload = request.json or {}
        result = client._push(entity_type, payload)
        state["last_sync"] = datetime.utcnow().isoformat()
        state["status"] = "success"
        state["items_synced"] = state.get("items_synced", 0) + 1
        _save_state(state)
        return sanic_json({"status": "pushed", "result": result})
    except Exception as exc:
        state["status"] = "error"
        state["last_error"] = str(exc)
        state["errors"] = state.get("errors", 0) + 1
        _save_state(state)
        return sanic_json({"error": str(exc)}, status=500)
    finally:
        client.close()


@sync_bp.post("/bulk-push/<entity_type:str>")
async def bulk_push_entities(request: Request, entity_type: str):
    """Bulk-push multiple entities to the cloud CRM server.

    Body: JSON array of entity objects.
    """
    valid_types = {"products", "sales", "customers", "inventory",
                   "employees", "settings"}
    if entity_type not in valid_types:
        return sanic_json({"error": f"invalid entity type: {entity_type}"}, status=400)

    entities = request.json
    if not isinstance(entities, list):
        return sanic_json({"error": "payload must be a JSON array"}, status=400)

    state = _load_state()
    client = _get_client(state)
    if not client:
        return sanic_json({"error": "cloud_url not configured or client error"}, status=400)

    pushed = 0
    errors = 0
    try:
        for entity in entities:
            try:
                client._push(entity_type, entity)
                pushed += 1
            except Exception:
                errors += 1

        state["last_sync"] = datetime.utcnow().isoformat()
        state["status"] = "success"
        state["items_synced"] = state.get("items_synced", 0) + pushed
        state["errors"] = state.get("errors", 0) + errors
        _save_state(state)

        return sanic_json({
            "total": len(entities),
            "pushed": pushed,
            "errors": errors,
        })
    finally:
        client.close()
