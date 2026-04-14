from django.urls import include, path

urlpatterns = [
    # Health check + auth routes served by django-grep
    path("", include("django_rseal.pipelines.urls")),

    # Allauth URLs (accounts/login/, accounts/signup/, etc.)
    path("accounts/", include("allauth.urls")),

    # Registration views (allauth-backed login/signup)
    path("", include("apps.handlers.registration.urls")),

    # Core handler URLs
    path("", include("apps.handlers.urls")),
]
