"""Root URL patterns for www.apps — served from plugins/."""
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    # Legacy 'pipelines' namespace — auth URL aliases for templates
    path("auth/", include("plugins.pipelines_urls", namespace="pipelines")),
]
