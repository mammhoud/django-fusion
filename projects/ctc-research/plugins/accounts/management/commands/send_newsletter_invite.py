"""
Management command: send_newsletter_invite
==========================================
Send newsletter subscription invitations from a CSV file.

This is a newsletter-only invite — no account creation, no signup link.
Recipients receive a simple subscribe link to join the mailing list.

Usage:
    python manage.py send_newsletter_invite --csv emails.csv
    python manage.py send_newsletter_invite --csv emails.csv --newsletter "Weekly Digest"
    python manage.py send_newsletter_invite --csv emails.csv --dry-run
"""

import csv
import logging
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

HTML_TEMPLATE = "emails/newsletter_invite.html"
TXT_TEMPLATE = "emails/newsletter_invite.txt"


def _build_subscribe_url(base_url: str, email: str) -> str:
    """Build a newsletter subscribe URL with the recipient's email pre-filled."""
    from urllib.parse import quote
    return f"{base_url.rstrip('/')}/newsletter/subscribe/?email={quote(email)}"


class Command(BaseCommand):
    help = "Send newsletter subscription invitations from a CSV file (no account creation)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            default="emails.csv",
            help="Path to CSV file with email (and optional name) columns",
        )
        parser.add_argument(
            "--newsletter",
            type=str,
            default=None,
            help="Newsletter display name (defaults to SITE_NAME newsletter)",
        )
        parser.add_argument(
            "--subscribe-url",
            type=str,
            default=None,
            help="Base subscribe URL (defaults to WAGTAILADMIN_BASE_URL/newsletter/subscribe/)",
        )
        parser.add_argument(
            "--from-email",
            type=str,
            default=None,
            help="Sender email (defaults to DEFAULT_FROM_EMAIL)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be sent without actually sending",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv"])
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        site_name = getattr(settings, "SITE_NAME", None) or getattr(settings, "WAGTAIL_SITE_NAME", "Platform")
        site_url = (
            getattr(settings, "SITE_URL", None)
            or getattr(settings, "WAGTAILADMIN_BASE_URL", "")
        ).rstrip("/")

        newsletter_name = options["newsletter"] or f"{site_name} Newsletter"
        from_email = options["from_email"] or getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
        base_subscribe_url = options["subscribe_url"] or site_url
        dry_run = options["dry_run"]

        # Read CSV
        recipients = []
        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    email = row.get("email", "").strip()
                    if email:
                        recipients.append({
                            "email": email,
                            "name": row.get("name", "").strip(),
                        })
        except Exception as e:
            raise CommandError(f"Error reading CSV: {e}")

        if not recipients:
            raise CommandError("No email addresses found in CSV")

        self.stdout.write(f"Found {len(recipients)} recipient(s) for newsletter: {newsletter_name}")

        sent = failed = 0

        for item in recipients:
            email = item["email"]
            name = item["name"]
            subscribe_url = _build_subscribe_url(base_subscribe_url, email)
            unsubscribe_url = f"{site_url}/newsletter/unsubscribe/?email={email}"

            context = {
                "recipient_email": email,
                "name": name,
                "site_name": site_name,
                "site_url": site_url,
                "newsletter_name": newsletter_name,
                "subscribe_url": subscribe_url,
                "unsubscribe_url": unsubscribe_url,
                "privacy_url": f"{site_url}/privacy/",
            }

            if dry_run:
                self.stdout.write(
                    self.style.NOTICE(
                        f"[DRY RUN] Would send newsletter invite to {email}"
                        f"{' (' + name + ')' if name else ''} → {subscribe_url}"
                    )
                )
                continue

            try:
                html_body = render_to_string(HTML_TEMPLATE, context)
                try:
                    text_body = render_to_string(TXT_TEMPLATE, context)
                except Exception:
                    text_body = strip_tags(html_body)

                subject = f"You're invited to subscribe to {newsletter_name}"
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=from_email,
                    to=[email],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)

                sent += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ Sent to {email}"))

            except Exception as e:
                failed += 1
                logger.error(f"Failed to send newsletter invite to {email}: {e}")
                self.stdout.write(self.style.ERROR(f"  ✗ Failed for {email}: {e}"))

        if dry_run:
            self.stdout.write(self.style.WARNING(f"\n[DRY RUN] Would have sent to {len(recipients)} recipients."))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\nDone. Sent: {sent}") +
                (self.style.ERROR(f", Failed: {failed}") if failed else "")
            )
