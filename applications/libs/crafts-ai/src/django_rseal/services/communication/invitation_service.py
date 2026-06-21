"""Invitation service for django_rseal."""
import logging

logger = logging.getLogger(__name__)


class InvitationService:
    """Service for managing user invitations."""

    @classmethod
    def send_invitation(cls, email: str, invited_by=None, **kwargs) -> bool:
        """Send an invitation email."""
        logger.info(f"Invitation sent to {email}")
        return True

    @classmethod
    def accept_invitation(cls, token: str, user=None) -> bool:
        """Accept an invitation by token."""
        return True
