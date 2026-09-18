"""Management command to send invite emails from emails.csv."""
import csv
import logging
import secrets
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.utils import timezone
from django_fusion.management.commands.base import BaseCommand

from apps.domain.services.email.email_service import EmailService

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

        # Read email + role pairs from the CSV
        invites = []
        try:
            with open(csv_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    email = row.get("email", "").strip()
                    role = row.get("role", "").strip()
                    if email:
                        invites.append({"email": email, "role": role})
        except Exception as e:
            raise CommandError(f"Error reading CSV file: {e}")

        if not invites:
            raise CommandError("No emails found in CSV file")

        self.stdout.write(f"Found {len(invites)} email(s) to invite")

        site_name = getattr(settings, "WAGTAIL_SITE_NAME", "CTC Research")
        site_url = getattr(settings, "SITE_URL", "").rstrip("/")
        if not site_url:
            try:
                from wagtail.models import Site

                site_url = f"http://{Site.objects.get(is_default_site=True).hostname}"
            except Exception:
                site_url = "http://localhost:8000"

        # Send invites
        sent_count = 0
        failed_count = 0
        sent_invites = []

        for invite in invites:
            email = invite["email"]
            role = invite["role"]
            try:
                # Generate the token up front so the email goes out with a
                # working /invite/<token>/ link.
                token = secrets.token_urlsafe(32)
                invite_url = f"{site_url}/invite/{token}/"
                subject = f"You're invited to {site_name}"

                if dry_run:
                    self.stdout.write(
                        f"[DRY RUN] Would send invite to: {email} "
                        f"(role: {role or 'default'})"
                    )
                    sent_invites.append(
                        {"email": email, "role": role, "status": "dry-run"}
                    )
                    sent_count += 1
                    continue

                # Route through EmailService so the invitation is persisted on
                # an EmailLog (token + role) and the accept flow works. The
                # service renders emails/invitation.html and stores the raw
                # role in EmailLog.group_name for registration-time group
                # assignment.
                email_log = EmailService().send_invitation(
                    recipient=email,
                    context={
                        "email": email,
                        "recipient_email": email,
                        "role": role,
                        "site_name": site_name,
                        "subject": subject,
                        "token": token,
                        "invite_url": invite_url,
                    },
                    queue=False,
                )

                # Persist the invite token so /invite/<token>/ can validate it
                # and the registration flow can consume it exactly once.
                email_log.invitation_token = token
                email_log.token_expires_at = timezone.now() + timedelta(days=7)
                email_log.save(
                    update_fields=["invitation_token", "token_expires_at", "updated_at"]
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Sent invite to: {email} (role: {role or 'default'})"
                    )
                )
                sent_invites.append(
                    {
                        "email": email,
                        "role": role,
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
        self.stdout.write(f"Total emails: {len(invites)}")
        self.stdout.write(self.style.SUCCESS(f"Sent: {sent_count}"))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f"Failed: {failed_count}"))

        # Log sent invites
        if sent_invites:
            self.stdout.write("\nSent invites:")
            for invite in sent_invites:
                self.stdout.write(
                    f"  - {invite['email']} (role: {invite.get('role') or 'default'}"
                    f"{', token: ' + invite['token'] if invite.get('token') else ''})"
                )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n[DRY RUN] No emails were actually sent")
            )

        return 0 if failed_count == 0 else 1
