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
    Central email service with template support and queuing.
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

        Args:
            to: Recipient email address(es)
            subject: Email subject
            template: Template path (without extension)
            context: Template context dictionary
            attachments: Optional list of attachments
            from_email: Optional sender email (defaults to DEFAULT_FROM_EMAIL)

        Returns:
            True if email was sent successfully
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
                # Fall back to stripping HTML
                import re
                text_content = re.sub(r"<[^>]+>", "", html_content)

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
            logger.error(f"Failed to send email to {to}: {e}")
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

        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            from_email: Optional sender email

        Returns:
            True if email was sent successfully
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
            logger.error(f"Failed to send simple email to {to}: {e}")
            return False

    def queue(
        self,
        to: str,
        subject: str,
        template: str,
        context: dict[str, Any],
        delay: int = 0,
    ) -> str:
        """Queue a template email through the shared Dramatiq worker."""
        from plugins.workers.legacy_email_tasks import send_template_email

        options = {"delay": delay * 1000} if delay > 0 else None
        message_id = send_template_email.send(
            to,
            subject,
            template,
            context,
            **({"_fusion_options": options} if options else {}),
        )
        logger.info("Email job queued for %s: %s (job: %s)", to, subject, message_id)
        return message_id

    # Convenience methods for common email types

    def send_welcome(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user."""
        return self.send(
            to=user_email,
            subject="Welcome!",
            template="email/welcome",
            context={"name": user_name},
        )

    def send_password_reset(self, user_email: str, reset_url: str) -> bool:
        """Send password reset email."""
        return self.send(
            to=user_email,
            subject="Reset Your Password",
            template="email/password_reset",
            context={"reset_url": reset_url},
        )

    def send_enrollment_confirmation(
        self,
        user_email: str,
        user_name: str,
        course_title: str,
        course_url: str,
    ) -> bool:
        """Send course enrollment confirmation."""
        return self.send(
            to=user_email,
            subject=f"Enrollment Confirmed: {course_title}",
            template="email/enrollment",
            context={
                "name": user_name,
                "course_title": course_title,
                "course_url": course_url,
            },
        )

    def send_course_completion(
        self,
        user_email: str,
        user_name: str,
        course_title: str,
        certificate_url: Optional[str] = None,
    ) -> bool:
        """Send course completion notification."""
        return self.send(
            to=user_email,
            subject=f"Congratulations! You completed {course_title}",
            template="email/completion",
            context={
                "name": user_name,
                "course_title": course_title,
                "certificate_url": certificate_url,
            },
        )


# Singleton instance
email_service = EmailService()
