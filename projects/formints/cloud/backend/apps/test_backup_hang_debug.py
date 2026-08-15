import os
import sqlite3
import tempfile

from django.db import connection
from django.test import TestCase


class DebugBackupHang(TestCase):
    def test_trace_hang(self):
        print("\n[DEBUG] step 1: create BackupRun", flush=True)
        from apps.core.models import BackupRun
        run = BackupRun.objects.create(filename="x.db", status="running")
        print("[DEBUG] step 2: BackupRun created, pk =", run.pk, flush=True)

        with tempfile.TemporaryDirectory() as dest:
            dest_path = os.path.join(dest, "out.db")
            d = sqlite3.connect(dest_path)
            try:
                print("[DEBUG] step 3: calling connection.connection.backup()", flush=True)
                connection.connection.backup(d)
                print("[DEBUG] step 4: backup returned", flush=True)
            finally:
                d.close()
        print("[DEBUG] done", flush=True)
