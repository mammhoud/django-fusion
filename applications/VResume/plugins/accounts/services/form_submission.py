"""
Form Submission Service for handling contact form submissions.

Delegates to ceptor_ai.pipelines.services.FormSubmissionService
Canonical import: from ceptor_ai.pipelines.services import FormSubmissionService
"""
import logging
from typing import Any, Optional

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from wagtail.models import Page

from plugins.accounts.models import FormSubmission

logger = logging.getLogger(__name__)


class FormSubmissionService:
    """
    Service for handling form submissions including saving and email notifications.
    """

    @staticmethod
    def save_submission(
        form_id: str,
        data: dict[str, Any],
        page: Optional[Page] = None,
        ip_address: Optional[str] = None,
        user_agent: str = "",
    ) -> FormSubmission:
        """
        Save a form submission to the database.

        Args:
            form_id: Unique identifier for the form
            data: Dictionary of form field values
            page: Optional Wagtail page where form was submitted
            ip_address: Client IP address
            user_agent: Client browser user agent

        Returns:
            FormSubmission instance
        """
        submission = FormSubmission.objects.create(
            form_id=form_id,
            page=page,
            data=data,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        logger.info(f"Form submission saved: {submission.id} for form {form_id}")
        return submission

    @staticmethod
    def send_notification_email(
        submission: FormSubmission,
        recipients: list[str],
        subject: Optional[str] = None,
        template_name: str = "email/form_submission_notification.html",
    ) -> bool:
        """
        Send email notification for a form submission.

        Args:
            submission: FormSubmission instance
            recipients: List of email addresses to notify
            subject: Email subject (defaults to "New Form Submission")
            template_name: Path to email template

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not recipients:
            logger.warning(f"No recipients for form submission {submission.id}")
            return False

        try:
            # Build email subject
            if not subject:
                subject = f"New Form Submission: {submission.form_id}"

            # Build email context
            context = {
                "submission": submission,
                "form_id": submission.form_id,
                "data": submission.data,
                "submitted_at": submission.submitted_at,
                "ip_address": submission.ip_address,
                "page_url": submission.page.full_url if submission.page else None,
            }

            # Render email body
            try:
                html_content = render_to_string(template_name, context)
            except Exception as e:
                logger.warning("Template %s rendering failed, using fallback: %s", template_name, e)
                html_content = FormSubmissionService._build_plain_email(submission)

            # Create and send email
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
                to=recipients,
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)

            # Mark email as sent
            submission.mark_email_sent()
            logger.info(f"Notification email sent for submission {submission.id}")
            return True

        except Exception as e:
            logger.error("Failed to send notification email for submission %s: %s", submission.id, e, exc_info=True)
            return False

    @staticmethod
    def _build_plain_email(submission: FormSubmission) -> str:
        """Build a plain HTML email when template is not available."""
        lines = [
            "<html><body>",
            f"<h2>New Form Submission: {submission.form_id}</h2>",
            f"<p><strong>Submitted:</strong> {submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}</p>",
        ]

        if submission.page:
            lines.append(f"<p><strong>Page:</strong> {submission.page.title}</p>")

        lines.append("<h3>Form Data:</h3><ul>")
        for key, value in submission.data.items():
            lines.append(f"<li><strong>{key}:</strong> {value}</li>")
        lines.append("</ul>")

        if submission.ip_address:
            lines.append(f"<p><small>IP: {submission.ip_address}</small></p>")

        lines.append("</body></html>")
        return "\n".join(lines)

    @staticmethod
    def get_submissions_for_form(
        form_id: str,
        limit: Optional[int] = None,
        unread_only: bool = False,
    ) -> list[FormSubmission]:
        """
        Get submissions for a specific form.

        Args:
            form_id: Form identifier
            limit: Maximum number of submissions to return
            unread_only: If True, only return unread submissions

        Returns:
            List of FormSubmission instances
        """
        queryset = FormSubmission.objects.filter(form_id=form_id)

        if unread_only:
            queryset = queryset.filter(is_read=False)

        if limit:
            queryset = queryset[:limit]

        return list(queryset)

    @staticmethod
    def get_submission_stats(form_id: Optional[str] = None) -> dict[str, Any]:
        """
        Get statistics for form submissions.

        Args:
            form_id: Optional form identifier to filter by

        Returns:
            Dictionary with submission statistics
        """
        queryset = FormSubmission.objects.all()

        if form_id:
            queryset = queryset.filter(form_id=form_id)

        total = queryset.count()
        unread = queryset.filter(is_read=False).count()
        email_sent = queryset.filter(email_sent=True).count()

        # Get submissions from last 24 hours
        last_24h = timezone.now() - timezone.timedelta(hours=24)
        recent = queryset.filter(submitted_at__gte=last_24h).count()

        return {
            "total": total,
            "unread": unread,
            "email_sent": email_sent,
            "recent_24h": recent,
        }
