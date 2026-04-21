"""
Management command: send_registration_email
============================================
Resend registration confirmation emails to pending (inactive) users.

Usage:
    uv run manage.py send_registration_email
    uv run manage.py send_registration_email --email user@example.com
    uv run manage.py send_registration_email --user-id 42
    uv run manage.py send_registration_email --dry-run
"""

import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

logger = logging.getLogger("apps.registration")
User = get_user_model()


class Command(BaseCommand):
    help = "Resend registration confirmation emails to pending (inactive) users."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--email", type=str, help="Target a specific user by email.")
        group.add_argument("--user-id", type=int, dest="user_id", help="Target a specific user by ID.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be sent without actually sending.",
        )

    def handle(self, *args, **options):
        from www.apps.accounts.registration.emails import send_registration_email
        from www.apps.accounts.registration.tokens import registration_token_generator
        from www.apps.accounts.registration.views import get_site_url

        dry_run = options["dry_run"]
        email_filter = options.get("email")
        user_id = options.get("user_id")

        # Build queryset
        qs = User.objects.filter(is_active=False)
        if email_filter:
            qs = qs.filter(email__iexact=email_filter)
            if not qs.exists():
                raise CommandError(f"No inactive user found with email: {email_filter}")
        elif user_id:
            qs = qs.filter(pk=user_id)
            if not qs.exists():
                raise CommandError(f"No inactive user found with id: {user_id}")

        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("No pending users found."))
            return

        self.stdout.write(f"Found {count} pending user(s).")

        site_url = get_site_url()
        sent = 0
        failed = 0

        for user in qs.iterator():
            token = registration_token_generator.make_token(user)
            path = reverse("handlers:create-password", kwargs={"token": token})
            confirmation_url = f"{site_url}{path}"

            if dry_run:
                self.stdout.write(
                    self.style.NOTICE(f"[DRY RUN] Would send to {user.email} → {confirmation_url}")
                )
                continue

            success = send_registration_email(user, confirmation_url)
            if success:
                sent += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ Sent to {user.email}"))
            else:
                failed += 1
                self.stdout.write(self.style.ERROR(f"  ✗ Failed for {user.email}"))

        if not dry_run:
            self.stdout.write(f"\nDone. Sent: {sent}, Failed: {failed}")
