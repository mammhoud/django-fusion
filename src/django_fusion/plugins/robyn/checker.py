"""
RobynFusionChecker — fragment-rendering preference for Robyn sidecar servers.

Mirrors ``django_fusion.fragments.session.FusionSessionChecker`` but adapted
for Robyn's ``Request`` (no Django session middleware).  Instead of caching
in ``request.session``, the health-check result is returned per-request —
the frontend ``FusionDecoder`` caches it in ``sessionStorage``.

The default ``check_fn`` accepts any request; customize via the constructor
to restrict fragment-first mode based on device roles, headers, or capabilities.

Usage::

    from django_fusion.comp.robyn.checker import RobynFusionChecker

    checker = RobynFusionChecker()

    @app.get("/fusion/health")
    async def fusion_health(request: Request):
        pref = checker.get_preference(request)
        return jsonify({"fusion_render_first": pref})

    # Custom logic — admin/manager devices get fragments:
    from shared.auth import get_token_info

    checker = RobynFusionChecker(
        check_fn=lambda req: (
            get_token_info() is not None
            and get_token_info().get("role") in ("admin", "manager")
        ),
    )

    # Register the /fusion/health endpoint:
    checker.register_health_route(app)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("django_fusion.robyn")


class RobynFusionChecker:
    """Session-checker for Robyn sidecar servers.

    The default ``check_fn`` returns ``True`` (fragment-first) for all
    requests.  Override via the constructor to restrict fragment rendering
    to admin/manager roles, specific user-agents, or custom capability checks.

    The frontend ``FusionDecoder`` caches the ``fusion_render_first``
    preference in the browser's ``sessionStorage``, so the server-side
    check runs only when the cache is cold or expired.
    """

    def __init__(
        self,
        check_fn: Callable[[Any], bool] | None = None,
    ) -> None:
        self._check_fn = check_fn

    def get_preference(self, request: Any) -> bool:
        """Return the effective rendering preference for *request*.

        Delegates to ``_check()`` every call — no session caching on the
        server side.
        """
        return self._check(request)

    def _check(self, request: Any) -> bool:
        """Run the health check / capability detection.

        Priority:
        1. Custom ``check_fn`` if provided.
        2. User-Agent heuristic — programmatic clients (curl, wget, etc.)
           get ``False``; browsers get ``True``.
        """
        if self._check_fn is not None:
            return bool(self._check_fn(request))

        # User-Agent fallback — programmatic clients default to JSON
        ua = (getattr(request, "headers", {}).get("User-Agent") or "").lower()
        if any(kw in ua for kw in ("curl", "wget", "python-requests", "okhttp", "axios")):
            return False
        return True

    def register_health_route(self, app: Any, path: str = "/fusion/health") -> None:
        """Register ``GET {path}`` endpoint that returns the preference.

        Response format::

            {
                "fusion_render_first": true | false,
                "reason": "check_fn" | "user_agent: <ua>",
                "token_present": false
            }
        """
        checker = self  # capture for closure

        @app.get(path)
        async def _fusion_health(request):
            from robyn import jsonify  # lazy import — only needed if this route is registered

            preference = checker.get_preference(request)

            ua = (request.headers.get("User-Agent") or "").lower()
            reason = f"user_agent: {ua[:50]}" if ua else "default"

            return jsonify({
                "fusion_render_first": preference,
                "reason": reason,
                "token_present": False,
            })

        logger.info("Registered fusion health endpoint at %s", path)
