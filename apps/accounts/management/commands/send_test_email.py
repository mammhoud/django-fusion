from django.core.management.base import BaseCommand
from apps.accounts.services.email.service import email_service

class Command(BaseCommand):
    help = 'Send a test email to verify configuration'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Recipient email address')

    def handle(self, *args, **options):
        recipient = options['email']
        self.stdout.write(f"Attempting to send test email to {recipient}...")
        
        success = email_service.send_test(to=recipient)
        
        if success:
            self.stdout.write(self.style.SUCCESS(f"Successfully sent test email to {recipient}"))
        else:
            self.stdout.write(self.style.ERROR(f"Failed to send test email to {recipient}. Check logs for details."))
