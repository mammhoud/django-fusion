"""POS Cloud — django-fusion contract views (Django-native sidecar surface).

The removed Robyn sidecar exposed a ``/fusion/*`` render-mode contract that
the Astro frontend consumed (health, render-mode, nav, session-mode,
assets).  These views replicate that exact contract directly on Django so
the frontend URL surface is unchanged::

    GET    /fusion/health       — sidecar-compatible health
    GET    /fusion/render-mode  — effective render preference
    GET    /fusion/nav          — POS Cloud shell navigation tree
    GET    /fusion/session-mode — current session render preference
    POST   /fusion/session-mode — set session preference ({mode: data-api|fusion-render})
    DELETE /fusion/session-mode — clear session preference
    GET    /fusion/assets       — fusion CSS/JS asset lists
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_fusion.routes.rendering.session import FusionSessionChecker

# Global checker — caches the render preference in the Django session.
_checker = FusionSessionChecker()

NAV_ITEMS = [
    {"label": "Dashboard", "href": "/", "icon": "dashboard"},
    {"label": "Organizations", "href": "/organizations", "icon": "corporate_fare"},
    {"label": "Branches", "href": "/branches", "icon": "store"},
    {"label": "CRM", "href": "/crm", "icon": "handshake"},
    {"label": "Sync", "href": "/sync", "icon": "sync"},
    {"label": "Admin", "href": "/admin", "icon": "admin"},
]


def fusion_health(request: HttpRequest) -> JsonResponse:
    """GET /fusion/health — sidecar contract health for the frontend."""
    return JsonResponse({
        "status": "healthy",
        "service": "pos-cloud",
        "fusion": True,
        "render_modes": ["data-api", "fusion-render"],
        "version": "1.0",
    })


def render_mode(request: HttpRequest) -> JsonResponse:
    """GET /fusion/render-mode — current effective render preference."""
    preference = _checker.get_preference(request)
    return JsonResponse({
        "render_first": preference,
        "render_mode": "fusion-render" if preference else "data-api",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })


def navigation(request: HttpRequest) -> JsonResponse:
    """GET /fusion/nav — navigation tree for the POS Cloud shell."""
    return JsonResponse({"language": "en", "nav_items": NAV_ITEMS})


def assets(request: HttpRequest) -> JsonResponse:
    """GET /fusion/assets — fusion CSS/JS asset lists."""
    return JsonResponse({"css": ["/static/css/fusion.css"], "js": []})


@csrf_exempt
def session_mode(request: HttpRequest) -> JsonResponse:
    """GET/POST/DELETE /fusion/session-mode — session render preference.

    * GET    — return the current preference (``render_first`` / ``mode``).
    * POST   — accept ``{"mode": "data-api" | "fusion-render"}`` (or
      ``{"fusion_render_first": bool}``) and persist it in the session.
    * DELETE — clear the cached preference back to the default.
    """
    if request.method == "POST":
        body = json.loads(request.body or b"{}")
        mode = body.get("mode")
        if mode is None and "fusion_render_first" in body:
            mode = "fusion-render" if body["fusion_render_first"] else "data-api"
        if mode not in ("data-api", "fusion-render"):
            mode = "data-api"
        _checker.set_preference(request, mode == "fusion-render")
        return JsonResponse({"mode": mode, "saved": True})

    if request.method == "DELETE":
        _checker.clear_preference(request)
        return JsonResponse({"mode": "data-api", "cleared": True})

    preference = _checker.get_preference(request)
    return JsonResponse({
        "render_first": preference,
        "mode": "fusion-render" if preference else "data-api",
    })
