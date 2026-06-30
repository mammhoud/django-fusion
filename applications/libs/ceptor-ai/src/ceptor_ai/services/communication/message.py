"""
MessageServiceBase: Base class for message service implementations.

Canonical import: from ceptor_ai.services import MessageServiceBase
"""

class MessageServiceBase:
    """Base class for message service implementations."""

    message_model = None  # Injected by subclass

    @classmethod
    def send_message(cls, recipient, subject: str, body: str, **kwargs):
        """Send a message."""
        if cls.message_model is None:
            raise NotImplementedError("message_model must be set by subclass")
        raise NotImplementedError

    @classmethod
    def get_messages(cls, user, **kwargs):
        """Get messages for user."""
        if cls.message_model is None:
            raise NotImplementedError("message_model must be set by subclass")
        raise NotImplementedError
