from __future__ import annotations

from django.db import connections
from django.http import JsonResponse
from django.views import View

from .checks import asset_health_check, media_health_check


class MediaHealthView(View):
    """Expose the reusable media storage health check as a class-based view."""

    def get(self, request, *args, **kwargs):
        return media_health_check(request)


class AssetHealthView(View):
    """Expose the reusable static/webpack health check as a class-based view."""

    def get(self, request, *args, **kwargs):
        return asset_health_check(request)


# Plural spelling retained for existing project URL imports.
AssetsHealthView = AssetHealthView


class HealthCheckView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "ok"})


class DatabaseHealthView(View):
    def get(self, request, *args, **kwargs):
        status = "ok"
        try:
            connections["default"].cursor()
        except Exception as exc:  # pragma: no cover - health endpoint payload
            status = "error"
            return JsonResponse({"status": status, "error": str(exc)}, status=503)
        return JsonResponse({"status": status})


def health_check(request):
    return JsonResponse({"status": "ok"})
