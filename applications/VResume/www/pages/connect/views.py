"""
Consolidated views for the connect app.
Handles newsletter subscriptions, confirmation, and tracking.
"""
import logging
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView

from pages.connect.forms.subscription import SubscriptionForm
from pages.connect.models import Subscriber, Campaign, EmailDelivery, TrackedURL

logger = logging.getLogger(__name__)

# 1x1 transparent GIF for tracking
TRACKING_PIXEL = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
    b"\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
    b"\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
)

# ── Subscription Views ───────────────────────────────────────────────

class SubscribeView(FormView):
    """Handle newsletter subscription with double opt-in."""
    form_class = SubscriptionForm
    template_name = "connect/newsletter/subscribe.html"
    success_url = "/comm/newsletter/thank-you/"

    def form_valid(self, form):
        subscriber = form.save(source=self.request.GET.get("source", "website"))
        from pages.connect.services.newsletter_tasks import send_confirmation_email
        send_confirmation_email.delay(subscriber.id)

        if self.request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="alert alert-success">{_("Please check your email to confirm.")}</div>'
            )
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            errors = form.errors.get("email", [_("Invalid email address.")])
            return HttpResponse(f'<div class="alert alert-danger">{errors[0]}</div>', status=400)
        return super().form_invalid(form)


class ConfirmSubscriptionView(View):
    """Confirm newsletter subscription via token."""
    def get(self, request, token):
        subscriber = get_object_or_404(Subscriber, confirmation_token=token, status="pending")
        if subscriber.confirm():
            return render(request, "connect/newsletter/confirmed.html", {"subscriber": subscriber})
        return render(request, "connect/newsletter/already_confirmed.html", {"subscriber": subscriber})


class UnsubscribeView(View):
    """Handle one-click unsubscribe."""
    def get(self, request, token):
        subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
        return render(request, "connect/newsletter/unsubscribe_confirm.html", {"subscriber": subscriber})

    def post(self, request, token):
        subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
        if subscriber.unsubscribe():
            return render(request, "connect/newsletter/unsubscribed.html", {"subscriber": subscriber})
        return render(request, "connect/newsletter/already_unsubscribed.html", {"subscriber": subscriber})


# ── Tracking Views ───────────────────────────────────────────────────

class TrackOpenView(View):
    """Track email open - serve 1x1 pixel and record the open"""
    def get(self, request, token):
        delivery = get_object_or_404(EmailDelivery, tracking_token=token)
        if not delivery.opened_at:
            delivery.opened_at = timezone.now()
        delivery.open_count += 1
        delivery.save(update_fields=["opened_at", "open_count"])
        
        if delivery.campaign_id:
            Campaign.objects.filter(pk=delivery.campaign_id).update(total_opened=F("total_opened") + 1)
        
        return HttpResponse(TRACKING_PIXEL, content_type="image/gif")


class TrackClickView(View):
    """Track email click - record click and redirect to actual URL"""
    def get(self, request, token, url_hash):
        delivery = get_object_or_404(EmailDelivery, tracking_token=token)
        tracked_url = get_object_or_404(TrackedURL, url_hash=url_hash)
        
        if not delivery.clicked_at:
            delivery.clicked_at = timezone.now()
        delivery.click_count += 1
        delivery.save(update_fields=["clicked_at", "click_count"])
        
        if delivery.campaign_id:
            Campaign.objects.filter(pk=delivery.campaign_id).update(total_clicked=F("total_clicked") + 1)
        
        TrackedURL.objects.filter(pk=tracked_url.id).update(click_count=F("click_count") + 1)
        return HttpResponseRedirect(tracked_url.url)
