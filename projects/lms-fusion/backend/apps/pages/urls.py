"""Root URL patterns for lms-fusion — served from apps/pages/."""
from importlib.util import find_spec

from allauth.account.views import LoginView, LogoutView, PasswordResetView, SignupView
from django.http import JsonResponse
from django.urls import include, path
from django.views import View
from django.views.generic import TemplateView


class NewsletterSubscribeView(View):
    """Simple newsletter subscription stub."""

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "").strip()
        if not email:
            return JsonResponse({"status": "error", "message": "Email is required."}, status=400)
        return JsonResponse({"status": "ok", "message": "Thank you for subscribing!"})


app_name = "apps_pages"  # The effective namespace is "plugins" — set by namespace= in www/urls.py

urlpatterns = [
    # accounts plugin — explicit namespace so {% url 'accounts:...' %} resolves
    path("accounts/", include("apps.pages.accounts.urls", namespace="accounts")),
    path("profile/", include("apps.pages.profile.urls", namespace="profile")),
    # LMS (courses, learning, enrollments)
    path("learning/", include("apps.pages.lms.urls", namespace="lms")),
    # Auth URL aliases
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/register/", SignupView.as_view(), name="register"),
    path("auth/password/forgot/", PasswordResetView.as_view(), name="password_forgot"),
    path(
        "auth/privacy-modal/",
        TemplateView.as_view(template_name="auth/privacy_modal_content.html"),
        name="privacy_modal",
    ),
    path(
        "auth/newsletter/subscribe/",
        NewsletterSubscribeView.as_view(),
        name="subscribe_newsletter",
    ),
]

# Products plugin — optional, guard so missing module doesn't break URL loading
if find_spec("apps.pages.products") is not None and find_spec("apps.pages.products.urls") is not None:
    urlpatterns.append(path("", include("apps.pages.products.urls", namespace="products")))
