"""
Newsletter Subscription Views
"""
import logging
from typing import Any

from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django_osoul.site import PageHandler

from ceptor_ai.content.forms.newsletter.subscription import SubscriptionForm
from ceptor_ai.content.models.newsletter import Subscriber
from ceptor_ai.services.jobs import dispatch_job
from ceptor_ai.services.newsletter import send_confirmation_email

logger = logging.getLogger(__name__)

class SubscribeView(PageHandler):
    """
    Handle newsletter subscription with double opt-in.
    Supports both regular form submission and HTMX.
    """

    form_class = SubscriptionForm
    template_name = "newsletter/subscribe.html"
    page_title = _("Newsletter Subscription")
    fragment_name = "newsletter.subscribe"

    def process_post(self, request: HttpRequest, *args, **kwargs) -> Any:
        """Process subscription data."""
        form = self.form_class(request.POST)

        if form.is_valid():
            subscriber = form.save(source=request.POST.get("source", "website"))

            # Send confirmation email
            self._send_confirmation_email(subscriber)

            # If HTMX, return a notification success
            if self.is_htmx(request):
                return self.show_notification(
                    message=_("Successfully subscribed! Please check your email for confirmation."),
                    level="success",
                    title=_("Newsletter"),
                    duration=5000,
                    request=request
                )

            return subscriber

        else:
            # Handle invalid form
            error_msg = _("Invalid email.")
            if "email" in form.errors:
                error_msg = form.errors["email"][0]

            if self.is_htmx(request):
                return self.show_notification(
                    message=error_msg,
                    level="error",
                    title=_("Subscription Failed"),
                    request=request,
                    replace_form=False
                )

            # Re-render form with errors
            return render(request, self.template_name, {"form": form})

    def _send_confirmation_email(self, subscriber: Subscriber) -> None:
        """Send confirmation email to subscriber using RQ."""
        dispatch_job(send_confirmation_email, subscriber.id, queue_name="newsletter")
        logger.info(f"Confirmation email job dispatched for {subscriber.email}")


class ConfirmSubscriptionView(View):
    """
    Confirm newsletter subscription via token.
    """

    def get(self, request, token):
        subscriber = get_object_or_404(
            Subscriber,
            confirmation_token=token,
            status="pending"
        )

        if subscriber.confirm():
            logger.info(f"Subscription confirmed for {subscriber.email}")
            return render(request, "newsletter/confirmed.html", {
                "subscriber": subscriber
            })

        return render(request, "newsletter/already_confirmed.html", {
            "subscriber": subscriber
        })


class UnsubscribeView(View):
    """
    Handle one-click unsubscribe.
    """

    def get(self, request, token):
        subscriber = get_object_or_404(
            Subscriber,
            unsubscribe_token=token
        )

        return render(request, "newsletter/unsubscribe_confirm.html", {
            "subscriber": subscriber
        })

    def post(self, request, token):
        subscriber = get_object_or_404(
            Subscriber,
            unsubscribe_token=token
        )

        if subscriber.unsubscribe():
            logger.info(f"Unsubscribed: {subscriber.email}")
            return render(request, "newsletter/unsubscribed.html", {
                "subscriber": subscriber
            })

        return render(request, "newsletter/already_unsubscribed.html", {
            "subscriber": subscriber
        })
