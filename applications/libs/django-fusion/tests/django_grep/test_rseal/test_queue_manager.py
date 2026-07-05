"""
Unit tests for EmailQueueManager — all three backend paths.

Covers Django Q, Celery, and no-backend (synchronous fallback) code paths
using mocks so no live Redis or worker is required.

Coverage target: queue_manager.py ≥ 80%
"""

from unittest.mock import MagicMock, Mock, call, patch

from django.test import TestCase
from ceptor_ai.communication.email.models import EmailLog
from ceptor_ai.services.email.queue_manager import EmailQueueManager

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_log(**kwargs):
    """Create a minimal EmailLog for testing."""
    defaults = dict(
        recipient="test@example.com",
        subject="Test Subject",
        template_used="emails/invitation.html",
        status=EmailLog.Status.FAILED,
        retry_count=0,
    )
    defaults.update(kwargs)
    return EmailLog.objects.create(**defaults)


# ---------------------------------------------------------------------------
# Django Q backend
# ---------------------------------------------------------------------------

class EmailQueueManagerDjangoQTestCase(TestCase):
    """Tests for EmailQueueManager when backend='django_q'."""

    def setUp(self):
        self.manager = EmailQueueManager()
        self.manager.backend = "django_q"  # force backend regardless of env

    # --- queue_email ---

    @patch("django_seed.services.queue_manager.EmailQueueManager._queue_with_django_q",
           return_value="mock-task-id-123")
    def test_queue_email_happy_path(self, mock_q):
        """queue_email with Django Q creates log and sets task_id."""
        log = self.manager.queue_email(
            recipient="user@example.com",
            subject="Hello",
            template_name="emails/invitation.html",
            context={"name": "User"},
            group_name="instructors",
        )

        mock_q.assert_called_once()
        self.assertEqual(log.task_id, "mock-task-id-123")
        self.assertEqual(log.status, EmailLog.Status.QUEUED)
        self.assertEqual(log.recipient, "user@example.com")
        self.assertEqual(log.group_name, "instructors")

    @patch("django_seed.services.queue_manager.EmailQueueManager._queue_with_django_q",
           side_effect=Exception("broker unavailable"))
    def test_queue_email_django_q_raises(self, mock_q):
        """queue_email propagates exception from _queue_with_django_q."""
        with self.assertRaises(Exception) as ctx:
            self.manager.queue_email(
                recipient="user@example.com",
                subject="Hello",
                template_name="emails/invitation.html",
                context={},
            )
        self.assertIn("broker unavailable", str(ctx.exception))

    # --- _queue_with_django_q ---

    def test_queue_with_django_q_calls_async_task(self):
        """_queue_with_django_q calls async_task with correct function path."""
        mock_async = Mock(return_value="dq-task-abc")
        mock_django_q = Mock()
        mock_django_q.tasks.async_task = mock_async

        log = _make_log(status=EmailLog.Status.QUEUED)

        import sys
        sys.modules.setdefault("django_q", mock_django_q)
        sys.modules.setdefault("django_q.tasks", mock_django_q.tasks)

        with patch.dict("sys.modules", {"django_q": mock_django_q, "django_q.tasks": mock_django_q.tasks}):
            task_id = self.manager._queue_with_django_q(
                log, "user@example.com", "Subject", "emails/invitation.html", {"k": "v"}
            )

        mock_async.assert_called_once()
        call_args = mock_async.call_args
        self.assertEqual(call_args[0][0], "django_seed.tasks.send_email_task")
        self.assertEqual(task_id, "dq-task-abc")

    def test_queue_with_django_q_passes_hook(self):
        """_queue_with_django_q passes email_sent_hook as hook kwarg."""
        mock_async = Mock(return_value="dq-task-xyz")
        mock_django_q = Mock()
        mock_django_q.tasks.async_task = mock_async

        log = _make_log(status=EmailLog.Status.QUEUED)

        with patch.dict("sys.modules", {"django_q": mock_django_q, "django_q.tasks": mock_django_q.tasks}):
            self.manager._queue_with_django_q(log, "u@e.com", "S", "emails/t.html", {})

        kwargs = mock_async.call_args[1]
        self.assertEqual(kwargs["hook"], "django_seed.tasks.email_sent_hook")
        self.assertEqual(kwargs["group"], "email")

    # --- retry_failed_email ---

    @patch("django_seed.services.queue_manager.EmailQueueManager._retry_with_django_q")
    def test_retry_failed_email_django_q(self, mock_retry):
        """retry_failed_email increments retry_count and calls _retry_with_django_q."""
        log = _make_log(retry_count=0)

        result = self.manager.retry_failed_email(log.id)

        self.assertTrue(result)
        mock_retry.assert_called_once()
        log.refresh_from_db()
        self.assertEqual(log.retry_count, 1)

    @patch("django_seed.services.queue_manager.EmailQueueManager._retry_with_django_q")
    def test_retry_uses_correct_delay_for_first_retry(self, mock_retry):
        """retry_failed_email uses 60s delay for first retry."""
        log = _make_log(retry_count=0)
        self.manager.retry_failed_email(log.id)

        call_args = mock_retry.call_args
        delay = call_args[0][1]  # second positional arg is delay
        self.assertEqual(delay, 60)

    @patch("django_seed.services.queue_manager.EmailQueueManager._retry_with_django_q")
    def test_retry_uses_correct_delay_for_second_retry(self, mock_retry):
        """retry_failed_email uses 300s delay for second retry."""
        log = _make_log(retry_count=1)
        self.manager.retry_failed_email(log.id)
        delay = mock_retry.call_args[0][1]
        self.assertEqual(delay, 300)

    @patch("django_seed.services.queue_manager.EmailQueueManager._retry_with_django_q")
    def test_retry_uses_correct_delay_for_third_retry(self, mock_retry):
        """retry_failed_email uses 900s delay for third retry."""
        log = _make_log(retry_count=2)
        self.manager.retry_failed_email(log.id)
        delay = mock_retry.call_args[0][1]
        self.assertEqual(delay, 900)

    def test_retry_max_retries_returns_false(self):
        """retry_failed_email returns False when retry_count >= MAX_RETRIES."""
        log = _make_log(retry_count=3)
        result = self.manager.retry_failed_email(log.id)
        self.assertFalse(result)

    def test_retry_nonexistent_log_returns_false(self):
        """retry_failed_email returns False for non-existent log ID."""
        result = self.manager.retry_failed_email(99999)
        self.assertFalse(result)

    # --- _retry_with_django_q ---

    def test_retry_with_django_q_updates_log(self):
        """_retry_with_django_q sets log.task_id and status=QUEUED."""
        mock_async = Mock(return_value="retry-task-id")
        mock_django_q = Mock()
        mock_django_q.tasks.async_task = mock_async

        log = _make_log(retry_count=1, status=EmailLog.Status.FAILED)

        with patch.dict("sys.modules", {"django_q": mock_django_q, "django_q.tasks": mock_django_q.tasks}):
            self.manager._retry_with_django_q(log, delay=60)

        log.refresh_from_db()
        self.assertEqual(log.task_id, "retry-task-id")
        self.assertEqual(log.status, EmailLog.Status.QUEUED)

    # --- schedule_periodic_task ---

    def test_schedule_periodic_task_creates_schedule(self):
        """schedule_periodic_task calls get_or_create with correct args."""
        mock_schedule = Mock()
        mock_schedule_cls = Mock()
        mock_schedule_cls.objects.get_or_create.return_value = (mock_schedule, True)

        mock_django_q = Mock()
        mock_django_q.models.Schedule = mock_schedule_cls

        with patch.dict("sys.modules", {"django_q": mock_django_q, "django_q.models": mock_django_q.models}):
            result = self.manager.schedule_periodic_task(
                name="check_registrations",
                func="django_seed.tasks.check_registrations_task",
                schedule_type="D",
                repeats=-1,
            )

        mock_schedule_cls.objects.get_or_create.assert_called_once_with(
            name="check_registrations",
            defaults={
                "func": "django_seed.tasks.check_registrations_task",
                "schedule_type": "D",
                "repeats": -1,
            },
        )
        self.assertEqual(result, mock_schedule)

    def test_schedule_periodic_task_updates_existing(self):
        """schedule_periodic_task updates existing schedule when not created."""
        mock_schedule = Mock()
        mock_schedule_cls = Mock()
        mock_schedule_cls.objects.get_or_create.return_value = (mock_schedule, False)

        mock_django_q = Mock()
        mock_django_q.models.Schedule = mock_schedule_cls

        with patch.dict("sys.modules", {"django_q": mock_django_q, "django_q.models": mock_django_q.models}):
            self.manager.schedule_periodic_task(
                name="check_registrations",
                func="django_seed.tasks.check_registrations_task",
                schedule_type="W",
            )

        self.assertEqual(mock_schedule.func, "django_seed.tasks.check_registrations_task")
        self.assertEqual(mock_schedule.schedule_type, "W")
        mock_schedule.save.assert_called_once()


# ---------------------------------------------------------------------------
# Celery backend
# ---------------------------------------------------------------------------

class EmailQueueManagerCeleryTestCase(TestCase):
    """Tests for EmailQueueManager when backend='celery'."""

    def setUp(self):
        self.manager = EmailQueueManager()
        self.manager.backend = "celery"

    def test_queue_email_celery_happy_path(self):
        """queue_email with Celery sets task_id from delay() result."""
        mock_task = Mock()
        mock_task.delay.return_value = Mock(id="celery-task-id-456")

        with patch("django_seed.services.queue_manager.EmailQueueManager._queue_with_celery",
                   return_value="celery-task-id-456") as mock_q:
            log = self.manager.queue_email(
                recipient="user@example.com",
                subject="Hello",
                template_name="emails/invitation.html",
                context={},
            )

        mock_q.assert_called_once()
        self.assertEqual(log.task_id, "celery-task-id-456")
        self.assertEqual(log.status, EmailLog.Status.QUEUED)

    def test_retry_failed_email_celery(self):
        """retry_failed_email with Celery calls _retry_with_celery."""
        log = _make_log(retry_count=0)

        with patch("django_seed.services.queue_manager.EmailQueueManager._retry_with_celery") as mock_retry:
            result = self.manager.retry_failed_email(log.id)

        self.assertTrue(result)
        mock_retry.assert_called_once()
        log.refresh_from_db()
        self.assertEqual(log.retry_count, 1)

    def test_schedule_periodic_task_celery_not_supported(self):
        """schedule_periodic_task returns None for Celery backend."""
        result = self.manager.schedule_periodic_task(
            name="test",
            func="django_seed.tasks.check_registrations_task",
        )
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# No backend (synchronous fallback)
# ---------------------------------------------------------------------------

class EmailQueueManagerNoBackendTestCase(TestCase):
    """Tests for EmailQueueManager when no queue backend is available."""

    def setUp(self):
        self.manager = EmailQueueManager()
        self.manager.backend = None

    @patch("django_seed.services.email_service.EmailService._send_now")
    def test_queue_email_no_backend_sends_immediately(self, mock_send):
        """queue_email with no backend calls _send_now synchronously."""
        mock_send.return_value = None

        log = self.manager.queue_email(
            recipient="user@example.com",
            subject="Hello",
            template_name="emails/invitation.html",
            context={},
        )

        mock_send.assert_called_once()
        self.assertIsNotNone(log)
        self.assertEqual(log.recipient, "user@example.com")

    def test_retry_no_backend_returns_false(self):
        """retry_failed_email with no backend returns False."""
        log = _make_log(retry_count=0)
        result = self.manager.retry_failed_email(log.id)
        self.assertFalse(result)

    def test_schedule_periodic_task_no_backend_returns_none(self):
        """schedule_periodic_task with no backend returns None."""
        result = self.manager.schedule_periodic_task(
            name="test",
            func="django_seed.tasks.check_registrations_task",
        )
        self.assertIsNone(result)
