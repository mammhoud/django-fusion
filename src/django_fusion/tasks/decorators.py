"""Broker-agnostic @task decorator."""

from __future__ import annotations

import functools
from typing import Any, Callable, Optional


class TaskOptions:
    """Broker-agnostic task configuration."""

    queue: str = "default"
    max_retries: int = 3
    min_backoff: int = 15_000       # milliseconds
    max_backoff: int = 86_400_000   # milliseconds (24 h)
    time_limit: int = 1_800_000     # milliseconds (30 min)
    schedule: Optional[str] = None  # cron expression
    actor_name: Optional[str] = None
    bind: bool = False

    def __init__(
        self,
        queue: str = "default",
        max_retries: int = 3,
        min_backoff: int = 15_000,
        max_backoff: int = 86_400_000,
        time_limit: int = 1_800_000,
        schedule: Optional[str] = None,
        actor_name: Optional[str] = None,
        bind: bool = False,
    ):
        self.queue = queue
        self.max_retries = max_retries
        self.min_backoff = min_backoff
        self.max_backoff = max_backoff
        self.time_limit = time_limit
        self.schedule = schedule
        self.actor_name = actor_name
        self.bind = bind


def task(
    queue: str = "default",
    max_retries: int = 3,
    min_backoff: int = 15_000,
    max_backoff: int = 86_400_000,
    time_limit: int = 1_800_000,
    schedule: Optional[str] = None,
    actor_name: Optional[str] = None,
    bind: bool = False,
    **backend_kwargs: Any,
):
    """Register a function as a background task.

    This decorator is broker-agnostic — it registers with
    django-fusion's :class:`TaskRegistry`, which routes to the
    configured backend (Dramatiq, RQ, or in-process for testing).

    Usage::

        @task(queue="email", max_retries=5)
        def send_welcome_email(user_id: int):
            ...

        # Enqueue
        send_welcome_email.send(user_id=42)

        # Run synchronously (testing)
        send_welcome_email.run(user_id=42)
    """

    options = TaskOptions(
        queue=queue,
        max_retries=max_retries,
        min_backoff=min_backoff,
        max_backoff=max_backoff,
        time_limit=time_limit,
        schedule=schedule,
        actor_name=actor_name,
        bind=bind,
    )

    def decorator(func: Callable) -> Callable:
        from django_fusion.tasks.registry import task_registry

        task_registry.register(func, options, backend_kwargs)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.send = lambda *a, **kw: task_registry.send(wrapper, *a, **kw)

        def send_with_options(*a, **kw):
            """Dramatiq-compatible enqueue helper for broker options.

            Supports Dramatiq's common ``args=``/``kwargs=`` calling form
            while keeping the neutral registry API underneath.
            """
            call_args = tuple(kw.pop("args", a))
            call_kwargs = dict(kw.pop("kwargs", {}))
            broker_options = {
                key: kw.pop(key)
                for key in ("delay", "at_front")
                if key in kw
            }
            call_kwargs.update(kw)
            return task_registry.send(
                wrapper,
                *call_args,
                _fusion_options=broker_options,
                **call_kwargs,
            )

        # Dramatiq's actor exposes ``fn`` and ``send_with_options``; retaining
        # those names makes the migration safe for existing producers/tests.
        wrapper.fn = func
        wrapper.send_with_options = send_with_options
        # ``delay`` is retained as a neutral migration alias for callers that
        # previously used Celery-style enqueue syntax; it never imports Celery.
        wrapper.delay = wrapper.send
        wrapper.run = lambda *a, **kw: task_registry.run(wrapper, *a, **kw)
        wrapper._fusion_task = True
        wrapper.options = options

        return wrapper

    return decorator
