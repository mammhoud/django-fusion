"""
Fusion CMS — Fusion health-check endpoint.

Provides a ``/api/fusion/health`` endpoint that the frontend ``FusionMiddleware``
can call on app startup to seed the ``sessionStorage`` preference instead of
defaulting to data mode.

The endpoint uses ``FusionSessionChecker`` from django-fusion to determine
the rendering preference based on the request's User-Agent and/or session.
"""

from __future__ import annotations

import logging

from django.http import HttpRequest, JsonResponse
from django_fusion.routes import FusionSessionChecker, fusion_json_response

logger = logging.getLogger(__name__)

# Global checker instance — uses default heuristic (browser UA → True)
fusion_health_checker = FusionSessionChecker()


def fusion_health(request: HttpRequest):
    """GET /api/fusion/health — return the rendering-strategy preference.

    Uses ``FusionSessionChecker`` to evaluate the request and cache the
    result in the Django session (7-day expiry).

    Returns::

        {
            "status": 200,
            "message": "Success",
            "data": {
                "fusion_render_first": true | false,
                "reason": "user_agent: Mozilla/5.0 ...",
                "session_cached": true | false
            }
        }
    """
    was_cached = "fusion_render_first" in request.session
    preference = fusion_health_checker.get_preference(request)

    ua = (request.META.get("HTTP_USER_AGENT") or "").lower()[:60]

    return fusion_json_response(
        data={
            "fusion_render_first": preference,
            "reason": f"user_agent: {ua}",
            "session_cached": was_cached,
        },
        status=200,
    )


__all__ = ["fusion_health", "fusion_health_checker"]
