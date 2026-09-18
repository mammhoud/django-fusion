"""
Management command to create an online SQLite backup of the Cloud database.

Uses SQLite's backup API so the source database can continue serving
reads and writes during the backup.  Records the run in ``BackupRun``.

Usage::

    # Default: backup to <db-dir>/backups/
    python manage.py backup_db

    # Custom destination directory
    python manage.py backup_db --dest /mnt/backups/pos-cloud/

    # Custom backup filename
    python manage.py backup_db --name pre-upgrade-$(date +%Y%m%d).db
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone

from apps.core.models import BackupRun

logger = logging.getLogger("pos.cloud.backup")


class Command(BaseCommand):
    help = (
        "Create an online SQLite backup of the Cloud database and "
        "record the run in BackupRun."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dest",
            default=None,
            help=(
                "Backup directory.  Default: <database directory>/backups/."
            ),
        )
        parser.add_argument(
            "--name",
            default=None,
            help=(
                "Custom backup filename.  Default: "
                "pos_cloud-YYYYMMDD-HHMMSS.db."
            ),
        )

    def handle(self, *args, **options):
        db_path = settings.DATABASES["default"]["NAME"]
        if not isinstance(db_path, (str, os.PathLike)):
            raise CommandError(
                "DATABASES['default']['NAME'] must be a file path for "
                "SQLite backup.  Got: {!r}".format(db_path)
            )
        db_path = str(db_path)
        # Django's SQLite test runner points NAME at an in-memory URI
        # (``file:memorydb_default?mode=memory&cache=shared``). It is not a
        # real file — the live database lives behind ``django.db.connection``.
        is_in_memory = ":memory:" in db_path or "mode=memory" in db_path

        # ── Resolve destination directory ──
        dest_dir = options["dest"]
        if dest_dir is None:
            if is_in_memory:
                dest_dir = os.path.join(str(settings.BASE_DIR), "backups")
            else:
                dest_dir = os.path.join(
                    os.path.dirname(os.path.abspath(db_path)), "backups"
                )
        os.makedirs(dest_dir, exist_ok=True)

        # ── Resolve filename ──
        filename = options["name"]
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"pos_cloud-{timestamp}.db"
        dest = os.path.join(dest_dir, filename)

        # Avoid accidental self-backup (only meaningful for a real file).
        if not is_in_memory and os.path.abspath(dest) == os.path.abspath(db_path):
            raise CommandError(
                "Backup destination must differ from the source database."
            )

        # ── Create the BackupRun row BEFORE starting ──────────
        run = BackupRun.objects.create(
            filename=os.path.basename(dest),
            status="running",
        )
        self.stdout.write(
            self.style.NOTICE(
                f"Starting backup → {dest}"
            )
        )

        try:
            # Back up the *live* connection's database. In tests that is the
            # in-memory test DB (with the migrated schema); in production it
            # is the on-disk ``formint_cloud.db``.
            _sqlite_backup(connection.connection, dest)

            # Record size.
            size = os.path.getsize(dest)
            run.status = "success"
            run.size_bytes = size
            run.finished_at = timezone.now()
            run.save(update_fields=["status", "size_bytes", "finished_at"])

            self.stdout.write(
                self.style.SUCCESS(
                    f"Backup complete: {filename} "
                    f"({_fmt_bytes(size)})"
                )
            )

        except Exception as exc:
            run.status = "failed"
            run.error_message = str(exc)
            run.finished_at = timezone.now()
            run.save(update_fields=["status", "error_message", "finished_at"])

            # Remove partial backup file.
            if os.path.exists(dest):
                try:
                    os.remove(dest)
                except OSError:
                    pass

            raise CommandError(f"Backup failed: {exc}") from exc


# ── Helpers ──────────────────────────────────────────────────────


def _sqlite_backup(source_connection, dest_path: str) -> None:
    """Copy the live SQLite connection's database to dest.

    ``source_connection`` is the raw ``sqlite3.Connection`` behind Django's
    ``django.db.connection``. Using the live connection (rather than re-opening
    ``DATABASES['default']['NAME']``) makes the command correct for both the
    on-disk production database and the in-memory test database.
    """
    dest = sqlite3.connect(dest_path)
    try:
        source_connection.backup(dest)
    finally:
        dest.close()


def _fmt_bytes(size: int) -> str:
    """Human-readable byte size."""
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
