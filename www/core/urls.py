from django.urls import include, path

urlpatterns = [
    # Allauth URLs (accounts/login/, accounts/signup/, etc.)
    path("accounts/", include("allauth.urls")),
    # Registration views (allauth-backed login/signup)
    path("", include("apps.accounts.registration.urls")),
    # Core handler URLs
    path("", include("apps.accounts.urls")),
    # Profile plugin URLs
    path("profile/", include("apps.profile.urls")),
    # Blog URLs
    path("blog/", include("apps.blog.urls")),
]
