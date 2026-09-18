"""Workspace-level provider connectors (email, Slack).

These wrap the concrete providers so workflow actions and future screens share
one integration boundary. Both degrade honestly: an unconfigured provider is
reported as such instead of claiming a successful external call.
"""
from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail

from apps.core.webhooks import post_json


class EmailConnector:
    """Transactional email over Django's configured backend (SMTP first)."""

    def send(self, subject: str, body: str, recipients, from_email=None) -> int:
        """Send and return the count of messages accepted by the backend."""
        recipients = [str(r) for r in recipients if r]
        if not recipients:
            return 0
        return send_mail(subject, body, from_email, recipients, fail_silently=False)


class SlackConnector:
    """Post a message to a Slack incoming webhook."""

    def __init__(self, webhook_url: str | None = None):
        self.webhook_url = webhook_url or getattr(settings, "SLACK_WEBHOOK_URL", "")

    @property
    def configured(self) -> bool:
        return bool(self.webhook_url)

    def post(self, text: str) -> tuple[int, dict]:
        """Post ``{"text": ...}`` and return ``(status, body)``."""
        if not self.webhook_url:
            return 0, {"detail": "No Slack webhook URL is configured."}
        return post_json(self.webhook_url, {"text": text})
