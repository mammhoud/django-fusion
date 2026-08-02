"""
Management command: send_bulk_emails
=====================================
Send bulk emails from a CSV file with template support.

Usage:
    python manage.py send_bulk_emails emails.csv
    python manage.py send_bulk_emails emails.csv --template path/to/template.html
    python manage.py send_bulk_emails emails.csv --dry-run
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
from django.core.management.base import CommandError
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django_fusion.management.commands.base import BaseCommand

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE_NAME = "emails/bulk_email_default.html"


def _parse_csv(csv_path: Path) -> List[Dict[str, Any]]:
    emails = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("email"):
                continue
            emails.append({
                "email": row["email"].strip(),
                "name": row.get("name", "").strip(),
                "subject": row.get("subject", ""),
                "template_vars": {k: v for k, v in row.items() if k not in ("email", "name", "subject")},
            })
    return emails


def _render(template_path: Path | None, context: Dict) -> str:
    if template_path and template_path.exists():
        tmpl = Template(template_path.read_text(encoding="utf-8"))
        return tmpl.render(Context(context))
    return render_to_string(DEFAULT_TEMPLATE_NAME, context)


def _send_one(email_data: Dict, from_email: str, subject: str,
              template_path: Path | None, max_retries: int) -> Dict:
    context = {
        "email": email_data["email"],
        "name": email_data["name"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **email_data["template_vars"],
    }
    html = _render(template_path, context)
    text = strip_tags(html)
    subj = email_data["subject"] or subject
    msg = EmailMultiAlternatives(subj, text, from_email, [email_data["email"]],
                                 alternatives=[(html, "text/html")])
    for attempt in range(max_retries + 1):
        try:
            msg.send(fail_silently=False)
            return {"status": "success", "email": email_data["email"], "attempts": attempt + 1}
        except Exception as e:
            if attempt == max_retries:
                return {"status": "failed", "email": email_data["email"],
                        "error": str(e), "attempts": attempt + 1}
            time.sleep(1)
    return {"status": "failed", "email": email_data["email"], "error": "max retries"}


class Command(BaseCommand):
    help = "Send bulk emails from CSV file with template support"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to CSV file")
        parser.add_argument("--template", type=str, help="Path to HTML template file")
        parser.add_argument("--from-email", type=str,
                            default=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"))
        parser.add_argument("--subject", type=str, default="Bulk Email")
        parser.add_argument("--batch-size", type=int, default=50)
        parser.add_argument("--max-retries", type=int, default=3)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--output", type=str, help="Save results to JSON file")

    def handle(self, *args, **options):
        csv_path = Path(options["csv_file"])
        template_path = Path(options["template"]) if options.get("template") else None
        from_email = options["from_email"]
        subject = options["subject"]
        batch_size = options["batch_size"]
        max_retries = options["max_retries"]
        dry_run = options["dry_run"]
        output_file = options.get("output")

        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        try:
            emails = _parse_csv(csv_path)
        except Exception as e:
            raise CommandError(f"Error parsing CSV: {e}")

        if not emails:
            raise CommandError("No valid emails found in CSV")

        self.stdout.write(f"Found {len(emails)} emails. From: {from_email}, Subject: {subject}")

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"[DRY RUN] Would send to {len(emails)} recipients."))
            return

        results = {"total": len(emails), "successful": 0, "failed": 0, "errors": []}

        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            for item in batch:
                result = _send_one(item, from_email, subject, template_path, max_retries)
                if result["status"] == "success":
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({"email": result["email"], "error": result.get("error")})
            self.stdout.write(f"Processed {min(i + batch_size, len(emails))}/{len(emails)}...")

        self.stdout.write(f"Done. Sent: {results['successful']}, Failed: {results['failed']}")

        if output_file:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2, default=str)
            self.stdout.write(f"Results saved to: {output_file}")

        if results["failed"]:
            self.stdout.write(self.style.WARNING(f"{results['failed']} emails failed."))
        else:
            self.stdout.write(self.style.SUCCESS("All emails sent successfully."))
