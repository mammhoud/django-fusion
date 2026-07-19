"""
URL configuration for Minimal POS Portal.
Node-only edition with shared portal viewsets and minimal node agent.

@tested pos-portal/minimal - URL config
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("shared.portal_urls")),
    path("api/nodes/", include("node.urls")),
]
