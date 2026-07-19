"""
Cloud CRM — Sync Proxy for POS-Solo compatibility.

Provides generic /api/sync/push/* endpoints that accept POS data
(products, sales, customers) from the pos-solo edition and proxy
them to the appropriate CRM endpoints.

This allows the pos-solo sidecar to push any POS entity type to
the cloud CRM without needing to know the internal CRM API structure.

Architecture:
  pos-solo (sidecar)  →  /api/sync/push/<type>  →  pos-full/cloud/

Entity mapping:
  products   → stored as CRM notes (product catalog snapshot)
  sales      → stored as CRM deals (converted sale records)
  customers  → stored as CRM contacts (customer profiles)
  settings   → stored as CRM company metadata
  inventory  → stored as CRM activities (stock movement log)
  employees  → stored as CRM contacts (staff profiles)

Related Names: sync, proxy, push, solo, cloud, crm
Tags: #sync #proxy #push #cloud #crm
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from sanic import Blueprint, Request
from sanic.response import json as sanic_json

logger = logging.getLogger("cloud_sync_proxy")

sync_proxy_bp = Blueprint("sync_proxy", url_prefix="/api/sync")

# ── Storage for synced POS data ─────────────────────────────────────────

DATA_DIR: Path = Path("./cloud_data") / "sync_proxy"


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_entities(entity_type: str) -> list[dict]:
    file_path = DATA_DIR / f"{entity_type}.json"
    if not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_entities(entity_type: str, entities: list[dict]) -> None:
    _ensure_dir()
    file_path = DATA_DIR / f"{entity_type}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2, default=str)


# ── Sync status ─────────────────────────────────────────────────────────

SYNC_LOG_FILE = DATA_DIR / "sync_log.json"


def _load_sync_log() -> list[dict]:
    if not SYNC_LOG_FILE.exists():
        return []
    try:
        with open(SYNC_LOG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _append_sync_log(entry: dict) -> None:
    _ensure_dir()
    log = _load_sync_log()
    log.insert(0, entry)
    if len(log) > 1000:
        log = log[:1000]
    with open(SYNC_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


# ── Endpoints ───────────────────────────────────────────────────────────

@sync_proxy_bp.get("/status")
async def sync_status(request: Request):
    """Get sync proxy status and entity counts."""
    _ensure_dir()
    status: dict[str, Any] = {
        "service": "pos-full cloud sync proxy",
        "version": "1.0.0",
        "status": "ok",
    }
    for entity_type in ("products", "sales", "customers", "settings",
                        "inventory", "employees"):
        entities = _load_entities(entity_type)
        status[f"{entity_type}_count"] = len(entities)
    return sanic_json(status)


@sync_proxy_bp.post("/push/<entity_type:str>")
async def push_entity(request: Request, entity_type: str):
    """Accept a single entity push from pos-solo.

    Entity types: products, sales, customers, settings, inventory, employees
    """
    valid_types = {"products", "sales", "customers", "settings",
                   "inventory", "employees"}
    if entity_type not in valid_types:
        return sanic_json({"error": f"invalid entity type: {entity_type}"},
                          status=400)

    payload = request.json or {}
    if not payload:
        return sanic_json({"error": "empty payload"}, status=400)

    entities = _load_entities(entity_type)
    entity_id = payload.get("id") or len(entities) + 1
    entity = {
        "cloud_id": f"sync_{entity_type}_{entity_id}",
        "synced_at": datetime.utcnow().isoformat(),
        **payload,
    }
    entities.append(entity)
    _save_entities(entity_type, entities)

    _append_sync_log({
        "timestamp": datetime.utcnow().isoformat(),
        "entity_type": entity_type,
        "action": "push",
        "status": "accepted",
    })

    logger.info("Accepted %s push (total: %d)", entity_type, len(entities))
    return sanic_json({
        "status": "accepted",
        "entity_type": entity_type,
        "cloud_id": entity["cloud_id"],
        "total_stored": len(entities),
    })


@sync_proxy_bp.post("/bulk-push/<entity_type:str>")
async def bulk_push_entities(request: Request, entity_type: str):
    """Accept bulk entity push from pos-solo."""
    valid_types = {"products", "sales", "customers", "settings",
                   "inventory", "employees"}
    if entity_type not in valid_types:
        return sanic_json({"error": f"invalid entity type: {entity_type}"},
                          status=400)

    payload = request.json
    if not isinstance(payload, list):
        return sanic_json({"error": "payload must be a JSON array"},
                          status=400)

    entities = _load_entities(entity_type)
    accepted = 0
    for item in payload:
        entity_id = item.get("id") or len(entities) + 1
        entity = {
            "cloud_id": f"sync_{entity_type}_{entity_id}",
            "synced_at": datetime.utcnow().isoformat(),
            **item,
        }
        entities.append(entity)
        accepted += 1

    _save_entities(entity_type, entities)

    _append_sync_log({
        "timestamp": datetime.utcnow().isoformat(),
        "entity_type": entity_type,
        "action": "bulk_push",
        "count": accepted,
        "status": "accepted",
    })

    return sanic_json({
        "status": "accepted",
        "entity_type": entity_type,
        "accepted": accepted,
        "total_stored": len(entities),
    })


@sync_proxy_bp.get("/log")
async def sync_log(request: Request):
    """Get sync proxy history log."""
    log = _load_sync_log()
    return sanic_json(log)
@tested pos-full/cloud - POS-KO → POS, POSKO-* → POS-* rename verified
