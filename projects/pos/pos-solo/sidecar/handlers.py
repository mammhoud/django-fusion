"""
POS Server (Solo) — shared request handlers, serialization, CRUD factory, and sync client.

Extracted from routes/state.py. All handler utilities are imported by routes/state.py
which re-exports them for route modules.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from asgiref.sync import sync_to_async
from robyn import jsonify, Response

logger = logging.getLogger("pos_server")


def _ser(obj) -> dict:
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
    if node is None:
        return {}
    return {
        "node_id": node.node_id, "hostname": node.hostname,
        "node_type": node.node_type, "version": node.version,
        "api_version": node.api_version, "status": node.status,
        "status_message": node.status_message, "is_active": node.is_active,
        "product_count": node.product_count, "transaction_count": node.transaction_count,
        "customer_count": node.customer_count,
        "ip_address": str(node.ip_address) if node.ip_address else None,
        "port": node.port, "capabilities": node.capabilities, "metadata": node.metadata,
        "first_seen": node.first_seen.isoformat() if node.first_seen else None,
        "last_seen": node.last_seen.isoformat() if node.last_seen else None,
        "last_synced_at": node.last_synced_at.isoformat() if node.last_synced_at else None,
    }


def _paginate(qs, page: int = 1, per_page: int = 50) -> dict:
    page = max(1, page)
    per_page = max(1, min(per_page, 200))
    total = qs.count()
    start = (page - 1) * per_page
    items = list(qs[start:start + per_page])
    return {"data": [_ser(i) for i in items], "pagination": {"page": page, "per_page": per_page, "total": total, "total_pages": max(1, -(-total // per_page))}}


def _error(status: int, msg: str) -> Response:
    return Response(status_code=status, headers={"Content-Type": "application/json"}, description=json.dumps({"error": msg}))


async def _list(model, request) -> dict:
    page = int(str(request.query_params.get("page", "1")))
    per_page = int(str(request.query_params.get("per_page", "50")))
    @sync_to_async
    def _q():
        return _paginate(model.objects.all(), page, per_page)
    return await _q()


async def _get(model, pk: int) -> dict | None:
    @sync_to_async
    def _q():
        try:
            return _ser(model.objects.get(id=pk))
        except model.DoesNotExist:
            return None
    return await _q()


async def _create(model, data: dict) -> dict:
    @sync_to_async
    def _c():
        return _ser(model.objects.create(**data))
    return await _c()


async def _update(model, pk: int, data: dict) -> dict | None:
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
    @sync_to_async
    def _d():
        try:
            model.objects.get(id=pk).delete()
            return True
        except model.DoesNotExist:
            return False
    return await _d()


async def _count(model) -> int:
    @sync_to_async
    def _c():
        return model.objects.count()
    return await _c()


# Sync state and client
def _load_sync_state() -> dict:
    from routes.state import SYNC_STATE_PATH, CLOUD_CRM_URL, CLOUD_API_KEY
    if not SYNC_STATE_PATH or not SYNC_STATE_PATH.exists():
        return {"enabled": True, "cloud_url": CLOUD_CRM_URL or "", "api_key": CLOUD_API_KEY or "", "last_sync": None, "status": "idle", "items_synced": 0, "errors": 0}
    try:
        with open(SYNC_STATE_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_sync_state(state: dict) -> None:
    from routes.state import SYNC_STATE_PATH
    if SYNC_STATE_PATH:
        with open(SYNC_STATE_PATH, "w") as f:
            json.dump(state, f, indent=2, default=str)


class SyncClient:
    def __init__(self, base_url: str = "", api_key: str | None = None, timeout: float = 30.0):
        from routes.state import CLOUD_CRM_URL, CLOUD_API_KEY
        state = _load_sync_state()
        self.base_url = (base_url or state.get("cloud_url", "") or CLOUD_CRM_URL).rstrip("/")
        self.api_key = api_key or state.get("api_key", "") or CLOUD_API_KEY
        self.timeout = timeout
        self._enabled = state.get("enabled", True)

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            h["X-API-Key"] = self.api_key
        return h

    async def _push(self, entity_type: str, data: dict) -> dict:
        if not self._enabled:
            return {"status": "skipped", "reason": "sync_disabled"}
        if not self.base_url:
            return {"status": "skipped", "reason": "no_cloud_url"}
        try:
            import httpx
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/sync/push/{entity_type}", json=data, headers=self._headers())
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.warning("Sync push %s failed: %s", entity_type, exc)
            state = _load_sync_state()
            state["status"] = "error"
            state["last_error"] = str(exc)
            state["errors"] = state.get("errors", 0) + 1
            _save_sync_state(state)
            return {"status": "failed", "error": str(exc)}

    async def push_node(self, data: dict) -> dict:
        return await self._push("nodes", data)

    async def push_heartbeat(self, data: dict) -> dict:
        return await self._push("heartbeats", data)

    async def health(self) -> dict:
        if not self.base_url:
            return {"status": "no_cloud_url"}
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/health", headers=self._headers())
                resp.raise_for_status()
                return resp.json()
        except Exception:
            return {"status": "unreachable"}


async def _log_sync(node_id, entity_type, entity_id, status, error=""):
    from routes.state import SyncLog
    @sync_to_async
    def _log():
        SyncLog.objects.create(node_id=node_id, entity_type=entity_type, entity_id=entity_id, direction="push", status=status, error_message=error)
    await _log()


def _register_crud(app, prefix: str, model, name: str):
    """Register GET/POST/PATCH/DELETE routes for a model on a Robyn app."""

    @app.get(f"/{prefix}")
    async def list_all(request):
        return jsonify(await _list(model, request))

    @app.get(f"/{prefix}/:pk")
    async def get_one(request, pk: int):
        obj = await _get(model, pk)
        if not obj:
            return _error(404, f"{name} not found")
        return jsonify(obj)

    @app.post(f"/{prefix}")
    async def create_one(request):
        body = request.json() or {}
        obj = await _create(model, body)
        return Response(
            status_code=201,
            headers={"Content-Type": "application/json"},
            description=json.dumps(obj),
        )

    @app.patch(f"/{prefix}/:pk")
    async def update_one(request, pk: int):
        body = request.json() or {}
        obj = await _update(model, pk, body)
        if not obj:
            return _error(404, f"{name} not found")
        return jsonify(obj)

    @app.delete(f"/{prefix}/:pk")
    async def delete_one(request, pk: int):
        ok = await _delete(model, pk)
        if not ok:
            return _error(404, f"{name} not found")
        return jsonify({"status": "deleted"})
