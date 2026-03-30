"""
Email Background Jobs (formerly Celery Tasks)
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

def send_email_task(
    to: str,
    subject: str,
    template: str,
    context: dict[str, Any],
) -> bool:
    """
    Background job for sending emails.
    """
    from apps.handlers.services.email.service import EmailService

    try:
        service = EmailService()
        result = service.send(
            to=to,
            subject=subject,
            template=template,
            context=context,
        )

        if not result:
            raise Exception("Email send returned False")

        return True

    except Exception as e:
        logger.error(f"Email job failed: {e}")
        raise e

def send_bulk_email_task(
    recipients: list[dict],
    subject: str,
    template: str,
    base_context: dict[str, Any],
) -> dict:
    """
    Background job for sending bulk emails.
    """
    from apps.handlers.services.email.service import EmailService

    service = EmailService()
    success = 0
    failed = 0

    for recipient in recipients:
        email = recipient.get("email")
        if not email:
            continue

        # Merge base context with recipient-specific context
        context = {**base_context, **recipient.get("context", {})}

        try:
            if service.send(to=email, subject=subject, template=template, context=context):
                success += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Failed to send to {email}: {e}")
            failed += 1

    logger.info(f"Bulk email complete: {success} sent, {failed} failed")
    return {"success": success, "failed": failed}

def send_email_raw(
    subject: str,
    recipients: list[str],
    html_content: str,
    text_content: str,
    from_email: str,
    reply_to: str = None,
    bcc: list[str] = None,
    attachments: list[dict] = None,
) -> bool:
    """
    Low-level email sending job.
    """
    from django.core.mail import EmailMultiAlternatives
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipients,
        bcc=bcc or [],
        reply_to=[reply_to] if reply_to else None,
    )
    email.attach_alternative(html_content, "text/html")
    if attachments:
        for attachment in attachments:
            email.attach(
                filename=attachment.get('filename'),
                content=attachment.get('content'),
                mimetype=attachment.get('mimetype')
            )
    return email.send() > 0
