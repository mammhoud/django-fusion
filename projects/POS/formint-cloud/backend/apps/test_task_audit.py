"""POS Cloud — task audit parity tests.

Formint Cloud's django-fusion task backend dual-writes every enqueue to two
tables: the shared ``BackgroundTaskLog`` audit trail (materialized by
``core.0011_background_task_log``) and the website-local ``core.TaskExecution``
record (configured via ``FUSION_TASK_EXECUTION_MODEL``). These tests prove the
enqueue path — previously a harmless "BackgroundTaskLog unavailable" warning
with no persisted audit record — now writes both, matching Loop-CRM's Task
Center parity.
"""

from __future__ import annotations

from unittest import mock

import plugins.workers.backup_tasks  # noqa: F401  (registers run_backup via @task)
from django.test import TestCase

from apps.core.models import TaskExecution


class TaskExecutionAuditTest(TestCase):
    """Enqueue must persist both the website-local and shared audit records."""

    def test_enqueue_persists_website_and_shared_audit_records(self):
        from django_fusion.models.tasks import BackgroundTaskLog
        from django_fusion.tasks.registry import task_registry

        reg = task_registry.get("plugins.workers.backup_tasks.run_backup")
        self.assertIsNotNone(reg, "run_backup should be registered on import")

        backend = task_registry.backend
        self.assertIsNotNone(backend, "task registry has no configured backend")

        actor = backend._get_or_create_actor(reg)
        fake_message = mock.Mock()
        fake_message.message_id = "dramatiq-message-1"

        # Stub the actor's send (and the broker gate) so this test proves the
        # audit dual-write without requiring a live Redis broker (the Redis
        # road is covered by test_redis_broker_smoke).
        with mock.patch.object(actor, "send", return_value=fake_message), mock.patch.object(
            backend, "broker_reachable", return_value=True
        ):
            message_id = backend.enqueue(reg, (), {})

        self.assertEqual(message_id, "dramatiq-message-1")

        # Website-local record via FUSION_TASK_EXECUTION_MODEL = core.TaskExecution
        site_records = TaskExecution.objects.filter(task_name=reg.name)
        self.assertEqual(site_records.count(), 1, "expected one TaskExecution record")
        site_record = site_records.get()
        self.assertEqual(site_record.status, "queued")
        self.assertEqual(site_record.queue_name, "system")
        self.assertEqual(site_record.site_name, "formint_cloud")

        # Shared audit record (materialized grep_background_task_log table)
        shared_records = BackgroundTaskLog.objects.filter(task_name=reg.name)
        self.assertEqual(shared_records.count(), 1, "expected one BackgroundTaskLog record")
        shared = shared_records.get()
        self.assertEqual(shared.status, "queued")
        # enqueue re-stamps the shared record with dramatiq's message id.
        self.assertEqual(shared.job_id, "dramatiq-message-1")

    def test_website_record_model_resolves(self):
        """FUSION_TASK_EXECUTION_MODEL must resolve to core.TaskExecution."""
        from django_fusion.tasks.backends.dramatiq import DramatiqBackend

        model = DramatiqBackend._website_record_model()
        self.assertIs(model, TaskExecution)
