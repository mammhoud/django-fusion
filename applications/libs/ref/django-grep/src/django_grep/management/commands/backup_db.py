"""Management command: backup_db — dump database to timestamped JSON file."""
import os
from datetime import datetime
from io import StringIO

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Dump the database to a timestamped JSON file in BACKUP_DIR."

    def add_arguments(self, parser):
        parser.add_argument(
            "--compress",
            action="store_true",
            default=os.getenv("DB_BACKUP_COMPRESS", "false").lower() == "true",
            help="Compress output with gzip",
        )
        parser.add_argument(
            "--dir",
            default=os.getenv("BACKUP_DIR", "./backups"),
            help="Directory to write backup (default: ./backups)",
        )

    def handle(self, *args, **options):
        backup_dir = options["dir"]
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"db_{timestamp}.json"
        filepath = os.path.join(backup_dir, filename)

        self.stdout.write(f"Dumping database to {filepath} ...")

        buf = StringIO()
        call_command("dumpdata", "--natural-foreign", "--natural-primary",
                     "--indent=2", stdout=buf)
        data = buf.getvalue()

        if options["compress"]:
            import gzip
            filepath += ".gz"
            with gzip.open(filepath, "wt", encoding="utf-8") as f:
                f.write(data)
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(data)

        size = os.path.getsize(filepath)
        self.stdout.write(self.style.SUCCESS(
            f"Backup created: {filepath} ({size:,} bytes)"
        ))
