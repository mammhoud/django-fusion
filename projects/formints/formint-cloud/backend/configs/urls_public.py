"""Formint Cloud — public-schema URLconf (django-tenants).

Used via ``PUBLIC_SCHEMA_URLCONF = "configs.urls_public"`` when tenancy is
enabled: requests whose Host does not resolve to a tenant schema are routed
here instead of the tenant URLconf (``configs.urls``). It exposes the tenant
registry (admin), health, monitor, and the django-fusion designer tools.

Under SQLite (``TENANCY_ENABLED=False``) this module is never referenced —
``ROOT_URLCONF`` (``configs.urls``) serves every request as today.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django_fusion.designer import urls as fusion_designer_urls

from apps.handlers.surface import monitor_status as surface_monitor_status


def _root_health(_request):
    return JsonResponse({"status": "healthy", "service": "formint-cloud", "schema": "public"})


urlpatterns = [
    path("health", _root_health, name="root_health"),
    path("monitor/status", surface_monitor_status, name="monitor-status"),
    # Unfold Admin — hosts the Tenant/Domain registry in the public schema.
    path("admin/", admin.site.urls),
    # Protected, read-only MCP designer tools (same view as the tenant URLconf).
    path("fusion/mcp/designer/", include(fusion_designer_urls)),
]
