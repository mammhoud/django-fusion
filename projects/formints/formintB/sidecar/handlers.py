"""POS Cloud sidecar — shared handler helpers.

Serialization + generic CRUD over the Django ORM, mirroring the formint
sidecar's handlers.py but tailored to the pos-cloud models in apps.core.
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from asgiref.sync import sync_to_async
from robyn import Response, jsonify

logger = logging.getLogger("pos_cloud_sidecar")


# ===========================================================================
# Serialization helpers
# ===========================================================================


def _json_safe(val: Any) -> Any:
    """Coerce a model field value into a JSON-serializable primitive."""
    if isinstance(val, (Decimal,)):
        return float(val)
    if isinstance(val, (datetime, date, time)):
        return val.isoformat() if val else None
    # File/image fields (e.g. Organization.logo) — expose the URL or None.
    try:
        url = getattr(val, "url", None)
        if url is not None:
            if not val:
                return None
            return str(url)
    except (ValueError, TypeError, OSError):
        # ``FileField.url`` raises ValueError when no file is associated.
        return None
    if hasattr(val, "__str__") and not isinstance(val, (str, int, float, bool)):
        try:
            return str(val)
        except Exception:  # noqa: BLE001
            return None
    return val


def _ser(obj) -> dict:
    """Serialize a Django model instance to a plain dict."""
    data = {}
    for field in obj._meta.fields:
        val = getattr(obj, field.attname, None)
        data[field.attname] = _json_safe(val)
    return data


def _error(status: int, message: str) -> Response:
    return Response(
        status_code=status,
        headers={"Content-Type": "application/json"},
        description=json.dumps({"error": message}),
    )


def _parse_pk(pk: str, name: str):
    try:
        return int(pk), None
    except (TypeError, ValueError):
        return None, _error(400, f"Invalid {name} pk: {pk!r}")


# ===========================================================================
# CRUD async helpers
# ===========================================================================


@sync_to_async
def _list(model, request=None) -> dict:
    qs = model.objects.all()
    # Light pagination via ?limit=&offset=
    if request is not None:
        try:
            limit = int(request.query_params.get("limit", 100) if hasattr(request, "query_params") else 100)
        except (TypeError, ValueError):
            limit = 100
    else:
        limit = 100
    items = [_ser(o) for o in qs[:limit]]
    return {"count": qs.count(), "items": items}


@sync_to_async
def _get(model, pk: int):
    try:
        obj = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None
    return _ser(obj)


def _field_map(model) -> dict[str, str]:
    """Map accepted JSON keys → model field attnames.

    Accepts both the field name (``organization``) and the attname
    (``organization_id``) for foreign keys, so API clients can POST
    ``{"organization_id": 2}`` and it lands on the FK column.
    """
    mapping: dict[str, str] = {}
    for f in model._meta.fields:
        mapping[f.name] = f.attname
        mapping[f.attname] = f.attname
    return mapping


@sync_to_async
def _create(model, data: dict) -> dict:
    """Create a row, mapping JSON keys to model fields (skipping unknown)."""
    field_map = _field_map(model)
    clean = {}
    for key, value in data.items():
        if key == "id":
            continue
        attname = field_map.get(key)
        if attname:
            clean[attname] = value
    obj = model.objects.create(**clean)
    return _ser(obj)


@sync_to_async
def _update(model, pk: int, data: dict):
    try:
        obj = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None
    field_map = _field_map(model)
    for key, value in data.items():
        if key == "id":
            continue
        attname = field_map.get(key)
        if attname:
            setattr(obj, attname, value)
    obj.save()
    return _ser(obj)


@sync_to_async
def _delete(model, pk: int) -> bool:
    try:
        obj = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return False
    obj.delete()
    return True


@sync_to_async
def _count(model) -> int:
    return model.objects.count()


# ===========================================================================
# Generic CRUD router factory
# ===========================================================================


def _register_crud(app, prefix: str, model, name: str):
    """Register GET/POST/PATCH/DELETE routes for a model on a Robyn app."""

    @app.get(f"/{prefix}")
    async def list_all(request):
        return jsonify(await _list(model, request))

    @app.get(f"/{prefix}/:pk")
    async def get_one(request, pk):
        pk_int, err = _parse_pk(pk, name)
        if err:
            return err
        obj = await _get(model, pk_int)
        if not obj:
            return _error(404, f"{name} not found")
        return jsonify(obj)

    @app.post(f"/{prefix}")
    async def create_one(request):
        body = request.json() or {}
        try:
            obj = await _create(model, body)
        except Exception as exc:  # noqa: BLE001 — surface validation errors
            return _error(400, f"{name} create failed: {exc}")
        return Response(
            status_code=201,
            headers={"Content-Type": "application/json"},
            description=json.dumps(obj),
        )

    @app.patch(f"/{prefix}/:pk")
    async def update_one(request, pk):
        pk_int, err = _parse_pk(pk, name)
        if err:
            return err
        body = request.json() or {}
        obj = await _update(model, pk_int, body)
        if not obj:
            return _error(404, f"{name} not found")
        return jsonify(obj)

    @app.delete(f"/{prefix}/:pk")
    async def delete_one(request, pk):
        pk_int, err = _parse_pk(pk, name)
        if err:
            return err
        ok = await _delete(model, pk_int)
        if not ok:
            return _error(404, f"{name} not found")
        return jsonify({"status": "deleted"})
