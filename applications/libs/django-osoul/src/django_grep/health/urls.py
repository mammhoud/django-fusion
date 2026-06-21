"""URL patterns for health check endpoints."""
from django.urls import path

from .views import (
    AssetsHealthView,
    DatabaseHealthView,
    HealthCheckView,
    MediaHealthView,
)

app_name = "health"

urlpatterns = [
    path("", HealthCheckView.as_view(), name="health"),
    path("database/", DatabaseHealthView.as_view(), name="database"),
    path("assets/", AssetsHealthView.as_view(), name="assets"),
    path("media/", MediaHealthView.as_view(), name="media"),
]
