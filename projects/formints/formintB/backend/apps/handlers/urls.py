"""POS Cloud — Handlers URL routing (django-fusion API-first surface)."""

from django.http import JsonResponse
from django.urls import path


def _fusion_health(request):
    """GET /fusion/health — sidecar contract health for the frontend."""
    return JsonResponse(
        {
            "status": "healthy",
            "service": "pos-cloud",
            "fusion": True,
            "render_modes": ["data-api", "fusion-render"],
        }
    )


def _render_mode(request):
    """GET /fusion/render-mode — current default render mode."""
    return JsonResponse({"render_first": False, "render_mode": "data-api"})


urlpatterns = [
    path("health", _fusion_health, name="fusion_health"),
    path("render-mode", _render_mode, name="fusion_render_mode"),
]
