"""URL configuration for django-fusion tests."""
from django.urls import include, path

urlpatterns = [
    path("health/", include("django_fusion.health.urls")),
]
