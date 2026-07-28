"""Views for django-fusion assets endpoints.

Provides JSON endpoints that describe which CSS, font, and JS assets
should be loaded by the frontend.

* ``AssetsTopView`` — CSS links and font preloads for ``<head>``
* ``AssetsBottomView`` — JS scripts for ``</body>``
* ``AssetsManifestView`` — combined top + bottom manifest
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.http import JsonResponse
from django.views import View


def _get_assets_config() -> dict[str, Any]:
    """Read ``FUSION_ASSETS`` from Django settings with sensible defaults."""
    defaults: dict[str, Any] = {
        "top": {
            "css": [],
            "fonts": [],
            "preconnect": [],
            "inline_css": [],
        },
        "bottom": {
            "js": [],
            "inline_js": [],
        },
    }
    configured = getattr(settings, "FUSION_ASSETS", {})
    # Deep-merge top-level keys
    result = defaults.copy()
    for section in ("top", "bottom"):
        if section in configured:
            result[section].update(configured[section])
    return result


class AssetsTopView(View):
    """GET /fusion/assets/top/

    Returns CSS links, font preloads, and preconnect hints for ``<head>``.
    """

    def get(self, request, *args, **kwargs):
        config = _get_assets_config()
        return JsonResponse({
            "status": "ok",
            "data": config["top"],
        })


class AssetsBottomView(View):
    """GET /fusion/assets/bottom/

    Returns JS scripts for before ``</body>``.
    """

    def get(self, request, *args, **kwargs):
        config = _get_assets_config()
        return JsonResponse({
            "status": "ok",
            "data": config["bottom"],
        })


class AssetsManifestView(View):
    """GET /fusion/assets/manifest/

    Returns the complete assets manifest (top + bottom).
    """

    def get(self, request, *args, **kwargs):
        config = _get_assets_config()
        return JsonResponse({
            "status": "ok",
            "data": {
                "top": config["top"],
                "bottom": config["bottom"],
            },
        })
