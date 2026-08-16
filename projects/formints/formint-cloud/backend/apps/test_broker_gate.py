"""POS Cloud — broker-reachability gate for the Dramatiq enqueue path.

``run_backup`` (and django-fusion's own ``sync_task_history``) enqueue through
``DramatiqBackend.enqueue``. With ``GATE_ON_BROKER_REACHABLE=True`` (see
``configs/__init__.py``), a down/hung Redis is probed once (cached for 5s) and
the enqueue fails fast instead of paying a per-enqueue socket timeout.
"""

from __future__ import annotations

from unittest import mock

import plugins.workers.backup_tasks  # noqa: F401  (registers run_backup via @task)
from django.test import TestCase

from apps.core.models import TaskExecution


class BrokerGateTest(TestCase):
    def _backend_and_reg(self):
        from django_fusion.tasks.registry import task_registry

        backend = task_registry.backend
        reg = task_registry.get("plugins.workers.backup_tasks.run_backup")
        self.assertIsNotNone(backend, "task registry has no configured backend")
        self.assertIsNotNone(reg, "run_backup should be registered on import")
        return backend, reg

    def test_gate_is_enabled_for_formint_cloud(self):
        backend, _ = self._backend_and_reg()
        self.assertTrue(backend.gate_on_broker_reachable)

    def test_enqueue_fails_fast_when_broker_unreachable(self):
        backend, reg = self._backend_and_reg()
        actor = backend._get_or_create_actor(reg)

        with mock.patch.object(backend, "broker_reachable", return_value=False):
            with mock.patch.object(actor, "send") as send:
                with self.assertRaises(ConnectionError) as cm:
                    backend.enqueue(reg, (), {})

        send.assert_not_called()
        self.assertIn("broker unreachable", str(cm.exception))

        # The audit record is still persisted, marked failed.
        record = TaskExecution.objects.get(task_name=reg.name)
        self.assertEqual(record.status, "failed")
        self.assertIn("broker unreachable", record.error_message)

    def test_enqueue_enqueues_when_broker_reachable(self):
        backend, reg = self._backend_and_reg()
        actor = backend._get_or_create_actor(reg)
        fake_message = mock.Mock()
        fake_message.message_id = "dramatiq-message-1"

        with mock.patch.object(backend, "broker_reachable", return_value=True):
            with mock.patch.object(actor, "send", return_value=fake_message):
                message_id = backend.enqueue(reg, (), {})

        self.assertEqual(message_id, "dramatiq-message-1")
        record = TaskExecution.objects.get(task_name=reg.name)
        self.assertEqual(record.status, "queued")

    def test_broker_reachable_caches_result_within_ttl(self):
        backend, _ = self._backend_and_reg()
        backend._broker_reachable_cache = None
        with mock.patch.object(backend, "_probe_broker", return_value=True) as probe:
            self.assertTrue(backend.broker_reachable())
            self.assertTrue(backend.broker_reachable())
        probe.assert_called_once()

    def test_probe_returns_false_for_unroutable_broker(self):
        backend, _ = self._backend_and_reg()
        original_url = backend.broker_url
        backend.broker_url = "redis://127.0.0.1:1/0"  # closed/unroutable port
        try:
            self.assertFalse(backend._probe_broker(timeout=0.2))
        finally:
            backend.broker_url = original_url
