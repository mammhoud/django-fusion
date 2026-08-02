# Structa Cloud — Documentation

> ⚡ **New here?** Start with [Backend Environment](back-env/) — it covers env setup for all projects.

## Project Tree (Language → Directory → Project)

| Language | Directory | Projects |
|----------|-----------|----------|
| 🦀 **Rust** | `docs/rust/` | POS backend (Tauri + Diesel + SQLite) |
| ⚛️ **TypeScript** | `docs/typescript/` | POS frontend (React 19 + Vite + i18next) |
| 🐍 **Python/Django** | `docs/python/` | Django core, sites, libs, fusion components |
| 🐍 **Python/Sanic** | `docs/server/` | POS sidecar (REST + WebSocket API) |
| 🏗️ **Docker/YAML** | `docs/infrastructure/` | Proxy, databases, Compose, deployment |
| ⚙️ **Config/Env** | `docs/back-env/` | Backend env vars, settings, site registry |
| 🗄️ **SQL** | `docs/databases/` | SQLite schema, PostgreSQL, migrations |
| 🧪 **All** | `docs/tests/` | Testing: Vitest, Rust, pytest, Selenium, E2E |

## Project Tree

```
structa.cloud/
├── projects/                         # Django monorepo
│   ├── configs/                      # Shared Django settings
│   │   ├── base/                     # Base configuration modules
│   │   └── settings/                 # Environment/site settings (YAML)
│   ├── assets/                       # Shared frontend assets
│   │   ├── templates/                # Cross-site Django templates
│   │   ├── static/                   # Shared static files (CSS, JS, images)
│   │   └── locale/                   # Shared translation files
│   ├── www/                          # Shared/core Django code (merged)
│   │   ├── __main__.py               # CLI entry for www sentinel site
│   │   ├── settings.py               # Django config for shared-task stack
│   │   ├── ci/                       # CI/CD preflight utilities
│   │   │   └── utils.py              # Deploy-preflight helpers
│   │   └── worker/                   # Celery + Dramatiq tasks
│   │       ├── celery.py             # Celery app bootstrap
│   │       ├── tasks.py              # Heartbeat & shared tasks
│   │       ├── email.py              # Dramatiq email actors
│   │       ├── content.py            # Content management actors
│   │       ├── decorators.py         # Task decorators
│   │       ├── runtime.py            # Runtime helpers
│   │       ├── modules.py            # Task module registry
│   │       └── apps.py               # Django AppConfig
│   ├── libs/                         # Local reusable libraries
│   │   ├── django-fusion/            # Component system + routing framework
│   │   └── ceptor-ai/                # AI assistant & MCP server
│   ├── ctc-research/                 # CTC Research site (port 5070)
│   ├── lms/                          # LMS Demo site (port 5071)
│   ├── VResume/                      # VResume site (port 5072)
│   ├── cypercloud/                   # AI Chat Customizer (port 5073)
│   └── pos/                          # Desktop POS app (Tauri 2 + Rust)
│       ├── src/                      # React/TypeScript frontend
│       ├── src-tauri/                # Rust/Tauri backend
│       ├── sidecar/                  # Python/Sanic sidecar server
│       └── docs/                     # POS specific docs
│
├── applications/                     # Infrastructure & tooling
│   ├── proxy/                        # Traefik reverse proxy + SSL
│   ├── databases/                    # Database containers (Postgres, Redis)
│   ├── compose/                      # Docker Compose orchestration
│   │   ├── docker-compose.tasks.yml  # Shared-worker stack
│   │   ├── docker-compose.docs.yml   # Documentation site
│   │   └── docker-compose.applications.yml  # Site services
│   └── scripts/                      # Shared build + automation scripts
│
├── tests/                            # Integration & E2E tests
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   ├── selenium/                     # Selenium browser tests
│   ├── http/                         # HTTP API tests
│   └── fixtures/                     # Test fixtures (JSON)
│
├── docs/                             # ← You are here
│   ├── README.md                     # This file
│   ├── rust/                         # Rust/Diesel/Tauri backend docs
│   ├── typescript/                   # TypeScript/React frontend docs
│   ├── python/                       # Python/Django backend docs
│   ├── infrastructure/               # Proxy, DB, deployment, workers
│   ├── server/                       # Sidecar/Sanic server docs
│   ├── core/                         # Core architecture docs
│   ├── sites/                        # Per-site documentation
│   └── getting-started/              # Quick-start guides
```

## Platform Documentation

| Platform | Directory | Covers |
|----------|-----------|--------|
| 🦀 **Rust** | [`docs/rust/`](rust/) | POS auth, operations, database schema, email |
| ⚛️ **TypeScript** | [`docs/typescript/`](typescript/) | POS API layer, components, contexts, hooks |
| 🐍 **Python/Django** | [`docs/python/`](python/) | Django sites, libs, templates, fusion components |
| 🏗️ **Infrastructure** | [`docs/infrastructure/`](infrastructure/) | Proxy, databases, workers, Docker Compose, deployment |
| 🌐 **Server** | [`docs/server/`](server/) | Sanic sidecar, REST endpoints, WebSocket |

## Sites & Projects at a Glance

| Project | Directory | Port | Stack | Domain |
|---------|-----------|------|-------|--------|
| **CTC Research** | `projects/ctc-research/` | 5070 | Django + Wagtail | ctc-research.com |
| **LMS** | `projects/lms/` | 5071 | Django + Wagtail + LMS | structa.cloud |
| **VResume** | `projects/portfolio/` | 5072 | Django + Wagtail | vresume.structa.cloud |
| **Cypercloud** | `projects/cypercloud/` | 5073 | Django + AI Chat | localhost |
| **POS** | `projects/pos/` | — | Tauri 2 + React + Rust | Desktop app |
| **WWW (Shared Core)** | `projects/www/` | 5080 | Celery + Dramatiq | sentinel site |
| **Libs** | `libs/` | — | Python packages | submodules |

Each project has a dedicated documentation page in [`docs/sites/`](sites/) with:
- **Guide** — Development commands and workflows
- **Code Map** — Key files with paths and customization tags
- **Remarks** — Notable gotchas, tips, and warnings
- **Customization Key** — What's 🟢/🔴/🟡/🔵/⚪ per project

### Project Documentation Pages

| Page | Covers |
|------|--------|
| [`CTC Research`](sites/ctc-research.md) | CMS, auth, blog, LMS, profile, components |
| [`LMS`](sites/lms.md) | Learning, courses, certifications, payments |
| [`VResume`](sites/portfolio.md) | Resume builder, portfolio, blog, PDF export |
| [`Cypercloud`](sites/cypercloud.md) | AI chat, template discovery, code editor |
| [`POS`](sites/pos.md) | Desktop POS, Tauri, Rust, React, sidecar |
| [`WWW (Shared Core)`](sites/www.md) | Task workers, Celery, Dramatiq, CI utils |
| [`Libs`](sites/libs.md) | django-fusion, ceptor-ai libraries |

## Customization Key (used throughout docs)

| Tag | Meaning |
|-----|---------|
| 🟢 `customizable` | Safe to modify, extend, or override |
| 🔴 `not-customizable` | Core framework code — modify at your own risk |
| 🟡 `delegate` | Can be extended through delegation/hooks |
| 🔵 `template` | Template-level customization only |
| ⚪ `config` | Configured via settings/env vars only |

## Quick Links

- [📚 Guides](guides/) — step-by-step tutorials
- [🗺️ Plans](plans/) — consolidated implementation plans and status
- [🚀 Getting Started](getting-started/)
- [🔄 Recent Changes](recent-changes.md)
- [🎯 Features Index](features/) — capabilities by project
- [🔧 Backend Environment](back-env/)
- [🦀 Rust Backend (POS)](rust/)
- [⚛️ TypeScript Frontend (POS)](typescript/)
- [🐍 Python/Django Core](python/)
- [🏗️ Infrastructure & Deployment](infrastructure/)
- [🌐 Sidecar Server](server/)
- [🗄️ Databases](databases/)
- [🧪 Testing](tests/)
- [🏢 Sites & Projects](sites/)
- [🏛️ Core Architecture](core/)
- [📦 Publishing](publish/) — marketplace & distribution
- [🤖 Agents](agents/) — AI agent instructions
- [💬 Prompts](prompts/) — prompt engineering
- [📐 Best Practices](best-practices/) — Markdown conventions & usage

## Code-Level READMEs

Simple READMEs at key code locations for quick on-the-spot guidance:

| Location | Links to |
|----------|----------|
| `projects/shared/README.md` | → Shared core docs & [`docs/sites/www.md`](sites/www.md) |
| `projects/shared/shared-methods.md` | → Worker task docs |
| `projects/configs/README.md` | → `docs/back-env/` |
| `projects/pos/src/api/README.md` | → `docs/typescript/api.md` |
| `projects/pos/src/components/README.md` | → `docs/typescript/components.md` |
| `projects/pos/sidecar/README.md` | → `docs/server/` |
| `applications/proxy/README.md` | → `docs/infrastructure/proxy.md` |
| `libs/django-fusion/README.md` | → django-fusion docs & [`docs/sites/libs.md`](sites/libs.md) |
| `libs/ceptor-ai/README.md` | → ceptor-ai docs & [`docs/sites/libs.md`](sites/libs.md) |
| `projects/cypercloud/README.md` | → AI Chat Customizer & [`docs/sites/cypercloud.md`](sites/cypercloud.md) |

---

*Structa Cloud — https://structa.cloud*
