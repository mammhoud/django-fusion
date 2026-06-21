"""
Email services for django-rseal.

Provides EmailService for single-email sending and BulkEmailService for
batch operations. Both support simple (template_name string) and advanced
(EmailTemplate object / template_type lookup) usage patterns.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from django.conf import settings

if TYPE_CHECKING:
    from crafts_ai.communication.email.models import EmailLog, EmailTemplate

logger = logging.getLogger(__name__)


class EmailService:
    """
    Core email sending service with template rendering and logging.

    Simple usage (backward compatible):
        service = EmailService()
        service.send_email(
            recipient="user@example.com",
            subject="Hello",
            template_name="emails/hello.html",
            context={"name": "Alice"},
        )

    Advanced usage (database template object):
        template = EmailTemplate.objects.get(name="welcome")
        service.send_email(
            recipient="user@example.com",
            template_obj=template,
            context={"name": "Alice"},
        )

    Advanced usage (template type lookup):
        service.send_with_template_type(
            recipient="user@example.com",
            template_type="invitation",
            context={"event": "Conference"},
        )
    """

    def __init__(self) -> None:
        self.from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

    # ------------------------------------------------------------------
    # Primary send method
    # ------------------------------------------------------------------

    def send_email(
        self,
        recipient: str,
        subject: Optional[str] = None,
        template_name: Optional[str] = None,
        template_obj: Optional["EmailTemplate"] = None,
        context: Optional[Dict[str, Any]] = None,
        queue: bool = True,
    ) -> "EmailLog":
        """
        Send (or queue) a single email.

        Accepts either a ``template_name`` (Django template path or DB template
        name) or a ``template_obj`` (EmailTemplate instance).  When both are
        omitted the email is sent with the raw ``subject`` only.

        Returns:
            ``EmailLog`` instance.
        """
        from crafts_ai.communication.email.models import EmailLog, EmailTemplate

        context = context or {}

        # --- Resolve template ---
        resolved_subject = subject or ""
        html_content = ""
        text_content = ""
        from_email = self.from_email
        reply_to = None

        if template_obj is not None:
            # Advanced: use EmailTemplate instance directly
            try:
                rendered = template_obj.render_for_email(context, validate_live=False)
                resolved_subject = rendered.get("subject") or subject or ""
                html_content = rendered.get("html", "")
                text_content = rendered.get("text", "")
                from_email = rendered.get("from_email") or self.from_email
                reply_to = rendered.get("reply_to") or None
            except Exception as e:
                logger.warning(f"Failed to render template_obj '{template_obj}': {e}")

        elif template_name:
            # Try to find a DB template by name first
            db_template = None
            try:
                db_template = EmailTemplate.objects.get(name=template_name, is_active=True)
            except EmailTemplate.DoesNotExist:
                pass

            if db_template:
                try:
                    rendered = db_template.render_for_email(context, validate_live=False)
                    resolved_subject = rendered.get("subject") or subject or ""
                    html_content = rendered.get("html", "")
                    text_content = rendered.get("text", "")
                    from_email = rendered.get("from_email") or self.from_email
                    reply_to = rendered.get("reply_to") or None
                except Exception as e:
                    logger.warning(f"Failed to render DB template '{template_name}': {e}")
            else:
                # Fall back to Django filesystem template
                try:
                    from django.template.loader import render_to_string
                    html_content = render_to_string(template_name, context)
                except Exception as e:
                    logger.warning(f"Failed to render filesystem template '{template_name}': {e}")

        # --- Create log entry ---
        log = EmailLog.objects.create(
            recipient=recipient,
            subject=resolved_subject,
            template_used=template_name or (str(template_obj) if template_obj else ""),
            message_body=html_content,
            status=EmailLog.Status.QUEUED if queue else EmailLog.Status.SENDING,
        )

        if not queue:
            self._send_now(
                recipient=recipient,
                subject=resolved_subject,
                html_content=html_content,
                text_content=text_content,
                from_email=from_email,
                reply_to=reply_to,
                log=log,
            )

        return log

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    def send_invitation(
        self,
        recipient: str,
        context: Optional[Dict[str, Any]] = None,
        template_name: str = "emails/invitation.html",
        queue: bool = True,
    ) -> "EmailLog":
        """Send an invitation email."""
        context = context or {}
        subject = context.get("subject", "You are invited!")
        return self.send_email(recipient, subject=subject, template_name=template_name,
                               context=context, queue=queue)

    def send_notification(
        self,
        recipient: str,
        context: Optional[Dict[str, Any]] = None,
        template_name: str = "emails/notification.html",
        queue: bool = True,
    ) -> "EmailLog":
        """Send a notification email."""
        context = context or {}
        subject = context.get("subject", "Notification")
        return self.send_email(recipient, subject=subject, template_name=template_name,
                               context=context, queue=queue)

    def send_report(
        self,
        recipient: str,
        context: Optional[Dict[str, Any]] = None,
        template_name: str = "emails/report.html",
        queue: bool = True,
    ) -> "EmailLog":
        """Send a report email."""
        context = context or {}
        subject = context.get("subject", "Report")
        return self.send_email(recipient, subject=subject, template_name=template_name,
                               context=context, queue=queue)

    def send_with_template_type(
        self,
        recipient: str,
        template_type: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = "en",
        queue: bool = True,
    ) -> "EmailLog":
        """
        Send email using the default template for a given type.

        Looks up the active default EmailTemplate for ``template_type`` and
        ``language``, then sends using that template.

        Raises:
            ValueError: If no matching template is found.
        """
        from crafts_ai.communication.email.models import EmailTemplate

        template = EmailTemplate.get_default_for_type(template_type, language)
        if not template:
            raise ValueError(
                f"No active default template found for type='{template_type}', "
                f"language='{language}'"
            )
        return self.send_email(recipient, template_obj=template, context=context, queue=queue)

    def send_for_object(
        self,
        recipient: str,
        obj: Any,
        template_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        language: str = "en",
        queue: bool = True,
    ) -> "EmailLog":
        """
        Send email for a specific model object.

        Automatically determines the template type from the object's model
        name if ``template_type`` is not provided.

        Raises:
            ValueError: If no matching template is found.
        """
        from crafts_ai.communication.email.models import EmailTemplate

        template = EmailTemplate.find_for_object(obj, template_type, language)
        if not template:
            raise ValueError(
                f"No template found for object '{obj}' with type='{template_type}'"
            )
        return self.send_email(recipient, template_obj=template, context=context, queue=queue)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _send_now(
        self,
        recipient: str,
        subject: str,
        html_content: str,
        text_content: str,
        from_email: str,
        reply_to: Optional[str],
        log: "EmailLog",
    ) -> None:
        """Send immediately (not queued)."""
        try:
            from django.core.mail import EmailMultiAlternatives

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content or html_content,
                from_email=from_email,
                to=[recipient],
                reply_to=[reply_to] if reply_to else None,
            )
            if html_content:
                email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            log.mark_sent()
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            log.mark_failed(str(e))


class BulkEmailService:
    """Bulk email service for sending to multiple recipients."""

    def __init__(self) -> None:
        self._service = EmailService()

    def send_batch(
        self,
        recipients: List[str],
        subject: Optional[str] = None,
        template_name: Optional[str] = None,
        template_obj: Optional["EmailTemplate"] = None,
        context: Optional[Dict[str, Any]] = None,
        queue: bool = True,
    ) -> List["EmailLog"]:
        """
        Send the same email to multiple recipients.

        Returns:
            List of ``EmailLog`` instances.
        """
        logs = []
        for recipient in recipients:
            log = self._service.send_email(
                recipient=recipient,
                subject=subject,
                template_name=template_name,
                template_obj=template_obj,
                context=context,
                queue=queue,
            )
            logs.append(log)
        return logs

    def send_group_email(
        self,
        group_name: str,
        subject: Optional[str] = None,
        template_name: Optional[str] = None,
        template_obj: Optional["EmailTemplate"] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> List["EmailLog"]:
        """
        Send email to all users in a Django auth Group.

        Raises:
            ValueError: If the group does not exist.

        Returns:
            List of ``EmailLog`` instances.
        """
        from django.contrib.auth.models import Group
        from django.core.exceptions import ObjectDoesNotExist

        try:
            group = Group.objects.get(name=group_name)
        except ObjectDoesNotExist:
            raise ValueError(f"Group not found: {group_name}")

        recipients = list(group.user_set.values_list("email", flat=True))
        return self.send_batch(
            recipients=recipients,
            subject=subject,
            template_name=template_name,
            template_obj=template_obj,
            context=context,
            queue=True,
        )

    def send_batch_with_template_type(
        self,
        recipients: List[str],
        template_type: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = "en",
    ) -> List["EmailLog"]:
        """
        Send email to multiple recipients using a template type lookup.

        Returns:
            List of ``EmailLog`` instances.
        """
        from crafts_ai.communication.email.models import EmailTemplate

        template = EmailTemplate.get_default_for_type(template_type, language)
        if not template:
            raise ValueError(
                f"No active default template found for type='{template_type}', "
                f"language='{language}'"
            )
        return self.send_batch(
            recipients=recipients,
            template_obj=template,
            context=context,
            queue=True,
        )
