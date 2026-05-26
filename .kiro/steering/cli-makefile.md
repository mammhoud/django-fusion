---
title: Websites CLI & Makefile
description: CLI commands, Makefile targets, and Docker workflow for both websites
inclusion: auto
---

# Websites CLI & Makefile

## Overview

The workspace has two levels of Makefile/CLI tooling:

| Level | Location | Scope |
|---|---|---|
| Root Makefile | `Makefile` | Cross-site Docker management (rebuild, remove, logs, health) |
| Site Makefile | `websites/ctc-research.com/makefile` | Per-site dev workflow (migrate, test, frontend, sync) |
| Websites CLI | `websites/cli.py` | Deploy, check, push libs, container management |

Both sites share the same `makefile` — `websites/structa.cloud/` has an equivalent.

---

## Root Makefile (`Makefile`)

Manages Docker containers for both sites from the monorepo root.

### Services

```
ctc-research : website  website-media  website-worker
alliance     : core  alliance-media  lms
infra        : traefik  redis  adminer  blinko  docs
```

### Key Targets

```bash
# Rebuild and restart containers (never touches postgres)
make rebuild                    # rebuild all services
make rebuild svc=website        # rebuild only ctc website
make rebuild svc=core           # rebuild only alliance core

# Remove container + image, then rebuild fresh
make remove svc=website
make remove                     # remove and rebuild everything

# Build with full log output saved to ./docker-build-logs/
make build-with-logs
make build-with-logs svc=core

# Show container logs
make logs svc=core
make logs                       # all services

# Validate compose files without building
make validate

# Health checks
make health-check

# Docker cleanup (never removes volumes)
make cleanup                    # prune unused images/containers/networks
make prune                      # deep clean including volumes (DESTRUCTIVE)
```

### Compose Files

```
Makefile                        → docker-compose.yml (infra: traefik, redis, postgres, etc.)
websites/ctc-research.docker-compose.yml  → ctc-research.com services
websites/structa.docker-compose.yml       → structa.cloud services
```

---

## Websites CLI (`websites/cli.py`)

Python CLI using `fire`. Run from the `websites/` directory or the monorepo root.

```bash
# From monorepo root
python websites/cli.py <command>

# From websites/ directory
python cli.py <command>
```

### Commands

#### `check` — Run Django system checks locally

```bash
python websites/cli.py check structa.cloud
python websites/cli.py check ctc-research.com
```

Runs `<site>/__main__.py check` using the workspace `.venv`. Does not require a running database.

#### `deploy` — Build, check, and deploy a site

```bash
python websites/cli.py deploy structa.cloud
python websites/cli.py deploy ctc-research.com --no-cache
python websites/cli.py deploy structa.cloud --skip-local-check
python websites/cli.py deploy structa.cloud --skip-container-check
```

Steps:
1. Local Django check via `__main__.py check`
2. `docker compose build [--no-cache]`
3. Container Django check via `docker run manage.py check`
4. `docker compose up -d`

#### `logs` — Show container logs

```bash
python websites/cli.py logs structa.cloud
python websites/cli.py logs structa.cloud --tail=50
python websites/cli.py logs ctc-research.com --service=website-worker
```

#### `down` — Stop containers

```bash
python websites/cli.py down structa.cloud
```

#### `ps` — Show container status

```bash
python websites/cli.py ps
```

#### `test` — Run tests against running containers

```bash
python websites/cli.py test structa.cloud
python websites/cli.py test all
python websites/cli.py test all --live   # use live domains
```

#### `push` — Commit and push internal library changes

```bash
python websites/cli.py push                          # push all libs
python websites/cli.py push --lib django-osoul
python websites/cli.py push --lib django-rseal --message "fix: email template"
```

After pushing, the CLI automatically updates `uv.lock` files with the new commit SHAs. Then run `docker compose build --no-cache` to pick up the changes.

---

## Per-Site Makefile (`websites/ctc-research.com/makefile`)

Run from inside the site directory:

```bash
cd websites/ctc-research.com
make <target>
```

Or from the monorepo root using `make -C`:

```bash
make -C websites/ctc-research.com dev
make -C websites/structa.cloud migrate
```

### Development Server

```bash
make dev          # Start Django with Uvicorn (auto-reload)
make run          # Alias for dev
```

### Database

```bash
make migrate      # makemigrations + migrate
make reset-migrations   # Delete migration files and re-migrate (DANGER)
make clean-migrations   # Delete migration .py files only
```

### Static Files & Frontend

```bash
make static           # collectstatic
make frontend-build   # webpack development build
make frontend-production  # webpack production build (with PurgeCSS)
make frontend-watch   # webpack watch mode (dev server)
make frontend-install # npm install
```

### Testing & Quality

```bash
make test             # Django test runner
make test-coverage    # pytest with coverage report
make check            # Django system checks
make check-deploy     # Django deployment checks
make lint             # ruff check (imports only, fast)
make format           # ruff format
make fix              # ruff check --fix (all fixable issues)
make fix-unused       # Remove unused imports (F401, F841)
```

### Setup (First Time)

```bash
make setup    # Full setup: uv sync → migrate → collectstatic → check → frontend → superuser
make install  # uv sync only
```

### Superuser

```bash
make superuser       # Interactive
make superuser-auto  # From .env credentials (DJANGO_SUPERUSER_*)
```

### Shortcuts

```bash
make s    # setup
make d    # dev
make t    # test
make m    # migrate
make f    # format
make l    # lint
make fb   # frontend-build
make fp   # frontend-production
make fw   # frontend-watch
make st   # static
make su   # superuser
```

### Docker (per-site)

```bash
make up           # docker compose up -d
make down         # docker compose down
make docker-logs  # docker compose logs -f
```

### Variant Management

Sites support feature variants (core, blog, lms, all):

```bash
make setup-core   # No LMS, No Blog
make setup-blog   # Blog only, No LMS
make setup-lms    # LMS only, No Blog
make setup-all    # Full (LMS + Blog)
```

---

## Python Package Management (uv)

The workspace uses **uv** for Python dependency management.

```bash
# Install all workspace dependencies
cd websites
uv sync

# Install for a specific site
cd websites/ctc-research.com
uv sync

# Run a command in the venv
uv run python manage.py check
uv run pytest

# Add a dependency (workspace level)
cd websites
uv add <package>

# Add a site-specific dependency
cd websites/ctc-research.com
uv add <package>
```

### Workspace Structure

```toml
# websites/pyproject.toml
[tool.uv.workspace]
members = ["ctc-research.com", "structa.cloud"]

[tool.uv.sources]
django-osoul = { git = "https://github.com/mammhoud/django-osoul", branch = "generic" }
django-rseal = { git = "https://github.com/mammhoud/django-rseal", branch = "generic" }
django-grep  = { git = "https://github.com/mammhoud/django-grep",  branch = "generic" }
```

Shared dependencies are declared in `websites/pyproject.toml`. Site-specific extras go in `websites/<site>/pyproject.toml`.

---

## Health Checks

```bash
# Root Makefile
make health-check           # runs scripts/health-check.sh

# Per-site
make check                  # Django system checks
make check-deploy           # Django deployment checks

# CLI
python websites/cli.py check structa.cloud
```

Health endpoint: `https://<domain>/health/` (provided by `django-grep`)

---

## Version Bumping

```bash
# Bump version across all pyproject.toml and __about__.py files
cd websites
bumpver update --patch    # 1.0.3 → 1.0.4
bumpver update --minor    # 1.0.3 → 1.1.0
bumpver update --major    # 1.0.3 → 2.0.0
```

`bumpver` is configured in `websites/pyproject.toml` and updates all three `pyproject.toml` files and both `__about__.py` files atomically.
