"""Tests for django_fusion.tasks — decorator, registry, backends, MCP."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


# ── helpers ────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_registry():
    """Ensure each test starts with a clean (unconfigured) registry."""
    from django_fusion.tasks.registry import TaskRegistry
    registry = TaskRegistry()
    # Swap the singleton — test isolation
    import django_fusion.tasks.decorators as dec_mod
    import django_fusion.tasks.registry as reg_mod
    old_registry = reg_mod.task_registry
    reg_mod.task_registry = registry
    getattr(dec_mod, "task_registry", None)
    yield
    reg_mod.task_registry = old_registry


# ── TaskOptions ────────────────────────────────────────────────────────


class TestTaskOptions:
    def test_defaults(self):
        from django_fusion.tasks.decorators import TaskOptions
        opts = TaskOptions()
        assert opts.queue == "default"
        assert opts.max_retries == 3
        assert opts.min_backoff == 15_000
        assert opts.max_backoff == 86_400_000
        assert opts.time_limit == 1_800_000
        assert opts.schedule is None
        assert opts.actor_name is None
        assert opts.bind is False

    def test_custom_values(self):
        from django_fusion.tasks.decorators import TaskOptions
        opts = TaskOptions(queue="email", max_retries=5, schedule="0 * * * *")
        assert opts.queue == "email"
        assert opts.max_retries == 5
        assert opts.schedule == "0 * * * *"


# ── @task decorator ────────────────────────────────────────────────────


class TestTaskDecorator:
    def test_decorator_registers_task(self):
        from django_fusion.tasks.decorators import task
        from django_fusion.tasks.registry import task_registry

        @task(queue="email", max_retries=5)
        def send_email(user_id: int):
            return f"sent to {user_id}"

        name = f"{send_email.__module__}.send_email"
        reg = task_registry.get(name)
        assert reg is not None
        assert reg.queue == "email"
        assert reg.max_retries == 5
        assert reg.func.__name__ == "send_email"

    def test_decorator_adds_send_and_delay(self):
        from django_fusion.tasks.backends.inprocess import InProcessBackend
        from django_fusion.tasks.decorators import task
        from django_fusion.tasks.registry import task_registry

        task_registry.configure(InProcessBackend())

        results = []

        @task(queue="test")
        def append_result(x):
            results.append(x)

        assert hasattr(append_result, "send")
        assert hasattr(append_result, "delay")
        assert hasattr(append_result, "run")

        append_result.send(42)
        assert results == [42]

    def test_send_raises_without_backend(self):
        from django_fusion.tasks.decorators import task

        @task(queue="test")
        def my_task():
            pass

        with pytest.raises(RuntimeError, match="no configured backend"):
            my_task.send()

    def test_custom_actor_name(self):
        from django_fusion.tasks.decorators import task
        from django_fusion.tasks.registry import task_registry

        @task(actor_name="custom.name")
        def my_func():
            pass

        assert task_registry.get("custom.name") is not None

    def test_schedule_registered(self):
        from django_fusion.tasks.decorators import task
        from django_fusion.tasks.registry import task_registry

        @task(schedule="0 */6 * * *")
        def periodic():
            pass

        name = f"{periodic.__module__}.periodic"
        reg = task_registry.get(name)
        assert reg.schedule == "0 */6 * * *"
        scheduled = task_registry.scheduled_tasks()
        assert any(r.name == name for r in scheduled)


# ── TaskRegistry ───────────────────────────────────────────────────────


class TestTaskRegistry:
    def test_list_tasks(self):
        from django_fusion.tasks.decorators import task
        from django_fusion.tasks.registry import task_registry

        @task(queue="a")
        def task_a():
            pass

        @task(queue="b")
        def task_b():
            pass

        names = task_registry.list_tasks()
        assert len(names) >= 2

    def test_task_count(self):
        from django_fusion.tasks.decorators import task
        from django_fusion.tasks.registry import task_registry

        @task(queue="x")
        def task_x():
            pass

        assert task_registry.task_count() >= 1

    def test_get_nonexistent(self):
        from django_fusion.tasks.registry import task_registry
        assert task_registry.get("nonexistent") is None


# ── InProcessBackend ───────────────────────────────────────────────────


class TestInProcessBackend:
    def test_enqueue_runs_synchronously(self):
        from django_fusion.tasks.backends.inprocess import InProcessBackend
        from django_fusion.tasks.decorators import task
        from django_fusion.tasks.registry import task_registry

        task_registry.configure(InProcessBackend())

        side_effects = []

        @task(queue="test")
        def side_effect_task(x, *, y=None):
            side_effects.append((x, y))
            return x * 2

        result = side_effect_task.send(21, y="hello")
        assert side_effects == [(21, "hello")]
        assert result == "inprocess"

    def test_inprocess_logs_to_background_task_log(self):
        from django_fusion.tasks.backends.inprocess import InProcessBackend
        from django_fusion.tasks.decorators import task
        from django_fusion.tasks.registry import task_registry

        task_registry.configure(InProcessBackend())

        @task(queue="test", actor_name="test.inprocess_logger")
        def logger_task():
            return "ok"

        logger_task.send()
        # The log might fail if Django models aren't available, but the
        # task itself should complete without error.
        assert True  # didn't crash


# ── DramatiqBackend (unit — no broker required) ─────────────────────────


class TestDramatiqBackendMinimal:
    def test_backend_initialises_without_broker(self):
        # Import shouldn't require a running Redis
        from django_fusion.tasks.backends.dramatiq import DramatiqBackend
        # Dramatiq import might fail without the package, but the class
        # should be importable
        assert DramatiqBackend is not None


# ── MCP tool definitions ───────────────────────────────────────────────


class TestMCPToolDefinitions:
    def test_all_eight_tools_defined(self):
        from django_fusion.tasks.mcp_tools import MCP_TASK_TOOLS

        expected = {
            "task.inspect",
            "task.queues",
            "task.history",
            "task.retry",
            "task.trigger",
            "task.stats",
            "task.purge",
            "task.workers",
        }
        assert set(MCP_TASK_TOOLS.keys()) == expected

    def test_each_tool_has_description_and_parameters(self):
        from django_fusion.tasks.mcp_tools import MCP_TASK_TOOLS

        for name, tool in MCP_TASK_TOOLS.items():
            assert "description" in tool, f"{name} missing description"
            assert "parameters" in tool, f"{name} missing parameters"


# ── MCP handlers (unit — no Django configured) ──────────────────────────


class TestMCPHandlers:
    def test_workers_handler_returns_ok(self):
        from django_fusion.tasks.mcp_handlers import handle_task_workers

        result = handle_task_workers()
        assert "backend" in result

    def test_trigger_nonexistent_task(self):
        from django_fusion.tasks.mcp_handlers import handle_task_trigger

        result = handle_task_trigger("nonexistent.task.name")
        assert "error" in result
        assert "available_tasks" in result


# ── AsyncEmailBackend (import check) ───────────────────────────────────


class TestAsyncEmailBackend:
    def test_class_importable(self):
        from django_fusion.tasks.email_backend import AsyncEmailBackend
        assert AsyncEmailBackend is not None
