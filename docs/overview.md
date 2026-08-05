# 🏠 Repo Overview — Structa Cloud Monorepo

> Wide-angle view of the full repository environment: what it is, how it fits together, and how to build, deploy, and publish new projects.

---

## What This Repo Contains

The Structa Cloud monorepo is a **multi-project Django + Rust + TypeScript platform** that builds, deploys, and publishes multiple independent web applications, desktop apps, and AI services from a single codebase.

| Layer | Technology | Projects Using It |
|-------|-----------|-------------------|
| **Backend** | Python 3.11 + Django 5.1 | LMS, Portfolio, Cypercloud, CTC Research |
| **Desktop** | Rust + Tauri 2.x | POS (Minimal / Solo / Full) |
| **Frontend** | TypeScript 5.8 + Vue 3 + React 19 | POS Client, Cypercloud Chat |
| **AI** | Ollama + OpenAI-compatible + MCP | Cypercloud (CeptorAI) |
| **Infrastructure** | Docker + Traefik + Nginx + Coolify | All projects |
| **Database** | PostgreSQL 16 (prod) / SQLite (dev) | All Django projects |
| **Build** | Webpack + Cargo + uv | All projects |

---

## Quick Command Reference

### Git & Repo Sync

```bash
make push              # Push repo + lib submodules to GitHub
make push-libs         # Push only lib submodules (django-fusion, ceptor-ai)
make push-lib LIB=django-fusion  # Push a single lib
make pull              # Fetch + fast-forward/rebase from origin
make sync              # Pull then push in one step
```

### Development

```bash
make venv-setup        # Create unified .venv at repo root (uv sync)
make venv-sync         # Sync deps only (faster)
make venv-info         # Show venv status
cd projects && make dev WEBSITE=lms   # Run LMS dev server
cd projects && make check WEBSITE=lms  # Django system checks
make pos               # POS dev targets
make cypercloud        # Cypercloud dev targets
```

### Docker Deployment

```bash
make deploy            # Full stack deploy (DB → media → apps → proxy)
make deploy-databases  # Postgres + Redis only
make deploy-app        # Django apps only
make deploy-proxy      # Traefik reverse proxy
make deploy-tasks      # Dramatiq worker + Celery scheduler
make deploy-cypercloud # Cypercloud build + migrate
make status            # Show all container statuses
make logs              # Tail all service logs
make stop              # Stop all services
make restart           # Stop then redeploy all
```

### Build & Publish Pipeline

```bash
make build             # Build all Docker images
make build-app         # Build Django app images
make build-media       # Build Nginx media server
make build-cypercloud  # Build Cypercloud webpack bundles
```

---

## Project Map

| Project | Dir | Type | Port | Stack |
|---------|-----|------|------|-------|
| **LMS** | `projects/lms/` | Django Site | 5071 | Wagtail + django-fusion |
| **Portfolio** | `projects/portfolio/` | Django Site | 5072 | Wagtail + Resume Builder |
| **Cypercloud** | `projects/cypercloud/` | Django Site | 5073 | AI Chat + CeptorAI + Ollama |
| **CTC Research** | `projects/ctc-research/` | Django Site | 5070 | Research Portal (merged into LMS) |
| **POS** | `projects/pos/` | Tauri Desktop | — | Rust + Vue 3 + SQLite |
| **Shared** | `projects/www/` | Shared Core | — | Shared Django code + workers across sites |
| **Libs** | `libs/` | Python Packages | — | django-fusion, ceptor-ai |

### Sub-Projects (POS Variants)

| Variant | Dir | Description |
|---------|-----|-------------|
| **POS Minimal** | `projects/pos/pos-minimal/` | Bare-bones Tauri + Rust backend |
| **POS Solo** | `projects/pos/pos-solo/` | Standalone with embedded sidecar API |
| **POS Full** | `projects/pos/pos-full/` | Multi-terminal with external sidecar server |

---

## Infrastructure Architecture

```
                  ┌──────────────────────────────────┐
                  │         Traefik Proxy :443        │
                  │   (Let's Encrypt SSL, auto-cert)  │
                  └────┬──────┬──────┬──────┬────────┘
                       │      │      │      │
           ┌───────────┼──────┼──────┼──────┼───────────┐
           │           │      │      │      │           │
     ctc-research    LMS  portfolio  cypercloud   shared-media
       :5070        :5071    :5072     :5073        :80
           │           │      │      │      │           │
           └───────────┴──────┴──────┴──────┴───────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              PostgreSQL 16        Redis (broker)
              (per-site DBs)     (shared-worker queue)
```

### Docker Networks

| Network | Purpose |
|---------|---------|
| `common` | Inter-container comms for Django apps + workers |
| `traefik-net` | Proxy ↔ backend routing |
| `internal` | DB ↔ app private channel |
| `utilities-net` | Monitoring stack |
| `warehouse-net` | POS sync services |
| `ollama-net` | AI model inference |

---

## Build & Publish New Project — Pipeline

### 1. Clone a Template

```bash
cd projects
make clone-site WEBSITE=new-project SOURCE_SITE=lms
```

This copies the LMS structure (or any source) as a starting point for a new Django site.

### 2. Configure the Site

Edit `projects/new-project/configs/settings.yml`:
- Set `SITE_ID`, `ALLOWED_HOSTS`, database connection
- Enable plugins: accounts, blog, courses, etc.

### 3. Register in Traefik

Add a router in `applications/proxy/traefik/dynamic/`:
```yaml
http:
  routers:
    new-project:
      rule: "Host(`new-project.structa.cloud`)"
      service: new-project
      tls:
        certResolver: letsencrypt
  services:
    new-project:
      loadBalancer:
        servers:
          - url: "http://new-project-web:5080"
```

### 4. Add Docker Compose

Create `projects/new-project/docker-compose.yml` with the standard Django + Gunicorn setup.

### 5. Deploy

```bash
make deploy-app    # The new site starts alongside existing ones
```

---

## Directory Reference

```
structa.cloud/
├── projects/              # All Django + desktop projects
│   ├── Makefile           # Canonical dispatcher (WEBSITE= selection)
│   ├── configs/           # Shared Django settings
│   ├── assets/            # Shared static/templates/locale
│   ├── compose/           # Dockerfiles + shared compose
│   ├── www/               # Shared Django core code
│   ├── lms/               # LMS site
│   ├── portfolio/         # Portfolio site
│   ├── cypercloud/        # AI chat platform
│   ├── ctc-research/      # Research portal
│   └── pos/               # POS Tauri desktop app
├── libs/                  # Reusable Python packages (git submodules)
│   ├── django-fusion/     # Component system + routing
│   └── ceptor-ai/         # AI client library
├── applications/          # Infrastructure + tooling
│   ├── proxy/             # Traefik reverse proxy
│   ├── databases/         # Postgres + Redis compose
│   └── scripts/           # Automation scripts
├── docs/                  # Documentation (mkdocs)
│   ├── projects/          # Per-project docs
│   ├── guides/            # Developer guides
│   ├── infrastructure/    # Infra docs
│   └── ai/                # AI agents + prompts
├── tests/                 # Workspace-level test suite
├── .venv/                 # Unified Python venv (git-ignored)
├── Makefile               # Root dispatcher
└── pyproject.toml         # Workspace config (uv + pytest + ruff)
```

---

## Multi-Project Philosophy

This monorepo is designed to **build, deploy, and publish multiple independent products** from shared infrastructure:

1. **Single venv** — One `.venv` at repo root serves ALL local development
2. **Shared settings** — `projects/configs/` provides base Django config reused across sites
3. **Shared assets** — `projects/assets/` has cross-site templates, static files, locale
4. **Shared infrastructure** — One Traefik proxy, one Nginx media server, one Postgres cluster
5. **Per-site isolation** — Each site has its own container, port, database, and domain

Adding a new project requires: Django site scaffold → Traefik router → Docker Compose → deploy.

---

## Related Docs

| Topic | Path |
|-------|------|
| Clone a site | [`guides/06-clone-site.md`](guides/06-clone-site.md) |
| Deployment guide | [`guides/04-deploy.md`](guides/04-deploy.md) |
| Infrastructure | [`infrastructure/`](infrastructure/) |
| Project index | [`projects/`](projects/) |
| AI platform plan | [`projects/cypercloud/platform-plan.md`](projects/cypercloud/platform-plan.md) |
