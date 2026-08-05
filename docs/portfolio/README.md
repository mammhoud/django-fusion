# VResume (Portfolio Project)

> **Related Names:** `vresume.structa.cloud`, `Django site`, `resume`, `portfolio`, `skills`, `blog`, `events`
> **Tags:** #site #vresume #django #portfolio

**Canonical path:** `projects/portfolio/`  
**Domain:** vresume.structa.cloud  
**Port:** 5072  
**Stack:** Django 4.2+ · Wagtail 7.4+ · PostgreSQL (`vresume`)  
**SITE_ID:** 3

---

## Overview

VResume is a professional resume builder and portfolio website (project directory: `projects/portfolio/`). Users can create, customize, and publish professional resumes with Wagtail CMS-powered content management, rich portfolios, and PDF export.

---

## Guide

### Development

```bash
cd projects

# Django dev server
make docker-up WEBSITE=vresume

# Or locally:
cd projects/portfolio
make dev                    # Dev server on :5072
make migrate                # Apply migrations
make collectstatic          # Collect static files
make frontend-production    # Build webpack bundles
make shell                  # Django shell (shell_plus)
make test                   # Run test suite
```

### Common Makefile Commands

| Command | Description |
|---------|-------------|
| `make dev` | Run Django dev server on :5072 |
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
| `portfolio/settings.py` | Site Django settings | ⚪ config-only |
| `portfolio/server.py` | ASGI/WSGI application entry point | 🔴 not-customizable |
| `portfolio/manage.py` | Django management entry point | 🔴 not-customizable |
| `portfolio/Makefile` | Site-specific commands | 🟢 customizable |
| `portfolio/plugins/accounts/adapters.py` | Auth adapters (RegistrationAdapter, AuthHTMXSocialAccountAdapter) | 🟡 delegate |
| `portfolio/plugins/blog/` | Blog plugin (models, templates, views) | 🟢 customizable |
| `portfolio/plugins/profile/` | User profile plugin | 🟢 customizable |
| `portfolio/www/pages/` | Site-specific page views (home, about, resume, portfolio, blog, connect) | 🟢 customizable |
| `portfolio/www/core/` | Core site handlers | 🔴 not-customizable |
| `portfolio/assets/static/` | Site-specific static files | 🟢 customizable |
| `portfolio/templates/` | Site-level template overrides | 🔵 template |

### Key Components

| Fragment | Template |
|----------|----------|
| `home.main` | `portfolio/www/pages/templates/home/main.html` |
| `resume.main` | `portfolio/www/pages/templates/resume/main.html` |
| `portfolio.main` | `portfolio/www/pages/templates/portfolio/main.html` |
| `blog.main` | `portfolio/www/pages/templates/blog/main.html` |
| `connect.main` | `portfolio/www/pages/templates/connect/main.html` |

### Route Registration

```python
# projects/configs/settings/ENV/sites.yml
sites:
  vresume:
    domain: vresume.structa.cloud
    db_name: vresume
    port: 5072
```

---

## Remarks

| # | Note |
|---|------|
| ⚠️ | Require migrations: `make migrate WEBSITE=vresume` (from `projects/` dir) |
| ⚠️ | Database is PostgreSQL `vresume` — configured via `DB_NAME_VRESUME` env var |
| 🔌 | Page templates are in `portfolio/www/pages/templates/` — not in a top-level `templates/` dir |
| 📄 | PDF export generates print-ready resumes from Wagtail-rendered content |

---

## Customization Key

| Tag | Scope | What it means here |
|-----|-------|-------------------|
| 🟢 `customizable` | Pages & plugins | Add/modify resume templates, portfolio sections, blog posts |
| 🟡 `delegate` | Auth adapters | Extend `RegistrationAdapter` for custom auth flows |
| 🔴 `not-customizable` | Core infra | `settings.py` structure, `manage.py`, WSGI entry point |
| 🔵 `template` | Templates | Override Wagtail templates in site `templates/` dir |
| ⚪ `config` | Settings | Database name, allowed hosts, debug mode via env vars |

---

## Related Documentation

| Resource | Path |
|----------|------|
| Project README | [Portfolio source](https://github.com/mammhoud/structa.cloud/tree/generic/projects/portfolio) |
| Deployment guide | [`../../guides/04-deploy.md`](../../guides/04-deploy.md) |
| Backend environment | [`../../back-env/`](../../back-env/) |
| Customization | [`../../customization/`](../../customization/) |
