"""JSON views for the django-fusion asset manifest.

This module is intentionally framework-level. Site-specific webpack output
paths remain configured by each Django project's ``FUSION_ASSETS`` setting.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from django.http import JsonResponse
from django.views import View

from django_fusion.config.manifest import load_merged_asset_manifest


_DEFAULT_ASSETS: dict[str, dict[str, list[Any]]] = {
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


def _get_assets_config() -> dict[str, Any]:
    """Return a defensive merged config for API and template consumers."""
    merged = load_merged_asset_manifest()
    result: dict[str, Any] = deepcopy(_DEFAULT_ASSETS)
    for section in ("top", "bottom"):
        values = merged.get(section, {}) or {}
        if isinstance(values, dict):
            result[section].update(values)
    for key in ("version", "components", "webpack"):
        if key in merged:
            result[key] = deepcopy(merged[key])
    return result


class AssetsTopView(View):
    """Return CSS links, font preloads, and preconnect hints."""

    def get(self, request, *args: Any, **kwargs: Any) -> JsonResponse:
        return JsonResponse({"status": "ok", "data": _get_assets_config()["top"]})


class AssetsBottomView(View):
    """Return deferred JavaScript assets for the end of the document."""

    def get(self, request, *args: Any, **kwargs: Any) -> JsonResponse:
        return JsonResponse({"status": "ok", "data": _get_assets_config()["bottom"]})


class AssetsManifestView(View):
    """Return the complete top/bottom asset manifest."""

    def get(self, request, *args: Any, **kwargs: Any) -> JsonResponse:
        return JsonResponse({"status": "ok", "data": _get_assets_config()})
