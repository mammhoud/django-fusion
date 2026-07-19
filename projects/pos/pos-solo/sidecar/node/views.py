"""
Node API views for Solo POS Portal.
Handles heartbeats, registration, and data sync from POS nodes.
Extends VResume base with sync-specific functionality.

@tested pos-portal/solo - Node API views
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


@csrf_exempt
@require_POST
def node_transactions(request):
    """Accept transaction data from nodes."""
    payload = json.loads(request.body)
    tx_file = NODE_REGISTRY_FILE.parent / "transactions.jsonl"

    with open(tx_file, "a") as f:
        f.write(json.dumps({
            "received_at": datetime.utcnow().isoformat(),
            **payload,
        }) + "\n")

    return JsonResponse({"status": "received", "node_id": payload.get("node_id")})


@csrf_exempt
@require_POST
def node_products(request):
    """Accept product catalog sync from nodes."""
    payload = json.loads(request.body)
    products_file = NODE_REGISTRY_FILE.parent / "products_sync.json"

    existing = []
    if products_file.exists():
        try:
            with open(products_file) as f:
                existing = json.load(f)
        except (json.JSONDecodeError, OSError):
            existing = []

    existing.append({
        "synced_at": datetime.utcnow().isoformat(),
        **payload,
    })

    with open(products_file, "w") as f:
        json.dump(existing, f, indent=2, default=str)

    return JsonResponse({
        "status": "synced",
        "total_products": len(existing),
    })
