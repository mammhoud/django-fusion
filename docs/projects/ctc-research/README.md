# CTC Research — Project Documentation

> Django + Wagtail + django-bolt backend for the CTC Research site.

## Overview

CTC Research is a research organization website powered by:
- **Django** — Web framework
- **Wagtail** — CMS for content management
- **django-bolt** — High-performance Rust API engine (Actix Web, 60k+ RPS)
- **django-fusion** — Component-based UI framework

## Structure

```
projects/ctc-research/
├── www/                   # Django app (views, models, URLs)
│   ├── urls.py            # ROOT_URLCONF
│   ├── content/           # Wagtail page models
│   │   └── models/        # Publication, Course, TeamMember, etc.
│   ├── schemas/           # Pydantic API schemas (source of truth)
│   └── auth.py            # Token auth backend
├── assets/                # Frontend assets (webpack, SCSS, JS)
├── templates/             # Django templates
├── plugins/               # Wagtail plugins (accounts, research, blog, lms)
├── settings.py            # Django settings
├── server.py              # ASGI/WSGI server entry
├── manage.py              # Django management
├── Makefile               # Task runner (dev, test, deploy, etc.)
└── docker-compose.yml     # Docker service definition
```

## Ports

| Service | Port | Protocol |
|---------|------|----------|
| Wagtail Admin | 5070 | HTTP |
| Django Dev Server | 5070 | HTTP |
| Production (gunicorn) | 5070 | HTTP |

## Makefile Quick Reference

```bash
# Development
make dev               # Start Django dev server (port 5070)
make check             # Django system checks
make shell             # Django shell

# Setup
make setup             # Full setup (install, migrate, static, data)
make install           # Install Python dependencies
make migrate           # Run migrations

# Testing
make test              # Run tests
make lint              # Run ruff lint
make format            # Format code with ruff

# Production
make server            # Production server (auto WSGI/ASGI)
make docker-up         # Build and start Docker containers
make docker-logs       # Follow container logs

# Frontend
make assets-setup      # Full frontend build (install + webpack)
make frontend-watch    # Watch frontend for changes
```

## Deployment

The site is deployed as a Docker container via the root `docker-compose.yml`:

```bash
# From repo root
make ctc-research
make docker-up WEBSITE=ctc-research

# Or directly
cd projects/ctc-research && make docker-up
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_NAME_CTC` | Database name | `db_ctc` |
| `DB_HOST` | Database host | `postgres` |
| `DB_PORT` | Database port | `5432` |
| `DJANGO_SUPERUSER_PASSWORD` | Auto-create superuser | (not set) |
| `SERVER_TYPE` | Server mode | `wsgi` |
| `HOST` | Bind address | `0.0.0.0` |
| `PORT` | Bind port | `5070` |

## Architecture

```
┌──────────────────────┐         ┌──────────────────────┐
│   ctc-research       │         │   next-lms           │
│   (Django/Wagtail)   │  bolt   │   (Next.js)          │
│                      │◄────────│                      │
│ Port 5070 (Wagtail)  │  JSON   │ Port 3000 (React)    │
│ Port 8087 (bolt API) │  API    │                      │
└──────────────────────┘         └──────────────────────┘
```
