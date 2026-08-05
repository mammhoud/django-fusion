"""
Formint — Fusion render-mode contract (mirrors landing-fusion's /apis/ helpers).

Dual-mode content delivery, identical to ``projects/landing-fusion/backend/apps/pages/api.py``:

* ``fusion_render_first=True``  → “fusion render first” — Django serves finished
  server-rendered HTML / fusion-encoded JSON as the source of truth.
* ``fusion_render_first=False`` → “data APIs” — the Astro client renders from
  ``/api/v1/*`` JSON.

Endpoints exposed here:

    GET /api/v1/render-mode/   — report the active mode (+ header override)
    GET /api/v1/navigation/    — nav items from FormintSite (source of truth)
    GET /api/v1/assets/        — FUSION_ASSETS manifest for bundle parity
    GET /fusion/render-mode/   — same contract at the fragment path (HTMX)

The ``X-Fusion-Render-First: true|false`` request header overrides the
configured default for a single request (see ``get_effective_render_first``).
"""

from __future__ import annotations

from typing import Any

from django.conf import settings as django_settings
from django.http import HttpRequest, JsonResponse

__all__ = [
    "get_effective_render_first",
    "render_mode_payload",
    "navigation_payload",
    "assets_payload",
    "render_mode_api",
    "navigation_api",
    "assets_api",
]


# ── Effective render-first (mirrors landing-fusion's helper) ───────────────

def get_effective_render_first(request: HttpRequest | None = None) -> bool:
    """Return the effective ``fusion_render_first`` preference.

    Priority:
    1. ``X-Fusion-Render-First`` header — per-request override.
    2. ``FUSION_RENDER_FIRST_DEFAULT`` setting (env ``FUSION_RENDER_FIRST``),
       which is what django-fusion's ``DjangoComponentsSettings`` resolves at
       init for components and fragments.

    ``True``  → “fusion render first” — Django renders finished HTML.
    ``False`` → “data APIs” — the client renders from /api/v1/* JSON.
    """
    if request is not None:
        header = request.headers.get("X-Fusion-Render-First")
        if header in ("true", "false"):
            return header == "true"
    return bool(getattr(django_settings, "FUSION_RENDER_FIRST_DEFAULT", True))


def render_mode_payload(request: HttpRequest | None = None) -> dict[str, Any]:
    """Build the render-mode report payload shared by the API endpoints."""
    render_first = get_effective_render_first(request)
    return {
        "fusion_render_first": render_first,
        "mode": "fusion-render" if render_first else "data-api",
        "content": {
            "html": "/",
            "data": "/api/v1/",
        },
    }


def navigation_payload(request: HttpRequest | None = None) -> dict[str, Any]:
    """Build the nav payload from FormintSite (single source of truth)."""
    from formint.core import formint_site

    nav_items = formint_site.get_navigation_context(request)
    nav_items = [item for item in nav_items if item.get("show_in_nav", True)]
    for item in nav_items:
        item.pop("show_in_nav", None)
    return {"nav_items": nav_items}


def assets_payload(request: HttpRequest | None = None) -> dict[str, Any]:
    """Build the FUSION_ASSETS manifest payload (bundle parity)."""
    from django_fusion.config.assets import get_asset_pipeline_options

    try:
        opts = get_asset_pipeline_options()
    except Exception:
        opts = None

    static_url = getattr(django_settings, "STATIC_URL", "/static/")
    fusion_assets = getattr(django_settings, "FUSION_ASSETS", {}) or {}
    version = hex(hash(str(fusion_assets)) & 0xFFFFFFFF)[2:]

    return {
        "version": version,
        "static_url": static_url,
        "fusion_render_first": get_effective_render_first(request),
        "enabled": opts.enabled if opts else True,
        "webpack_enabled": opts.webpack_enabled if opts else False,
        "webpack_bundle_dir": opts.webpack_bundle_dir if opts else "",
        "top": fusion_assets.get("top", {}),
        "bottom": fusion_assets.get("bottom", {}),
        "fonts": fusion_assets.get("fonts", []),
        "preconnect": fusion_assets.get("preconnect", []),
    }


def render_mode_api(request: HttpRequest) -> JsonResponse:
    """GET /api/v1/render-mode/ — report the active fusion render mode.

    Lets operators (and the frontend) switch between and verify the two
    content-delivery options. The ``X-Fusion-Render-First`` header overrides
    the configured default for a single request.
    """
    return JsonResponse(render_mode_payload(request))


# ── Navigation ──────────────────────────────────────────────────────────────

def navigation_api(request: HttpRequest) -> JsonResponse:
    """GET /api/v1/navigation/ — nav links from the django-fusion Site.

    Uses ``FormintSite.get_navigation_context()`` as the single source of
    truth for the POS navigation structure (Home / Data / Admin).
    """
    return JsonResponse(navigation_payload(request))


# ── Assets ──────────────────────────────────────────────────────────────────

def assets_api(request: HttpRequest) -> JsonResponse:
    """GET /api/v1/assets/ — unified asset manifest for bundler integration.

    Returns the FUSION_ASSETS config that both Django template tags and the
    Astro frontend can consume to keep CSS/JS bundles in sync.
    """
    return JsonResponse(assets_payload(request))
