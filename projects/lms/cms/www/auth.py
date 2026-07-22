"""
CTC Research — Bolt-native token authentication backend.

Provides a BaseAuthentication subclass that validates bolt-native Token
records (SHA-256 hashed) from the Authorization: Bearer <token> header.

Usage (per-route):
    from www.auth import TokenAuthBackend

    @bolt.get("/protected", auth=[TokenAuthBackend()])
    def my_handler(request): ...

Usage (default for all routes):
    # In settings.py or BoltAPI init:
    BOLT_AUTHENTICATION_CLASSES = [TokenAuthBackend()]
"""

from __future__ import annotations

import logging
from typing import Any

from django_bolt.auth.backends import BaseAuthentication

logger = logging.getLogger(__name__)


class TokenAuthBackend(BaseAuthentication):
    """Bolt-native token authentication — validates against the Token table.

    Extracts ``Bearer <token>`` from the ``Authorization`` header, SHA-256 hashes
    it, and looks up the matching ``Token`` record.  Only tokens whose
    ``token_type`` is in ``accept_types`` pass authentication.

    Args:
        accept_types: Set of token types allowed for API auth.
            Default: ``{"access", "api"}`` — rejects sync & refresh tokens.
        category: Optional filter — only tokens with this category value
            are accepted (e.g. ``"pos-branch-1"`` to scope to one device).

    Example:
        # Accept only access tokens:
        auth=[TokenAuthBackend(accept_types={"access"})]

        # Accept access + api tokens for a specific category:
        auth=[TokenAuthBackend(accept_types={"access", "api"}, category="mobile-app")]
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
        """Metadata for bolt Rust-side header extraction + Python user resolution."""
        return {
            "type": "token",
            "header": "authorization",
            "accept_types": sorted(self.accept_types),
            "category": self.category,
        }

    async def get_user(self, user_id: str | None, auth_context: dict[str, Any]) -> Any | None:
        """Resolve User from the auth context after Rust extracts the token.

        The raw token string is placed in ``auth_context["raw_token"]`` by bolt's
        Rust layer (or by the Python fallback path).  We hash it and look it up
        in the Token table.
        """
        Token = _resolve_token_model()

        raw = auth_context.get("raw_token") if auth_context else None
        if not raw:
            return None

        token_obj, user = Token.validate_raw_token(raw, accept_types=self.accept_types)
        if user is None:
            return None

        if self.category and token_obj.category != self.category:
            return None

        # Update last-used timestamp (fire-and-forget — non-critical)
        try:
            token_obj.update_last_used()
        except Exception:
            pass

        return user

    def get_user_sync(self, user_id: str | None, auth_context: dict[str, Any]) -> Any | None:
        """Synchronous user resolution (used by sync handlers in thread pool)."""
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
    """Get the Token model via Django's app registry to ensure proper initialization.

    Using ``apps.get_model()`` forces Django's model metaclass to run,
    which properly sets up ``.objects`` and other Manager attributes.
    This is needed because direct ``import`` statements inside the bolt
    TestClient's Rust sub-interpreter may bypass the metaclass, yielding
    a plain Python class without Manager attributes.
    """
    try:
        from django.apps import apps as _apps
        Token = _apps.get_model("content", "Token")
        if Token is not None:
            return Token
    except Exception as exc:
        logger.debug("Token model lookup via apps.get_model failed: %s", exc)
    # Fallback: direct import
    from www.content.models.others import Token as _TokenDirect
    return _TokenDirect


def extract_bearer_token(request) -> str | None:
    """Extract the ``Bearer <token>`` value from the request's Authorization header.

    Compatible with both Django HttpRequest (``request.headers`` as dict-like)
    and bolt PyRequest (``request.headers`` as dict).  Falls back to
    ``request.META`` for Django requests and returns ``None`` on failure.
    """
    # Try primary path: PyRequest.headers or DRF's request.headers (both dict-like)
    try:
        if hasattr(request, "headers") and isinstance(request.headers, dict):
            auth_header = request.headers.get("authorization", "") or request.headers.get("Authorization", "")
        elif hasattr(request, "META"):
            # Django HttpRequest
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        else:
            return None
    except Exception:
        # Fallback for bare dict-like access failures
        return None

    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return None


def authenticate_request(request, *, accept_types: set[str] | None = None):
    """Validate the bearer token on a request.  Returns user or None.

    This is the Python-side fallback path — call it inside a handler when
    bolt's Rust-side auth didn't pick up the token (e.g. for custom types).

    Example:
        def my_handler(request):
            user = authenticate_request(request)
            if user is None:
                return {"error": "Unauthorized"}, 401
            ...
    """
    raw = extract_bearer_token(request)
    if not raw:
        return None

    Token = _resolve_token_model()

    token_obj, user = Token.validate_raw_token(raw, accept_types=accept_types)
    if user is None:
        return None

    try:
        token_obj.update_last_used()
    except Exception:
        pass

    return user


# ═══════════════════════════════════════════════════════════════════════════
# Convenience factory
# ═══════════════════════════════════════════════════════════════════════════


def auth_required(*, accept_types: set[str] | None = None, category: str | None = None):
    """Return ``auth=[TokenAuthBackend(...)]`` for use in route decorators.

    Shorthand so you can write::

        @bolt.get("/me", **auth_required())
        def get_me(request): ...

    instead of::

        @bolt.get("/me", auth=[TokenAuthBackend()])
        def get_me(request): ...
    """
    return {"auth": [TokenAuthBackend(accept_types=accept_types, category=category)]}
