"""
InvitationEmailSender — send invitation emails from a CSV list.
"""
import logging
import time
from pathlib import Path
from typing import Optional

from django.core.mail import send_mail
from django.template.loader import render_to_string

from .csv_manager import EmailCSVManager

logger = logging.getLogger(__name__)


class InvitationEmailSender:
    """
    Send invitation emails to addresses in a CSV file.

    Usage::

        sender = InvitationEmailSender(
            csv_path="emails.csv",
            subject="You're invited!",
            from_email="noreply@example.com",
        )
        sender.send_all(dry_run=True)
    """

    def __init__(
        self,
        csv_path: Path,
        subject: str,
        from_email: str,
        template: str = "emails/invitation.html",
        rate_limit: float = 0.5,  # seconds between sends
        context: Optional[dict] = None,
    ):
        self.csv_path = Path(csv_path)
        self.subject = subject
        self.from_email = from_email
        self.template = template
        self.rate_limit = rate_limit
        self.context = context or {}

    def _render_body(self, email: str) -> str:
        ctx = {**self.context, "recipient_email": email}
        try:
            return render_to_string(self.template, ctx)
        except Exception:
            return (
                f"You are invited to join our platform.\n\n"
                f"Visit: {self.context.get('registration_url', '')}\n\n"
                f"This invitation was sent to {email}."
            )

    def send_all(self, dry_run: bool = False) -> dict:
        """Send to all emails in CSV. Returns summary dict."""
        manager = EmailCSVManager(self.csv_path)
        rows = manager.read()
        sent, failed, skipped = 0, 0, 0

        for row in rows:
            email = row.get("email", "").strip()
            if not email:
                skipped += 1
                continue

            body = self._render_body(email)

            if dry_run:
                logger.info(f"[DRY RUN] Would send to: {email}")
                sent += 1
                continue

            try:
                send_mail(
                    subject=self.subject,
                    message=body,
                    from_email=self.from_email,
                    recipient_list=[email],
                    html_message=body,
                    fail_silently=False,
                )
                logger.info(f"[Invitation] Sent to {email}")
                sent += 1
                time.sleep(self.rate_limit)
            except Exception as exc:
                logger.error(f"[Invitation] Failed for {email}: {exc}")
                failed += 1

        return {"sent": sent, "failed": failed, "skipped": skipped}
