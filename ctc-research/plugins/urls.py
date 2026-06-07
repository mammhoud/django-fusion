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
    path("accounts/", include("allauth.urls")),
    # Plugin namespaces
    path("accounts/", include("plugins.accounts.urls", namespace="accounts")),
    path("profile/", include("plugins.profile.urls", namespace="profile")),
    path("", include("plugins.products.urls", namespace="products")),
    # LMS plugin (courses, learning, enrollments)
    path("learning/", include("plugins.lms.urls", namespace="lms")),
    # Auth URL aliases — merged from legacy 'pipelines' namespace
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/register/", SignupView.as_view(), name="register"),
    path("auth/password/forgot/", PasswordResetView.as_view(), name="password_forgot"),
    path("auth/privacy-modal/", TemplateView.as_view(template_name="auth/privacy_modal_content.html"), name="privacy_modal"),
    path("auth/newsletter/subscribe/", NewsletterSubscribeView.as_view(), name="subscribe_newsletter"),
]
