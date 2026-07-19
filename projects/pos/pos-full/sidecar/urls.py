"""
URL configuration for Full POS Portal.
Includes shared portal viewsets plus cloud master CRM endpoints.

@tested pos-portal/full - URL config with cloud CRM
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("shared.portal_urls")),
    # Cloud CRM master endpoints
    path("api/crm/", include("cloud.api_urls")),
    path("api/webhooks/", include("cloud.webhook_urls")),
    path("api/sync/", include("cloud.sync_urls")),
]
