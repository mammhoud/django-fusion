"""Invitation workflows for domain users."""

from __future__ import annotations

import logging
import secrets
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone

from apps.domain.models.users.users import Person
from apps.domain.services.email.email_service import EmailService
from apps.domain.services.email.models import EmailLog

logger = logging.getLogger(__name__)


class InvitationService:
    """Create, send, and accept registration invitations."""

    TOKEN_LIFETIME = timedelta(days=7)

    @classmethod
    def send_invitation(
        cls,
        person_id: str,
        inviter: Any = None,
        invitation_type: str = "join",
        message: str = "",
    ) -> dict[str, Any]:
        """Send an invitation and return its token or a structured error."""
        try:
            person = Person.objects.get(id=person_id)
            recipient = person.email or person.user.email
            if not recipient:
                return {"success": False, "error": "Person has no email address"}

            token = secrets.token_urlsafe(32)
            site_url = getattr(settings, "SITE_URL", "").rstrip("/")
            site_name = getattr(settings, "SITE_NAME", "Structa Cloud")
            invite_url = f"{site_url}/invite/{token}/"
            subject = "You are invited to join"
            context = {
                "email": recipient,
                "invite_url": invite_url,
                "token": token,
                "inviter": inviter,
                "invitation_type": invitation_type,
                "message": message,
                "subject": subject,
                "site_name": site_name,
                "site_url": site_url,
            }

            email_log = EmailService().send_invitation(
                recipient=recipient,
                context=context,
                queue=False,
            )
            email_log.invitation_token = token
            email_log.token_expires_at = timezone.now() + cls.TOKEN_LIFETIME
            email_log.save(
                update_fields=["invitation_token", "token_expires_at", "updated_at"]
            )

            logger.info("Invitation sent to %s", recipient)
            return {"success": True, "token": token}
        except Person.DoesNotExist:
            return {"success": False, "error": "Person not found"}
        except Exception as exc:
            logger.exception("Failed to send invitation for person %s", person_id)
            return {"success": False, "error": str(exc)}

    @classmethod
    def accept_invitation(
        cls,
        token: str,
        user: Any = None,
    ) -> dict[str, Any]:
        """Validate and consume an invitation token."""
        if not token:
            return {"success": False, "error": "Invalid token"}

        try:
            email_log = EmailLog.objects.get(invitation_token=token)
        except EmailLog.DoesNotExist:
            return {"success": False, "error": "Invalid token"}

        if not email_log.is_token_valid():
            return {"success": False, "error": "Token expired or invalid"}

        recipient = email_log.recipient
        email_log.invalidate_token()
        logger.info("Invitation accepted for %s", recipient)
        return {"success": True, "email": recipient}
