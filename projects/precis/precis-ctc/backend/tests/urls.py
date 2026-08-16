"""Minimal URL configuration for API smoke tests.

Imports the real API URL patterns from apps.core.api.urls so that
the test client can exercise the actual endpoint code paths.
"""

from __future__ import annotations

from django.urls import include, path

from django_fusion.core.assets import urls as assets_urls

urlpatterns = [
    path("api/", include("apps.core.api.urls")),
    path("fusion/assets/", include(assets_urls)),
]
