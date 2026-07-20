"""
Shared server base for POS Robyn + Django ORM sidecars.

Provides serialization and CRUD helper functions:
  - Serialization: _ser, _ser_node, _paginate, _error
  - CRUD: _list, _get, _create, _update, _delete, _count
  - Router: _register_crud
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from asgiref.sync import sync_to_async
from robyn import Request, Response, jsonify

logger = logging.getLogger("pos.server_base")

# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------


def _ser(obj: Any) -> dict:
    """Serialize a Django model instance to a plain dict."""
    data = {}
    for field in obj._meta.fields:
        val = getattr(obj, field.attname, None)
        if isinstance(val, Decimal):
            val = float(val)
        elif isinstance(val, datetime):
            val = val.isoformat() if val else None
        data[field.attname] = val
    return data


def _ser_node(node) -> dict:
    """Serialize a Node with all fields."""
    return {
        "node_id": node.node_id,
        "hostname": node.hostname,
        "node_type": node.node_type,
        "version": node.version,
        "api_version": node.api_version,
        "status": node.status,
        "status_message": node.status_message,
        "is_active": node.is_active,
        "product_count": node.product_count,
        "transaction_count": node.transaction_count,
        "customer_count": node.customer_count,
        "ip_address": str(node.ip_address) if node.ip_address else None,
        "port": node.port,
        "capabilities": node.capabilities,
        "metadata": node.metadata,
        "first_seen": node.first_seen.isoformat() if node.first_seen else None,
        "last_seen": node.last_seen.isoformat() if node.last_seen else None,
        "last_synced_at": node.last_synced_at.isoformat() if node.last_synced_at else None,
    }


def _paginate(qs, page: int = 1, per_page: int = 50) -> dict:
    """Paginate a queryset and return data + pagination metadata."""
    page = max(1, page)
    per_page = max(1, min(per_page, 200))
    total = qs.count()
    start = (page - 1) * per_page
    items = list(qs[start:start + per_page])
    return {
        "data": [_ser(i) for i in items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": max(1, -(-total // per_page)),
        },
    }


def _error(status: int, msg: str) -> Response:
    """Build a JSON error response."""
    return Response(
        status_code=status,
        headers={"Content-Type": "application/json"},
        description=json.dumps({"error": msg}),
    )


# ---------------------------------------------------------------------------
# CRUD helpers (async, sync_to_async wrapped)
# ---------------------------------------------------------------------------


async def _list(model, request: Request) -> dict:
    """Paginated list endpoint for a model."""
    page = int(str(request.query_params.get("page", "1")))
    per_page = int(str(request.query_params.get("per_page", "50")))

    @sync_to_async
    def _q():
        qs = model.objects.all()
        return _paginate(qs, page, per_page)

    return await _q()


async def _get(model, pk: int) -> dict | None:
    """Get a single model instance by ID."""
    @sync_to_async
    def _q():
        try:
            return _ser(model.objects.get(id=pk))
        except model.DoesNotExist:
            return None

    return await _q()


async def _create(model, data: dict) -> dict:
    """Create a new model instance."""
    @sync_to_async
    def _c():
        obj = model.objects.create(**data)
        return _ser(obj)

    return await _c()


async def _update(model, pk: int, data: dict) -> dict | None:
    """Update an existing model instance by ID."""
    @sync_to_async
    def _u():
        try:
            obj = model.objects.get(id=pk)
            for key, val in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, val)
            obj.save()
            return _ser(obj)
        except model.DoesNotExist:
            return None

    return await _u()


async def _delete(model, pk: int) -> bool:
    """Delete a model instance by ID."""
    @sync_to_async
    def _d():
        try:
            model.objects.get(id=pk).delete()
            return True
        except model.DoesNotExist:
            return False

    return await _d()


async def _count(model) -> int:
    """Count model instances."""
    @sync_to_async
    def _c():
        return model.objects.count()

    return await _c()


# ---------------------------------------------------------------------------
# Generic CRUD router factory
# ---------------------------------------------------------------------------


def _register_crud(app, prefix: str, model, name: str):
    """Register GET/POST/PATCH/DELETE routes for a model on a Robyn app.

    Args:
        app: Robyn application instance
        prefix: URL prefix for the routes (e.g., "products")
        model: Django model class
        name: Human-readable model name for error messages
    """

    @app.get(f"/{prefix}")
    async def list_all(request: Request):
        return jsonify(await _list(model, request))

    @app.get(f"/{prefix}/:pk")
    async def get_one(request: Request, pk: int):
        obj = await _get(model, pk)
        if not obj:
            return _error(404, f"{name} not found")
        return jsonify(obj)

    @app.post(f"/{prefix}")
    async def create_one(request: Request):
        body = request.json() or {}
        obj = await _create(model, body)
        return Response(
            status_code=201,
            headers={"Content-Type": "application/json"},
            description=json.dumps(obj),
        )

    @app.patch(f"/{prefix}/:pk")
    async def update_one(request: Request, pk: int):
        body = request.json() or {}
        obj = await _update(model, pk, body)
        if not obj:
            return _error(404, f"{name} not found")
        return jsonify(obj)

    @app.delete(f"/{prefix}/:pk")
    async def delete_one(request: Request, pk: int):
        ok = await _delete(model, pk)
        if not ok:
            return _error(404, f"{name} not found")
        return jsonify({"status": "deleted"})
