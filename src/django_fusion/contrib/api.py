"""
django-fusion — shared REST API views (health, branding, layouts).

These small, dependency-light endpoint views were previously duplicated in
every consumer site (cms-fusion, lms-fusion, ...).  They live here so that
projects only need to wire them into their URL configuration::

    # urls.py
    from django_fusion.contrib.api import branding, health, layouts

    urlpatterns = [
        path("health/", health, name="health"),
        path("branding/", branding, {"defaults": {...}}, name="branding"),
        path("layouts/", layouts, name="layouts"),
    ]

The ``branding`` view accepts an optional ``defaults`` mapping (passed via
URL kwargs) used as the env-variable fallback per site.
"""

from __future__ import annotations

import logging
import os

from django.http import HttpRequest, JsonResponse

from django_fusion.config.conf import get_settings
from django_fusion.routes.rendering.session import FusionSessionChecker
from django_fusion.routes.rendering.renderers import fusion_json_response

logger = logging.getLogger(__name__)

# Global checker instance — uses default heuristic (browser UA → True)
health_checker = FusionSessionChecker()


def health(request: HttpRequest):
    """GET /health — return the rendering-strategy preference.

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
    preference = health_checker.get_preference(request)

    ua = (request.META.get("HTTP_USER_AGENT") or "").lower()[:60]

    return fusion_json_response(
        data={
            "fusion_render_first": preference,
            "reason": f"user_agent: {ua}",
            "session_cached": was_cached,
        },
        status=200,
    )


def branding(request: HttpRequest):
    """GET /branding — return dynamic site branding.

    Reads from the Wagtail ``FusionBranding`` snippet first (via the
    ``django_fusion.contrib.branding`` context processor, which already
    falls back to ``FUSION_*`` environment variables), then falls back to
    environment variables directly if the context processor is unavailable.

    Per-site branding is configured through env vars (``FUSION_SITE_NAME``,
    ``FUSION_PRIMARY_COLOR``, ...) or the ``FusionBranding`` Wagtail snippet —
    no per-project code is required.
    """
    try:
        from django_fusion.contrib.branding.context_processors import (
            fusion_branding_context,
        )

        ctx = fusion_branding_context(request)
        data = ctx.get("fusion_branding") or {}
        if data:
            return JsonResponse(data)
    except ImportError:
        # Guard only against the context processor being removed/unavailable;
        # it already swallows runtime errors internally and falls back to env.
        logger.debug("Branding context processor unavailable, using env fallback")

    return JsonResponse(
        {
            "site_name": os.environ.get("FUSION_SITE_NAME", "Fusion"),
            "company_name": os.environ.get("FUSION_COMPANY_NAME", "Fusion Inc."),
            "creator_name": os.environ.get("FUSION_CREATOR_NAME", "Fusion Team"),
            "primary_color": os.environ.get("FUSION_PRIMARY_COLOR", "#00a1b3"),
            "secondary_color": os.environ.get("FUSION_SECONDARY_COLOR", "#5b21b6"),
        }
    )


def layouts(request: HttpRequest):
    """GET /layouts — return the available layout options.

    Reads from the django-fusion ``COMPONENTS`` settings
    (``LAYOUTS`` / ``DEFAULT_LAYOUT``) so backend and frontend stay in sync.
    Falls back to the standard set when the settings façade does not expose
    layout options (newer/leaner settings objects may omit them).

    Returns::

        {
            "status": 200,
            "message": "Success",
            "data": {
                "available": ["default", "full_width", "sidebar", "blank"],
                "default": "default"
            }
        }
    """
    components = get_settings()
    available = getattr(components, "LAYOUTS", ())
    default = getattr(components, "DEFAULT_LAYOUT", "")
    if not available:
        # Fallback set — the settings façade may not expose LAYOUTS.
        available = ("default", "full_width", "sidebar", "blank")
        default = default or "default"
    return fusion_json_response(
        data={
            "available": list(available),
            "default": default,
        },
        status=200,
    )


__all__ = ["branding", "health", "health_checker", "layouts"]

