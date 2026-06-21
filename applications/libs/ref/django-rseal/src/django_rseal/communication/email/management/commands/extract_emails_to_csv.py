"""
Management command: extract_emails_to_csv
Scans spec/markdown directories for email addresses and writes them to a CSV.

Usage:
    python manage.py extract_emails_to_csv
    python manage.py extract_emails_to_csv --dir .kiro/specs-organized --output emails.csv
"""
from pathlib import Path

from django.core.management.base import BaseCommand

from django_rseal.communication.email_tools.csv_manager import EmailCSVManager
from django_rseal.communication.email_tools.extractor import EmailExtractor


class Command(BaseCommand):
    help = "Extract email addresses from spec/markdown files into a CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            default=".kiro/specs-organized",
            help="Directory to scan (default: .kiro/specs-organized)",
        )
        parser.add_argument(
            "--output",
            default=".kiro/specs/email-list.csv",
            help="Output CSV file path (default: .kiro/specs/email-list.csv)",
        )
        parser.add_argument(
            "--extensions",
            default=".md,.txt,.rst",
            help="Comma-separated file extensions to scan",
        )

    def handle(self, *args, **options):
        scan_dir = Path(options["dir"])
        output = Path(options["output"])
        extensions = tuple(options["extensions"].split(","))

        if not scan_dir.exists():
            self.stderr.write(self.style.ERROR(f"Directory not found: {scan_dir}"))
            return

        self.stdout.write(f"Scanning: {scan_dir}")
        self.stdout.write(f"Extensions: {', '.join(extensions)}")

        extractor = EmailExtractor(extensions=extensions)
        manager = EmailCSVManager(output)

        # Extract emails with progress reporting
        self.stdout.write("Extracting emails from files...")
        rows = []
        file_count = 0

        for row in extractor.extract_from_directory(scan_dir):
            rows.append(row)
            file_count += 1
            if file_count % 10 == 0:
                self.stdout.write(f"  Processed {file_count} email occurrences...", ending='\r')

        if file_count > 0:
            self.stdout.write(f"  Processed {file_count} email occurrences... Done!")

        # Merge into CSV
        self.stdout.write("Merging emails into CSV...")
        added = manager.merge(rows)

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Found {len(rows)} occurrences, added {added} new emails → {output}"
            )
        )
