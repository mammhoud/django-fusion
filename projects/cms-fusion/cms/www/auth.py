"""
CTC Research — JWT + legacy token authentication backend.

Provides:
- ``JWTTokenAuthBackend``: validates JWT access tokens (HS256) from Bearer header.
- ``TokenAuthBackend``: validates SHA-256 hashed tokens from the ``Token`` table.
- ``auth_required()``: convenience factory for route decorators.

Usage (per-route — JWT preferred for new endpoints):
    from www.auth import JWTTokenAuthBackend, auth_required

    # JWT auth (default for new endpoints)
    @bolt.get("/protected", auth=[JWTTokenAuthBackend()])
    def my_handler(request): ...

    # Legacy token auth (for backward compat)
    @bolt.get("/legacy", auth=[TokenAuthBackend()])
    def legacy_handler(request): ...

    # Shortcut — always uses JWTTokenAuthBackend
    @bolt.get("/me", **auth_required())
    def get_me(request): ...
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt as pyjwt
from django.conf import settings
from django_bolt.auth.backends import BaseAuthentication

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# JWT encode / decode helpers
# ═══════════════════════════════════════════════════════════════════════════


def _get_jwt_config() -> dict:
    """Return the JWT_AUTH dict from settings, with defaults."""
    return getattr(settings, "JWT_AUTH", {})


def _jwt_encode(payload: dict) -> str:
    """Sign and encode a JWT payload using the project's JWT_AUTH settings."""
    cfg = _get_jwt_config()
    signing_key = cfg.get("SIGNING_KEY", settings.SECRET_KEY)
    algorithm = cfg.get("ALGORITHM", "HS256")
    return pyjwt.encode(payload, signing_key, algorithm=algorithm)


def _jwt_decode(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns the payload dict or None on failure."""
    cfg = _get_jwt_config()
    signing_key = cfg.get("SIGNING_KEY", settings.SECRET_KEY)
    algorithm = cfg.get("ALGORITHM", "HS256")
    try:
        return pyjwt.decode(token, signing_key, algorithms=[algorithm])
    except pyjwt.ExpiredSignatureError:
        logger.debug("JWT expired")
        return None
    except pyjwt.InvalidTokenError as exc:
        logger.debug("Invalid JWT: %s", exc)
        return None


def issue_jwt_tokens(user) -> dict:
    """Issue access + refresh JWT tokens for the given user.

    Returns::
        {
            "access": "<jwt>",
            "refresh": "<jwt>",
            "user": { id, email, username, first_name, last_name },
            "expires_in": 1800,  # seconds
        }
    """
    cfg = _get_jwt_config()
    access_lifetime = cfg.get("ACCESS_TOKEN_LIFETIME", timedelta(minutes=30))
    refresh_lifetime = cfg.get("REFRESH_TOKEN_LIFETIME", timedelta(days=7))
    user_id_claim = cfg.get("USER_ID_CLAIM", "user_id")
    user_id_field = cfg.get("USER_ID_FIELD", "id")

    now = datetime.now(tz=timezone.utc)

    # ── Access token payload ──
    access_payload = {
        "token_type": "access",
        user_id_claim: getattr(user, user_id_field),
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "iat": now,
        "exp": now + access_lifetime,
    }
    access_token = _jwt_encode(access_payload)

    # ── Refresh token payload ──
    refresh_payload = {
        "token_type": "refresh",
        user_id_claim: getattr(user, user_id_field),
        "email": user.email,
        "iat": now,
        "exp": now + refresh_lifetime,
    }
    refresh_token = _jwt_encode(refresh_payload)

    total_seconds = int(access_lifetime.total_seconds())

    return {
        "access": access_token,
        "refresh": refresh_token,
        "expires_in": total_seconds,
    }


def jwt_get_user_from_payload(payload: dict):
    """Resolve a Django User from a validated JWT payload."""
    cfg = _get_jwt_config()
    user_id_claim = cfg.get("USER_ID_CLAIM", "user_id")
    user_id = payload.get(user_id_claim)
    if user_id is None:
        return None
    from django.contrib.auth.models import User
    try:
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# JWTTokenAuthBackend — primary auth backend for new endpoints
# ═══════════════════════════════════════════════════════════════════════════


class JWTTokenAuthBackend(BaseAuthentication):
    """JWT-based authentication backend for django-bolt.

    Extracts ``Bearer <jwt-access-token>`` from the ``Authorization`` header,
    validates the JWT (signature + expiry), and resolves the user.
    Only tokens whose ``token_type`` is in ``accept_types`` pass.

    Args:
        accept_types: Allowed JWT token_type values.
            Default: ``{"access"}`` — rejects refresh & other types.

    Example:
        auth=[JWTTokenAuthBackend(accept_types={"access"})]
        auth=[JWTTokenAuthBackend(accept_types={"access", "api"})]
    """

    def __init__(self, accept_types: set[str] | None = None):
        self.accept_types = accept_types or {"access"}

    @property
    def scheme_name(self) -> str:
        return "jwt"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "type": "jwt",
            "header": "authorization",
            "accept_types": sorted(self.accept_types),
        }

    async def get_user(self, user_id: str | None, auth_context: dict[str, Any]) -> Any | None:
        return self._resolve(auth_context)

    def get_user_sync(self, user_id: str | None, auth_context: dict[str, Any]) -> Any | None:
        return self._resolve(auth_context)

    def _resolve(self, auth_context: dict[str, Any]) -> Any | None:
        raw = auth_context.get("raw_token") if auth_context else None
        if not raw:
            return None

        payload = _jwt_decode(raw)
        if payload is None:
            return None

        token_type = payload.get("token_type")
        if token_type not in self.accept_types:
            logger.debug("JWT token_type '%s' not in accept_types %s", token_type, self.accept_types)
            return None

        return jwt_get_user_from_payload(payload)


# ═══════════════════════════════════════════════════════════════════════════
# TokenAuthBackend — legacy SHA-256 token backend (kept for backward compat)
# ═══════════════════════════════════════════════════════════════════════════


class TokenAuthBackend(BaseAuthentication):
    """Legacy SHA-256 token authentication — validates against the Token table.

    **Prefer JWTTokenAuthBackend for new endpoints.**
    Kept for backward compatibility with existing tokens in the database.
    """

    def __init__(
        self,
        accept_types: set[str] | None = None,
        category: str | None = None,
    ):
        self.accept_types = accept_types or {"access", "api"}
        self.category = category

    @property
    def scheme_name(self) -> str:
        return "token"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "type": "token",
            "header": "authorization",
            "accept_types": sorted(self.accept_types),
            "category": self.category,
        }

    async def get_user(self, user_id: str | None, auth_context: dict[str, Any]) -> Any | None:
        return self._resolve(auth_context)

    def get_user_sync(self, user_id: str | None, auth_context: dict[str, Any]) -> Any | None:
        return self._resolve(auth_context)

    def _resolve(self, auth_context: dict[str, Any]) -> Any | None:
        Token = _resolve_token_model()

        raw = auth_context.get("raw_token") if auth_context else None
        if not raw:
            return None

        token_obj, user = Token.validate_raw_token(raw, accept_types=self.accept_types)
        if user is None:
            return None

        if self.category and token_obj.category != self.category:
            return None

        try:
            token_obj.update_last_used()
        except Exception:
            pass

        return user


# ═══════════════════════════════════════════════════════════════════════════
# Python-side helpers (for use inside handlers or as fallback)
# ═══════════════════════════════════════════════════════════════════════════


def _resolve_token_model():
    """Get the legacy Token model via Django's app registry."""
    try:
        from django.apps import apps as _apps
        Token = _apps.get_model("content", "Token")
        if Token is not None:
            return Token
    except Exception as exc:
        logger.debug("Token model lookup via apps.get_model failed: %s", exc)
    from www.content.models.others import Token as _TokenDirect
    return _TokenDirect


def extract_bearer_token(request) -> str | None:
    """Extract ``Bearer <token>`` from the Authorization header.

    Compatible with Django HttpRequest, PyRequest, and bare dicts.
    """
    try:
        if hasattr(request, "headers") and isinstance(request.headers, dict):
            auth_header = request.headers.get("authorization", "") or request.headers.get("Authorization", "")
        elif hasattr(request, "META"):
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        else:
            return None
    except Exception:
        return None

    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return None


def authenticate_request(request, *, accept_types: set[str] | None = None):
    """Validate a bearer token on a request.

    Tries JWT first, then falls back to legacy SHA-256 Token table lookup.
    Returns user or None.
    """
    raw = extract_bearer_token(request)
    if not raw:
        return None

    # Try JWT first
    payload = _jwt_decode(raw)
    if payload is not None:
        token_type = payload.get("token_type")
        if accept_types is None or token_type in accept_types:
            user = jwt_get_user_from_payload(payload)
            if user is not None:
                return user

    # Fallback to legacy token
    Token = _resolve_token_model()
    token_obj, user = Token.validate_raw_token(raw, accept_types=accept_types)
    if user is not None:
        try:
            token_obj.update_last_used()
        except Exception:
            pass
        return user

    return None


def authenticate_jwt_request(request, *, accept_types: set[str] | None = None):
    """Validate a JWT-only bearer token. Returns user or None."""
    raw = extract_bearer_token(request)
    if not raw:
        return None

    payload = _jwt_decode(raw)
    if payload is None:
        return None

    token_type = payload.get("token_type")
    if accept_types is not None and token_type not in accept_types:
        return None

    return jwt_get_user_from_payload(payload)


# ═══════════════════════════════════════════════════════════════════════════
# Convenience factory
# ═══════════════════════════════════════════════════════════════════════════


def auth_required(*, accept_types: set[str] | None = None):
    """Return ``auth=[JWTTokenAuthBackend(...)]`` for use in route decorators.

    Shorthand so you can write::

        @bolt.get("/me", **auth_required())
        def get_me(request): ...

    instead of::

        @bolt.get("/me", auth=[JWTTokenAuthBackend()])
        def get_me(request): ...

    Note: ``auth_required()`` now defaults to **JWT**.  Use
    ``auth=[TokenAuthBackend()]`` explicitly if you need legacy SHA-256 tokens.
    """
    return {"auth": [JWTTokenAuthBackend(accept_types=accept_types)]}
