---
id: plugin.tasks
title: Background Tasks
summary: Unified background-task API with broker-agnostic registration, Dramatiq/in-process backends, task logging, idempotency, and MCP-safe enqueue.
capabilities: [async-email, background-jobs, dramatiq, tasks]
signals: [task_completed, task_enqueued, task_failed]
requires: []
provides: [tasks, background-jobs]
surface: first-party
owner: Yahia
evidence:
  - path: libs/django-fusion/src/django_fusion/tasks/registry.py
    what: The broker-agnostic task registry — registration and lookup by name.
  - path: libs/django-fusion/src/django_fusion/tasks/decorators.py
    what: The decorators a site puts on its task functions.
  - path: libs/django-fusion/src/django_fusion/tasks/backends/dramatiq.py
    what: The Dramatiq backend.
  - path: libs/django-fusion/src/django_fusion/tasks/backends/inprocess.py
    what: The in-process backend, which is what makes the API testable without a broker.
  - path: libs/django-fusion/src/django_fusion/tasks/email_backend.py
    what: The async email backend, the canonical consumer of the task API.
  - path: libs/django-fusion/src/django_fusion/tasks/mcp_tools.py
    what: The MCP-safe enqueue surface for agents.
  - path: libs/django-fusion/src/django_fusion/tasks/scheduler.py
    what: Scheduled/recurring task registration.
limits:
  - "It is not auto-registered. The spec is deliberately not `core=True` and not in CORE_PLUGINS — a site opts into background work."
  - "Brokers are extras, not requirements: `django-fusion[tasks]` brings Dramatiq and APScheduler. Without them only the in-process backend runs, which is useful for tests and development, not for durable queues."
  - "It does not ship a worker. Dramatiq's own process (`dramatiq <module>`) runs the tasks; nothing here supervises, scales, or restarts it."
  - "It provides idempotency and logging primitives, not exactly-once delivery — a task still needs to be written idempotently to be safe on retry."
  - "Only two backends ship: Dramatiq and in-process. If the broker-agnostic claim is read as 'any broker', that is an aspiration, not a fact — a new broker means a new module under `tasks/backends/`."
---

# Background Tasks

## What it does

- Gives one task API that does not change when the broker changes: register a
  function, enqueue it by name, tune it with decorators.
- Ships a **Dramatiq** backend and an **in-process** backend, so the same task
  code runs under a real worker in production and synchronously in tests with no
  broker running.
- Logs task state and carries idempotency primitives, which is what
  `BackgroundTaskLog` (see `django_fusion.models`) records.
- Provides an async email backend built on the same API, and an MCP-safe enqueue
  path so an agent can schedule work without reaching into internals.
- Supports scheduled/recurring tasks through the scheduler.
- Emits `task_enqueued`, `task_completed` and `task_failed` as registry signals.

## What it does not do

- It does not run a worker for you, and it does not supervise one.
- It is not a queue by itself: without the `tasks` extra installed you get the
  in-process backend and nothing durable.
- It does not guarantee exactly-once execution. It gives you the tools to make a
  task safe to retry; the responsibility stays with the task.
