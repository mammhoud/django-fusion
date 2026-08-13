# 🏠 Repo Overview — Structa Cloud Monorepo

> Wide-angle view of the full repository environment: what it is, how it fits together, and how to build, deploy, and publish new projects.

---

## What This Repo Contains

The Structa Cloud monorepo is a **multi-project Django + Rust + TypeScript + Astro platform** that builds, deploys, and publishes multiple independent web applications, desktop apps, and AI services from a single codebase.

| Layer | Technology | Projects Using It |
|-------|-----------|-------------------|
| **Backend** | Python 3.11 + Django 5.2 + Wagtail 7.4 | Precis LMS, Landing-Fusion, Syntara, Formint Cloud |
| **Desktop** | Rust + Tauri 2.x | Formint Community, Formint Professional, Formint Client |
| **Frontend** | Astro 5 + TypeScript + Vue 3 + React 19 | Landing-Fusion, Formint editions, Syntara Chat |
| **AI** | Ollama + OpenAI-compatible + MCP | Syntara (CeptorAI) |
| **Infrastructure** | Docker + Traefik + Nginx + Coder | All projects |
| **Database** | PostgreSQL 16 (prod) / SQLite (dev) | All Django projects |
| **Build** | uv + pnpm + Cargo + Webpack | All projects |

---

## Quick Command Reference

### Project Dispatcher

```bash
cd projects
make check WEBSITE=lms-fusion         # Checks Precis LMS
make test WEBSITE=lms-fusion          # Tests Precis LMS
make run-dev WEBSITE=landing-fusion   # Landing-Fusion dev server
make check WEBSITE=landing-fusion
make test WEBSITE=landing-fusion
```

### Per-Product Commands

```bash
# Precis LMS
cd projects/precis/backend
make check && make test && make migrate

# Landing-Fusion
cd projects/landing-fusion
make install && make check && make build
make backend-migrate && make backend-check && make backend-test

# Formint Professional
cd projects/formints/formint
make install && make check && make test

# Formint Cloud
cd projects/formints/formint-cloud
make install && make check && make test

# Formint Community
cd projects/formints/formintA
pnpm install && pnpm tauri dev

# django-fusion library
cd libs/django-fusion
uv run pytest
```

### Docker Deployment

```bash
make deploy            # Full stack deploy (DB → media → apps → proxy)
make deploy-databases  # Postgres + Redis only
make deploy-app        # Django apps only
make deploy-proxy      # Traefik reverse proxy
make status            # Show all container statuses
make logs              # Tail all service logs
```

---

## Project Map

| Project | Dir | Type | Port | Stack |
|---------|-----|------|------|-------|
| **Precis LMS** | `projects/precis/` | Django Site | — | Wagtail + django-fusion |
| **Landing-Fusion** | `projects/landing-fusion/` | Astro + Django | 8074 | Wagtail + Astro 5 + Tailwind 4 |
| **Syntara** | `projects/syntara/` | Django Site | 5073 | AI Chat + CeptorAI + Ollama |
| **Formint Community** | `projects/formints/formintA/` | Tauri Desktop | — | Rust + React 19 + SQLite |
| **Formint Professional** | `projects/formints/formint/` | Tauri + Django | — | Astro + Django Ninja + Unfold |
| **Formint Cloud** | `projects/formints/formint-cloud/` | Django Server | 8767 | Django + Channels + Unfold |
| **Formint Client** | `projects/formints/formintC/` | Tauri Desktop | — | Tauri + Vue 3 + TypeScript |
| **django-fusion** | `libs/django-fusion/` | Python Package | — | Shared components (submodule) |

### Formint Edition Comparison

| Edition | Architecture | Sync | Admin |
|---------|-------------|------|-------|
| **Community** | Rust/Diesel + React 19 + SQLite | None (offline-first) | None |
| **Professional** | Django Ninja + Astro + Alpine/HTMX + Tauri | Sidecar sync | Unfold |
| **Cloud** | Full Django + Channels + WebSocket + Unfold | Multi-terminal SaaS | Unfold + Bolt |
| **Client** | Vue 3 + Tauri + Pinia | Via Cloud API | None |

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
        Precis    Landing   Syntara   Formint    shared-media
        LMS       Fusion    Chat      Cloud        :80
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

## Multi-Project Philosophy

This monorepo is designed to **build, deploy, and publish multiple independent products** from shared infrastructure:

1. **Single toolchain** — `uv` for Python, `pnpm` for frontend, `Cargo` for Rust
2. **Shared settings** — `projects/configs/` provides base Django config reused across sites
3. **Shared assets** — `projects/assets/` has cross-site templates, static files, locale
4. **Shared framework** — `libs/django-fusion/` provides components, routing, fragments
5. **Shared infrastructure** — One Traefik proxy, one Nginx media server, one Postgres cluster
6. **Per-site isolation** — Each site has its own container, port, database, and domain

---

## Directory Reference

```
structa.cloud/
├── projects/              # All Django + desktop projects
│   ├── Makefile           # Canonical dispatcher (WEBSITE= selection)
│   ├── configs/           # Shared Django settings
│   ├── assets/            # Shared static/templates/locale
│   ├── precis/            # Precis LMS
│   ├── landing-fusion/    # Landing-Fusion marketing site
│   ├── syntara/           # Cypercloud AI chat platform
│   └── formints/          # Multi-edition POS platform
├── libs/                  # Reusable Python packages (git submodules)
│   └── django-fusion/     # Component system + routing
├── applications/          # Infrastructure + tooling
│   ├── proxy/             # Traefik reverse proxy
│   ├── databases/         # Postgres + Redis compose
│   ├── templates/         # Coder/Terraform workspace templates
│   └── agents/            # Kilo MCP server
├── docs/                  # Documentation (docsify)
│   ├── assets/            # Screenshots and previews
│   ├── projects/          # Per-project docs
│   ├── guides/            # Developer guides
│   └── ai/                # AI agents + prompts
├── tests/                 # Workspace-level test suite
├── .agents/               # AI agent skills and configuration
├── .github/               # CI/CD workflows
├── Makefile               # Root dispatcher
└── pyproject.toml         # Workspace config (uv + pytest + ruff)
```

---

## Name Migration Reference

The codebase has been through several renames. See this guide for mapping old names to current:

| Legacy Name | Current Name | Current Path |
|---|---|---|
| `ctc-research` | **Precis LMS** | `projects/precis/` |
| `lms-fusion` | **Precis LMS** (alias) | `projects/precis/` |
| `cms-fusion` | Merged into Precis + Landing-Fusion | — |
| `cypercloud` | **Syntara** (runtime alias preserved) | `projects/syntara/` |
| `portfolio` / `VResume` | Merged into Precis | `projects/precis/` |
| `pos-mini` / `forge-pos` | **Formint Community** | `projects/formints/formintA/` |
| `pos-solo` / `pos-full` | **Formint Professional** (merged) | `projects/formints/formint/` |
| `pos-cloud` / `formintB` | **Formint Cloud** | `projects/formints/formint-cloud/` |
| `pos-client` / `formintC` | **Formint Client** | `projects/formints/formintC/` |
| `core/` | `projects/` | `projects/` |
| `core/libs/` | `libs/` | `libs/` |

> ⚠️ **Use current names in new code.** Legacy names may appear in migration docs or compatibility manifests but should not be used for new source paths.

---

## Related Docs

| Topic | Path |
|-------|------|
| Setup guide | [`guides/01-setup.md`](guides/01-setup.md) |
| Clone a site | [`guides/06-clone-site.md`](guides/06-clone-site.md) |
| Deployment guide | [`guides/04-deploy.md`](guides/04-deploy.md) |
| Infrastructure | [`dev/infrastructure/`](dev/infrastructure/) |
| django-fusion reference | [`libs/django-fusion.md`](libs/django-fusion.md) |
| AI agents & prompts | [`ai/agents.md`](ai/agents.md) |
| Formint editions | [`pos/editions.md`](pos/editions.md) |
