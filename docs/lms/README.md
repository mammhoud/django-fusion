# LMS (formerly lms-demo)

> **Related Names:** `structa.cloud`, `Django site`, `LMS`, `courses`, `learning`, `profile`, `dashboard`, `enrollment`, `payments`
> **Tags:** #site #lms #django #learning #courses

**Canonical path:** `projects/lms/`  
**Domain:** structa.cloud  
**Port:** 5071  
**Stack:** Django 4.2+ · Wagtail 7.4+ · PostgreSQL (`db_structa`)  
**SITE_ID:** 2

---

## Overview

LMS is the flagship Structa Cloud learning management system — powering structa.cloud. It provides online courses, certifications, student management, learning paths, and payment integration (Stripe/PayPal).

---

## Guide

### Development

```bash
cd projects

# Django dev server
make docker-up WEBSITE=lms

# Or locally:
cd projects/lms
make dev                    # Dev server on :5071
make migrate                # Apply migrations
make collectstatic          # Collect static files
make frontend-production    # Build webpack bundles
make shell                  # Django shell (shell_plus)
make test                   # Run test suite
```

### Common Makefile Commands

| Command | Description |
|---------|-------------|
| `make dev` | Run Django dev server on :5071 |
| `make check` | Django system checks |
| `make migrate` | Apply pending migrations |
| `make makemigrations` | Create new migrations |
| `make shell` | Django shell (shell_plus) |
| `make test` | Run test suite |
| `make collectstatic` | Collect static files |
| `make frontend-production` | Production webpack build |
| `make docker-up` | Start Docker container |
| `make docker-down` | Stop Docker container |

---

## Code Map

### Key Files

| Path | Purpose | Customization |
|------|---------|:---:|
| `lms/settings.py` | Site Django settings | ⚪ config-only |
| `lms/server.py` | ASGI/WSGI application entry point | 🔴 not-customizable |
| `lms/manage.py` | Django management entry point | 🔴 not-customizable |
| `lms/Makefile` | Site-specific commands | 🟢 customizable |
| `lms/plugins/accounts/adapters.py` | Auth adapters (RegistrationAdapter, AuthHTMXSocialAccountAdapter) | 🟡 delegate |
| `lms/plugins/blog/` | Blog plugin (models, templates, views) | 🟢 customizable |
| `lms/plugins/lms/` | **LMS core** — courses, lessons, enrollments, certifications | 🟢 customizable |
| `lms/plugins/products/` | Product/course catalog for payments | 🟢 customizable |
| `lms/plugins/profile/` | User profile plugin (dashboard) | 🟢 customizable |
| `lms/www/apps/` | Site-specific Django apps | 🟢 customizable |
| `lms/assets/templates/` | Site-specific Wagtail templates | 🔵 template |
| `lms/templates/` | Site-level template overrides | 🔵 template |

### Route Registration

```python
# projects/configs/settings/ENV/sites.yml
sites:
  lms:
    domain: structa.cloud
    db_name: db_structa
    port: 5071
```

---

## Remarks

| # | Note |
|---|------|
| ⚠️ | Require migrations: `make migrate WEBSITE=lms` (from `projects/` dir) |
| ⚠️ | Database is PostgreSQL `db_structa` — configured via `DB_NAME_LMS` env var |
| 💡 | The LMS plugin (`plugins/lms/`) handles course management, student progress, certifications, and learning paths |
| 💰 | Payment integration via Stripe and django-paypal — set `STRIPE_API_KEY` and `PAYPAL_*` env vars |
| 🔌 | All Wagtail page templates live in `lms/templates/` or `lms/assets/templates/` |
| 📧 | Email dispatch handled by the shared worker stack via `www/worker/email.py` |

---

## Customization Key

| Tag | Scope | What it means here |
|-----|-------|-------------------|
| 🟢 `customizable` | Plugins & apps | Add/modify courses, lessons, certifications; edit templates |
| 🟡 `delegate` | Auth adapters | Extend `RegistrationAdapter` for custom auth flows |
| 🔴 `not-customizable` | Core infra | `settings.py` structure, `manage.py`, WSGI entry point |
| 🔵 `template` | Templates | Override Wagtail templates in site `templates/` dir |
| ⚪ `config` | Settings | Database name, allowed hosts, payment keys, debug mode via env vars |

---

## Related Documentation

| Resource | Path |
|----------|------|
| Project README | [LMS source](https://github.com/mammhoud/structa.cloud/tree/generic/projects/lms) |
| Configuration | [`configuration.md`](configuration.md) |
| Use Cases | [`use-cases.md`](use-cases.md) |
| Clone Guide | [`clone-guide.md`](clone-guide.md) |
| Deployment guide | [`../../guides/04-deploy.md`](../../guides/04-deploy.md) |
| Backend environment | [`../../back-env/`](../../back-env/) |
| Customization | [`../../customization/`](../../customization/) |
