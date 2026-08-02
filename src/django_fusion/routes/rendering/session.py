"""
Session-aware fragment-rendering checker and component-data codec
for django-fusion.

Provides:

- ``FusionSessionChecker`` — middleware-like utility that checks the
  Django session for a cached ``django_render_first`` preference and
  initialises it on the first request.
- ``FusionCodec`` — encode/decode helpers that pair with the TypeScript
  ``FusionDecoder`` class on the frontend so component data is serialised
  and deserialised consistently.

Session flow (health check)
---------------------------

1. On the first request to any fragment endpoint, the checker examines
   the client (device type, user agent, feature flags, etc.) and decides
   whether server-rendered fragments should be preferred.
2. The boolean is stored in ``request.session['fusion_render_first']``.
3. On subsequent requests, the session value is returned immediately
   without re-running the health check.
4. A component or view can override the session value per-request.

Usage::

    from django_fusion.routes.rendering.session import FusionSessionChecker

    checker = FusionSessionChecker()
    preference = checker.get_preference(request)
    # preference is True if fragments should render first

Encode / decode flow
--------------------

The encoder produces a base64-encoded JSON payload with a version
prefix so the TypeScript ``FusionDecoder`` can validate structure.

Usage::

    from django_fusion.routes.rendering.session import FusionCodec

    encoded = FusionCodec.encode(
        data=pointer_dict,
        version="1",
    )
    # On the frontend the decoder class reconstructs the original dict.
"""

from __future__ import annotations

import base64
import json
import logging
from collections.abc import Callable
from typing import Any, TypeVar

from django.http import HttpRequest

from .renderers import FusionJSONEncoder

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SESSION_KEY = "fusion_render_first"
CODEC_VERSION = "1"
# Prefix built inline in FusionCodec.encode() and checked in decode().

# ---------------------------------------------------------------------------
# TypeVars
# ---------------------------------------------------------------------------

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Session Health Check
# ---------------------------------------------------------------------------


class FusionSessionChecker:
    """Session-aware decision maker for fragment-first rendering.

    Uses a simple heuristic on the first request (browser capabilities,
    feature flags, or a dedicated health-check endpoint) and caches the
    result in the Django session so that repeated fragment-pointer calls
    do not re-evaluate the check.

    The default heuristic always returns **True** (fragment-first) for
    browser-based requests because the frontend FusionPage component has
    its own fallback logic.  Subclass to add custom health-check logic.
    """

    def __init__(
        self,
        check_fn: Callable[[HttpRequest], bool] | None = None,
    ) -> None:
        """Optional *check_fn* overrides the built-in health-check heuristic.

        If provided, ``check_fn(request)`` is called instead of
        ``self._check(request)`` each time the session cache is empty.
        """
        self._check_fn = check_fn

    def get_preference(self, request: HttpRequest) -> bool:
        """Return the effective ``django_render_first`` preference.

        1. Return the session-cached value if present.
        2. Otherwise run the health check, cache the result in the
           session, and return it.
        """
        if SESSION_KEY in request.session:
            return bool(request.session[SESSION_KEY])

        preference = self._check(request)
        request.session[SESSION_KEY] = preference
        request.session.set_expiry(
            86400 * 7
        )  # 7 days — matches typical browser-session lifetime ##TODO: Days
        return preference

    def clear_preference(self, request: HttpRequest) -> None:
        """Remove the cached preference from the session.

        Call this after the user changes their rendering preference
        (e.g. via a settings toggle).
        """
        if SESSION_KEY in request.session:
            del request.session[SESSION_KEY]

    def _check(self, request: HttpRequest) -> bool:
        """Run the health check / capability detection.

        When ``self._check_fn`` is provided, delegates to that callable.
        Otherwise uses the built-in User-Agent heuristic.

        Override ``_check`` in a subclass (or pass ``check_fn`` to the
        constructor) to add custom logic such as:

        - Inspecting ``request.user`` for a profile preference.
        - Checking ``request.headers`` for a ``X-Fusion-First`` flag.
        - Calling a remote health-check endpoint.
        - Testing device capabilities via User-Agent analysis.

        The default implementation returns ``True`` for all non-script
        clients and ``False`` for programmatic (API/CLI) user agents.
        """
        if self._check_fn is not None:
            return bool(self._check_fn(request))

        ua = (request.META.get("HTTP_USER_AGENT") or "").lower()
        # Script-based or headless clients usually cannot render fragments.
        if any(kw in ua for kw in ("curl", "wget", "python-requests", "okhttp", "axios")):
            return False
        return True


# Global singleton for convenience
session_checker = FusionSessionChecker()


def get_session_render_first(request: HttpRequest) -> bool:
    """Convenience shortcut that delegates to the global checker."""
    return session_checker.get_preference(request)


# ---------------------------------------------------------------------------
# Component Data Codec
# ---------------------------------------------------------------------------


class FusionCodec:
    """Encode/decode helpers that pair with the TypeScript ``FusionDecoder``.

    The format is a base64-encoded JSON string prefixed with a version
    tag so the frontend can validate structure before decoding.

    Encoding::

        from django_fusion.routes.rendering.session import FusionCodec

        encoded = FusionCodec.encode({"key": "value"})
        # Result: "fusion_v1:eyJrZXkiOiAidmFsdWUifQ=="

    The frontend ``FusionDecoder.decode(encoded)`` reconstructs the dict.
    """

    @staticmethod
    def encode(
        data: Any,
        *,
        version: str = CODEC_VERSION,
        encoder_class: type[json.JSONEncoder] = FusionJSONEncoder,
    ) -> str:
        """Encode *data* to a version-prefixed, base64-encoded JSON string."""
        raw = json.dumps(data, cls=encoder_class, separators=(",", ":"))
        encoded = base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")
        return f"fusion_v{version}:{encoded}"

    @staticmethod
    def decode(encoded: str) -> Any:
        """Decode a string produced by :meth:`encode` back to the original data.

        Raises ``ValueError`` if the prefix or base64 payload is invalid.
        """
        if not encoded.startswith("fusion_v"):
            raise ValueError(f"Invalid codec prefix: {encoded[:20]!r}...")

        try:
            _, b64_part = encoded.split(":", 1)
        except ValueError:
            raise ValueError("Missing base64 payload after prefix") from None

        decoded_bytes = base64.urlsafe_b64decode(b64_part)
        return json.loads(decoded_bytes)

    @staticmethod
    def encode_fragment_pointer(
        pointer: dict[str, Any],
        request: HttpRequest | None = None,
        *,
        session_aware: bool = False,
        encoder_class: type[json.JSONEncoder] = FusionJSONEncoder,
    ) -> str:
        """Shortcut: wrap a fragment pointer dict with session awareness
        and encode it for the frontend decoder.

        When *session_aware* is ``True`` and a *request* is provided,
        the ``fusion_render_first`` value in the pointer is merged with
        the session preference (session wins).
        """
        if session_aware and request is not None:
            session_value = get_session_render_first(request)
            if session_value:
                pointer["fusion_render_first"] = True

        return FusionCodec.encode(pointer, encoder_class=encoder_class)


__all__ = [
    "SESSION_KEY",
    "CODEC_VERSION",
    "FusionSessionChecker",
    "session_checker",
    "get_session_render_first",
    "FusionCodec",
]
