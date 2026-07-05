# structa.cloud Application Documentation

**Project**: AllianceCore — Professional Wagtail CMS Foundation
**Location**: `structa.cloud/`
**Stack**: Django 5.x, Wagtail 6.x, django-allauth (MFA + Social), PostgreSQL, Redis, Celery/RQ, Traefik

---

## Overview

AllianceCore is a production-hardened, modular CMS foundation designed to power complex web applications. It shares the same app structure as ctc-research.com but adds:

- Multi-factor authentication (TOTP, WebAuthn, recovery codes)
- Social OAuth2 (Google, GitHub, Facebook, LinkedIn)
- Django Unfold modern admin UI
- Alliance CI/CD utilities
- Structured JSON logging (`django_structlog`)
- Server startup diagnostics

---

## Project Structure

```
structa.cloud/
├── apps/
│   ├── LMS/          # Learning Management System
│   ├── blog/         # Blog engine
│   ├── handlers/     # Auth, profiles, organizations
│   │   └── registration/  # Allauth adapter, tokens, emails
│   └── pages/        # Wagtail site pages
├── alliance/         # Alliance platform core + CI utilities
├── configs/          # Dynaconf + Pydantic settings
├── compose/          # Docker + Traefik configs
└── tests/            # Test suite
```

---

## Apps

### `apps/handlers` — Core Handlers

Extends the base handlers app with additional auth and startup features.

**Registration sub-app** (`apps/handlers/registration/`):
- `RegistrationAdapter` — custom allauth `DefaultAccountAdapter`; routes lifecycle events to email service
- `AuthEmailTemplate` — Wagtail snippet for editable transactional email templates (single-active invariant enforced)
- `RegistrationTokenGenerator` — HMAC-SHA256 signed tokens with 24-hour expiry
- `AllauthLoginView` / `AllauthSignupView` — `PageHandler` subclasses with HTMX fragment rendering and `HX-Trigger: showNotification`
- Multi-sender SMTP email service with failover and Django backend fallback

**Startup diagnostics** (`apps/handlers/startup.py`):
- Runs in `HandlersConfig.ready()`
- Validates: SECRET_KEY length, insecure placeholder detection, duplicate YAML settings, URL routing resolution, middleware ordering

**Management commands**:
- `validate_config` — audits YAML/`.env` for duplicate settings and insecure SECRET_KEY
- `verify_deployment` — checks Docker containers, network, ports, env vars, Traefik, and health endpoints

---

### `apps/LMS` — Learning Management System

Same structure as ctc-research.com LMS. See [ctc-research.com docs](ctc-research-app.md#appslms--learning-management-system).

---

### `apps/blog` — Blog

Same structure as ctc-research.com blog. See [ctc-research.com docs](ctc-research-app.md#appsblog--blog).

---

### `apps/pages` — Wagtail Site Pages

Same page models as ctc-research.com. See [Wagtail Models reference](wagtail-models.md).

---

### `alliance` — Alliance Platform Core

CI/CD utilities and deployment helpers.

- `alliance.CI` — CI/CD utilities
- `alliance` — core platform module

---

## Authentication

### Social OAuth2

Configured providers: Google, GitHub, Facebook, LinkedIn OAuth2.

```python
SOCIALACCOUNT_PROVIDERS = {
    "google": {...},
    "github": {...},
    "facebook": {...},
    "linkedin_oauth2": {...},
}
```

### MFA

Via `allauth.mfa`:
- TOTP (authenticator apps)
- WebAuthn (hardware keys)
- Recovery codes

---

## Key Third-Party Integrations

| Package | Purpose |
|---------|---------|
| `unfold` | Modern Django admin UI |
| `simple_history` | Model change history tracking |
| `django_structlog` | Structured JSON logging |
| `django_rq` | Redis Queue background jobs |
| `django_extensions` | Developer utilities (`shell_plus`, etc.) |
| `embed_video` | YouTube/Vimeo embedding |
| `colorfield` | Color picker model field |
| `heroicons` | SVG icon set |

---

## Health Check

```
GET /health/  →  {"status": "ok"}
```

Served by `django_fusion.pipelines`.

---

## Configuration

Uses **Dynaconf** + **Pydantic** for layered settings.

```
configs/
├── settings/     # Environment-specific settings
└── ...
```

Environment file: `.env` (copy from `.env.example`)

Key settings:
- `DATABASE_URL` — PostgreSQL connection
- `REDIS_URL` — Redis for cache and RQ
- `SECRET_KEY` — must be ≥50 chars (validated at startup)
- `WAGTAIL_SITE_NAME`
- `SOCIAL_AUTH_*` — OAuth2 credentials

---

## Development

```bash
# Local development
cd structa.cloud
./run_containers.sh

# Production (Traefik + SSL)
./run_containers.sh --prod

# Run tests
pytest tests/

# Validate config
python manage.py validate_config

# Verify deployment
python manage.py verify_deployment
```

---

## Differences from ctc-research.com

| Feature | ctc-research.com | structa.cloud |
|---------|-----------------|---------------|
| MFA | No | Yes (TOTP, WebAuthn) |
| Social auth | No | Yes (Google, GitHub, Facebook, LinkedIn) |
| Admin UI | Default Django | Unfold modern UI |
| Startup diagnostics | No | Yes |
| Structured logging | No | Yes (`django_structlog`) |
| Background jobs | Celery | Redis Queue (`django_rq`) |
| Alliance CI | No | Yes |
