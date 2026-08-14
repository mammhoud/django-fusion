"""Shared content/account utility actors.

Provides site-neutral Dramatiq actors for content and account operations.
Each message carries an optional website key; execution records are persisted
by the shared task backend before the selected site's data is touched.

Actors:
- ``get_users_count``: Query the user count for a specific website.
- ``send_user_welcome_notification_task``: Send a welcome email to a
  newly created user by primary key.

A compatibility helper ``send_user_welcome_notification`` is provided
for existing signal handlers that expect a synchronous function call
rather than awaiting the actor.

Queue: All content actors run on the shared ``content`` queue.
"""

from __future__ import annotations

import logging

from django_fusion.tasks import task

from .runtime import configure_django_for_website, import_first

logger = logging.getLogger(__name__)


@task(queue="content", actor_name="shared.content.users_count")
def get_users_count(website: str | None = None) -> int:
    """Count users for the selected website.

    Configures Django for the target website and returns the total
    number of ``User`` model instances.

    Args:
        website: Optional Precis website slug (for example ``"lms-fusion"``).
            Uses the active Precis website when ``None``.

    Returns:
        Total user count as an integer.
    """
    configure_django_for_website(website)
    get_user_model = import_first(["django.contrib.auth.get_user_model"])
    return get_user_model().objects.count()


@task(queue="email", actor_name="shared.content.welcome_email")
def send_user_welcome_notification_task(user_id: int, website: str | None = None) -> bool:
    """Send a welcome email by user id.

    Looks up the user by primary key and sends a simple welcome email
    using Django's ``send_mail``. Skips users without an email address.

    The subject line and from address are configured via Django settings
    ``WELCOME_EMAIL_SUBJECT`` and ``DEFAULT_FROM_EMAIL``.

    Args:
        user_id: Primary key of the ``User`` model instance.
        website: Optional website slug.

    Returns:
        ``True`` if the email was sent, ``False`` if skipped (no email).
    """
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
