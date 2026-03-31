from typing import List, Optional, Dict, Any
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from alliance.conf import app_settings


class InvitationEmailHandler:
    """Handler for sending invitation emails"""

    @staticmethod
    def send_invitation_email(invitation) -> bool:
        """Send invitation email"""
        if not app_settings.SEND_INVITATION_EMAIL:
            return True  # Return success if email sending is disabled

        context = app_settings.get_invitation_email_context(invitation)

        # Add invitation-specific context
        context.update({
            'invite_url': invitation.get_invite_url(),
            'email': invitation.email,
            'sent_by': invitation.inviter,
            'sent_at': invitation.sent,
        })

        # Render templates
        subject = app_settings.INVITATION_EMAIL_SUBJECT
        if app_settings.EMAIL_SUBJECT_PREFIX:
            subject = f"{app_settings.EMAIL_SUBJECT_PREFIX} {subject}"

        html_content = render_to_string(
            f"{app_settings.EMAIL_TEMPLATE_PREFIX}{app_settings.INVITATION_EMAIL_TEMPLATE}.html",
            context
        )

        text_content = render_to_string(
            f"{app_settings.EMAIL_TEMPLATE_PREFIX}{app_settings.INVITATION_EMAIL_TEMPLATE}.txt",
            context
        )

        # Send email
        return InvitationEmailHandler._send_email(
            subject=subject,
            recipients=[invitation.email],
            html_content=html_content,
            text_content=text_content,
            from_email=app_settings.INVITATION_FROM_EMAIL,
            reply_to=app_settings.INVITATION_REPLY_TO,
            bcc=app_settings.INVITATION_BCC,
        )

    @staticmethod
    def _send_email(
        subject: str,
        recipients: List[str],
        html_content: str,
        text_content: str,
        from_email: str,
        reply_to: Optional[str] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Internal email sending method"""
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=recipients,
                bcc=bcc or [],
                reply_to=[reply_to] if reply_to else None,
            )
            email.attach_alternative(html_content, "text/html")

            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    email.attach(
                        filename=attachment.get('filename'),
                        content=attachment.get('content'),
                        mimetype=attachment.get('mimetype')
                    )

            # Send email based on strategy
            if app_settings.EMAIL_AS_BACKGROUND_TASK:
                # Import here to avoid circular imports
                from apps.handlers.services.email.tasks import send_email_raw
                from django_grep.pipelines.services.jobs import dispatch_job

                dispatch_job(
                    send_email_raw,
                    subject=subject,
                    recipients=recipients,
                    html_content=html_content,
                    text_content=text_content,
                    from_email=from_email,
                    reply_to=reply_to,
                    bcc=bcc,
                    attachments=attachments,
                    queue_name="email"
                )
                return True
            else:
                return email.send() > 0

        except Exception as e:
            # Log error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send email: {str(e)}")
            return False
