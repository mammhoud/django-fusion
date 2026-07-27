"""
Management command: test_email_csv
=================================
Sends test emails from a CSV file with role-based templates and tracks results.

Usage:
    python manage.py test_email_csv --csv test_email.csv
    python manage.py test_email_csv --csv test_email.csv --dry-run
    python manage.py test_email_csv --csv test_email.csv --template-dir templates/emails
"""

import csv
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django_fusion.site.management.commands.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

# CSVEmailTest/CSVEmailTestBatch models removed — no longer available
try:
    from apps.core.models.email import CSVEmailTest, CSVEmailTestBatch  # type: ignore[import]
except ImportError:
    CSVEmailTest = None  # type: ignore[assignment,misc]
    CSVEmailTestBatch = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


class EmailCSVTester:
    """Handles CSV-based email testing with role-based templates."""

    def __init__(self, csv_path: str, template_dir: str = "templates/emails",
                 from_email: str = None, dry_run: bool = False):
        self.csv_path = Path(csv_path)
        self.template_dir = Path(template_dir)
        self.from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        self.dry_run = dry_run
        self.batch = None
        self.batch_id = f"batch_{int(time.time())}"

    def create_batch(self) -> CSVEmailTestBatch:
        """Create a new batch for tracking."""
        batch = CSVEmailTestBatch.objects.create(
            batch_id=self.batch_id,
            csv_file=str(self.csv_path),
            total_emails=0,
            sent_count=0,
            failed_count=0,
            skipped_count=0
        )
        return batch

    def read_csv(self) -> List[Dict[str, str]]:
        """Read and parse CSV file."""
        emails = []
        try:
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    email = row.get('email', '').strip()
                    role = row.get('role', '').strip() or 'default'
                    if email:
                        emails.append({
                            'email': email,
                            'role': role,
                            'original_row': row
                        })
        except Exception as e:
            raise CommandError(f"Error reading CSV file: {e}")

        return emails

    def get_template_context(self, email: str, role: str) -> Dict:
        """Get context for email template."""
        return {
            'email': email,
            'role': role,
            'site_name': getattr(settings, 'SITE_NAME', 'CTC Research'),
            'site_url': getattr(settings, 'SITE_URL', 'https://ctc-research.com'),
            'current_date': datetime.now().strftime('%B %d, %Y'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com')
        }

    def get_template_path(self, role: str) -> Path:
        """Get template path based on role."""
        role_templates = {
            'admin': 'admin_test.html',
            'admin/supervisor': 'admin_supervisor_test.html',
            'supervisor': 'supervisor_test.html',
            'default': 'test_email.html'
        }

        template_name = role_templates.get(role, 'test_email.html')
        template_path = self.template_dir / template_name

        # Fallback to default if specific template doesn't exist
        if not template_path.exists():
            template_path = self.template_dir / 'test_email.html'

        return template_path

    def render_email(self, email: str, role: str) -> tuple:
        """Render email content."""
        context = self.get_template_context(email, role)
        template_path = self.get_template_path(role)

        try:
            # Try to render template
            html_content = render_to_string(str(template_path.relative_to(settings.BASE_DIR)), context)
            text_content = strip_tags(html_content)
            subject = f"Test Email - {role.capitalize()} Role"

            return subject, html_content, text_content
        except Exception as e:
            logger.error(f"Error rendering template for {email}: {e}")
            # Fallback to simple email
            subject = f"Test Email - {role.capitalize()} Role"
            html_content = f"""
            <html>
            <body>
                <h1>Test Email</h1>
                <p>This is a test email for {role} role.</p>
                <p>Email: {email}</p>
                <p>Role: {role}</p>
            </html>
            """
            text_content = f"Test email for {email} with role {role}"
            return subject, html_content, text_content

    def send_email(self, email: str, role: str) -> tuple[bool, str, dict]:
        """Send email and return success status, message, and details."""
        start_time = time.time()
        success = False
        error_msg = ""
        details = {}

        try:
            if self.dry_run:
                return True, "DRY_RUN", {"status": "DRY_RUN"}

            subject, html_content, text_content = self.render_email(email, role)

            # Send email
            send_mail(
                subject=subject,
                message=text_content,
                from_email=self.from_email,
                recipient_list=[email],
                html_message=html_content,
                fail_silently=False
            )

            success = True
            message = "Email sent successfully"

        except Exception as e:
            success = False
            error_msg = str(e)
            message = f"Failed to send email: {error_msg}"
            details = {"error": error_msg}
        finally:
            duration = (time.time() - start_time) * 1000  # Convert to ms

        return success, message, {
            "status": "SENT" if success else "FAILED",
            "duration_ms": duration,
            "error": error_msg if not success else None
        }

    def process_csv(self) -> dict:
        """Process CSV file and send emails."""
        emails = self.read_csv()
        results = {
            'total': len(emails),
            'sent': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }

        # Create batch record
        self.batch = self.create_batch()
        self.batch.total_emails = len(emails)

        for email_data in emails:
            email = email_data['email']
            role = email_data['role']

            # Create test record
            test_record = CSVEmailTest.objects.create(
                batch=self.batch,
                test_name=f"Test for {email}",
                csv_file=str(self.csv_path),
                template_dir=str(self.template_dir),
                recipient_email=email,
                recipient_role=role,
                status='pending'
            )

            if self.dry_run:
                results['skipped'] += 1
                test_record.status = 'skipped'
                test_record.save()
                continue

            # Send email
            success, message, details = self.send_email(email, role)

            # Update test record
            test_record.status = 'sent' if success else 'failed'
            test_record.error_message = details.get('error', '') if not success else ''
            test_record.duration_ms = details.get('duration_ms', 0)
            test_record.save()

            # Update results
            if success:
                results['sent'] += 1
                self.batch.sent_count += 1
            else:
                results['failed'] += 1
                self.batch.failed_count += 1

            results['details'].append({
                'email': email,
                'role': role,
                'success': success,
                'message': message,
                'details': details
            })

        # Update batch
        self.batch.completed_at = timezone.now()
        self.batch.save()

        return results

    def save_results(self, results: dict, output_path: Path = None):
        """Save results to JSON file."""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = Path(f"email_test_results_{timestamp}.json")

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        return output_path


class Command(BaseCommand):
    help = 'Send test emails from CSV file with role-based templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='test_email.csv',
            help='Path to CSV file with email and role columns'
        )
        parser.add_argument(
            '--template-dir',
            type=str,
            default='templates/emails',
            help='Directory containing email templates'
        )
        parser.add_argument(
            '--from-email',
            type=str,
            help='Sender email address (defaults to DEFAULT_FROM_EMAIL)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Test run without sending emails'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output JSON file for results (default: auto-generated)'
        )

    def handle(self, *args, **options):
        csv_path = options['csv']
        template_dir = options['template_dir']
        from_email = options['from_email']
        dry_run = options['dry_run']
        output = options['output']

        # Check if CSV file exists
        if not Path(csv_path).exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        # Create tester instance
        tester = EmailCSVTester(
            csv_path=csv_path,
            template_dir=template_dir,
            from_email=from_email,
            dry_run=dry_run
        )

        # Process CSV and send emails
        self.stdout.write(f"Processing CSV: {csv_path}")
        results = tester.process_csv()

        # Save results
        if output:
            output_path = Path(output)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = Path(f"email_test_results_{timestamp}.json")

        tester.save_results(results, output_path)

        # Print summary
        self.stdout.write(self.style.SUCCESS(
            f"Processed {results['total']} emails: "
            f"{results['sent']} sent, {results['failed']} failed"
        ))

        if output_path:
            self.stdout.write(f"Results saved to: {output_path}")
