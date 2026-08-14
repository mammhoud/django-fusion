"""
POS Full — API key management routes.

Endpoints for creating, listing, and revoking scoped API keys.  All
endpoints require authentication (either bearer token or existing API key
with ``api-keys:*`` scope).

Endpoints::

    GET   /api-keys/            — list all keys (no raw keys exposed)
    POST  /api-keys/            — create a new key (returns plaintext once)
    POST  /api-keys/:id/revoke  — revoke a key
    POST  /api-keys/:id/rotate  — rotate (revoke old + create new)
"""

from __future__ import annotations

import json
import logging
from typing import Any

from robyn import Request, Response

logger = logging.getLogger("pos.apikeys")


def _json_response(data: dict[str, Any], status: int = 200) -> Response:
    return Response(
        status_code=status,
        headers={"Content-Type": "application/json; charset=utf-8"},
        description=json.dumps(data),
    )


def _error(message: str, status: int = 400, detail: str = "") -> Response:
    body: dict[str, Any] = {"error": message}
    if detail:
        body["detail"] = detail
    return _json_response(body, status)


async def list_api_keys(request: Request) -> Response:
    """GET /api-keys/ — list all keys (safe: no raw keys exposed)."""
    try:
        from models.apikey import ApiKey

        keys = ApiKey.objects.all().order_by("-created_at")
        result = []
        for k in keys:
            result.append({
                "id": k.id,
                "name": k.name,
                "prefix": k.prefix,
                "scopes": k.scopes,
                "is_active": k.is_active,
                "is_expired": k.is_expired,
                "expires_at": k.expires_at.isoformat() if k.expires_at else None,
                "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
                "use_count": k.use_count,
                "created_at": k.created_at.isoformat() if k.created_at else None,
                "description": k.description,
                "created_by": k.created_by,
            })
        return _json_response({"data": result, "count": len(result)})
    except Exception as exc:
        logger.exception("list_api_keys failed: %s", exc)
        return _error("Failed to list API keys", 500)


async def create_api_key(request: Request) -> Response:
    """POST /api-keys/ — create a new scoped API key."""
    try:
        body = request.json() or {}
        name = (body.get("name") or "").strip()
        if not name:
            return _error("Name is required", 400, "Provide a human-readable name for the key.")

        scopes = body.get("scopes", ["*:*"])
        if not isinstance(scopes, list) or not scopes:
            return _error("Scopes must be a non-empty list", 400)

        # Validate scopes
        from models.apikey import scope_is_valid, KNOWN_SCOPES
        for s in scopes:
            if not scope_is_valid(s):
                return _error(
                    f"Invalid scope: '{s}'",
                    400,
                    f"Valid format: resource:action (e.g. products:read). "
                    f"Known resources: {', '.join(r for r, _, _ in KNOWN_SCOPES)}.",
                )

        expires_days = body.get("expires_days")
        if expires_days is not None:
            try:
                expires_days = int(expires_days)
            except (ValueError, TypeError):
                return _error("expires_days must be an integer", 400)

        from models.apikey import ApiKey

        key = ApiKey.create_key(
            name=name,
            scopes=scopes,
            expires_days=expires_days,
            description=body.get("description", ""),
            created_by=body.get("created_by", "api"),
            metadata=body.get("metadata", {}),
        )
        key.save()
        plaintext = getattr(key, "_plaintext", None)

        logger.info("Created API key: %s [%s...] scopes=%s", name, key.prefix, scopes)

        return _json_response({
            "data": {
                "id": key.id,
                "name": key.name,
                "prefix": key.prefix,
                "scopes": key.scopes,
                "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                "created_at": key.created_at.isoformat() if key.created_at else None,
            },
            "api_key": plaintext,
            "warning": "Save this API key now — it will not be shown again.",
        }, status=201)
    except Exception as exc:
        logger.exception("create_api_key failed: %s", exc)
        return _error("Failed to create API key", 500)


async def revoke_api_key(request: Request) -> Response:
    """POST /api-keys/:id/revoke — revoke an API key."""
    try:
        pk = request.path_params.get("id")
        from models.apikey import ApiKey

        try:
            key = ApiKey.objects.get(pk=pk)
        except ApiKey.DoesNotExist:
            return _error("API key not found", 404)

        if not key.is_active:
            return _error("API key is already revoked", 400)

        key.revoke()
        key.save()

        logger.info("Revoked API key: %s [%s...]", key.name, key.prefix)
        return _json_response({
            "data": {
                "id": key.id,
                "name": key.name,
                "prefix": key.prefix,
                "is_active": False,
                "revoked_at": key.revoked_at.isoformat() if key.revoked_at else None,
            },
            "message": "API key revoked successfully.",
        })
    except Exception as exc:
        logger.exception("revoke_api_key failed: %s", exc)
        return _error("Failed to revoke API key", 500)


async def rotate_api_key(request: Request) -> Response:
    """POST /api-keys/:id/rotate — revoke old key and create a new one."""
    try:
        pk = request.path_params.get("id")
        from models.apikey import ApiKey

        try:
            old_key = ApiKey.objects.get(pk=pk)
        except ApiKey.DoesNotExist:
            return _error("API key not found", 404)

        # Revoke old key
        old_key.revoke()
        old_key.save()

        # Create new key with same scopes and name
        body = request.json() or {}
        new_name = body.get("name") or f"{old_key.name} (rotated)"
        expires_days = body.get("expires_days")

        new_key = ApiKey.create_key(
            name=new_name,
            scopes=list(old_key.scopes),
            expires_days=int(expires_days) if expires_days else None,
            description=f"Rotated from key #{old_key.id} [{old_key.prefix}...]",
            created_by="rotation",
        )
        new_key.save()
        plaintext = getattr(new_key, "_plaintext", None)

        logger.info(
            "Rotated API key: %s → %s [%s...]",
            old_key.name, new_key.name, new_key.prefix,
        )

        return _json_response({
            "data": {
                "old_key": {"id": old_key.id, "name": old_key.name, "prefix": old_key.prefix},
                "new_key": {
                    "id": new_key.id, "name": new_key.name, "prefix": new_key.prefix,
                    "scopes": new_key.scopes,
                    "expires_at": new_key.expires_at.isoformat() if new_key.expires_at else None,
                },
            },
            "api_key": plaintext,
            "warning": "Old key revoked. Save this new API key — it will not be shown again.",
        }, status=201)
    except Exception as exc:
        logger.exception("rotate_api_key failed: %s", exc)
        return _error("Failed to rotate API key", 500)


async def known_scopes_handler(request: Request) -> Response:
    """GET /api-keys/scopes — return the list of known scopes for the UI."""
    from models.apikey import KNOWN_SCOPES
    return _json_response({
        "data": [
            {"resource": r, "label": l, "actions": a}
            for r, l, a in KNOWN_SCOPES
        ],
    })


def register_apikey_routes(app: Any) -> None:
    """Register API key management routes on the Robyn app."""
    app.add_route("/api-keys/", "GET", list_api_keys)
    app.add_route("/api-keys/", "POST", create_api_key)
    app.add_route("/api-keys/scopes", "GET", known_scopes_handler)
    app.add_route("/api-keys/:id/revoke", "POST", revoke_api_key)
    app.add_route("/api-keys/:id/rotate", "POST", rotate_api_key)

    logger.info("Registered API key management routes: /api-keys/")
