"""Fusion introspection dashboard — plugin map + component usage + tracker.

Two views consumable from any Django/Wagtail project:

- ``fusion/introspection/api/``  — JSON snapshot (plugins, components,
  render history, cache stats) for tooling and the JS bundle.
- ``fusion/introspection/``      — human HTML dashboard.

Wire them with ``fusion_introspection_urls()``::

    from django_fusion.plugins.debug_tools.introspection import (
        fusion_introspection_urls,
    )

    urlpatterns += fusion_introspection_urls()
"""

from __future__ import annotations

import json
from typing import Any

from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import path
from django.views import View

from django_fusion.plugins.tracker import tracker


class FusionIntrospectionApiView(View):
    """JSON API exposing the full fusion introspection snapshot."""

    http_method_names = ("get", "options", "head")

    def get(self, request, *args, **kwargs) -> JsonResponse:
        data = tracker.stats()
        # Per-request detection makes the API useful from a browser/probe:
        data["detected"] = tracker_plugins_detect(request)
        data["request"] = {
            "path": request.path,
            "method": request.method,
        }
        return JsonResponse(data, json_dumps_params={"indent": 2, "sort_keys": True})


def tracker_plugins_detect(request) -> dict[str, Any]:
    """Plugin detection for the current request (public helper for views)."""
    from django_fusion.plugins.registry import plugins

    return plugins.detect(request)


class FusionIntrospectionDashboardView(View):
    """HTML dashboard rendering the plugin/component/usage snapshot."""

    http_method_names = ("get", "options", "head")

    def get(self, request, *args, **kwargs):
        data = tracker.stats()
        data["detected"] = tracker_plugins_detect(request)
        html = render_to_string(
            "django_fusion/plugins/debug_tools/introspection.html",
            {"snapshot": data, "json_snapshot": json.dumps(data, indent=2, sort_keys=True)},
            request=request,
        )
        return HttpResponse(html)


def fusion_introspection_urls() -> list:
    """URL patterns for the introspection API + dashboard (no dependencies)."""
    return [
        path(
            "fusion/introspection/api/",
            FusionIntrospectionApiView.as_view(),
            name="fusion_introspection_api",
        ),
        path(
            "fusion/introspection/",
            FusionIntrospectionDashboardView.as_view(),
            name="fusion_introspection_dashboard",
        ),
    ]


__all__ = [
    "FusionIntrospectionApiView",
    "FusionIntrospectionDashboardView",
    "fusion_introspection_urls",
]
