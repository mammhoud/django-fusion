---
Object type: Decision
Status: Accepted
Category: Architecture
Date: 2024-07-12
Decision Maker: mammhoud
Tags: adr, architecture, django, wagtail

# ADR-001: Monorepo with Django + Wagtail CMS

## Context

The Structa Cloud project needed to serve multiple distinct web presences — a research publication platform (CTC Research), a learning management demo (LMS Demo), a portfolio builder (VResume), and a template customizer (Tinker) — while keeping them related enough to share authentication, templates, UI components, and administrative tooling.

The alternatives considered included:

- **Separate repositories per site** — Each site as its own Django project with independent deployment
- **Django sites framework** — Single Django project with `django.contrib.sites` for multi-tenancy
- **Microservice architecture** — Each site as its own service communicating via APIs
- **Monorepo with shared core** — All sites in one repository sharing a common Django/Wagtail core

We also needed a CMS that editors could use directly, ruling out static-site generators and pure headless approaches.

## Options Considered

1. **Separate repos per site**
   - Pros: Complete isolation, independent deployment, team autonomy
   - Cons: Duplicated configuration, no shared components, harder cross-site navigation, multiplied maintenance burden

2. **Django sites framework**
   - Pros: Single deployment, shared database, built-in Django feature
   - Cons: Limited content sharing across sites, complex URL routing, no visual content management

3. **Microservice architecture**
   - Pros: Independent scaling, language flexibility, team autonomy
   - Cons: Operational complexity, network overhead, overkill for a small team, no shared templates

4. **Monorepo with shared Django core + Wagtail** — **Chosen**
   - Pros: Single source of truth, shared templates and components, unified authentication, Wagtail for visual editing, consistent deployment
   - Cons: Tight coupling between sites, single deployment risk, requires disciplined code organization

## Decision

We chose the **monorepo with Django + Wagtail** approach.

The project is organized as a single repository with a shared `projects/` directory containing all sites. A canonical dispatcher dispatches per-site commands via `WEBSITE=<name>` variables. Shared settings live in `projects/configs/`, shared templates in `projects/assets/templates/`, and shared static files in `projects/assets/static/`.

Wagtail provides visual page editing for all sites, allowing non-technical editors to manage content. Each site is a separate Django application within the monorepo, but they all share the same core infrastructure:

- **Django** — Backend framework (Python 3.11+, Django 4.2+)
- **Wagtail** — CMS for visual page management
- **PostgreSQL** — Primary database (shared instance, schema-per-site)
- **Redis** — Cache and task queue
- **Traefik** — Edge proxy with automatic SSL
- **Nginx** — Static/media file serving

## Consequences

**Positive:**
- Single `git clone` to get the entire platform
- Shared templates eliminate visual drift between sites
- Unified auth means users can move between sites seamlessly
- Wagtail gives editors direct control over page content
- Single CI/CD pipeline deploys all sites consistently

**Negative:**
- Sites are tightly coupled — a bad deployment can affect all sites
- Repository size grows with each site
- Changes to shared code require testing across all sites
- New team members have a larger codebase to learn

**Risks:**
- **Monorepo sprawl** — mitigated by consistent directory conventions and build discipline
- **Shared dependency conflicts** — mitigated by unified `pyproject.toml` and lockfile
- **Deployment coupling** — mitigated by Docker Compose isolation per site container

## Related Docs

- → `../architecture/overview.md` — Architecture overview
- → `../architecture/website-descriptions.md` — Site descriptions & use cases
- → `../architecture/editions.md` — POS editions architecture
- → `../features/_index.md` — Feature comparison
- → `../objects/decision.md` — Decision object type
