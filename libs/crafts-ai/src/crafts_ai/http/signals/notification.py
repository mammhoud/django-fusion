import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


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
