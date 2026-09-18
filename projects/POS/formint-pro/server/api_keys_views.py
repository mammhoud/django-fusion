"""
POS Full — Django views for scoped API key management.

Replaces ``routes/apikeys.py``.  All endpoints require authentication
(either Django session for admin UI, or existing API key with ``api-keys:*``
scope for programmatic access).

Endpoints:
    GET   /api-keys/            — List all keys (safe: no raw keys exposed)
    POST  /api-keys/            — Create a new key (returns plaintext once)
    GET   /api-keys/scopes      — Known scope catalog for UI
    POST  /api-keys/<id>/revoke — Revoke a key
    POST  /api-keys/<id>/rotate — Rotate (revoke old + create new)
"""

import json
import logging

from django.http import HttpRequest, JsonResponse

from models.apikey import ApiKey

logger = logging.getLogger("pos.api_keys")

# ── Known scopes catalog ──
_KWOWN_RESOURCES = [
    "products", "categories", "customers", "sales", "inventory",
    "employees", "suppliers", "nodes", "sync", "config", "crm",
    "kitchen", "reports", "health", "api-keys",
]
_KWOWN_ACTIONS = ["read", "write", "delete"]


def _safe_key(key: ApiKey) -> dict:
    """Serialize an ApiKey without exposing the raw key."""
    return {
        "id": key.id,
        "name": key.name,
        "prefix": key.prefix,
        "scopes": key.scopes,
        "is_active": key.is_active,
        "expires_at": key.expires_at.isoformat() if key.expires_at else None,
        "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
        "use_count": key.use_count,
        "created_at": key.created_at.isoformat() if key.created_at else None,
        "revoked_at": key.revoked_at.isoformat() if key.revoked_at else None,
    }


def list_api_keys(request: HttpRequest) -> JsonResponse:
    """GET /api-keys/ — List all API keys (no raw keys exposed)."""
    keys = ApiKey.objects.all().order_by("-created_at")
    return JsonResponse({"keys": [_safe_key(k) for k in keys], "count": len(keys)})


def create_api_key(request: HttpRequest) -> JsonResponse:
    """POST /api-keys/ — Create a new scoped API key.

    Body: {"name": "Mobile App", "scopes": ["products:read", "sales:*"], "expires_days": 365}
    Returns the plaintext key *once* — caller must save it.
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = body.get("name", "").strip()
    if not name:
        return JsonResponse({"error": "name is required"}, status=400)

    scopes = body.get("scopes", ["*:*"])
    expires_days = body.get("expires_days") or None

    try:
        record, plaintext = ApiKey.objects.create_key(
            name=name,
            scopes=scopes,
            expires_days=expires_days,
        )
    except Exception as exc:
        logger.exception("Failed to create API key")
        return JsonResponse({"error": str(exc)}, status=500)

    return JsonResponse({
        "key": _safe_key(record),
        "plaintext": plaintext,
        "warning": "Save this key now — it will not be shown again.",
    }, status=201)


def known_scopes(request: HttpRequest) -> JsonResponse:
    """GET /api-keys/scopes — Return the known scope catalog."""
    return JsonResponse({
        "resources": _KWOWN_RESOURCES,
        "actions": _KWOWN_ACTIONS,
        "examples": [
            "*:*",
            "products:*",
            "products:read",
            "sales:read",
            "api-keys:*",
        ],
    })


def revoke_api_key(request: HttpRequest, key_id: int) -> JsonResponse:
    """POST /api-keys/<id>/revoke — Revoke an API key."""
    try:
        key = ApiKey.objects.get(id=key_id)
    except ApiKey.DoesNotExist:
        return JsonResponse({"error": "Key not found"}, status=404)

    key.revoke()
    return JsonResponse({"status": "revoked", "key": _safe_key(key)})


def rotate_api_key(request: HttpRequest, key_id: int) -> JsonResponse:
    """POST /api-keys/<id>/rotate — Rotate (revoke old + create new with same scopes)."""
    try:
        old_key = ApiKey.objects.get(id=key_id)
    except ApiKey.DoesNotExist:
        return JsonResponse({"error": "Key not found"}, status=404)

    try:
        new_record, plaintext = ApiKey.objects.create_key(
            name=f"{old_key.name} (rotated)",
            scopes=old_key.scopes,
            expires_days=None,
        )
    except Exception as exc:
        logger.exception("Failed to rotate API key")
        return JsonResponse({"error": str(exc)}, status=500)

    old_key.revoke()
    return JsonResponse({
        "status": "rotated",
        "revoked": _safe_key(old_key),
        "new_key": _safe_key(new_record),
        "plaintext": plaintext,
        "warning": "Save this new key now — it will not be shown again.",
    })
