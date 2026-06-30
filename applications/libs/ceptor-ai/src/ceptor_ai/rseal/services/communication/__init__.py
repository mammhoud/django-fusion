"""
Communication services for ceptor_ai.

Handles user communications including invitations, messages, and newsletters.

Modules:
- invitation_service: User invitation management
- message: Message sending and management
- newsletter: Newsletter management and sending
"""

from .invitation_service import InvitationService
from .message import MessageServiceBase
from .newsletter import send_confirmation_email

__all__ = [
    "InvitationService",
    "MessageServiceBase",
    "send_confirmation_email",
]
