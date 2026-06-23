"""URL configuration for django-grep tests."""
from django.urls import include, path

urlpatterns = [
    path("health/", include("django_grep.health.urls")),
]
