"""URL patterns for django-fusion health endpoints."""

from django.urls import path

from django_fusion.health import (
    AssetsHealthView,
    DatabaseHealthView,
    HealthCheckView,
)

urlpatterns = [
    path("", HealthCheckView.as_view(), name="health"),
    path("assets/", AssetsHealthView.as_view(), name="assets-health"),
    path("database/", DatabaseHealthView.as_view(), name="health-database"),
]
