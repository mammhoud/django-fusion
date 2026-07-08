from __future__ import annotations

from django.db import connections
from django.http import JsonResponse
from django.views import View


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


class AssetsHealthView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "ok"})


def health_check(request):
    return JsonResponse({"status": "ok"})
