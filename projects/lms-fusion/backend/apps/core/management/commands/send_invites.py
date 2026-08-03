"""Management command to send invite emails from emails.csv."""
import csv
import logging
from pathlib import Path

from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django_fusion.management.commands.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Send invite emails to addresses in emails.csv."""

    help = "Send invite emails to addresses in emails.csv"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--csv-file",
            type=str,
            default="emails.csv",
            help="Path to CSV file with email addresses (default: emails.csv)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be sent without actually sending",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        csv_file = options["csv_file"]
        dry_run = options["dry_run"]

        # Find the CSV file
        csv_path = Path(csv_file)
        if not csv_path.exists():
            # Try from workspace root
            csv_path = Path("/root/site") / csv_file
            if not csv_path.exists():
                raise CommandError(f"CSV file not found: {csv_file}")

        self.stdout.write(f"Reading emails from: {csv_path}")

        # Read emails from CSV
        emails = []
        try:
            with open(csv_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    email = row.get("email", "").strip()
                    if email:
                        emails.append(email)
        except Exception as e:
            raise CommandError(f"Error reading CSV file: {e}")

        if not emails:
            raise CommandError("No emails found in CSV file")

        self.stdout.write(f"Found {len(emails)} email(s) to invite")

        # Send invites
        sent_count = 0
        failed_count = 0
        sent_invites = []

        for email in emails:
            try:
                # Generate unique invite token
                token = get_random_string(32)

                # Prepare email
                subject = "You're invited to fusion-cms.com"
                invite_url = f"http://localhost:8270/invite/{token}/"

                # Try to render email template
                try:
                    html_message = render_to_string(
                        "emails/invitation.html",
                        {
                            "email": email,
                            "invite_url": invite_url,
                            "token": token,
                        },
                    )
                except:
                    # Fallback to plain text
                    html_message = f"""
                    <h1>You're invited to fusion-cms.com</h1>
                    <p>Click the link below to accept your invitation:</p>
                    <p><a href="{invite_url}">{invite_url}</a></p>
                    <p>Or use this code: {token}</p>
                    """

                if dry_run:
                    self.stdout.write(
                        f"[DRY RUN] Would send invite to: {email} (token: {token})"
                    )
                else:
                    # Send email
                    send_mail(
                        subject,
                        f"Visit {invite_url} to accept your invitation",
                        "noreply@fusion-cms.com",
                        [email],
                        html_message=html_message,
                        fail_silently=False,
                    )

                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Sent invite to: {email}")
                    )

                sent_invites.append(
                    {
                        "email": email,
                        "token": token,
                        "status": "sent",
                    }
                )
                sent_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Failed to send invite to {email}: {e}")
                )
                logger.error(f"Failed to send invite to {email}: {e}")
                failed_count += 1

        # Print summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("INVITE SUMMARY")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total emails: {len(emails)}")
        self.stdout.write(self.style.SUCCESS(f"Sent: {sent_count}"))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f"Failed: {failed_count}"))

        # Log sent invites
        if sent_invites:
            self.stdout.write("\nSent invites:")
            for invite in sent_invites:
                self.stdout.write(f"  - {invite['email']} (token: {invite['token']})")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n[DRY RUN] No emails were actually sent")
            )

        return 0 if failed_count == 0 else 1
