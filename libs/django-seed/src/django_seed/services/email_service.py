"""
Email Service for Django Seed

This service provides email sending functionality for the Django Seed package.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending emails with template support.
    """

    def __init__(self, from_email: str = None):
        """
        Initialize the email service.

        Args:
            from_email: Default from email address
        """
        self.from_email = from_email or getattr(
            settings,
            'DEFAULT_FROM_EMAIL',
            'noreply@example.com'
        )

    def send_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        template_name: str = None,
        context: Dict[str, Any] = None,
        html_content: str = None,
        text_content: str = None,
        from_email: str = None,
        bcc: List[str] = None,
        attachments: List[Any] = None,
        **kwargs
    ) -> bool:
        """
        Send an email with optional template support.

        Args:
            to: Recipient email address(es)
            subject: Email subject
            template_name: Template name (without extension)
            context: Context for template rendering
            html_content: HTML content (overrides template)
            text_content: Plain text content
            from_email: Sender email (overrides default)
            bcc: Blind carbon copy recipients
            attachments: List of attachments
            **kwargs: Additional email options

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Prepare recipients
            if isinstance(to, str):
                to = [to]

            # Set default from email
            from_email = from_email or self.from_email

            # Prepare email content
            if template_name:
                # Render template if provided
                html_content = render_to_string(f"{template_name}.html", context or {})
                text_content = render_to_string(f"{template_name}.txt", context or {})
            else:
                html_content = html_content or ""
                text_content = text_content or ""

            # Create email message
            if html_content:
                # Create multipart email with HTML and text alternatives
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=from_email,
                    to=to,
                    bcc=bcc or [],
                    **kwargs
                )
                email.attach_alternative(html_content, "text/html")
            else:
                # Plain text email
                email = EmailMessage(
                    subject=subject,
                    body=text_content or html_content,
                    from_email=from_email,
                    to=to,
                    bcc=bcc or [],
                    **kwargs
                )

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    if isinstance(attachment, tuple) and len(attachment) >= 2:
                        email.attach(*attachment)
                    else:
                        email.attach(attachment)

            # Send email
            email.send(fail_silently=False)
            logger.info(f"Email sent to {to}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_welcome_email(
        self,
        to: Union[str, List[str]],
        user_name: str,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Send a welcome email to new users.

        Args:
            to: Recipient email(s)
            user_name: Name of the user
            context: Additional context for the template

        Returns:
            True if email was sent successfully
        """
        context = context or {}
        context.update({
            'user_name': user_name,
            'welcome_message': f"Welcome {user_name} to our platform!"
        })

        return self.send_email(
            to=to,
            subject=f"Welcome, {user_name}!",
            template_name="email/welcome",
            context=context
        )

    def send_password_reset(
        self,
        to: Union[str, List[str]],
        reset_url: str,
        user_name: str = None,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Send a password reset email.

        Args:
            to: Recipient email(s)
            reset_url: Password reset URL
            user_name: User's name
            context: Additional context

        Returns:
            True if email was sent successfully
        """
        context = context or {}
        context.update({
            'reset_url': reset_url,
            'user_name': user_name or 'User',
            'expiry_hours': 24  # Default expiry
        })

        return self.send_email(
            to=to,
            subject="Password Reset Request",
            template_name="email/password_reset",
            context=context
        )

    def send_notification(
        self,
        to: Union[str, List[str]],
        subject: str,
        message: str,
        notification_type: str = "info",
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Send a notification email.

        Args:
            to: Recipient email(s)
            subject: Email subject
            message: Notification message
            notification_type: Type of notification
            context: Additional context

        Returns:
            True if email was sent successfully
        """
        context = context or {}
        context.update({
            'message': message,
            'notification_type': notification_type,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return self.send_email(
            to=to,
            subject=subject,
            template_name=f"email/notification_{notification_type}",
            context=context
        )

    def send_bulk_emails(
        self,
        recipients: List[Dict[str, Any]],
        template_name: str,
        context_generator: callable = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send bulk emails with personalized content.

        Args:
            recipients: List of recipient dictionaries with at least 'email' key
            template_name: Template name for rendering
            context_generator: Function to generate context for each recipient
            **kwargs: Additional email options

        Returns:
            Dictionary with results
        """
        results = {
            'sent': 0,
            'failed': 0,
            'errors': [],
            'sent_to': [],
            'failed_to': []
        }

        for recipient in recipients:
            try:
                # Generate context for this recipient
                if context_generator:
                    context = context_generator(recipient)
                else:
                    context = recipient.get('context', {})

                # Send individual email
                success = self.send_email(
                    to=recipient['email'],
                    template_name=template_name,
                    context=context,
                    **kwargs
                )

                if success:
                    results['sent'] += 1
                    results['sent_to'].append(recipient['email'])
                else:
                    results['failed'] += 1
                    results['failed_to'].append(recipient['email'])
                    results['errors'].append(f"Failed to send to {recipient['email']}")

            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error sending to {recipient.get('email', 'unknown')}: {str(e)}")

        return results


# Default email service instance
email_service = EmailService()


class EmailServiceFactory:
    """Factory for creating email service instances."""

    @staticmethod
    def create_email_service(from_email: str = None) -> EmailService:
        """
        Create an email service instance.

        Args:
            from_email: Default from email address

        Returns:
            EmailService instance
        """
        return EmailService(from_email=from_email)

    @staticmethod
    def create_default_email_service() -> EmailService:
        """
        Create email service with default settings.

        Returns:
            EmailService instance with default settings
        """
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        return EmailService(from_email=from_email)


# Default email service instance
default_email_service = EmailServiceFactory.create_default_email_service()
