"""
URL configuration for django-fusion tests.

Kept minimal — only imports what is available in the test conftest's
INSTALLED_APPS so we avoid ``LookupError`` during configure-time.
"""
from django.urls import include, path
from django_fusion.plugins.debug_tools.introspection import (
    fusion_introspection_urls,
)

urlpatterns = [
    path("fragments/", include("django_fusion.fragments.urls")),
]
urlpatterns += fusion_introspection_urls()
