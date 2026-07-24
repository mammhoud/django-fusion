"""
Management command: send_test_email
====================================
Sends a test email to verify the multi-sender email configuration.
Delegates to the apps.accounts.registration.emails service.
"""

import sys

from django.core.management.base import BaseCommand
from django_fusion.site.management.commands.base import BaseCommand
from plugins.accounts.emails import (
    _get_sender_accounts,
    _send_via_smtp,
    _send_with_django_backend,
)


class Command(BaseCommand):
    help = "Send a test email to verify configuration"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, required=True, help="Recipient email address")

    def handle(self, *args, **options):
        recipient = options["email"]
        self.stdout.write(f"Attempting to send test email to {recipient}...")

        subject = "Test Email — LMS Demo Configuration Check"
        html_content = (
            "<html><body>"
            "<h2>Test Email</h2>"
            "<p>This is a test email sent from the LMS Demo platform to verify"
            " that the email configuration is working correctly.</p>"
            "</body></html>"
        )
        text_content = (
            "Test Email\n\n"
            "This is a test email sent from the LMS Demo platform to verify"
            " that the email configuration is working correctly."
        )

        sender_accounts = _get_sender_accounts()

        success = False
        if sender_accounts:
            for i, account in enumerate(sender_accounts):
                try:
                    self.stdout.write(
                        f"  Trying sender {i + 1} ({account['email']})..."
                    )
                    result = _send_via_smtp(
                        sender_email=account["email"],
                        sender_password=account["password"],
                        sender_name=account["name"],
                        recipient_email=recipient,
                        subject=subject,
                        html_content=html_content,
                        text_content=text_content,
                    )
                    if result:
                        success = True
                        break
                except Exception as exc:
                    self.stderr.write(
                        f"  Sender {i + 1} ({account['email']}) failed: {exc}"
                    )
                    continue

        if not success:
            self.stdout.write("  Falling back to Django default email backend...")
            success = _send_with_django_backend(subject, text_content, html_content, recipient)

        if success:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully sent test email to {recipient}")
            )
        else:
            self.stderr.write(
                self.style.ERROR(
                    f"Failed to send test email to {recipient}. Check logs for details."
                )
            )
            sys.exit(1)
