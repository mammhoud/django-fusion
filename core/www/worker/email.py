"""Shared email background actors for all websites."""

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
    """Send one templated email using the selected website's EmailService."""
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
    """Send a templated email to many recipients for one website."""
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
    """Low-level raw HTML/text email task."""
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
