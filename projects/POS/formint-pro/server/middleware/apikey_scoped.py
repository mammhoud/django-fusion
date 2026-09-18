"""
POS Full — Scoped API key middleware for the /api/v1/ contract.

Validates ``X-API-Key`` header against the ``ApiKey`` model with scope
enforcement.  Maps URL paths (e.g. ``/api/v1/products/``) to resource
names (``products``) and HTTP methods to actions (``read``, ``write``,
``delete``).

Usage (in server.py)::

    from middleware.apikey_scoped import create_scoped_api_key_middleware
    app.before_request()(create_scoped_api_key_middleware(
        public_paths={...},
    ))
"""

from __future__ import annotations

import json
import logging
from contextvars import ContextVar

from robyn import Request, Response

logger = logging.getLogger("pos.apikey.scoped")

# Context var populated by middleware so route handlers can check which key
# was used (and its scopes).
_current_api_key: ContextVar[dict | None] = ContextVar("current_api_key", default=None)


def get_current_api_key() -> dict | None:
    """Return the currently-authenticated API key info (or None)."""
    return _current_api_key.get()


# ── URL path → resource mapping ──
# Maps /api/v1/<resource>/ to a known resource name for scope checking.
_PATH_RESOURCE_MAP: dict[str, str] = {
    "products": "products",
    "categories": "categories",
    "customers": "customers",
    "sales": "sales",
    "sale-items": "sales",
    "employees": "employees",
    "inventory": "inventory",
    "inventory-adjustments": "inventory",
    "inventory-transactions": "inventory",
    "suppliers": "suppliers",
    "purchase-orders": "suppliers",
    "purchase-order-items": "suppliers",
    "nodes": "nodes",
    "heartbeats": "nodes",
    "node-events": "nodes",
    "sync-logs": "sync",
    "sync-approvals": "sync",
    "config": "config",
    "device-configs": "config",
    "master-devices": "config",
    "cloud-links": "config",
    "crm": "crm",
    "kitchen-tickets": "kitchen",
    "support-tickets": "kitchen",
    "payroll": "reports",
    "employee-schedules": "reports",
    "tax-reports": "reports",
    "health": "health",
    "stats": "health",
    "api-keys": "api-keys",
    "ingredients": "inventory",
    "recipes": "inventory",
    "roles": "config",
    "receipt-templates": "config",
    "notes": "crm",
    "client-categories": "customers",
    "loyalty-transactions": "customers",
    "user-settings": "config",
    "device-tokens": "config",
    "signal-events": "sync",
    "menu-items": "products",
    "menus": "products",
}

# HTTP method → action mapping
_METHOD_ACTION_MAP: dict[str, str] = {
    "GET": "read",
    "OPTIONS": "read",
    "POST": "write",
    "PUT": "write",
    "PATCH": "write",
    "DELETE": "delete",
}


def _extract_resource_and_action(path: str, method: str) -> tuple[str | None, str | None]:
    """Parse a URL path into a (resource, action) tuple for scope checking."""
    # Only check paths under /api/v1/
    if not path.startswith("/api/v1/"):
        return None, None

    # Strip prefix and trailing slash, extract first path segment
    sub = path[len("/api/v1/"):].strip("/")
    if not sub:
        return "health", "read"  # GET /api/v1/ → health:read

    # Split on /, first segment is the resource name
    resource_slug = sub.split("/")[0]
    resource = _PATH_RESOURCE_MAP.get(resource_slug, resource_slug)
    action = _METHOD_ACTION_MAP.get(method.upper(), "read")

    return resource, action


def create_scoped_api_key_middleware(
    public_paths: set | None = None,
    api_key_header: str = "X-API-Key",
):
    """Create a Robyn before-request middleware for scoped API key auth.

    Parameters:
        public_paths: Paths that bypass API key auth (e.g. health, docs)
        api_key_header: Header name for the API key (default: X-API-Key)
    """
    public = public_paths or {
        "/", "/health", "/auth/token", "/auth/verify", "/docs",
        "/openapi.json", "/fusion/health",
    }

    async def middleware(request: Request) -> Request | Response:
        url = str(request.url)
        path = url.split("?", 1)[0] if "?" in url else url

        # Skip auth for public paths
        for p in public:
            if path == p or path.rstrip("/") == p.rstrip("/") or path.startswith(p.rstrip("/") + "/"):
                _current_api_key.set(None)
                return request

        # Only enforce API key auth on /api/v1/ paths
        if not path.startswith("/api/v1/"):
            # For non-API paths, the existing token middleware handles auth
            _current_api_key.set(None)
            return request

        raw_key = (request.headers.get(api_key_header) or "").strip()
        if not raw_key:
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json"},
                description=json.dumps({
                    "error": "API key required",
                    "detail": f"Provide a valid API key in the {api_key_header} header.",
                }),
            )

        try:
            from models.apikey import ApiKey
        except Exception:
            # Model not available (e.g. during early startup) — pass through
            logger.warning("ApiKey model not importable; skipping scoped auth")
            _current_api_key.set(None)
            return request

        key_obj = ApiKey.lookup_key(raw_key)
        if key_obj is None:
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json"},
                description=json.dumps({
                    "error": "Invalid or expired API key",
                    "detail": "The provided API key is not valid, has been revoked, or has expired.",
                }),
            )

        # Scope check
        resource, action = _extract_resource_and_action(path, request.method)
        if resource and action:
            if not key_obj.has_scope(resource, action):
                return Response(
                    status_code=403,
                    headers={"Content-Type": "application/json"},
                    description=json.dumps({
                        "error": "Insufficient scope",
                        "detail": (
                            f"API key '{key_obj.name}' does not have "
                            f"'{resource}:{action}' permission."
                        ),
                        "key_scopes": key_obj.scopes,
                        "required": f"{resource}:{action}",
                    }),
                )

        # Record usage (best-effort; don't fail the request if this errors)
        try:
            key_obj.record_usage()
            key_obj.save(update_fields=["last_used_at", "use_count"])
        except Exception:
            pass

        _current_api_key.set({
            "key_id": key_obj.id,
            "key_name": key_obj.name,
            "prefix": key_obj.prefix,
            "scopes": key_obj.scopes,
            "auth_method": "api_key",
        })
        return request

    return middleware


# ── Utility: create a test API key ──

def ensure_default_api_key() -> str | None:
    """Create a default full-access API key if none exist.

    Returns the plaintext key or ``None`` if keys already exist.
    Called once at server startup for development convenience.
    """
    try:
        from models.apikey import ApiKey

        if ApiKey.objects.filter(is_active=True).exists():
            return None

        key = ApiKey.create_key(
            name="Default Admin Key",
            scopes=["*:*"],
            description="Auto-generated default key for development. Rotate in production.",
            created_by="server-bootstrap",
        )
        key.save()
        plaintext = getattr(key, "_plaintext", None)
        logger.info(
            "Created default API key: %s... (scopes: %s)",
            key.prefix, key.scopes,
        )
        return plaintext
    except Exception as exc:
        logger.warning("Could not create default API key: %s", exc)
        return None
