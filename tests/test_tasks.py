"""Tests for django_fusion.tasks module."""

import contextlib
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from django_fusion.tasks.backends.base import AbstractTaskBackend
from django_fusion.tasks.backends.inprocess import InProcessBackend
from django_fusion.tasks.decorators import TaskOptions, task
from django_fusion.tasks.registry import TaskRegistry, task_registry

# ── Helpers ────────────────────────────────────────────────────

def _fresh_registry():
    """Return a fresh registry for isolated tests."""
    return TaskRegistry()


# ── TaskOptions ────────────────────────────────────────────────

class TestTaskOptions:
    def test_defaults(self):
        opts = TaskOptions()
        assert opts.queue == "default"
        assert opts.max_retries == 3
        assert opts.min_backoff == 15_000
        assert opts.max_backoff == 86_400_000
        assert opts.time_limit == 1_800_000
        assert opts.schedule is None
        assert opts.actor_name is None
        assert opts.bind is False

    def test_custom(self):
        opts = TaskOptions(
            queue="email",
            max_retries=5,
            schedule="0 * * * *",
            actor_name="my.task",
        )
        assert opts.queue == "email"
        assert opts.max_retries == 5
        assert opts.schedule == "0 * * * *"
        assert opts.actor_name == "my.task"


# ── TaskRegistry ───────────────────────────────────────────────

class TestTaskRegistry:
    def test_register_and_lookup(self):
        reg = _fresh_registry()
        reg.configure(InProcessBackend())

        def my_func():
            pass

        reg.register(my_func, TaskOptions(queue="test"))
        name = f"{my_func.__module__}.{my_func.__name__}"
        assert reg.get(name) is not None
        assert reg.get(name).queue == "test"
        assert reg.task_count() == 1

    def test_send_runs_inprocess(self):
        reg = _fresh_registry()
        reg.configure(InProcessBackend())

        results = []

        def append_value(x):
            results.append(x)

        reg.register(append_value, TaskOptions(queue="test"))
        reg.send(append_value, 42)
        assert results == [42]

    def test_scheduled_tasks(self):
        reg = _fresh_registry()

        def periodic():
            pass

        reg.register(periodic, TaskOptions(schedule="0 */6 * * *"))
        assert len(reg.scheduled_tasks()) == 1

    def test_lookup_unregistered_raises(self):
        reg = _fresh_registry()
        reg.configure(InProcessBackend())

        def missing():
            pass

        with pytest.raises(KeyError):
            reg.send(missing)

    def test_send_without_backend_raises(self):
        reg = _fresh_registry()

        def f():
            pass

        reg.register(f, TaskOptions())
        with pytest.raises(RuntimeError) as exc:
            reg.send(f)
        assert "no configured backend" in str(exc.value).lower()

    def test_list_tasks(self):
        reg = _fresh_registry()
        reg.configure(InProcessBackend())

        def task_a():
            pass

        def task_b():
            pass

        reg.register(task_a, TaskOptions())
        reg.register(task_b, TaskOptions())
        names = reg.list_tasks()
        assert len(names) == 2


# ── @task Decorator ────────────────────────────────────────────

class TestTaskDecorator:
    def test_registers_with_registry(self):
        # The decorator registers with the package singleton; verify its
        # public wrapper contract through synchronous execution.
        results = []

        @task(queue="test")
        def add_to_results(x):
            results.append(x)

        # Run synchronously via .run
        add_to_results.run(42)
        assert results == [42]
        assert hasattr(add_to_results, "_fusion_task")
        assert add_to_results.options.queue == "test"

    def test_task_has_send_method(self):
        results = []

        @task(queue="test")
        def collect(value):
            results.append(value)

        assert callable(collect.send)
        assert callable(collect.delay)  # Celery-compat alias

    def test_task_actor_name(self):
        @task(queue="default", actor_name="custom.actor")
        def named():
            pass

        assert named.options.actor_name == "custom.actor"


# ── sync_task_history scheduled task ────────────────────────

class TestSyncTaskHistory:
    def test_registered_with_schedule(self):
        """The scheduled sync task is registered with a cron schedule."""
        from django_fusion.tasks import sync_task_history

        assert getattr(sync_task_history, "_fusion_task", False) is True
        assert sync_task_history.options.queue == "system"
        assert sync_task_history.options.schedule == "*/10 * * * *"

    def test_registry_lists_it_as_scheduled(self):
        """The registry exposes the sync task through scheduled_tasks()."""
        from django_fusion.tasks import sync_task_history

        scheduled = {
            reg.name for reg in task_registry.scheduled_tasks() if reg.schedule
        }
        assert f"{sync_task_history.__module__}.{sync_task_history.__name__}" in scheduled

    def test_sync_calls_website_record(self, monkeypatch):
        """Running the task mirrors the website record for the resolved site."""
        from django_fusion.tasks import sync_task_history
        from django_fusion.tasks import views as views_mod

        seen = []
        monkeypatch.setattr(views_mod, "resolve_default_site", lambda: "loop-crm")
        monkeypatch.setattr(
            views_mod, "sync_website_record", lambda site: seen.append(site) or 3
        )

        assert sync_task_history() == 3
        assert seen == ["loop-crm"]


# ── InProcessBackend ───────────────────────────────────────────

class TestDramatiqBackend:
    def test_scheduler_publishes_scheduled_entries(self, monkeypatch):
        """The scheduler publishes jobs; it never executes product code locally."""
        from django_fusion.tasks import scheduler

        backend = MagicMock()
        monkeypatch.setattr(task_registry, "_backend", backend)
        entry = SimpleNamespace(name="scheduled.task")

        scheduler._enqueue_scheduled_task(entry)

        backend.enqueue.assert_called_once_with(entry, (), {})

    def test_delayed_enqueue_uses_keyword_argument_payload(self, monkeypatch):
        """Dramatiq options must keep actor args/kwargs in their named slots."""
        from django_fusion.tasks.backends.dramatiq import DramatiqBackend

        backend = DramatiqBackend.__new__(DramatiqBackend)
        actor = MagicMock()
        actor.send_with_options.return_value = SimpleNamespace(message_id="msg-1")
        backend._get_or_create_actor = lambda registration: actor

        monkeypatch.setattr(
            DramatiqBackend,
            "_create_log",
            staticmethod(lambda *args, **kwargs: None),
        )
        monkeypatch.setattr(
            DramatiqBackend,
            "_touch_website_log",
            staticmethod(lambda *args, **kwargs: None),
        )

        registration = SimpleNamespace(
            name="test.delayed",
            queue="email",
            max_retries=1,
        )
        message_id = backend.enqueue(
            registration,
            (42,),
            {"recipient": "user@example.com"},
            options={"delay": 1_000},
        )

        assert message_id == "msg-1"
        actor.send_with_options.assert_called_once()
        call = actor.send_with_options.call_args.kwargs
        assert call["args"] == (42,)
        assert call["kwargs"]["recipient"] == "user@example.com"
        assert call["kwargs"]["_fusion_job_id"]
        assert call["delay"] == 1_000


class TestInProcessBackend:
    def test_runs_task_synchronously(self):
        backend = InProcessBackend()
        reg = _fresh_registry()
        reg.configure(backend)

        side_effect = []

        def work(x):
            side_effect.append(x)
            return x * 2

        reg.register(work, TaskOptions(queue="test"))
        msg_id = reg.send(work, 21)
        assert msg_id == "inprocess"
        assert side_effect == [21]

    def test_raises_on_error(self):
        backend = InProcessBackend()
        reg = _fresh_registry()
        reg.configure(backend)

        def bad():
            raise ValueError("boom")

        reg.register(bad, TaskOptions(queue="test"))
        with pytest.raises(ValueError, match="boom"):
            reg.send(bad)


# ── AbstractTaskBackend ────────────────────────────────────────

class TestAbstractTaskBackend:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            AbstractTaskBackend()


# ── Services jobs.py backward compat ───────────────────────────

class TestDispatchJobDeprecation:
    def test_dispatch_job_still_importable(self):
        from django_fusion.services.jobs import dispatch_job
        assert callable(dispatch_job)

    def test_dispatch_job_emits_deprecation_warning(self, monkeypatch):
        """dispatch_job emits a DeprecationWarning before any DB access.

        The BackgroundTaskLog model has ``app_label = "shared"``, which
        doesn't match any installed app — so migrate can't create its
        table.  Mock ``_get_task_log_model`` to return None so the
        deprecation path is exercised without hitting the DB.
        """
        import django_fusion.services.jobs as jmod
        from django_fusion.services.jobs import dispatch_job

        # Reset the module-level flag so the warning fires again
        jmod._DEPRECATION_SHOWN = False

        # Avoid the DB-dependent BackgroundTaskLog model entirely.
        monkeypatch.setattr(jmod, "_get_task_log_model", lambda: None)

        with pytest.warns(DeprecationWarning, match="dispatch_job"):
            def noop():
                pass

            # Expected when django-rq is not installed.
            with contextlib.suppress(RuntimeError):
                dispatch_job(noop)
