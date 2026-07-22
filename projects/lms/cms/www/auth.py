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

from typing import Any

from django_bolt.auth.backends import BaseAuthentication


class TokenAuthBackend(BaseAuthentication):
    """Bolt-native token authentication — validates against the Token table.

    Extracts ``Bearer <token>`` from the ``Authorization`` header, SHA-256 hashes
    it, and looks up the matching ``Token`` record.  Only tokens whose
    ``token_type`` is in ``accept_types`` pass authentication.

    Args:
        accept_types: Set of token types allowed for API auth.
            Default: ``{\"access\", \"api\"}`` — rejects sync & refresh tokens.
        category: Optional filter — only tokens with this category value
            are accepted (e.g. ``\"pos-branch-1\"`` to scope to one device).

    Example:
        # Accept only access tokens:
        auth=[TokenAuthBackend(accept_types={\"access\"})]

        # Accept access + api tokens for a specific category:
        auth=[TokenAuthBackend(accept_types={\"access\", \"api\"}, category=\"mobile-app\")]
    """

    def __init__(
        self,
        accept_types: set[str] | None = None,
        category: str | None = None,
    ):
        self.accept_types = accept_types or {\"access\", \"api\"}
        self.category = category

    @property
    def scheme_name(self) -> str:
        return \"token\"

    def to_metadata(self) -> dict[str, Any]:
        """Metadata for bolt Rust-side header extraction + Python user resolution."""
        return {
            \"type\": \"token\",
            \"header\": \"authorization\",
            \"accept_types\": sorted(self.accept_types),
            \"category\": self.category,
        }

    async def get_user(self, user_id: str | None, auth_context: dict[str, Any]) -> Any | None:
        """Resolve User from the auth context after Rust extracts the token.

        The raw token string is placed in ``auth_context[\"raw_token\"]`` by bolt's
        Rust layer (or by the Python fallback path).  We hash it and look it up
        in the Token table.
        """
        from www.content.models.others import Token

        raw = auth_context.get(\"raw_token\") if auth_context else None
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
        from www.content.models.others import Token

        raw = auth_context.get(\"raw_token\") if auth_context else None
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


def extract_bearer_token(request) -> str | None:
    """Extract the ``Bearer <token>`` value from the request's Authorization header."""
    auth_header = request.headers.get(\"authorization\", \"\") or request.headers.get(\"Authorization\", \"\")
    if auth_header.lower().startswith(\"bearer \"):
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
                return {\"error\": \"Unauthorized\"}, 401
            ...
    """
    raw = extract_bearer_token(request)
    if not raw:
        return None

    from www.content.models.others import Token

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

        @bolt.get(\"/me\", **auth_required())
        def get_me(request): ...

    instead of::

        @bolt.get(\"/me\", auth=[TokenAuthBackend()])
        def get_me(request): ...
    """
    return {\"auth\": [TokenAuthBackend(accept_types=accept_types, category=category)]}
