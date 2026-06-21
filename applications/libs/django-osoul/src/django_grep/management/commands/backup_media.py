"""Management command: backup_media — archive MEDIA_ROOT to timestamped tar.gz."""
import os
import tarfile
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Archive MEDIA_ROOT to a timestamped tar.gz in BACKUP_DIR."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            default=os.getenv("BACKUP_DIR", "./backups"),
            help="Directory to write backup (default: ./backups)",
        )

    def handle(self, *args, **options):
        backup_dir = options["dir"]
        os.makedirs(backup_dir, exist_ok=True)

        media_root = getattr(settings, "MEDIA_ROOT", None)
        if not media_root or not os.path.isdir(media_root):
            self.stderr.write(self.style.ERROR(
                f"MEDIA_ROOT '{media_root}' does not exist or is not set."
            ))
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"media_{timestamp}.tar.gz"
        filepath = os.path.join(backup_dir, filename)

        self.stdout.write(f"Archiving {media_root} → {filepath} ...")

        with tarfile.open(filepath, "w:gz") as tar:
            tar.add(media_root, arcname="media")

        size = os.path.getsize(filepath)
        self.stdout.write(self.style.SUCCESS(
            f"Media backup created: {filepath} ({size:,} bytes)"
        ))
