"""Minimal URL configuration for API smoke tests.

Imports the real API URL patterns from apps.core.api.urls so that
the test client can exercise the actual endpoint code paths.
"""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("apis/", include("apps.core.api.urls")),
]
