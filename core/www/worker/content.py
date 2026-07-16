"""Shared content/account utility actors."""

from __future__ import annotations

import logging

import dramatiq

from .runtime import configure_django_for_website, import_first

logger = logging.getLogger(__name__)


@dramatiq.actor(actor_name="shared.content.users_count")
def get_users_count(website: str | None = None) -> int:
    """Count users for the selected website."""
    configure_django_for_website(website)
    get_user_model = import_first(["django.contrib.auth.get_user_model"])
    return get_user_model().objects.count()


@dramatiq.actor(actor_name="shared.content.welcome_email")
def send_user_welcome_notification_task(user_id: int, website: str | None = None) -> bool:
    """Send a welcome email by user id."""
    configure_django_for_website(website)
    get_user_model = import_first(["django.contrib.auth.get_user_model"])
    settings = import_first(["django.conf.settings"])
    send_mail = import_first(["django.core.mail.send_mail"])
    user = get_user_model().objects.get(pk=user_id)
    if not user.email:
        logger.info("Skipping welcome email for user %s without email", user_id)
        return False
    subject = getattr(settings, "WELCOME_EMAIL_SUBJECT", "Welcome!")
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
    return send_mail(
        subject=subject,
        message=f"Hi {user.get_full_name() or user.username},\n\nWelcome to the platform!",
        from_email=from_email,
        recipient_list=[user.email],
        fail_silently=False,
    ) > 0


def send_user_welcome_notification(user, profile=None) -> None:
    """Compatibility helper used by existing signal handlers."""
    send_fn = getattr(send_user_welcome_notification_task, "send", None)
    if callable(send_fn):
        send_fn(user.pk)
    else:
        send_user_welcome_notification_task(user.pk)
