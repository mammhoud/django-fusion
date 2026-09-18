"""Root URL patterns for precis-lms — served from apps/pages/.

All authentication/accounts routes live in the single group defined by
``apps/pages/accounts/urls.py`` (mounted at /accounts/, namespace
``accounts``). This module only wires app includes and public routes.
"""
from importlib.util import find_spec

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import include, path
from django.views import View


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


app_name = "apps_pages"  # The effective namespace is "plugins" — set by namespace= in apps/urls.py

urlpatterns = [
    path("profile/", include("apps.pages.profile.urls", namespace="profile")),
    # LMS (courses, learning, enrollments)
    path("learning/", include("apps.learning.urls", namespace="lms")),
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
