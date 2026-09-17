---
title: Repository overview
description: The wide-angle map of Structa Cloud products, infrastructure, commands, and data flow.
navigation:
  title: Repository overview
  icon: i-lucide-map
object:
  type: "architecture"
  id: "docs.overview"
attributes:
  source_path: "overview.md"
  canonical_route: "/docs/en/overview"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
tags:
  - structa-cloud
  - architecture
  - project-awareness
  - commands
links:
  - label: "Project awareness"
    to: "/guides/00-project-awareness"
    icon: "i-lucide-compass"
  - label: "Full architecture"
    to: "/architecture"
    icon: "i-lucide-landmark"
---

# 🏠 Repo Overview — Structa Cloud Monorepo

> Wide-angle view of the full repository environment: what it is, how it fits together, and how to build, deploy, and publish new projects.

<!-- AI-generated: review needed -->

> **Canonical orientation:** [`guides/00-project-awareness.md`](guides/00-project-awareness.md) explains the object graph, source-of-truth rules, commands, and Docus metadata model.

---

## What This Repo Contains

The Structa Cloud monorepo is a **multi-project Django + Rust + TypeScript + Astro platform** that builds, deploys, and publishes multiple independent web applications, desktop apps, and AI services from a single codebase.

| Layer | Technology | Projects Using It |
|-------|-----------|-------------------|
| **Backend** | Python 3.11 + Django 5.2 + Wagtail 7.4 | Precis LMS, Precis Landing, Syntara, Formint Cloud |
| **Desktop** | Rust + Tauri 2.x | Formint Community, Formint Professional, Formint Client |
| **Frontend** | Astro 5 + TypeScript + Vue 3 + React 19 | Precis Landing, Formint editions, Syntara Chat |
| **AI** | Ollama + OpenAI-compatible + MCP | Syntara (CeptorAI) |
| **Infrastructure** | Docker + Traefik + Nginx + Coder | All projects |
| **Database** | PostgreSQL 16 (prod) / SQLite (dev) | All Django projects |
| **Build** | uv + package-local npm/pnpm + Cargo + Webpack | All projects |

---

## Quick Command Reference

### Project Dispatcher

```bash
cd projects
make check WEBSITE=structa.cloud         # Checks Precis LMS
make test WEBSITE=structa.cloud          # Tests Precis LMS
make run-dev WEBSITE=precis-landing   # Precis Landing dev server
make check WEBSITE=precis-ctc         # CTC Research backend/frontend checks
make check WEBSITE=precis-landing
make test WEBSITE=precis-landing
```

### Per-Product Commands

```bash
# Precis LMS
cd projects/structa.cloud/backend
make check && make test && make migrate

# Precis Landing
cd projects/precis/precis-landing
just install && make check && make build
make backend-migrate && make backend-check && make backend-test

# Formint Professional
cd projects/formints/formint-pro
just install && make check && make test

# Formint Cloud
cd projects/formints/formint-cloud
just install && make check && make test

# Formint Community
cd projects/formints/formint-community
pnpm install && pnpm tauri dev

# CTC Research
cd projects/precis/precis-ctc
make check && make test

# Docus documentation
cd docs
make check && make build

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
| **Precis (unified LMS + landing)** | `projects/structa.cloud/` | Astro + Django | backend 8074 · frontend 3000 (Docker) | Wagtail + Astro 5 + django-fusion |
| **Precis Landing** | `projects/precis/precis-landing/` | Legacy compatibility copy | — | Historical source; runtime maps to Precis Main |
| **CTC Research** | `projects/precis/precis-ctc/` | Django Site | — | Wagtail + django-fusion |
| **Syntara** | `projects/syntara/` | Django Site | 5073 | AI Chat + CeptorAI + Ollama |
| **Loop-CRM** | `projects/loop-crm/` | Django + Astro | 8000 | django-fusion + React islands |
| **Formint Community** | `projects/formints/formint-community/` | Tauri Desktop | — | Rust + React 19 + SQLite |
| **Formint Standard** | `projects/formints/formint-standard/` | Tauri + Astro | — | Tauri + FlyonUI |
| **Formint Professional** | `projects/formints/formint-pro/` | Tauri + Django | — | Astro + Django + Unfold |
| **Formint Cloud** | `projects/formints/formint-cloud/` | Django Server | 8767 | Django + Channels + Unfold |
| **Formint Client** | `projects/formints/formint-client/` | Tauri Desktop | — | Tauri + Vue 3 + TypeScript |
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
        Precis    Landing   Syntara   Formint    shared-proxy
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
2. **Shared settings** — `projects/precis/configs/` provides base Django config reused across Precis sites
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
│   ├── assets/            # Shared static/templates/locale
│   ├── precis/            # Precis group (precis-main, precis-landing, precis-ctc)
│   │   ├── precis-main/   #   Precis LMS
│   │   ├── precis-landing/   #   Precis Landing marketing site
│   │   ├── precis-ctc/    #   CTC Research
│   │   └── configs/       #   Shared Django settings
│   ├── syntara/           # Syntara AI chat platform
│   ├── loop-crm/          # Loop-CRM unified CRM
│   └── formints/          # Multi-edition POS (community/standard/pro/cloud/client)
├── libs/                  # Reusable Python packages (git submodules)
│   └── django-fusion/     # Component system + routing
├── application/          # Infrastructure + tooling
│   ├── proxy/             # Traefik reverse proxy
│   ├── databases/         # Postgres + Redis compose
│   ├── templates/         # Coder/Terraform workspace templates
│   └── agents/            # Kilo MCP server
├── docs/                  # Documentation (Docus + Nuxt Content)
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
| `precis-ctc` / `ctc` | **CTC Research** | `projects/precis/precis-ctc/` |
| `precis-lms` / `lms` | **Precis LMS** (alias) | `projects/structa.cloud/` |
| `precis-landing` | **Precis Landing** | `projects/precis/precis-landing/` |
| `cms-fusion` | Merged into Precis + Precis Landing | — |
| `cypercloud` | **Syntara** (runtime alias preserved) | `projects/syntara/` |
| `portfolio` / `VResume` | Merged into Precis | `projects/structa.cloud/` |
| `pos-mini` / `forge-pos` / `formintA` / `formint-community` | **Formint Community** | `projects/formints/formint-community/` |
| `formint-standard` | **Formint Standard** | `projects/formints/formint-standard/` |
| `pos-solo` / `pos-full` / `formint` / `formint-pro` | **Formint Professional** (merged) | `projects/formints/formint-pro/` |
| `pos-cloud` / `formintB` / `formint-cloud` | **Formint Cloud** | `projects/formints/formint-cloud/` |
| `pos-client` / `formintC` / `formint-client` | **Formint Client** | `projects/formints/formint-client/` |
| `core/` | `projects/` | `projects/` |
| `core/libs/` | `libs/` | `libs/` |
| `core/configs/` | Shared Django settings | `projects/precis/configs/` |

> ⚠️ **Use current names in new code.** Legacy names may appear in migration docs or compatibility manifests but should not be used for new source paths.

## Remarks & Notes

- Use `docs/guides/00-project-awareness.md` as the operational index; this overview intentionally stays wide-angle.
- Treat `projects/Makefile`, product `AGENTS.md`, and product Makefiles as executable sources of truth for paths and commands.
- The diagrams describe request and build boundaries; verify route names and service names against the owning configuration before operating on them.

---

## Related Docs

| Topic | Path |
|-------|------|
| Project awareness and commands | [`guides/00-project-awareness.md`](guides/00-project-awareness.md) |
| Setup guide | [`guides/01-setup.md`](guides/01-setup.md) |
| Clone a site | [`guides/06-clone-site.md`](guides/06-clone-site.md) |
| Deployment guide | [`guides/04-deploy.md`](guides/04-deploy.md) |
| Infrastructure | [`dev/infrastructure/`](dev/infrastructure/) |
| django-fusion reference | [`libs/django-fusion.md`](libs/django-fusion.md) |
| AI agents & prompts | [`ai/agents.md`](ai/agents.md) |
| Formint editions | [`pos/editions.md`](pos/editions.md) |
