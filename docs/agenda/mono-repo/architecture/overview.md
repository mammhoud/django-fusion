---
Object type: Workspace
Tags: architecture, overview, stack, infrastructure
Status: Published
---

# Architecture Overview

> **Description:** High-level architecture of Structa Cloud — how sites, libraries, and infrastructure fit together.

## Monorepo layout

### Projects (core)

| Path | Purpose |
|------|---------|
| core/ctc-research/ | CTC Research site |
| core/lms-demo/ | LMS demo site |
| core/VResume/ | VResume site |
| core/tinker/ | Template customizer |
| core/configs/ | Shared Django settings |
| core/assets/ | Shared templates, static files, scripts |
| core/libs/ | Local reusable libraries |
| core/www/ | Shared/core Django code |
| core/compose/ | Dockerfile and entrypoint |

### Applications and supporting areas

| Path | Purpose |
|------|---------|
| applications/proxy/ | Traefik + Nginx |
| applications/databases/ | PostgreSQL + Redis |
| tests/ | Shared and per-site tests |
| docs/ | Documentation |
| docker-compose.yml | Root orchestration |

## Technology stack

| Layer | Technology |
|-------|------------|
| Backend | Django, Wagtail |
| Frontend | SCSS, Webpack, HTMX |
| Libraries | django-fusion, ceptor-ai |
| Auth | django-allauth |
| Task queue | Celery + Redis |
| Database | PostgreSQL |
| Cache | Redis |
| Proxy | Traefik |
| Static/media | Nginx |
| Container | Docker, Docker Compose |

## Shared components

All sites share templates, static files, settings, and libraries. Per-site code lives under its own directory and can override shared templates and styles.

## Request flow

- User request hits the proxy
- Proxy routes to the correct site container based on host
- The site container runs the Django/Wagtail code for that site
- Static and media files are served by Nginx
- Background tasks are processed by background workers

## Data flow

- PostgreSQL stores application data
- Redis stores cache and background-task broker state
- Site media is stored in per-site volumes and served by Nginx

## Scalability

- New sites can be added under their own directory
- Shared components reduce duplication
- Background tasks are centralized in shared workers
- Multi-domain or single-domain deployment is supported

## Related

- → `../plans/project-guide.md` — Repository navigation
- → `../plans/startup-planner.md` — Product and business strategy
- → `../plans/operational-plan.md` — Deployment and operations
