# Shared Background Task Architecture

This repository runs multiple Django websites from one workspace.  Web requests
remain website-specific, while asynchronous work is handled by one shared task
project at the repository root: `tasks/`.

## Runtime roles

| Layer | Location | Responsibility |
| --- | --- | --- |
| Website servers | `ctc-research.com/`, `structa.cloud/` | HTTP/ASGI/WSGI, templates, site settings, static/media configuration |
| Shared settings | `configs/` | Site discovery, security defaults, Celery/RQ/Redis configuration, app registry |
| Shared tasks server | `tasks/` | Celery app and reusable email/content/background tasks for every website |
| Broker/backend | Redis (`CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`) | Queue transport and task results |

## Task package

The root `tasks/` package is the canonical place for shared background jobs:

- `tasks.celery` defines the Celery application (`celery -A tasks ...`).
- `tasks.email` contains templated, bulk, and raw email tasks.
- `tasks.content` contains content/account utility tasks, including user counts
  and welcome email delivery.
- `tasks.ceptor_ai` records the ceptor-ai task modules the shared worker
  should import/autodiscover when ceptor-ai is installed in production.

Website-local task modules now act as compatibility imports.  Existing imports
such as `plugins.accounts.services.email.tasks.send_email_task` still work, but
they point at the shared implementation in `tasks.email`.

## Website selection

Shared tasks accept a `website` argument when work is site-specific:

```python
from tasks.email import send_email_task

send_email_task.delay(
    to="student@example.com",
    subject="Welcome",
    template="emails/welcome.html",
    context={"name": "Student"},
    website="ctc-research.com",
)
```

At execution time the task calls `configure_site_environment()` from
`configs.site`, selects the correct website settings/source tree, and then
initializes Django if needed.  If `website` is omitted, the worker falls back to
`DJANGO_WEBSITE`, `WEBSITE`, or the configured default site.

## Docker Compose

Use `compose/docker-compose.tasks.yml` with the base infrastructure compose file
to run one shared worker and one shared beat scheduler:

```bash
docker compose \
  -f compose/docker-compose.yml \
  -f compose/docker-compose.tasks.yml \
  up shared-tasks-worker shared-tasks-beat
```

Both services use the same Redis broker/result backend and can process tasks
submitted by either website server.  Queue routing is configured in
`configs/settings/ENV/celery.yml`:

- `shared.email.*` routes to the `email` queue.
- `shared.content.*` routes to the `shared` queue.

## Email sending

Email tasks use the selected website's `EmailService` when available, falling
back across the known service import paths for the two site layouts.  Raw email
sending uses Django's `EmailMultiAlternatives` after the selected site's Django
settings are initialized.

## ceptor-ai tasks

`ceptor-ai` is an optional production dependency.  The shared worker keeps
its imports deferred so local environments without ceptor-ai still boot.  The
expected ceptor-ai task modules are listed in `tasks/ceptor_ai.py` and can
be added to as upstream exposes more task modules.
