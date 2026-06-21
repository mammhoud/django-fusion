"""
Signal handlers for django_rseal.

All signal handlers are consolidated in handlers.py.

Canonical imports::
    from django_rseal.http.signals import bind_custom_metadata
    from django_rseal.http.signals import send_user_welcome_notification
    from django_rseal.http.signals import invite_url_sent
    from django_rseal.http.signals import invite_accepted
"""

from .handlers import (  # noqa: F401
    bind_custom_metadata,
    invite_accepted,
    invite_url_sent,
    send_user_welcome_notification,
)

__all__ = [
    "bind_custom_metadata",
    "send_user_welcome_notification",
    "invite_url_sent",
    "invite_accepted",
]
