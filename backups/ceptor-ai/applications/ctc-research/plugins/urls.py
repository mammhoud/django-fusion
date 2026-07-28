"""Root URL patterns for ctc-research — served from plugins/."""
from importlib.util import find_spec

from allauth.account.views import LoginView, LogoutView, PasswordResetView, SignupView
from django.http import JsonResponse
from django.urls import include, path
from django.views import View
from django.views.generic import TemplateView

from plugins.accounts.views.auth import AllauthLoginView, AllauthSignupView


class NewsletterSubscribeView(View):
    """Simple newsletter subscription stub."""

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "").strip()
        if not email:
            return JsonResponse({"status": "error", "message": "Email is required."}, status=400)
        return JsonResponse({"status": "ok", "message": "Thank you for subscribing!"})


app_name = "plugins"

urlpatterns = [
    # accounts plugin — explicit namespace so {% url 'accounts:...' %} resolves
    path("accounts/", include("plugins.accounts.urls", namespace="accounts")),
    path("profile/", include("plugins.profile.urls", namespace="profile")),
    # LMS plugin (courses, learning, enrollments)
    path("learning/", include("plugins.lms.urls", namespace="lms")),
    # Auth URL aliases — use custom HTMX-aware views from accounts plugin
    path("auth/login/", AllauthLoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/register/", AllauthSignupView.as_view(), name="register"),
    path("auth/password/forgot/", PasswordResetView.as_view(), name="password_forgot"),
    path(
        "auth/privacy-modal/",
        TemplateView.as_view(template_name="account/privacy_modal_content.html"),
        name="privacy_modal",
    ),
    path(
        "auth/newsletter/subscribe/",
        NewsletterSubscribeView.as_view(),
        name="subscribe_newsletter",
    ),
    # Event URLs
    path("events/", include("plugins.accounts.urls_events")),
]

# Products plugin — optional, guard so missing module doesn't break URL loading
if find_spec("plugins.products") is not None and find_spec("plugins.products.urls") is not None:
    urlpatterns.append(path("", include("plugins.products.urls", namespace="products")))
