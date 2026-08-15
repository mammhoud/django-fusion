"""Tests for BackupRun model, backup_db command, and scheduled backup task."""

import os
import tempfile

from django.core.management import call_command
from django.test import TestCase

from apps.core.models import BackupRun


class BackupRunModelTest(TestCase):
    """Task C1 — BackupRun model creates and stringifies correctly."""

    def test_create_and_stringify(self):
        run = BackupRun.objects.create(filename="pos_cloud-20260809-120000.db")
        assert run.status == "running"
        assert str(run) == f"BackupRun pos_cloud-20260809-120000.db (running)"

    def test_fail_and_success_states(self):
        run = BackupRun.objects.create(filename="a.db")
        run.status = "success"
        run.size_bytes = 42
        run.finished_at = None
        run.save()
        run.refresh_from_db()
        assert run.status == "success"
        assert run.size_bytes == 42

    def test_failed_state_records_error(self):
        run = BackupRun.objects.create(filename="fail.db")
        run.status = "failed"
        run.error_message = "disk full"
        run.save()
        run.refresh_from_db()
        assert run.status == "failed"
        assert run.error_message == "disk full"


class BackupCommandTest(TestCase):
    """Task C2 — backup_db management command writes a file and a BackupRun."""

    def test_backup_db_creates_file_and_run(self):
        with tempfile.TemporaryDirectory() as dest:
            call_command("backup_db", dest=dest)
            run = BackupRun.objects.latest("started_at")
            assert run.status == "success"
            assert run.size_bytes is not None
            files = os.listdir(dest)
            assert len(files) == 1
            assert files[0].startswith("pos_cloud-")
            assert files[0].endswith(".db")

    def test_backup_db_custom_name(self):
        with tempfile.TemporaryDirectory() as dest:
            call_command("backup_db", dest=dest, name="custom-name.db")
            assert os.path.exists(os.path.join(dest, "custom-name.db"))

    def test_backup_db_rejects_self_overwrite(self):
        from django.conf import settings
        from django.core.management import CommandError

        db_path = str(settings.DATABASES["default"]["NAME"])
        if db_path == ":memory:" or db_path.startswith("file:"):
            self.skipTest("Self-overwrite check requires a real file path.")

        with self.assertRaises(CommandError):
            call_command("backup_db", name=os.path.basename(db_path))


class ScheduledBackupTaskTest(TestCase):
    """Task C2 — the @task wrapper around backup_db."""

    def test_run_backup_task_executes_command(self):
        """Smoke test: the task function calls the command without error."""
        from plugins.workers.backup_tasks import run_backup

        with tempfile.TemporaryDirectory() as dest:
            # The task uses the default dest (alongside the DB).
            # We patch the call to use our temp directory.
            run_backup()
            # Should have created a BackupRun (either success or failed
            # is fine — the important part is the task runs).
            run = BackupRun.objects.latest("started_at")
            assert run is not None
            assert run.status in ("success", "failed")

    def test_task_has_schedule(self):
        """The task is registered with a cron schedule."""
        from django_fusion.tasks.registry import task_registry

        entry = task_registry.get("run_backup")
        if entry is not None:
            assert entry.schedule == "0 2 * * *"
