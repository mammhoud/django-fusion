"""
Cloud Sync Proxy — accepts entity pushes from Solo edition.
Replaces the old Sanic sync proxy with Django views.

@tested pos-portal/full - Sync proxy for Solo compatibility
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger("cloud.sync_proxy")

SYNC_DATA_DIR = Path(__file__).parent.parent / "cloud_data" / "sync_proxy"


def _ensure_dir() -> None:
    SYNC_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_entities(entity_type: str) -> list[dict]:
    file_path = SYNC_DATA_DIR / f"{entity_type}.json"
    if not file_path.exists():
        return []
    try:
        with open(file_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_entities(entity_type: str, entities: list[dict]) -> None:
    _ensure_dir()
    with open(SYNC_DATA_DIR / f"{entity_type}.json", "w") as f:
        json.dump(entities, f, indent=2, default=str)


@require_GET
def sync_status(request):
    """Get sync proxy status and entity counts."""
    _ensure_dir()
    status = {"service": "sync-proxy", "status": "ok"}
    for entity_type in ("products", "sales", "customers", "inventory", "employees"):
        entities = _load_entities(entity_type)
        status[f"{entity_type}_count"] = len(entities)
    return JsonResponse(status)


@csrf_exempt
@require_POST
def push_entity(request, entity_type: str):
    """Accept a single entity push from Solo edition."""
    valid_types = {"products", "sales", "customers", "inventory", "employees", "settings"}
    if entity_type not in valid_types:
        return JsonResponse({"error": f"invalid type: {entity_type}"}, status=400)

    payload = json.loads(request.body)
    entities = _load_entities(entity_type)
    entity_id = payload.get("id") or len(entities) + 1

    entity = {
        "cloud_id": f"sync_{entity_type}_{entity_id}",
        "synced_at": datetime.utcnow().isoformat(),
        **payload,
    }
    entities.append(entity)
    _save_entities(entity_type, entities)

    logger.info("Accepted %s push (total: %d)", entity_type, len(entities))
    return JsonResponse({
        "status": "accepted",
        "entity_type": entity_type,
        "cloud_id": entity["cloud_id"],
        "total_stored": len(entities),
    })


@csrf_exempt
@require_POST
def bulk_push_entities(request, entity_type: str):
    """Accept bulk entity push from Solo edition."""
    valid_types = {"products", "sales", "customers", "inventory", "employees"}
    if entity_type not in valid_types:
        return JsonResponse({"error": f"invalid type: {entity_type}"}, status=400)

    payload = json.loads(request.body)
    if not isinstance(payload, list):
        return JsonResponse({"error": "payload must be a JSON array"}, status=400)

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
    return JsonResponse({
        "status": "accepted",
        "entity_type": entity_type,
        "accepted": accepted,
        "total_stored": len(entities),
    })
