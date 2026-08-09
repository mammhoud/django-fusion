"""Root URL patterns for lms-fusion — served from apps/pages/."""
from importlib.util import find_spec

from allauth.account.views import LoginView, LogoutView, PasswordResetView, SignupView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import include, path
from django.views import View
from django.views.generic import TemplateView


class NewsletterSubscribeView(View):
    """Newsletter subscription — creates a pending Subscriber and triggers confirmation email."""

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "").strip()
        if not email:
            return JsonResponse({"status": "error", "message": "Email is required."}, status=400)

        from apps.domain.models.newsletter.subscriber import Subscriber

        subscriber, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={
                "name": request.POST.get("name", "").strip(),
                "status": "pending",
                "source": "website_footer",
            },
        )

        if not created and subscriber.status == "confirmed":
            return JsonResponse({
                "status": "ok",
                "message": "You are already subscribed!",
            })

        # If previously unsubscribed, reactivate
        if not created and subscriber.status == "unsubscribed":
            subscriber.regenerate_tokens()
            subscriber.status = "pending"
            subscriber.save(update_fields=["status", "confirmation_token", "unsubscribe_token", "updated_at"])

        # Send confirmation email (best-effort)
        try:
            from apps.domain.services.communication.newsletter import send_confirmation_email
            send_confirmation_email(subscriber.id)
        except Exception:
            pass  # Non-blocking — subscription is still saved

        return JsonResponse({
            "status": "ok",
            "message": "Thank you! Please check your email to confirm your subscription.",
        })


class NewsletterConfirmView(View):
    """Confirm newsletter subscription via token link from email."""

    def get(self, request, token, *args, **kwargs):
        from apps.domain.models.newsletter.subscriber import Subscriber

        subscriber = get_object_or_404(Subscriber, confirmation_token=token)

        if subscriber.status == "confirmed":
            return render(request, "plugins/newsletter/confirmed.html", {
                "subscriber": subscriber,
                "already_confirmed": True,
            })

        subscriber.confirm()
        return render(request, "plugins/newsletter/confirmed.html", {
            "subscriber": subscriber,
            "already_confirmed": False,
        })


class NewsletterUnsubscribeView(View):
    """Unsubscribe from newsletter via token link from email.

    GET  — show confirmation page ("Are you sure?")
    POST — execute the unsubscription
    """

    def get(self, request, token, *args, **kwargs):
        from apps.domain.models.newsletter.subscriber import Subscriber

        subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)

        if subscriber.status == "unsubscribed":
            return render(request, "plugins/newsletter/unsubscribed.html", {
                "subscriber": subscriber,
                "already_unsubscribed": True,
            })

        return render(request, "plugins/newsletter/unsubscribe_confirm.html", {
            "subscriber": subscriber,
        })

    def post(self, request, token, *args, **kwargs):
        from apps.domain.models.newsletter.subscriber import Subscriber

        subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
        subscriber.unsubscribe()

        return render(request, "plugins/newsletter/unsubscribed.html", {
            "subscriber": subscriber,
            "already_unsubscribed": False,
        })


app_name = "apps_pages"  # The effective namespace is "plugins" — set by namespace= in www/urls.py

urlpatterns = [
    # accounts plugin — explicit namespace so {% url 'accounts:...' %} resolves
    path("accounts/", include("apps.pages.accounts.urls", namespace="accounts")),
    path("profile/", include("apps.pages.profile.urls", namespace="profile")),
    # LMS (courses, learning, enrollments)
    path("learning/", include("apps.learning.urls", namespace="lms")),
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
    # Newsletter confirmation & unsubscription (public, no auth required)
    path(
        "newsletter/confirm/<str:token>/",
        NewsletterConfirmView.as_view(),
        name="newsletter_confirm",
    ),
    path(
        "newsletter/unsubscribe/<str:token>/",
        NewsletterUnsubscribeView.as_view(),
        name="newsletter_unsubscribe",
    ),
]

# Products plugin — optional, guard so missing module doesn't break URL loading
if find_spec("apps.pages.products") is not None and find_spec("apps.pages.products.urls") is not None:
    urlpatterns.append(path("", include("apps.pages.products.urls", namespace="products")))
