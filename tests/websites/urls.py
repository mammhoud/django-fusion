"""URL variations used by website smoke tests."""

from django.http import JsonResponse
from django.urls import path


def assets_health(request):
    return JsonResponse({"status": "ok", "assets": "available"})


urlpatterns = [path("assets/health/", assets_health, name="assets-health")]
