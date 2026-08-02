"""URL patterns for django-fusion health endpoints."""

from django.urls import path

from .views import AssetHealthView, DatabaseHealthView, HealthCheckView, MediaHealthView

urlpatterns = [
    path("", HealthCheckView.as_view(), name="health"),
    path("assets/", AssetHealthView.as_view(), name="assets-health"),
    path("media/", MediaHealthView.as_view(), name="media-health"),
    path("database/", DatabaseHealthView.as_view(), name="health-database"),
]
