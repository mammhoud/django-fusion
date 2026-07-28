"""Shared email background actors for all websites.

Provides Dramatiq actors for sending templated, bulk, and raw emails
across all tenant websites (fusion-cms, lms, VResume). Each actor
accepts an optional ``website`` parameter to configure Django for the
correct site before sending.

Actors handle three email patterns:
- **Single templated email** (``send_email_task``): Render and send a
  Django template-based email to one recipient.
- **Bulk templated email** (``send_bulk_email_task``): Send the same
  template to many recipients with per-recipient context overrides.
- **Raw email** (``send_email_raw``): Low-level send with pre-rendered
  HTML and text content, including attachments.

Queue: All email actors run on the ``email`` queue.
"""

from __future__ import annotations

import logging
from typing import Any

import dramatiq

from .runtime import configure_django_for_website, import_first

logger = logging.getLogger(__name__)

EMAIL_SERVICE_PATHS = [
    "plugins.accounts.management.services.email.service.EmailService",
    "www.apps.services.email.service.EmailService",
    "www.core.handlers.services.email.service.EmailService",
]


@dramatiq.actor(actor_name="shared.email.send")
def send_email_task(
    to: str,
    subject: str,
    template: str,
    context: dict[str, Any] | None = None,
    website: str | None = None,
) -> bool:
    """Send one templated email using the selected website's EmailService.

    Resolves the email service implementation for the given website,
    renders the template with the provided context, and sends via the
    configured email backend.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        template: Django template name to render for the email body.
        context: Template context variables.
        website: Optional website slug (e.g. ``"fusion-cms"``).
            Uses the active website when ``None``.

    Returns:
        ``True`` on successful send.

    Raises:
        RuntimeError: If the email service returns ``False``,
            indicating the send was not acknowledged.
    """
    selected = configure_django_for_website(website)
    email_service = import_first(EMAIL_SERVICE_PATHS)
    result = email_service().send(
        to=to,
        subject=subject,
        template=template,
        context=context or {},
    )
    if not result:
        raise RuntimeError(f"Email service returned False for {to} on {selected}")
    return True


@dramatiq.actor(actor_name="shared.email.bulk")
def send_bulk_email_task(
    recipients: list[dict[str, Any]],
    subject: str,
    template: str,
    base_context: dict[str, Any] | None = None,
    website: str | None = None,
) -> dict[str, int]:
    """Send a templated email to many recipients for one website.

    Each recipient dict may include an ``email`` key (required) and a
    ``context`` key (optional per-recipient context overrides merged
    atop ``base_context``). Failed sends are caught and logged without
    aborting the remaining recipients.

    Args:
        recipients: List of recipient dicts, each with at least
            ``{"email": "user@example.com"}`` and optionally
            ``{"context": {...}}`` for per-user overrides.
        subject: Email subject line.
        template: Django template name for the email body.
        base_context: Base context dict shared by all recipients.
        website: Optional website slug.

    Returns:
        Dict with ``success`` and ``failed`` integer counts.
    """
    configure_django_for_website(website)
    email_service = import_first(EMAIL_SERVICE_PATHS)()
    success = 0
    failed = 0
    base_context = base_context or {}

    for recipient in recipients:
        email = recipient.get("email")
        if not email:
            continue
        context = {**base_context, **recipient.get("context", {})}
        try:
            if email_service.send(to=email, subject=subject, template=template, context=context):
                success += 1
            else:
                failed += 1
        except Exception as exc:
            logger.warning("Failed to send bulk email to %s: %s", email, exc)
            failed += 1

    return {"success": success, "failed": failed}


@dramatiq.actor(actor_name="shared.email.raw")
def send_email_raw(
    subject: str,
    recipients: list[str],
    html_content: str,
    text_content: str,
    from_email: str,
    reply_to: str | None = None,
    bcc: list[str] | None = None,
    attachments: list[dict[str, Any]] | None = None,
    website: str | None = None,
) -> bool:
    """Low-level raw HTML/text email task.

    Sends a pre-rendered email without template lookup. Supports
    HTML alternative, plain text fallback, custom from/reply-to
    addresses, BCC, and file attachments.

    Each attachment dict should have ``filename``, ``content``, and
    ``mimetype`` keys.

    Args:
        subject: Email subject line.
        recipients: List of recipient email addresses.
        html_content: Pre-rendered HTML body.
        text_content: Plain text fallback body.
        from_email: Sender email address.
        reply_to: Optional reply-to address.
        bcc: Optional list of BCC recipients.
        attachments: Optional list of attachment dicts.
        website: Optional website slug.

    Returns:
        ``True`` if the email was sent to at least one recipient.
    """
    configure_django_for_website(website)
    mail_module = import_first(["django.core.mail.EmailMultiAlternatives"])
    email = mail_module(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipients,
        bcc=bcc or [],
        reply_to=[reply_to] if reply_to else None,
    )
    email.attach_alternative(html_content, "text/html")
    for attachment in attachments or []:
        email.attach(
            filename=attachment.get("filename"),
            content=attachment.get("content"),
            mimetype=attachment.get("mimetype"),
        )
    return email.send() > 0
