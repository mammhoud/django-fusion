"""
Shared authentication middleware and endpoint registration for POS Robyn servers.

Provides:
  - Token validation middleware factory (create_auth_middleware)
  - Auth endpoint registration (register_auth_routes)
  - Request context helper (get_token_info)
  - Decorator for role-based access control (require_role)

Usage in server.py:
    from shared.middleware.auth import create_auth_middleware, register_auth_routes

    app.before_request()(create_auth_middleware(
        token_model=DeviceToken,
        api_key=API_KEY,
        public_paths={\"/\", \"/health\"},
    ))

    register_auth_routes(app, token_model=DeviceToken)
"""

from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

from robyn import Request, Response, jsonify

logger = logging.getLogger("pos.auth")

# ---------------------------------------------------------------------------
# Context variable for current request's token info
# ---------------------------------------------------------------------------

_current_token: ContextVar[dict | None] = ContextVar("current_token", default=None)


def get_token_info() -> dict | None:
    """Get the current request's token info (set by the auth middleware).

    Returns None if no token was used (e.g., API key auth or public route).
    """
    return _current_token.get()


# ---------------------------------------------------------------------------
# Public routes configuration
# ---------------------------------------------------------------------------

DEFAULT_PUBLIC_PATHS: set[str] = {
    "/",
    "/health",
    "/auth/token",
    "/auth/verify",
    "/docs",
    "/openapi.json",
}


# ---------------------------------------------------------------------------
# Middleware factory
# ---------------------------------------------------------------------------


def create_auth_middleware(
    token_model: type | None = None,
    api_key: str | None = None,
    public_paths: set[str] | None = None,
    validate_token_func=None,
):
    """Create a before_request middleware that authenticates requests.

    Authentication priority:
      1. Bearer token (Authorization: Bearer <token>)
      2. API key (X-API-Key header) — shared secret
      3. Public path — no auth required
    """
    public = public_paths or DEFAULT_PUBLIC_PATHS

    async def auth_middleware(request: Request) -> Request | Response:
        url = str(request.url)

        # 1. Skip public paths
        for p in public:
            if url == p or url.rstrip("/") == p.rstrip("/") or url.startswith(p.rstrip("/") + "/"):
                _current_token.set(None)
                return request

        # 2. Try Bearer token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            raw_token = auth_header[7:]
            token_data = None

            if validate_token_func:
                token_data = validate_token_func(raw_token)
            elif token_model:
                try:
                    token_obj = token_model.validate_token(raw_token)
                    if token_obj:
                        token_data = token_obj.to_dict()
                except Exception as exc:
                    logger.warning("Token validation error: %s", exc)

            if token_data:
                _current_token.set(token_data)
                return request

            logger.warning("Invalid Bearer token from %s", url)
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"error": "Invalid or expired token"}),
            )

        # 3. Try API key
        if api_key:
            key = request.headers.get("X-API-Key", "")
            if key == api_key:
                _current_token.set({
                    "device_id": "__api_key__",
                    "role": "admin",
                    "auth_method": "api_key",
                })
                return request

        # 4. No auth provided
        if api_key:
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"error": "Unauthorized — provide Bearer token or X-API-Key"}),
            )

        _current_token.set(None)
        return request

    return auth_middleware


# ---------------------------------------------------------------------------
# Auth endpoint registration
# ---------------------------------------------------------------------------


def register_auth_routes(
    app,
    token_model: type | None = None,
    issue_token_func=None,
    default_ttl_days: int = 90,
):
    """Register authentication endpoints on a Robyn app.

    Registers:
      POST /auth/token    — Issue a new token
      POST /auth/refresh  — Refresh an existing token
      GET  /auth/verify   — Verify a token and return its payload
      GET  /auth/status   — Get auth system status
    """

    @app.post("/auth/token")
    async def issue_token(request: Request):
        """Issue a new device token."""
        body = request.json() or {}
        device_id = body.get("device_id", "")
        secret = body.get("secret", "")
        role = body.get("role", "viewer")
        node_type = body.get("node_type", "pos-solo")
        ttl_days = body.get("ttl_days", default_ttl_days)

        if not device_id:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"error": "device_id is required"}),
            )

        if issue_token_func:
            try:
                result = await issue_token_func(device_id, role, node_type, ttl_days, body)
                return jsonify(result)
            except Exception as exc:
                return Response(
                    status_code=400,
                    headers={"Content-Type": "application/json"},
                    description=json.dumps({"error": str(exc)}),
                )

        if token_model:
            try:
                token_obj, raw_token = token_model.issue_token(
                    device_id=device_id,
                    role=role,
                    node_type=node_type,
                    ttl_days=ttl_days,
                    capabilities=body.get("capabilities"),
                    allowed_entities=body.get("allowed_entities"),
                    metadata={"issued_via": "api", "ip": request.ip_address if hasattr(request, "ip_address") else ""},
                )
                return Response(
                    status_code=201,
                    headers={"Content-Type": "application/json"},
                    description=json.dumps({
                        "status": "issued",
                        "token": raw_token,
                        "device": token_obj.to_dict(),
                        "warning": "Save this token — it will not be shown again.",
                    }),
                )
            except Exception as exc:
                return Response(
                    status_code=400,
                    headers={"Content-Type": "application/json"},
                    description=json.dumps({"error": f"Failed to issue token: {exc}"}),
                )

        return Response(
            status_code=501,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": "Token system not configured"}),
        )

    @app.post("/auth/refresh")
    async def refresh_token(request: Request):
        """Refresh an existing token."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"error": "Bearer token required"}),
            )

        raw_token = auth_header[7:]
        body = request.json() or {}
        ttl_days = body.get("ttl_days", default_ttl_days)

        if token_model:
            try:
                old_token = token_model.validate_token(raw_token)
                if not old_token:
                    return Response(
                        status_code=401,
                        headers={"Content-Type": "application/json"},
                        description=json.dumps({"error": "Invalid or expired token"}),
                    )

                new_token_obj, new_raw_token = old_token.refresh(ttl_days=ttl_days)
                return jsonify({
                    "status": "refreshed",
                    "token": new_raw_token,
                    "device": new_token_obj.to_dict(),
                    "warning": "Old token revoked. Save this new token.",
                })
            except Exception as exc:
                return Response(
                    status_code=400,
                    headers={"Content-Type": "application/json"},
                    description=json.dumps({"error": str(exc)}),
                )

        return Response(
            status_code=501,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": "Token system not configured"}),
        )

    @app.get("/auth/verify")
    async def verify_token(request: Request):
        """Verify the current token and return its payload."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"error": "Bearer token required"}),
            )

        raw_token = auth_header[7:]

        if token_model:
            token_obj = token_model.validate_token(raw_token)
            if not token_obj:
                return Response(
                    status_code=401,
                    headers={"Content-Type": "application/json"},
                    description=json.dumps({"error": "Invalid or expired token"}),
                )
            return jsonify({"status": "valid", "device": token_obj.to_dict()})

        token_info = get_token_info()
        if token_info:
            return jsonify({"status": "valid", "device": token_info})

        return Response(
            status_code=501,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": "Token system not configured"}),
        )

    @app.get("/auth/status")
    async def auth_status(request: Request):
        """Get auth system status and configuration."""
        token_info = get_token_info()
        return jsonify({
            "service": "POS Auth",
            "version": "1.0.0",
            "auth_methods": ["bearer_token"] + (["api_key"] if hasattr(app, "_api_key") else []),
            "token_model_configured": token_model is not None,
            "current_auth": {
                "authenticated": token_info is not None,
                "method": token_info.get("auth_method", "bearer") if token_info else None,
                "device_id": token_info.get("device_id") if token_info else None,
                "role": token_info.get("role") if token_info else None,
            } if token_info else {"authenticated": False},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


# ---------------------------------------------------------------------------
# Role-based access control helpers
# ---------------------------------------------------------------------------

ROLE_HIERARCHY = {
    "viewer": 0,
    "cashier": 1,
    "manager": 2,
    "admin": 3,
}


def has_minimum_role(token_info: dict | None, minimum_role: str) -> bool:
    """Check if the token info has at least the minimum role."""
    if not token_info:
        return False
    role = token_info.get("role", "viewer")
    return ROLE_HIERARCHY.get(role, 0) >= ROLE_HIERARCHY.get(minimum_role, 0)


def require_role(minimum_role: str = "viewer"):
    """Decorator factory for role-based access control on route handlers."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            token_info = get_token_info()
            if not token_info:
                return Response(
                    status_code=401,
                    headers={"Content-Type": "application/json"},
                    description=json.dumps({"error": "Authentication required"}),
                )
            if not has_minimum_role(token_info, minimum_role):
                return Response(
                    status_code=403,
                    headers={"Content-Type": "application/json"},
                    description=json.dumps({
                        "error": f"Insufficient role. Required: {minimum_role}, has: {token_info.get('role')}",
                    }),
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
