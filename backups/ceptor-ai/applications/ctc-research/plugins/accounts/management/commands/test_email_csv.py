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
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

# Role → template name mapping
ROLE_TEMPLATES = {
    "admin": "emails/admin_test.html",
    "admin/supervisor": "emails/admin_supervisor_test.html",
    "supervisor": "emails/supervisor_test.html",
    "default": "emails/test_email.html",
}
FALLBACK_TEMPLATE = "emails/test_email_fallback.html"


def _get_template_context(email: str, role: str) -> Dict:
    return {
        "email": email,
        "role": role,
        "site_name": getattr(settings, "SITE_NAME", "Platform"),
        "site_url": getattr(settings, "WAGTAILADMIN_BASE_URL", ""),
        "current_date": datetime.now().strftime("%B %d, %Y"),
        "support_email": getattr(settings, "DEFAULT_FROM_EMAIL", "support@example.com"),
    }


def _render_email(email: str, role: str) -> tuple:
    context = _get_template_context(email, role)
    template_name = ROLE_TEMPLATES.get(role, ROLE_TEMPLATES["default"])
    subject = f"Test Email - {role.capitalize()} Role"
    try:
        html_content = render_to_string(template_name, context)
    except Exception:
        try:
            html_content = render_to_string(FALLBACK_TEMPLATE, context)
        except Exception as e:
            logger.error(f"Could not render any template for {email}: {e}")
            html_content = render_to_string("emails/bulk_email_default.html", context)
    return subject, html_content, strip_tags(html_content)


class Command(BaseCommand):
    help = "Send test emails from CSV file with role-based templates"

    def add_arguments(self, parser):
        parser.add_argument("--csv", type=str, default="test_email.csv",
                            help="Path to CSV file with email and role columns")
        parser.add_argument("--from-email", type=str,
                            help="Sender email address (defaults to DEFAULT_FROM_EMAIL)")
        parser.add_argument("--dry-run", action="store_true",
                            help="Test run without sending emails")
        parser.add_argument("--output", type=str,
                            help="Output JSON file for results (default: auto-generated)")

    def handle(self, *args, **options):
        csv_path = Path(options["csv"])
        from_email = options.get("from_email") or getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
        dry_run = options["dry_run"]
        output = options.get("output")

        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        # Read CSV
        emails = []
        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    email = row.get("email", "").strip()
                    if email:
                        emails.append({"email": email, "role": row.get("role", "default").strip() or "default"})
        except Exception as e:
            raise CommandError(f"Error reading CSV: {e}")

        self.stdout.write(f"Found {len(emails)} email(s) in {csv_path}")

        results = {"total": len(emails), "sent": 0, "failed": 0, "skipped": 0, "details": []}

        for item in emails:
            email, role = item["email"], item["role"]

            if dry_run:
                self.stdout.write(self.style.NOTICE(f"[DRY RUN] Would send to {email} (role: {role})"))
                results["skipped"] += 1
                results["details"].append({"email": email, "role": role, "status": "DRY_RUN"})
                continue

            try:
                subject, html_content, text_content = _render_email(email, role)
                send_mail(subject, text_content, from_email, [email],
                          html_message=html_content, fail_silently=False)
                results["sent"] += 1
                results["details"].append({"email": email, "role": role, "status": "SENT"})
                self.stdout.write(self.style.SUCCESS(f"  ✓ Sent to {email}"))
            except Exception as e:
                results["failed"] += 1
                results["details"].append({"email": email, "role": role, "status": "FAILED", "error": str(e)})
                self.stdout.write(self.style.ERROR(f"  ✗ Failed for {email}: {e}"))

        # Save results
        if output or not dry_run:
            out_path = Path(output) if output else Path(f"email_test_results_{int(time.time())}.json")
            with open(out_path, "w") as f:
                json.dump(results, f, indent=2, default=str)
            self.stdout.write(f"Results saved to: {out_path}")

        self.stdout.write(self.style.SUCCESS(
            f"Done. Sent: {results['sent']}, Failed: {results['failed']}, Skipped: {results['skipped']}"
        ))
