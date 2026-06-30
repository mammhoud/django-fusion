"""
Management command: send_invitation_emails
Sends invitation emails to addresses in a CSV file.

Usage:
    python manage.py send_invitation_emails --csv emails.csv --dry-run
    python manage.py send_invitation_emails --csv emails.csv --from noreply@example.com
"""
from pathlib import Path

from django.core.management.base import BaseCommand

from ceptor_ai.communication.email_tools.sender import InvitationEmailSender


class Command(BaseCommand):
    help = "Send invitation emails to addresses listed in a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True, help="Path to the emails CSV file")
        parser.add_argument(
            "--subject",
            default="You're invited to join our platform",
            help="Email subject line",
        )
        parser.add_argument(
            "--from",
            dest="from_email",
            default="",
            help="Sender email address (defaults to DEFAULT_FROM_EMAIL setting)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Log emails without actually sending them",
        )
        parser.add_argument(
            "--rate-limit",
            type=float,
            default=0.5,
            help="Seconds to wait between sends (default: 0.5)",
        )
        parser.add_argument(
            "--url",
            default="",
            help="Registration URL to include in the invitation",
        )

    def handle(self, *args, **options):
        from django.conf import settings

        csv_path = Path(options["csv"])
        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"CSV not found: {csv_path}"))
            return

        from_email = options["from_email"] or getattr(settings, "DEFAULT_FROM_EMAIL", "")
        if not from_email:
            self.stderr.write(self.style.ERROR("No from_email provided and DEFAULT_FROM_EMAIL not set"))
            return

        sender = InvitationEmailSender(
            csv_path=csv_path,
            subject=options["subject"],
            from_email=from_email,
            rate_limit=options["rate_limit"],
            context={"registration_url": options["url"]},
        )

        mode = "DRY RUN" if options["dry_run"] else "LIVE"
        self.stdout.write(f"[{mode}] Sending invitations from {csv_path}...")

        result = sender.send_all(dry_run=options["dry_run"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Sent: {result['sent']}, Failed: {result['failed']}, Skipped: {result['skipped']}"
            )
        )
