"""cms-full — URL configuration (unified API routing).

Supports both /apis/ (django-bolt / RTK Query) and /api/ (legacy/fusion) prefixes.
All endpoints are served from the unified www.api.* module.
"""
from django.urls import include, path

urlpatterns: list = [
    path("apis/", include("www.api.urls", namespace="apis")),
    path("api/", include("www.api.urls", namespace="api")),
]
