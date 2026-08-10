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


# ── Per-component asset endpoints (Phase 3) ──────────────────────


class ComponentAssetsView(View):
    """Return the full component→chunk map."""

    def get(self, request, *args: Any, **kwargs: Any) -> JsonResponse:
        from django_fusion.core.assets.component_map import ComponentAssetMap

        asset_map = ComponentAssetMap()
        return JsonResponse({
            "status": "ok",
            "data": asset_map.get_all_components(),
        })


class ComponentAssetDetailView(View):
    """Return CSS/JS dependencies for a single component path."""

    def get(self, request, component_name: str, *args: Any, **kwargs: Any) -> JsonResponse:
        from django_fusion.core.assets.component_map import ComponentAssetMap

        asset_map = ComponentAssetMap()
        entry = asset_map.get_component_assets(component_name)
        if entry is None:
            return JsonResponse(
                {"status": "error", "message": f"Component not found: {component_name}"},
                status=404,
            )
        return JsonResponse({"status": "ok", "data": entry.to_dict()})


class PageAssetsView(View):
    """Return the minimal CSS/JS chunk set for a page's components."""

    def get(self, request, page_path: str, *args: Any, **kwargs: Any) -> JsonResponse:
        from django_fusion.fragments.skeleton.resolver import SkeletonResolver
        from django_fusion.core.assets.component_map import ComponentAssetMap

        resolver = SkeletonResolver()
        entries = resolver.resolve_page_skeleton(page_path)

        if not entries:
            return JsonResponse(
                {"status": "error", "message": f"No components found for: {page_path}"},
                status=404,
            )

        asset_map = ComponentAssetMap()
        component_paths = [e.component_path for e in entries]
        page_assets = asset_map.get_page_assets(component_paths)

        return JsonResponse({"status": "ok", "data": page_assets})
