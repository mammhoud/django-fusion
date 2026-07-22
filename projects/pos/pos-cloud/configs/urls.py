"""POS Cloud — URL configuration with Unfold admin, django-fusion, REST API."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

_root_health = lambda r: JsonResponse({"status": "healthy", "service": "pos-cloud"})

urlpatterns = [
    path("health", _root_health, name="root_health"),
    # Unfold Admin
    path("admin/", admin.site.urls),

    # Analytics & reports dashboard (django-bolt — auto-discovered from core/api.py)
    # The BoltAPI instance at prefix="/apis/data" registers its own routes.
    # Open /apis/data/ to access the bolt dashboard.

    # REST API (django-fusion viewsets + sync receivers)
    path("api/", include("core.urls")),
]
