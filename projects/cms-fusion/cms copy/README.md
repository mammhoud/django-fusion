# CTC Research — Website

> **Domain:** ctc-research.com | **Port:** 5070 | **Stack:** Django + Wagtail

<p align="center">
  <a href="../../docs/sites/ctc-research.md"><img src="https://img.shields.io/badge/docs-site-green" alt="Documentation"/></a>
  <a href="../../CHANGELOG.md"><img src="https://img.shields.io/badge/changelog-root-blue" alt="Changelog"/></a>
  <a href="https://ctc-research.com"><img src="https://img.shields.io/badge/demo-live-purple" alt="Demo"/></a>
</p>

## Overview

CTC Research is a full-featured Wagtail CMS website for professional training, consulting, and research services. Built on the Structa Cloud Django monorepo with shared authentication, component system (django-fusion), and asset pipeline.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 4.2+, Wagtail 7.4+, Celery |
| **Frontend** | Webpack + SCSS + HTMX |
| **Database** | PostgreSQL (`db_ctc`) |
| **Cache/Queue** | Redis (0=cache, 1=broker, 2=results) |
| **Auth** | django-allauth + django-fusion auth mixins |
| **Components** | django-fusion `{% comp %}` tag system |

## Quick Start

```bash
# From projects/ directory
make docker-up WEBSITE=ctc-research

# Or locally
cd projects/ctc-research
make dev                    # Django dev server on :5070
make migrate                # Run migrations
make collectstatic          # Collect static files
make frontend-production    # Build webpack bundles
```

## Key Features

- **Wagtail CMS** — Full content management with StreamField blocks
- **Blog** — Full-featured blog with categories, tags, and rich text
- **Courses & LMS** — Online course management with student tracking
- **User Profiles** — Customizable profiles with social auth
- **Contact Forms** — Configurable contact forms with email notifications
- **Events** — Event management with calendar integration
- **Newsletter** — Email newsletter subscriptions
- **Services** — Service showcase pages
- **Auth** — django-allauth with social login (Google, Facebook, GitHub)
- **HTMX** — Dynamic UI with HTMX fragments

## Project Structure

```
ctc-research/
├── assets/                 # Site-specific frontend assets
│   ├── static/             # Static files (CSS, JS, images)
│   ├── templates/          # Django/Wagtail templates
│   └── bundles/            # Webpack build output (gitignored)
├── plugins/                # Django apps (accounts, blog, lms, etc.)
├── www/                    # Site-specific Django apps
│   └── apps/               # Feature modules
├── templates/              # Site-level template overrides
├── settings/               # Environment-specific settings
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
DB_NAME_CTC=db_ctc
CTC_RESEARCH_HOST=ctc-research.com
```

## Shared Core (`projects/www/`)

This site shares background task processing with other sites via the
[`projects/www/`](../www/README.md) package:

- **`www/worker/`** — Celery + Dramatiq task definitions for email, content, and monitoring
- **`www/worker/email.py`** — Templated email dispatch across all sites
- **`www/worker/tasks.py`** — Shared Celery heartbeat and operational tasks

## Related Documentation

| Resource | Path |
|----------|------|
| Shared Core Docs | [`projects/www/README.md`](../www/README.md) |
| Main Docs | [`docs/`](../../docs/) |
| CTC Research Site Docs | [`docs/sites/ctc-research.md`](../../docs/sites/ctc-research.md) |
| Deployment Guide | [`docs/guides/04-deploy.md`](../../docs/guides/04-deploy.md) |
| Changelog | [`CHANGELOG.md`](../../CHANGELOG.md) |

<!-- @tested CTC Research - Django checks, migrations, webpack, test suite -->
