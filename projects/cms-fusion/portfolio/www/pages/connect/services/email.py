"""
Email Service - Central email sending infrastructure.
"""
import logging
from typing import Any, Optional

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class EmailService:
    """
    Central email service with template support.
    """

    def __init__(self):
        self.from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

    def send(
        self,
        to: str | list[str],
        subject: str,
        template: str,
        context: dict[str, Any],
        attachments: Optional[list] = None,
        from_email: Optional[str] = None,
    ) -> bool:
        """
        Send an email using a template.
        """
        if isinstance(to, str):
            to = [to]

        try:
            # Render HTML template
            html_content = render_to_string(f"{template}.html", context)

            # Try to render plain text version
            try:
                text_content = render_to_string(f"{template}.txt", context)
            except Exception:
                # Fall back to stripping HTML if .txt template unavailable
                import re
                text_content = re.sub(r"<[^>]+>", "", html_content)
                logger.debug("Plain text template %s.txt not found, stripping HTML", template)

            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email or self.from_email,
                to=to,
            )
            email.attach_alternative(html_content, "text/html")

            # Add attachments
            if attachments:
                for attachment in attachments:
                    if isinstance(attachment, tuple):
                        email.attach(*attachment)
                    else:
                        email.attach_file(attachment)

            email.send(fail_silently=False)
            logger.info(f"Email sent to {to}: {subject}")
            return True

        except Exception as e:
            logger.error("Failed to send email to %s: %s", to, e, exc_info=True)
            return False

    def send_simple(
        self,
        to: str | list[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> bool:
        """
        Send a simple email without template.
        """
        if isinstance(to, str):
            to = [to]

        try:
            if html_body:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=body,
                    from_email=from_email or self.from_email,
                    to=to,
                )
                email.attach_alternative(html_body, "text/html")
            else:
                email = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=from_email or self.from_email,
                    to=to,
                )

            email.send(fail_silently=False)
            logger.info(f"Simple email sent to {to}: {subject}")
            return True

        except Exception as e:
            logger.error("Failed to send simple email to %s: %s", to, e, exc_info=True)
            return False


# Singleton instance
email_service = EmailService()
