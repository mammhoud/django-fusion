"""
Management command for sending bulk emails from CSV files with template support.
Integrates with CSVEmailTest and CSVEmailTestBatch models for tracking.
"""

import csv
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError
from django_fusion.site.management.commands.base import BaseCommand
from django.template import Context, Template
from django.utils import timezone
from django.utils.html import strip_tags

# CSVEmailTestBatch model removed — no longer available
try:
    from apps.core.models import CSVEmailTestBatch
except ImportError:
    CSVEmailTestBatch = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


class BulkEmailSender:
    """Handles bulk email sending with CSV input and template support."""

    def __init__(self, csv_path: str, template_path: str = None,
                 batch_size: int = 50, max_retries: int = 3):
        """
        Initialize bulk email sender.

        Args:
            csv_path: Path to CSV file with email data
            template_path: Path to email template file (HTML)
            batch_size: Number of emails to process in each batch
            max_retries: Maximum retry attempts for failed sends
        """
        self.csv_path = Path(csv_path)
        self.template_path = Path(template_path) if template_path else None
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.batch_record = None
        self.results = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }

    def validate_inputs(self) -> bool:
        """Validate input files exist."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        if self.template_path and not self.template_path.exists():
            raise FileNotFoundError(f"Template file not found: {self.template_path}")

        return True

    def parse_csv(self) -> List[Dict[str, Any]]:
        """Parse CSV file and return list of email data."""
        emails = []

        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not row.get('email'):
                        continue

                    email_data = {
                        'email': row.get('email', '').strip(),
                        'name': row.get('name', '').strip(),
                        'subject': row.get('subject', ''),
                        'template_vars': {}
                    }

                    # Add all other columns as template variables
                    for key, value in row.items():
                        if key not in ['email', 'name', 'subject']:
                            email_data['template_vars'][key] = value

                    emails.append(email_data)

            return emails
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {e}")

    def load_template(self) -> str:
        """Load email template from file or use default."""
        if self.template_path and self.template_path.exists():
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()

        # Default template
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bulk Email</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Hello {{ name|default:"Valued Customer" }},</h2>
                <p>This is a bulk email sent from our system.</p>
                <p>Email: {{ email }}</p>
                <p>Date: {{ date }}</p>
                {% if custom_message %}
                <p>{{ custom_message }}</p>
                {% endif %}
                <p>Thank you for your attention.</p>
            </div>
        </body>
        </html>
        """

    def render_template(self, template: str, context: Dict[str, Any]) -> str:
        """Render template with context variables."""
        try:
            template_obj = Template(template)
            context_obj = Context(context)
            return template_obj.render(context_obj)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return f"<html><body><p>Error rendering template: {e}</p></body></html>"

    def send_email(self, email_data: Dict[str, Any], template: str,
                   from_email: str, subject: str) -> Dict[str, Any]:
        """Send a single email with retry logic."""
        email = email_data['email']
        name = email_data.get('name', '')

        # Prepare context
        context = {
            'email': email,
            'name': name,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **email_data.get('template_vars', {})
        }

        # Render template
        html_content = self.render_template(template, context)
        text_content = strip_tags(html_content)

        # Create email message
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[email],
            alternatives=[(html_content, 'text/html')]
        )

        # Send with retry logic
        for attempt in range(self.max_retries + 1):
            try:
                email_msg.send(fail_silently=False)
                return {'status': 'success', 'email': email, 'attempts': attempt + 1}
            except Exception as e:
                if attempt == self.max_retries:
                    return {
                        'status': 'failed',
                        'email': email,
                        'error': str(e),
                        'attempts': attempt + 1
                    }
                time.sleep(1)  # Wait before retry

        return {'status': 'failed', 'email': email, 'error': 'Max retries exceeded'}

    def process_batch(self, emails: List[Dict], template: str,
                     from_email: str, subject: str) -> Dict[str, Any]:
        """Process a batch of emails."""
        batch_results = {
            'total': len(emails),
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for email_data in emails:
            result = self.send_email(email_data, template, from_email, subject)

            if result['status'] == 'success':
                batch_results['successful'] += 1
            else:
                batch_results['failed'] += 1
                batch_results['errors'].append({
                    'email': result['email'],
                    'error': result.get('error', 'Unknown error')
                })

        return batch_results

    def send_bulk_emails(self, from_email: str, subject: str) -> Dict[str, Any]:
        """Main method to send bulk emails."""
        # Validate inputs
        self.validate_inputs()

        # Parse CSV
        emails = self.parse_csv()
        if not emails:
            raise ValueError("No valid emails found in CSV")

        # Load template
        template = self.load_template()

        # Create batch record
        if CSVEmailTestBatch is not None:
            self.batch_record = CSVEmailTestBatch.objects.create(
            batch_id=f"batch_{int(time.time())}",
            csv_file=str(self.csv_path),
            total_emails=len(emails),
            sent_count=0,
            failed_count=0
        )

        # Process in batches
        results = {
            'total': len(emails),
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for i in range(0, len(emails), self.batch_size):
            batch = emails[i:i + self.batch_size]
            batch_results = self.process_batch(batch, template, from_email, subject)

            # Update results
            results['successful'] += batch_results['successful']
            results['failed'] += batch_results['failed']
            results['errors'].extend(batch_results['errors'])

            # Log progress
            processed = min(i + self.batch_size, len(emails))
            print(f"Processed {processed}/{len(emails)} emails...")

        # Update batch record
        if self.batch_record is not None:
            self.batch_record.sent_count = results['successful']
            self.batch_record.failed_count = results['failed']
            self.batch_record.completed_at = timezone.now()
            self.batch_record.save()

        return results


class Command(BaseCommand):
    help = 'Send bulk emails from CSV file with template support'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument('--template', type=str, help='Path to email template file')
        parser.add_argument('--from-email', type=str,
                         default=settings.DEFAULT_FROM_EMAIL,
                         help='Sender email address')
        parser.add_argument('--subject', type=str, default='Bulk Email',
                         help='Email subject')
        parser.add_argument('--batch-size', type=int, default=50,
                         help='Number of emails per batch')
        parser.add_argument('--max-retries', type=int, default=3,
                         help='Max retry attempts')
        parser.add_argument('--dry-run', action='store_true',
                         help='Validate CSV without sending')
        parser.add_argument('--output', type=str,
                         help='Save results to JSON file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        template = options.get('template')
        from_email = options['from_email']
        subject = options['subject']
        batch_size = options['batch_size']
        max_retries = options['max_retries']
        dry_run = options.get('dry_run', False)
        output_file = options.get('output')

        self.stdout.write("Starting bulk email sending...")
        self.stdout.write(f"CSV file: {csv_file}")
        self.stdout.write(f"Template: {template or 'Default'}")
        self.stdout.write(f"From: {from_email}")
        self.stdout.write(f"Subject: {subject}")
        self.stdout.write(f"Batch size: {batch_size}")
        self.stdout.write(f"Max retries: {max_retries}")
        self.stdout.write("-" * 50)

        try:
            # Initialize sender
            sender = BulkEmailSender(
                csv_path=csv_file,
                template_path=template,
                batch_size=batch_size,
                max_retries=max_retries
            )

            if dry_run:
                emails = sender.parse_csv()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Dry run successful. Found {len(emails)} emails in CSV"
                    )
                )
                return

            # Send emails
            results = sender.send_bulk_emails(from_email, subject)

            # Display results
            self.stdout.write("\n" + "="*50)
            self.stdout.write("BULK EMAIL SENDING COMPLETE")
            self.stdout.write("="*50)
            self.stdout.write(f"Total emails: {results['total']}")
            self.stdout.write(f"Successful: {results['successful']}")
            self.stdout.write(f"Failed: {results['failed']}")

            if results['errors']:
                self.stdout.write("\nErrors:")
                for error in results['errors'][:5]:  # Show first 5 errors
                    self.stdout.write(f"  {error['email']}: {error.get('error', 'Unknown error')}")
                if len(results['errors']) > 5:
                    self.stdout.write(f"  ... and {len(results['errors']) - 5} more errors")

            # Save results if output file specified
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                self.stdout.write(f"\nResults saved to: {output_file}")

            if results['failed'] == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully sent {results['successful']} emails!"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Sent {results['successful']} emails, "
                        f"{results['failed']} failed"
                    )
                )

        except Exception as e:
            raise CommandError(f"Error sending bulk emails: {e}")
