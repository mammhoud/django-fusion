"""
Minimal node API views for Minimal POS Portal.
Node-only edition — provides heartbeat and registration.
No transaction sync (server not available).

@tested pos-portal/minimal - Node API views (minimal)
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

NODE_REGISTRY_FILE = Path(__file__).parent.parent / "node_registry.json"


def _load_registry() -> dict:
    if not NODE_REGISTRY_FILE.exists():
        return {"nodes": {}, "last_seen": None}
    try:
        with open(NODE_REGISTRY_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"nodes": {}, "last_seen": None}


def _save_registry(registry: dict) -> None:
    with open(NODE_REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2, default=str)


@require_GET
def node_heartbeat(request):
    """List all registered nodes."""
    registry = _load_registry()
    return JsonResponse({
        "nodes": list(registry.get("nodes", {}).values()),
        "total": len(registry.get("nodes", {})),
    })


@csrf_exempt
@require_POST
def node_register(request):
    """Register or update a node heartbeat."""
    import socket

    payload = json.loads(request.body)
    registry = _load_registry()
    node_id = payload.get("node_id", f"NODE-{uuid.uuid4().hex[:8]}")

    registry["nodes"][node_id] = {
        "node_id": node_id,
        "hostname": payload.get("hostname", socket.gethostname()),
        "last_seen": datetime.utcnow().isoformat(),
        "status": payload.get("status", "online"),
        "version": payload.get("version", "unknown"),
        "product_count": payload.get("product_count", 0),
    }
    registry["last_seen"] = datetime.utcnow().isoformat()
    _save_registry(registry)

    return JsonResponse({
        "status": "registered",
        "node_id": node_id,
        "total_nodes": len(registry["nodes"]),
    })
