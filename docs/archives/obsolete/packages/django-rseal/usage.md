# ceptor-ai Usage Guide

`ceptor-ai` is the email and notification service library for the structa.cloud monorepo. It provides templated email sending, bulk delivery, and newsletter subscription management.

## Installation

```bash
uv pip install -e core/libs/ceptor-ai/
```

## Email Tasks

```python
from ceptor_ai.tasks import send_email_task

send_email_task.delay(
    to="user@example.com",
    subject="Welcome to CTC Research",
    template="emails/welcome.html",
    context={"name": "User"},
    website="ctc-research.com",
)
```

## Newsletter Subscription

```python
from ceptor_ai.newsletter import subscribe, unsubscribe

subscribe(email="user@example.com", list_id="ctc-research-newsletter")
unsubscribe(email="user@example.com", list_id="ctc-research-newsletter")
```

## Template Variables

All email templates receive these base variables automatically:

| Variable | Description |
|----------|-------------|
| `site_name` | Site display name |
| `site_url` | Base URL of the site |
| `unsubscribe_url` | One-click unsubscribe link |
| `year` | Current year for copyright |

## Docker Compose Integration

The shared tasks worker handles rseal task modules. It is included in `applications/compose/docker-compose.tasks.yml`:

```yaml
# Tasks worker autodiscovers ceptor_ai task modules
# See core/tasks/ceptor_ai.py for registered modules
```

## Notes

- Requires Redis broker (`CELERY_BROKER_URL` env var)
- Email backend configured via `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`
- Task modules deferred in local environments without the package installed
