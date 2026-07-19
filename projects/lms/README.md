# LMS — Website (structa.cloud)

> **Domain:** structa.cloud | **Port:** 5071 | **Stack:** Django + Wagtail + LMS

<p align="center">
  <a href="../../docs/sites/lms.md"><img src="https://img.shields.io/badge/docs-site-green" alt="Documentation"/></a>
  <a href="../../CHANGELOG.md"><img src="https://img.shields.io/badge/changelog-root-blue" alt="Changelog"/></a>
  <a href="https://structa.cloud"><img src="https://img.shields.io/badge/demo-live-purple" alt="Demo"/></a>
</p>

## Overview

LMS Demo is the flagship Structa Cloud learning management system (LMS) website. It provides online courses, certifications, student management, and learning paths — powering structa.cloud.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 4.2+, Wagtail 7.4+, Celery |
| **Frontend** | Webpack + SCSS + HTMX |
| **Database** | PostgreSQL (`db_structa`) |
| **Cache/Queue** | Redis (0=cache, 1=broker, 2=results) |
| **Auth** | django-allauth + django-fusion auth mixins |
| **Components** | django-fusion `{% comp %}` tag system |
| **Payments** | stripe, django-paypal |
| **Storage** | django-storages (S3-compatible) |

## Quick Start

```bash
# From projects/ directory
make docker-up WEBSITE=lms

# Or locally
cd projects/lms
make dev                    # Django dev server on :5071
make migrate                # Run migrations
make collectstatic          # Collect static files
make frontend-production    # Build webpack bundles
```

## Project Structure

```
lms/
├── assets/                 # Site-specific frontend assets
│   ├── static/             # Static files (CSS, JS, images)
│   ├── templates/          # Django/Wagtail templates
│   └── bundles/            # Webpack build output (gitignored)
├── plugins/                # Django apps
│   ├── accounts/           # Auth adapters & templates
│   ├── blog/               # Blog engine
│   ├── lms/                # Learning management system
│   └── ...                 # Additional plugins
├── www/                    # Site-specific Django apps
│   ├── apps/               # Feature modules
│   └── core/               # Core site handlers
├── templates/              # Site-level template overrides
├── Makefile                # Django + frontend commands
├── manage.py               # Django management entry point
└── server.py               # ASGI/WSGI application
```

## Key Makefile Commands

| Command | Description |
|---------|-------------|
| `make dev` | Run Django dev server |
| `make migrate` | Apply migrations |
| `make collectstatic` | Collect static files |
| `make frontend-production` | Build production assets |
| `make shell` | Django shell (shell_plus) |
| `make check` | Django system checks |
| `make test` | Run test suite |

## Environment

Required env vars (set in `.env` at repo root):

```bash
DB_NAME_LMS=db_structa
LMS_DEMO_HOST=structa.cloud
```

## Features

- **Course Management** — Create, publish, and manage online courses with modular lessons
- **Student Dashboard** — Track progress, certificates, and enrollments
- **Learning Paths** — Curated sequences of courses with prerequisites
- **Certifications** — Auto-generated certificates on course completion
- **Payment Integration** — Stripe/PayPal for paid courses
- **Blog** — Full-featured Wagtail blog with categories and tags
- **User Profiles** — Customizable user profiles with avatars and social auth

## Shared Core (`projects/www/`)

This site shares background task processing with other sites via the
[`projects/www/`](../www/README.md) package:

- **`www/worker/`** — Celery + Dramatiq task definitions for email, content, and monitoring
- **`www/worker/email.py`** — Templated email dispatch across all sites
- **`www/worker/tasks.py`** — Shared Celery heartbeat and operational tasks

## Related Documentation

- [Shared Core Docs →](../www/README.md)
- [Main Docs →](../../docs/)
- [Deployment Guide →](../../docs/guides/04-deploy.md)
- [LMS Demo Site Docs →](../../docs/sites/lms.md)

<!-- @tested LMS - Django checks, migrations, webpack, test suite, Stripe/PayPal integration tested -->
