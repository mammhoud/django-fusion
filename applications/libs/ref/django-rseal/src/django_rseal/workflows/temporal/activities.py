"""
Temporal Activities for Django RSeal.

Activities are the building blocks of Temporal workflows. They encapsulate
business logic that can interact with external systems, databases, and APIs.

Best Practices:
- Use async def for I/O-bound activities
- Use sync_to_async() for Django ORM operations
- Keep activities idempotent when possible
- Use proper error handling and retries
"""

from dataclasses import dataclass
from typing import Any

import structlog
from asgiref.sync import sync_to_async

logger = structlog.get_logger(__name__)


@dataclass
class EmailPayload:
    """Payload for sending emails."""

    to: str
    subject: str
    body: str
    from_email: str | None = None


async def send_email_activity(payload: EmailPayload) -> dict[str, Any]:
    """
    Send an email asynchronously.

    This activity demonstrates:
    - Using dataclass for structured input
    - Async activity implementation
    - Proper logging
    - Integration with Django's email system
    """
    logger.info(
        "Sending email",
        to=payload.to,
        subject=payload.subject,
    )

    # Import Django's send_mail here to avoid import issues
    from django.core.mail import send_mail

    # Use sync_to_async to call Django's synchronous send_mail
    @sync_to_async
    def _send_mail():
        return send_mail(
            subject=payload.subject,
            message=payload.body,
            from_email=payload.from_email,
            recipient_list=[payload.to],
            fail_silently=False,
        )

    try:
        await _send_mail()
        logger.info("Email sent successfully", to=payload.to)
        return {"status": "sent", "to": payload.to}
    except Exception as e:
        logger.warning("Failed to send email", to=payload.to, error=str(e))
        raise


@dataclass
class UserProcessingPayload:
    """Payload for user processing."""

    user_id: int
    action: str


async def process_user_activity(payload: UserProcessingPayload) -> dict[str, Any]:
    """
    Process a user record.

    Demonstrates safe Django ORM usage in async activities.
    Note: The User model import should be configured per project.
    """
    logger.info(
        "Processing user",
        user_id=payload.user_id,
        action=payload.action,
    )

    # Try to get User from common locations
    try:
        from django.contrib.auth import get_user_model

        User = get_user_model()
    except ImportError:
        User = None

    if User is None:
        logger.warning(
            "User model not available, returning generic response",
            user_id=payload.user_id,
        )
        return {
            "status": "skipped",
            "user_id": payload.user_id,
            "action": payload.action,
            "reason": "user_model_not_configured",
        }

    @sync_to_async
    def _get_user():
        return User.objects.get(pk=payload.user_id)

    try:
        user = await _get_user()
        logger.info(
            "User processed",
            user_id=payload.user_id,
            username=getattr(user, "email", None) or getattr(user, "username", None),
        )
        return {
            "status": "processed",
            "user_id": payload.user_id,
            "action": payload.action,
        }
    except User.DoesNotExist:
        logger.warning("User not found", user_id=payload.user_id)
        raise
    except Exception as e:
        logger.warning(
            "Failed to process user",
            user_id=payload.user_id,
            error=str(e),
        )
        raise
