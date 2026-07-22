"""CTC Research — URL configuration (minimal, extended by plugins + api).

All API endpoints are served via django-bolt (www.api.bolt.*) at /apis/.
The legacy /api/ routes remain for backward compatibility.
"""
from django.urls import include, path

urlpatterns: list = [
    # REST API v1 — plain Django JSON views (existing)
    path("api/", include("www.api.urls", namespace="api")),
]
