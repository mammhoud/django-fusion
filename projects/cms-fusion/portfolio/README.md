# VResume — Website (Portfolio)

> **Domain:** vresume.structa.cloud | **Port:** 5072 | **Stack:** Django + Wagtail

<p align="center">
  <a href="../../docs/sites/portfolio.md"><img src="https://img.shields.io/badge/docs-site-green" alt="Documentation"/></a>
  <a href="../../CHANGELOG.md"><img src="https://img.shields.io/badge/changelog-root-blue" alt="Changelog"/></a>
  <a href="https://vresume.structa.cloud"><img src="https://img.shields.io/badge/demo-live-purple" alt="Demo"/></a>
</p>

## Overview

VResume is a professional resume builder and portfolio website built on the Structa Cloud platform. Users can create, customize, and publish professional resumes with Wagtail CMS-powered content management.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 4.2+, Wagtail 7.4+, Celery |
| **Frontend** | Webpack + SCSS + HTMX |
| **Database** | PostgreSQL (`vresume`) |
| **Cache/Queue** | Redis (0=cache, 1=broker, 2=results) |
| **Auth** | django-allauth + django-fusion auth mixins |
| **Components** | django-fusion `{% comp %}` tag system |

## Quick Start

```bash
# From projects/ directory
make docker-up WEBSITE=vresume

# Or locally
cd projects/portfolio
make dev                    # Django dev server on :5072
make migrate                # Run migrations
make collectstatic          # Collect static files
make frontend-production    # Build webpack bundles
```

## Project Structure

```
VResume/
├── assets/                 # Site-specific frontend assets
│   ├── static/             # Static files (CSS, JS, images)
│   ├── templates/          # Django/Wagtail templates
│   └── bundles/            # Webpack build output (gitignored)
├── plugins/                # Django apps & integrations
├── www/                    # Site-specific Django apps
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
DB_NAME_VRESUME=vresume
VRESUME_HOST=vresume.structa.cloud
```

## Features

- **Resume Builder** — Create professional resumes with customizable templates
- **Portfolio Pages** — Showcase work experience, education, and skills
- **PDF Export** — Generate print-ready PDF versions of resumes
- **User Profiles** — Manage personal information and branding

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
- [VResume Site Docs →](../../docs/sites/portfolio.md)

<!-- @tested VResume - Django system checks, migrations, webpack build, test suite passing -->
