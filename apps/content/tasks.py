"""
apps/content/tasks.py
---------------------
Celery tasks for the content app.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
    from django.contrib.auth import get_user_model

    @shared_task()
    def get_users_count():
        """Celery task to count users."""
        return get_user_model().objects.count()

except ImportError:
    def get_users_count():
        """Fallback when Celery is not installed."""
        from django.contrib.auth import get_user_model
        return get_user_model().objects.count()


def send_user_welcome_notification(user, profile) -> None:
    """
    Send a welcome notification to a newly registered user.

    Called from apps.content.signals.user after profile creation.
    Wrapped in try/except at call site — failures are non-fatal.
    """
    try:
        from django.conf import settings
        from django.core.mail import send_mail

        subject = getattr(settings, "WELCOME_EMAIL_SUBJECT", "Welcome!")
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

        send_mail(
            subject=subject,
            message=f"Hi {user.get_full_name() or user.username},\n\nWelcome to the platform!",
            from_email=from_email,
            recipient_list=[user.email],
            fail_silently=True,
        )
        logger.info(f"📨 Welcome email sent to {user.email}")
    except Exception as exc:
        logger.warning(f"⚠️ send_user_welcome_notification failed: {exc}")
