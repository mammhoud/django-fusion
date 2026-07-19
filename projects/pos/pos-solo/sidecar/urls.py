"""
URL configuration for Solo POS Portal.
Extends shared portal patterns with sync endpoints.

@tested pos-portal/solo - URL configuration
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Reuse shared portal viewsets
    path("", include("shared.portal_urls")),
    # Node API
    path("api/nodes/", include("node.urls")),
    # Sync API
    path("api/sync/", include("node.sync_urls")),
]
