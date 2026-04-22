"""Root URL patterns for www.apps."""
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    # Legacy 'pipelines' namespace — auth URL aliases for templates
    path("auth/", include("www.apps.pipelines_urls", namespace="pipelines")),
]
