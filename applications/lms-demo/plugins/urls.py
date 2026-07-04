"""Root URL patterns for www.apps — served from plugins/."""
from allauth.account.views import LoginView, LogoutView, PasswordResetView, SignupView
from django.http import JsonResponse
from django.urls import include, path
from django.views import View
from django.views.generic import TemplateView


class NewsletterSubscribeView(View):
    """Simple newsletter subscription stub — replace with full implementation when ready."""

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "").strip()
        if not email:
            return JsonResponse({"status": "error", "message": "Email is required."}, status=400)
        # TODO: wire to actual subscription backend
        return JsonResponse({"status": "ok", "message": "Thank you for subscribing!"})


app_name = "plugins"

urlpatterns = [
    # NOTE: allauth.urls is NOT included here — it lives at the top of
    # applications/lms-demo/www/urls.py (single source of truth, matching
    # CTC parity). Including it here would re-register the same URL names
    # under i18n_patterns and cause reverse('account_login') shadowing.
    # Plugin namespaces — accounts is already provided by plugins.accounts.urls
    # included at the accounts/ prefix; do NOT add namespace="accounts" here
    # because app_name="accounts" in that module handles it already.
    path("accounts/", include("plugins.accounts.urls")),
    path("profile/", include("plugins.profile.urls", namespace="profile")),
    path("", include("plugins.products.urls", namespace="products")),
    # LMS plugin (courses, learning, enrollments)
    path("learning/", include("plugins.lms.urls", namespace="lms")),
    # Auth URL aliases
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/register/", SignupView.as_view(), name="register"),
    path("auth/password/forgot/", PasswordResetView.as_view(), name="password_forgot"),
    path("auth/privacy-modal/", TemplateView.as_view(template_name="auth/privacy_modal_content.html"), name="privacy_modal"),
    path("auth/newsletter/subscribe/", NewsletterSubscribeView.as_view(), name="subscribe_newsletter"),
]
