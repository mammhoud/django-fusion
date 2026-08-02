"""
POS Full — FusionSessionChecker integration for Robyn sidecar.

Provides a ``RobynFusionChecker`` that mirrors the django-fusion
``FusionSessionChecker`` pattern but works with Robyn's ``Request``
(no Django session middleware).  The health-check result is not cached
server-side (Robyn has no session middleware); the Tauri frontend caches
the preference in ``sessionStorage`` via the ``FusionDecoder`` class.

Usage::

    from middleware.fusion import fusion_health_checker

    # In any route handler:
    preference = fusion_health_checker.get_preference(request)
    # → True (fragment-first) or False (JSON-first)

    # Or via the /fusion/health endpoint (registered below).

Customisation::

    from middleware.fusion import RobynFusionChecker

    checker = RobynFusionChecker(
        check_fn=lambda req: (
            get_token_info() is not None
            and get_token_info().get("role") == "admin"
        )
    )
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from robyn import Request, jsonify

from middleware.auth import get_token_info

logger = logging.getLogger("pos.fusion")

# ---------------------------------------------------------------------------
# RobynFusionChecker
# ---------------------------------------------------------------------------


class RobynFusionChecker:
    """Session-checker for Robyn sidecar servers.

    Mirrors ``django_fusion.routes.rendering.session.FusionSessionChecker`` but
    adapted for Robyn's ``Request`` (no Django session middleware).
    Instead of caching in ``request.session``, the health-check result
    is returned per-request — the frontend ``FusionDecoder`` caches it
    in the browser's ``sessionStorage``.

    The default ``check_fn`` inspects the device token (via
    ``get_token_info()``) and returns ``True`` (fragment-first) only for
    devices with an admin or manager role.

    Pass a custom ``check_fn`` to the constructor to override::

        checker = RobynFusionChecker(
            check_fn=lambda req: _is_admin_device(),
        )
    """

    def __init__(
        self,
        check_fn: Callable[[Request], bool] | None = None,
    ) -> None:
        self._check_fn = check_fn

    def get_preference(self, request: Request) -> bool:
        """Return the effective rendering preference.

        Delegates to ``_check()`` every call — no session caching on the
        server side (the frontend FusionDecoder caches in sessionStorage).
        """
        return self._check(request)

    def _check(self, request: Request) -> bool:
        """Run the health check / capability detection.

        Priority:
        1. Custom ``check_fn`` if provided.
        2. Device token role: admin/manager → ``True``, else ``False``.
        3. User-Agent heuristic (same as Django FusionSessionChecker).
        """
        if self._check_fn is not None:
            return bool(self._check_fn(request))

        # Device token based check
        token_info = get_token_info()
        if token_info is not None:
            role = token_info.get("role", "").lower()
            if role in ("admin", "manager"):
                return True
            return False

        # User-Agent fallback (for programmatic clients)
        ua = (request.headers.get("User-Agent") or "").lower()
        if any(kw in ua for kw in ("curl", "wget", "python-requests", "okhttp", "axios")):
            return False
        return True


# Global singleton
fusion_health_checker = RobynFusionChecker()


def register_fusion_health_routes(app: Any) -> None:
    """Register ``/fusion/health`` endpoint on the Robyn app."""

    @app.get("/fusion/health")
    async def fusion_health(request: Request):
        """GET /fusion/health — return the rendering-strategy preference.

        Returns::

            {
                "fusion_render_first": true | false,
                "reason": "device_role: admin" | "user_agent: ...",
                "token_present": true | false
            }
        """
        preference = fusion_health_checker.get_preference(request)

        token_info = get_token_info()
        if token_info:
            reason = f"device_role: {token_info.get('role', 'unknown')}"
        else:
            ua = (request.headers.get("User-Agent") or "").lower()
            reason = f"user_agent: {ua[:50]}"

        return jsonify({
            "fusion_render_first": preference,
            "reason": reason,
            "token_present": token_info is not None,
        })

    logger.info("Registered /fusion/health endpoint")
