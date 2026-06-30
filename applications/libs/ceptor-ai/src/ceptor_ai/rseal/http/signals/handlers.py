"""
Consolidated signal handlers for ceptor_ai.

This module consolidates all signal handlers from the signals package.

Canonical imports::
    from ceptor_ai.http.signals.handlers import bind_custom_metadata
    from ceptor_ai.http.signals.handlers import send_user_welcome_notification
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

try:
    from django_structlog.signals import bind_extra_request_metadata
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# Logging & Metadata Binding
# ============================================================================

if STRUCTLOG_AVAILABLE:
    @receiver(bind_extra_request_metadata)
    def bind_custom_metadata(sender, request, logger, **kwargs):
        """Bind custom metadata to request logger."""
        logger.bind(
            client_ip=request.META.get("REMOTE_ADDR", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )


# ============================================================================
# User & Profile Notifications
# ============================================================================

def send_user_welcome_notification(user, profile):
    """Send a welcome email to new users after profile creation."""
    try:
        if not user.email:
            return

        subject = _("Welcome to Our Platform")
        context = {
            "user": user,
            "profile": profile,
            "site_name": getattr(settings, "SITE_NAME", "Our Platform"),
            "login_url": getattr(settings, "LOGIN_URL", "/accounts/login/"),
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
        }

        html = render_to_string("emails/welcome_email.html", context)
        text = render_to_string("emails/welcome_email.txt", context)

        send_mail(
            subject=subject,
            message=text,
            html_message=html,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            recipient_list=[user.email],
            fail_silently=True,
        )

        logger.info(f"Welcome email sent to {user.email}")

    except Exception as e:
        logger.warning(f"Failed to send welcome email: {e!s}")


# ============================================================================
# Invitation Signals
# ============================================================================

from django.dispatch import Signal

invite_url_sent = Signal()
invite_accepted = Signal()

"""
@receiver(invite_url_sent, sender=Invitation)
def handle_invite_url_sent(sender, instance, invite_url_sent, inviter, **kwargs):
    pass

@receiver(invite_accepted, sender=Invitation)
def handle_invite_accepted(sender, email, **kwargs):
    pass
"""

__all__ = [
    "bind_custom_metadata",
    "send_user_welcome_notification",
    "invite_url_sent",
    "invite_accepted",
]
