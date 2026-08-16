"""Precis campaign actors migrated from the retired Temporal worker.

The previous implementation depended on a non-existent ``campaigns`` package and
an external Temporal worker command. These actors keep the useful onboarding and
batch-processing behavior on the shared Dramatiq broker using JSON-serializable
arguments only.
"""

from __future__ import annotations

import logging

from django_fusion.tasks import task

logger = logging.getLogger(__name__)


@task(queue="campaigns", max_retries=3, actor_name="precis.campaigns.process_user")
def process_user_task(user_id: int, action: str = "process") -> dict[str, object]:
    """Process one user and return a small serializable result."""
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.get(pk=user_id)
    logger.info(
        "Processed user %s for %s",
        user_id,
        action,
        extra={"user_id": user_id, "action": action},
    )
    return {"status": "processed", "user_id": user_id, "action": action}


@task(queue="email", max_retries=3, actor_name="precis.campaigns.send_email")
def send_campaign_email(
    recipient: str,
    subject: str,
    body: str,
    from_email: str | None = None,
) -> dict[str, object]:
    """Send one campaign email through Django's configured email backend."""
    from django.conf import settings
    from django.core.mail import send_mail

    send_mail(
        subject=subject,
        message=body,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False,
    )
    return {"status": "sent", "to": recipient}


@task(queue="email", max_retries=3, actor_name="precis.campaigns.followup")
def send_onboarding_followup(recipient: str, name: str) -> dict[str, object]:
    """Send the delayed onboarding follow-up email."""
    return send_campaign_email.run(
        recipient,
        "How are you liking our service?",
        (
            f"Hi {name},\n\n"
            "Just checking in to see how you're finding our service. "
            "Let us know if you have any questions!"
        ),
    )


@task(queue="campaigns", max_retries=2, actor_name="precis.campaigns.onboard")
def onboard_user(user_id: int, email: str, name: str) -> dict[str, object]:
    """Queue onboarding steps and a 24-hour follow-up on Dramatiq."""
    process_user_task.send(user_id, "onboard")
    send_campaign_email.send(
        email,
        f"Welcome, {name}!",
        f"Hello {name},\n\nWelcome! We're excited to have you on board.",
    )
    send_onboarding_followup.send(
        email,
        name,
        _fusion_options={"delay": 24 * 60 * 60 * 1000},
    )
    return {"status": "queued", "user_id": user_id, "steps": 3}


@task(queue="campaigns", max_retries=2, actor_name="precis.campaigns.batch")
def process_user_batch(batch_id: str, user_ids: list[int]) -> dict[str, object]:
    """Queue one independent Dramatiq message for each user in a batch."""
    for user_id in user_ids:
        process_user_task.send(user_id, "batch_process")
    return {"status": "queued", "batch_id": batch_id, "total": len(user_ids)}


__all__ = [
    "onboard_user",
    "process_user_batch",
    "process_user_task",
    "send_campaign_email",
    "send_onboarding_followup",
]
