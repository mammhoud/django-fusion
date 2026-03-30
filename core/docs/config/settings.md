# Settings Reference

AllianceCore uses **Dynaconf** layered on top of Django settings. Configuration is split by environment in `configs/settings/`.

## Settings Files

| File | Purpose |
|---|---|
| `configs/settings/base.py` | Shared settings for all environments |
| `configs/settings/local.py` | Local development overrides |
| `configs/settings/production.py` | Production-specific settings |
| `configs/settings/test.py` | Test-suite overrides |

Environment is selected via `DJANGO_ENV` (defaults to `local`).

---

## Environment Variables Reference

### Core Django

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | — | **Required.** Django secret key for CSRF, sessions, signing |
| `DJANGO_DEBUG` | `False` | Enable debug mode (never `True` in production) |
| `DJANGO_ALLOWED_HOSTS` | `localhost` | Comma-separated list of allowed hosts |
| `DJANGO_ENV` | `local` | Active settings profile (`local`, `production`, `test`) |
| `DJANGO_SETTINGS_MODULE` | auto | Set automatically via `com` wrapper |

### Database

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | — | **Required.** Full PostgreSQL DSN, e.g. `postgres://user:pass@host:5432/db` |
| `POSTGRES_DB` | `alliancecore` | Database name (used by Docker service) |
| `POSTGRES_USER` | `alliancecore` | Database user |
| `POSTGRES_PASSWORD` | — | Database password |

### Cache / Redis

| Variable | Default | Description |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `REDIS_CACHE_TIMEOUT` | `300` | Default cache timeout in seconds |

### Email

| Variable | Default | Description |
|---|---|---|
| `EMAIL_BACKEND` | `console` | Django email backend class |
| `EMAIL_HOST` | `localhost` | SMTP host |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_USE_TLS` | `True` | Enable TLS |
| `EMAIL_HOST_USER` | — | SMTP username |
| `EMAIL_HOST_PASSWORD` | — | SMTP password |
| `DEFAULT_FROM_EMAIL` | `noreply@alliancecore.io` | Default sender address |

### Wagtail

| Variable | Default | Description |
|---|---|---|
| `WAGTAIL_SITE_NAME` | `AllianceCore` | Site name shown in admin |

### Temporal (Background Workflows)

| Variable | Default | Description |
|---|---|---|
| `TEMPORAL_ADDRESS` | `localhost:7233` | Temporal server address |
| `TEMPORAL_NAMESPACE` | `default` | Temporal namespace |
| `TEMPORAL_TASK_QUEUE` | `alliancecore-tasks` | Worker task queue name |

### Storage (AWS S3)

| Variable | Default | Description |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | — | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | — | AWS secret key |
| `AWS_STORAGE_BUCKET_NAME` | — | S3 bucket name |
| `AWS_S3_REGION_NAME` | `us-east-1` | AWS region |

### Observability

| Variable | Default | Description |
|---|---|---|
| `SENTRY_DSN` | — | Sentry DSN for error tracking |
| `PROMETHEUS_METRICS_EXPORT_PORT` | `9000` | Prometheus metrics port |

### Payments

| Variable | Default | Description |
|---|---|---|
| `STRIPE_PUBLIC_KEY` | — | Stripe publishable key |
| `STRIPE_SECRET_KEY` | — | Stripe secret key |

### Twilio (SMS / 2FA)

| Variable | Default | Description |
|---|---|---|
| `TWILIO_ACCOUNT_SID` | — | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | — | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | — | Twilio phone number for SMS |

---

## INSTALLED_APPS Overview

```python
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Wagtail
    "wagtail",
    "wagtail.admin",
    "wagtail.documents",
    "wagtail.images",
    # ... other wagtail apps

    # AllianceCore apps
    "apps.blog",
    "apps.handlers",
    "apps.pages",
    "apps.LMS",

    # CI / Temporal
    "core.CI",

    # Third-party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django_grep",
    "django_grep.mcp_designer",   # MCP integration
    "ninja_extra",
    "django_htmx",
    "django_bird",
    # ...
]
```

---

## Further Reading

- [Installation Guide](../INSTALL.md)
- [MCP Integration](../integrations/mcp.md)
