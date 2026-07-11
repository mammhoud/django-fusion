from django.urls import include, path

urlpatterns = [
    # NOTE: allauth.urls is NOT included here — it lives at the top of
    # applications/lms-demo/www/urls.py (single source of truth, matching
    # CTC parity). Including it again would re-register URL names and
    # shadow the global allauth include under certain locale prefixes.
    # Registration views (allauth-backed login/signup)
    path("", include("plugins.accounts.urls", namespace="accounts")),
    # Core handler URLs
    path("", include("apps.accounts.urls")),
    # Profile plugin URLs
    path("profile/", include("apps.profile.urls")),
    # Blog URLs
    path("blog/", include("apps.blog.urls")),
]
