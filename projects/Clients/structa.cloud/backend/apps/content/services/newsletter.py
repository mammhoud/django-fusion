"""Newsletter services — branded welcome email, provider sync, broadcasts.

Responsibilities
----------------
* ``notify_newsletter_subscription()`` — the post-subscribe pipeline the API
  calls: a branded welcome email on fresh signups, provider sync on every
  signup. Never raises.
* ``send_welcome_email()`` — one branded HTML+plain welcome message.
* ``sync_subscriber_to_provider()`` — idempotent push of a subscriber to the
  configured provider (``NEWSLETTER_PROVIDER`` = ``mailchimp`` | ``brevo`` |
  ``webhook``). Unconfigured → no-op.
* ``send_newsletter_broadcast()`` — batch email for the Wagtail admin
  broadcast action; returns how many messages were handed to the backend.

Provider calls use only the stdlib (``urllib``) so the backend gains no new
dependencies. Every entry point catches its own exceptions and logs them —
the callers (subscribe API, admin view, management command) treat failures
as "done best-effort", never as an error to surface to the visitor.
"""

import base64
import hashlib
import json
import logging
import urllib.request

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


# ── Brand context ───────────────────────────────────────────────────────────

def _site_name() -> str:
    """The Wagtail-managed site name, falling back to the brand default."""
    try:
        from apps.content.models.settings import SiteSettings
        site = SiteSettings.objects.order_by("id").first()
        if site and site.site_name:
            return site.site_name
    except Exception:
        pass
    return "Structa Cloud"


def _site_links() -> dict:
    """Links the email shells share (products CTA, privacy policy)."""
    products_url = "https://structa.cloud/products/"
    privacy_url = "/privacy"
    try:
        from apps.content.models.settings import SiteSettings
        site = SiteSettings.objects.order_by("id").first()
        if site:
            if site.privacy_policy_url:
                privacy_url = site.privacy_policy_url
            if site.logo:
                products_url = "https://structa.cloud/products/"
    except Exception:
        pass
    return {
        "site_name": _site_name(),
        "products_url": products_url,
        "privacy_url": privacy_url,
        "contact_email": getattr(settings, "DEFAULT_FROM_EMAIL", "structa.cloud@gmail.com"),
    }


def _send_email(subject: str, to: list[str], template_base: str, context: dict) -> bool:
    """Render ``<template_base>.html`` + ``.txt`` and send a multipart message.

    Returns True when the message reached the mail backend. The subject comes
    from the caller (broadcast) or ``<template_base>_subject.txt`` (welcome).
    """
    try:
        html = render_to_string(f"{template_base}.html", context).strip()
        plain = render_to_string(f"{template_base}.txt", context).strip()
        message = EmailMultiAlternatives(
            subject=subject,
            body=plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to,
        )
        message.attach_alternative(html, "text/html")
        message.send(fail_silently=False)
        return True
    except Exception:
        logger.exception("newsletter email send failed (template=%s)", template_base)
        return False


# ── Welcome email ───────────────────────────────────────────────────────────

def send_welcome_email(subscriber) -> None:
    """Send the branded welcome email for a fresh subscription.

    On success stamps ``welcome_sent_at``; on failure logs and leaves it unset
    so a retry job could pick the address up later.
    """
    links = _site_links()
    subject = render_to_string(
        "newsletter/email/welcome_subject.txt", {"site_name": links["site_name"]},
    ).strip()
    if not subject:
        subject = f"Welcome to {links['site_name']}"
    ok = _send_email(subject, [subscriber.email], "newsletter/email/welcome_message", {
        "email": subscriber.email,
        **links,
    })
    if ok:
        try:
            subscriber.welcome_sent_at = timezone.now()
            subscriber.save(update_fields=["welcome_sent_at", "updated_at"])
            logger.info("newsletter welcome email sent: %s", subscriber.email)
        except Exception:
            logger.exception("newsletter welcome stamp failed for %s", subscriber.email)


# ── Provider sync (Mailchimp / Brevo / webhook) ────────────────────────────

def _open(request: urllib.request.Request) -> bytes:
    """Open a request with a short timeout; let the caller handle errors."""
    with urllib.request.urlopen(request, timeout=8) as response:
        return response.read()


def _sync_mailchimp(subscriber) -> None:
    api_key = settings.NEWSLETTER_MAILCHIMP_API_KEY
    list_id = settings.NEWSLETTER_MAILCHIMP_LIST_ID
    prefix = settings.NEWSLETTER_MAILCHIMP_SERVER_PREFIX or "us1"
    if not api_key or not list_id:
        logger.warning("mailchimp provider set but api key/list id missing; skipping")
        return

    subscriber_hash = hashlib.md5(subscriber.email.lower().encode("utf-8")).hexdigest()
    url = f"https://{prefix}.api.mailchimp.com/3.0/lists/{list_id}/members/{subscriber_hash}"
    payload = {
        "email_address": subscriber.email,
        "status": "subscribed" if subscriber.is_active else "unsubscribed",
        "status_if_new": "subscribed" if subscriber.is_active else "unsubscribed",
        "merge_fields": {"SOURCE": (subscriber.source or "footer")[:10]},
    }
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), method="PUT",
    )
    request.add_header("Content-Type", "application/json")
    # Mailchimp authenticates with HTTP Basic where the username IS the api key.
    credentials = base64.b64encode(f"{api_key}:".encode("utf-8")).decode("ascii")
    request.add_header("Authorization", f"Basic {credentials}")
    _open(request)


def _sync_brevo(subscriber) -> None:
    api_key = settings.NEWSLETTER_BREVO_API_KEY
    list_id = settings.NEWSLETTER_BREVO_LIST_ID
    if not api_key or not list_id:
        logger.warning("brevo provider set but api key/list id missing; skipping")
        return

    if subscriber.is_active:
        # Upsert the contact and add it to the list (updateEnabled lets an
        # existing contact be re-added without a duplicate).
        url = "https://api.brevo.com/v3/contacts"
        payload = {
            "email": subscriber.email,
            "listIds": [int(list_id)],
            "updateEnabled": True,
        }
        request = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"), method="POST",
        )
    else:
        # Paused → remove from the list (Brevo's unlink endpoint keeps the
        # contact record, matching "paused, not deleted").
        url = f"https://api.brevo.com/v3/contacts/lists/{int(list_id)}/contacts"
        payload = {"emails": [subscriber.email]}
        request = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"), method="DELETE",
        )
    request.add_header("Content-Type", "application/json")
    request.add_header("api-key", api_key)
    _open(request)


def _sync_webhook(subscriber) -> None:
    url = settings.NEWSLETTER_WEBHOOK_URL
    if not url:
        logger.warning("webhook provider set but NEWSLETTER_WEBHOOK_URL missing; skipping")
        return
    payload = {
        "event": "subscriber.sync",
        "email": subscriber.email,
        "active": subscriber.is_active,
        "source": subscriber.source,
        "synced_at": timezone.now().isoformat(),
    }
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), method="POST",
    )
    request.add_header("Content-Type", "application/json")
    _open(request)


def sync_subscriber_to_provider(subscriber) -> bool:
    """Push one subscriber to the configured provider. Idempotent, no-op when
    no provider is configured. Returns True when the push reached the provider
    (or was skipped as unconfigured-with-warning only when half-configured)."""
    provider = (getattr(settings, "NEWSLETTER_PROVIDER", "") or "").strip().lower()
    if not provider:
        return False
    try:
        if provider == "mailchimp":
            _sync_mailchimp(subscriber)
        elif provider == "brevo":
            _sync_brevo(subscriber)
        elif provider == "webhook":
            _sync_webhook(subscriber)
        else:
            logger.warning("unknown NEWSLETTER_PROVIDER %r; skipping sync", provider)
            return False
        subscriber.provider_synced_at = timezone.now()
        subscriber.save(update_fields=["provider_synced_at", "updated_at"])
        return True
    except Exception:
        logger.exception("newsletter provider sync failed for %s", subscriber.email)
        return False


# ── Post-subscribe pipeline ─────────────────────────────────────────────────

def notify_newsletter_subscription(subscriber, is_new: bool) -> None:
    """Fire the post-subscribe side effects without blocking the response.

    * Fresh signup  → branded welcome email (``welcome_sent_at`` stamp).
    * Every signup  → idempotent provider sync (``provider_synced_at`` stamp).

    Both steps are individually fault-tolerant; a failure in one never
    prevents the other, and neither ever raises to the caller.
    """
    if is_new:
        send_welcome_email(subscriber)
    sync_subscriber_to_provider(subscriber)


# ── Broadcast (Wagtail admin action) ────────────────────────────────────────

def send_newsletter_broadcast(subject: str, message: str, include_inactive: bool = False) -> int:
    """Batch-email subscribers through the branded broadcast shell.

    Defaults to active subscribers only; ``include_inactive`` widens to the
    whole list. Returns the number of messages the mail backend accepted —
    individual failures are logged, never raised, so the admin can report a
    partial result.
    """
    from apps.content.models.newsletter import NewsletterSubscriber

    queryset = (
        NewsletterSubscriber.objects.all()
        if include_inactive
        else NewsletterSubscriber.objects.filter(is_active=True)
    )
    subscribers = list(queryset)
    if not subscribers:
        return 0

    links = _site_links()
    messages = []
    for subscriber in subscribers:
        try:
            html = render_to_string("newsletter/email/broadcast_message.html", {
                "email": subscriber.email,
                "subject": subject,
                "message": message,
                **links,
            }).strip()
            plain = render_to_string("newsletter/email/broadcast_message.txt", {
                "message": message,
                **links,
            }).strip()
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email],
            )
            email.attach_alternative(html, "text/html")
            messages.append(email)
        except Exception:
            logger.exception("newsletter broadcast render failed for %s", subscriber.email)

    if not messages:
        return 0
    try:
        return get_connection().send_messages(messages)
    except Exception:
        logger.exception("newsletter broadcast send failed")
        return 0
