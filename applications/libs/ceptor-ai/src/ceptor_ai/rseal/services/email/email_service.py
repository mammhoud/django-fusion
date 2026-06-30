"""
Email Service for sending emails with template rendering.

Core email sending service with template rendering,
queue management, and logging.
"""

import logging
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class EmailService:
    """
    Core email sending service with template rendering,
    queue management, and logging.
    """

    def __init__(self):
        from .queue_manager import EmailQueueManager
        self.queue_manager = EmailQueueManager()

    def send_invitation(
        self,
        recipient: str,
        template_name: str = 'emails/invitation.html',
        context: Optional[Dict[str, Any]] = None,
        queue: bool = True
    ):
        """
        Send invitation email to a recipient.

        Args:
            recipient: Email address
            template_name: Template file path
            context: Template context variables
            queue: Whether to queue for background processing

        Returns:
            EmailLog instance
        """
        context = context or {}
        context.setdefault('recipient_email', recipient)

        subject = context.get('subject', 'You are invited!')

        if queue:
            return self.queue_manager.queue_email(
                recipient=recipient,
                subject=subject,
                template_name=template_name,
                context=context
            )
        else:
            from ceptor_ai.communication.email.models import EmailLog
            log = EmailLog.objects.create(
                recipient=recipient,
                subject=subject,
                template_used=template_name,
                status=EmailLog.Status.SENDING
            )
            return self._send_now(recipient, subject, template_name, context, log)

    def send_group_email(
        self,
        group_name: str,
        subject: str,
        template_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List:
        """
        Send email to all users in a group.

        Args:
            group_name: Name of the user group
            subject: Email subject
            template_name: Template file path
            context: Template context variables

        Returns:
            List of EmailLog instances
        """
        from ceptor_ai.communication.email.models import UserGroup

        try:
            group = UserGroup.objects.get(name=group_name)
        except UserGroup.DoesNotExist:
            logger.error(f"Group not found: {group_name}")
            raise ValueError(f"Group not found: {group_name}")

        recipients = group.get_recipients()
        logs = []

        for recipient in recipients:
            log = self.queue_manager.queue_email(
                recipient=recipient,
                subject=subject,
                template_name=template_name,
                context=context or {},
                group_name=group_name
            )
            logs.append(log)

        logger.info(f"Group email queued: {group_name} ({len(recipients)} recipients)")

        return logs

    def _send_now(
        self,
        recipient: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        log=None
    ):
        """
        Send email immediately (not queued).

        Args:
            recipient: Email address
            subject: Email subject
            template_name: Template file path
            context: Template context variables
            log: Optional EmailLog instance

        Returns:
            EmailLog instance
        """
        from ceptor_ai.communication.email.models import EmailLog

        # Create log entry if not provided
        if log is None:
            log = EmailLog.objects.create(
                recipient=recipient,
                subject=subject,
                template_used=template_name,
                status=EmailLog.Status.SENDING
            )

        try:
            # Render template
            html_content = self._render_template(template_name, context)
            text_content = self._render_template(
                template_name.replace('.html', '.txt'),
                context,
                fallback=True
            )

            # Create email
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[recipient]
            )
            email.attach_alternative(html_content, "text/html")

            # Send
            email.send(fail_silently=False)

            # Update log
            log.mark_sent()

            logger.info(f"Email sent: {recipient} - {subject}")

            return log

        except Exception as e:
            error_msg = str(e)
            log.mark_failed(error_msg)

            logger.error(f"Email send failed: {recipient} - {error_msg}")

            raise

    def _render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        fallback: bool = False
    ) -> str:
        """
        Render email template with context.

        Args:
            template_name: Template file path
            context: Template context variables
            fallback: Whether to return plain text fallback on error

        Returns:
            Rendered template string
        """
        try:
            return render_to_string(template_name, context)
        except Exception as e:
            logger.error(f"Template render failed: {template_name} - {e}")

            if fallback:
                return f"Subject: {context.get('subject', 'Notification')}\n\n" \
                       f"This is an automated email notification."
            else:
                raise
