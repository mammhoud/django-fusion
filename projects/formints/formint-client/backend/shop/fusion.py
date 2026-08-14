"""
FormintC — Fusion render-mode contract (mirrors formint/fusion.py + landing-fusion).

Dual-mode content delivery, identical to ``projects/formints/formint/server/formint/fusion.py``:

* ``fusion_render_first=True``  → "fusion render first" — Django serves finished
  server-rendered HTML / fusion-encoded JSON as the source of truth.
* ``fusion_render_first=False`` → "data APIs" — the Astro client renders from
  ``/api/catalog/`` JSON + ``/shop/fragments/*`` HTML fragments.

Endpoints exposed here:

    GET /fusion/render-mode/   — report the active mode (+ header override)
    GET /fusion/navigation/    — storefront nav (Home / Menu / Account / Staff)
    GET /fusion/assets/        — FUSION_ASSETS manifest for bundle parity
    GET|POST|DELETE /fusion/session-mode/ — per-session render-mode toggle

The ``X-Fusion-Render-First: true|false`` request header overrides the
configured default for a single request (see ``get_effective_render_first``).
"""

from __future__ import annotations

import json
from typing import Any

from django.conf import settings as django_settings
from django.http import HttpRequest, JsonResponse

from django_fusion.plugins.htmx import is_htmx_request
from django_fusion.routes.rendering.render_mode import resolve_render_first
from django_fusion.routes.rendering.session import FusionCodec, session_checker

__all__ = [
    "get_effective_render_first",
    "render_mode_payload",
    "render_mode_api",
    "navigation_payload",
    "navigation_api",
    "branding_payload",
    "branding_api",
    "assets_payload",
    "assets_api",
    "session_mode_payload",
    "session_mode_get_api",
    "session_mode_set_api",
    "session_mode_clear_api",
]


# ── Effective render-first (mirrors formint's helper) ──────────────────────


def get_effective_render_first(request: HttpRequest | None = None) -> bool:
    """Return the effective ``fusion_render_first`` preference.

    Thin wrapper over django-fusion's canonical ``resolve_render_first``
    chain: ``X-Fusion-Render-First`` header → explicit session preference →
    the ``FUSION_RENDER_FIRST`` setting.
    """
    return resolve_render_first(request)


def render_mode_payload(request: HttpRequest | None = None) -> dict[str, Any]:
    """Build the render-mode report payload shared by the API endpoints."""
    render_first = get_effective_render_first(request)
    return {
        "fusion_render_first": render_first,
        "mode": "fusion-render" if render_first else "data-api",
        "content": {
            "html": "/",
            "data": "/api/",
        },
        "session_cached": "fusion_render_first" in (request.session if request else {}),
        "pointer": FusionCodec.encode_fragment_pointer(
            {"component": "shop.fragments.product_grid"},
            request=request,
            session_aware=False,
        ),
    }


def navigation_payload(request: HttpRequest | None = None) -> dict[str, Any]:
    """Build the storefront nav payload.

    Mirrors landing-fusion's hierarchical nav shape: brand + modules, where
    each module carries its child routes. The Astro header/sidenav consumes
    this directly as the single source of truth for the storefront links.
    """
    shop_name = getattr(django_settings, "SHOP_NAME", "The Daily Grind")
    is_staff = bool(getattr(getattr(request, "user", None), "is_staff", False))
    modules = [
        {
            "id": "menu",
            "label": "Menu",
            "icon": "menu_book",
            "active": False,
            "routes": [
                {"label": "All items", "href": "/", "icon": "storefront", "active": True},
            ],
        },
        {
            "id": "account",
            "label": "Account",
            "icon": "account_circle",
            "active": False,
            "routes": [
                {"label": "My orders", "href": "/orders/mine/", "icon": "receipt_long", "active": False},
            ],
        },
    ]
    if is_staff:
        modules.append(
            {
                "id": "staff",
                "label": "Staff",
                "icon": "badge",
                "active": False,
                "routes": [
                    {"label": "Order inbox", "href": "/employee/", "icon": "inbox", "active": False},
                ],
            }
        )
    return {
        "brand": {"label": shop_name, "href": "/", "tag": "pos-client"},
        "modules": modules,
    }


def branding_payload(request: HttpRequest | None = None) -> dict[str, Any]:
    """Storefront branding — mirrors django_fusion.contrib.api.branding
    (which needs Wagtail) with a pure-settings fallback for the purchase app.

    Reads ``FUSION_SITE_NAME`` / ``FUSION_SITE_TAGLINE`` env vars first, then
    the shop settings, so the same contract is available to the Astro shell.
    """
    from django.utils.translation import get_language

    name = django_settings.FUSION_SITE_NAME if hasattr(django_settings, "FUSION_SITE_NAME") else None
    tagline = (
        django_settings.FUSION_SITE_TAGLINE
        if hasattr(django_settings, "FUSION_SITE_TAGLINE")
        else None
    )
    return {
        "site": {
            "name": name or getattr(django_settings, "SHOP_NAME", "The Daily Grind"),
            "tagline": tagline or getattr(django_settings, "SHOP_TAGLINE", ""),
            "language": get_language(),
        },
        "palette": {
            "paper": "hsl(46 25% 98%)",
            "ink": "hsl(40 6% 10%)",
            "link": "hsl(158 42% 32%)",
        },
    }


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
    """GET /fusion/render-mode/ — report the active fusion render mode."""
    return JsonResponse(render_mode_payload(request))


def navigation_api(request: HttpRequest) -> JsonResponse:
    """GET /fusion/navigation/ — storefront nav from the fusion Site contract."""
    return JsonResponse(navigation_payload(request))


def branding_api(request: HttpRequest) -> JsonResponse:
    """GET /fusion/branding/ — storefront branding (settings-driven)."""
    return JsonResponse(branding_payload(request))


def assets_api(request: HttpRequest) -> JsonResponse:
    """GET /fusion/assets/ — unified asset manifest for bundler integration."""
    return JsonResponse(assets_payload(request))


# ── Session-mode settings toggle (FusionSessionChecker) ────────────────────


def session_mode_payload(request: HttpRequest | None = None) -> dict[str, Any]:
    """Report the current session render-mode state."""
    session = request.session if request is not None else None
    session_cached = bool(session and "fusion_render_first" in session)
    return {
        "fusion_render_first": get_effective_render_first(request),
        "session_cached": session_cached,
        "session_preference": session.get("fusion_render_first") if session_cached else None,
        "default": bool(getattr(django_settings, "FUSION_RENDER_FIRST_DEFAULT", False)),
        "htmx": is_htmx_request(request) if request is not None else False,
    }


def session_mode_get_api(request: HttpRequest) -> JsonResponse:
    """GET /fusion/session-mode/ — report the session render-mode state."""
    return JsonResponse(session_mode_payload(request))


def session_mode_set_api(request: HttpRequest) -> JsonResponse:
    """POST /fusion/session-mode/ — store an explicit render-mode preference.

    Body: ``{"fusion_render_first": true|false}``. Uses
    ``FusionSessionChecker.set_preference`` so the stored value drives
    ``get_effective_render_first`` for subsequent requests.
    """
    try:
        body = json.loads(request.body or b"{}")
        value = body["fusion_render_first"]
        if not isinstance(value, bool):
            raise ValueError("fusion_render_first must be a boolean")
    except (ValueError, TypeError, KeyError) as exc:
        return JsonResponse({"detail": f"Invalid body: {exc}"}, status=400)

    session_checker.set_preference(request, value)
    return JsonResponse(session_mode_payload(request))


def session_mode_clear_api(request: HttpRequest) -> JsonResponse:
    """DELETE /fusion/session-mode/ — clear the stored preference."""
    session_checker.clear_preference(request)
    return JsonResponse(session_mode_payload(request))
