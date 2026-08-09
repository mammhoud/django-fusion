# Structa Cloud — Documentation

> ⭐ **Start here:** read [Recommendations first](recommendations.md), then open the relevant guide, project reference, or implementation plan.

> ⚡ **New here?** Start with [Backend Environment](back-env/) — it covers env setup for all projects.

## Documentation ownership

| Need | Canonical location |
|---|---|
| Recommended priorities and sequencing | [`recommendations.md`](recommendations.md) |
| Engineering plans and implementation tasks | [`plans/`](plans/README.md) |
| Product decisions and knowledge-graph objects | `Anytype/` when present |
| Current project, architecture, development, and deployment references | The topic/project sections below |
| Historical plan evidence | [`plans/legacy/`](plans/legacy/) |

All new plans must be added under `docs/plans/<scope>/` and linked from the canonical plan registry. The old `docs/dev/plans/`, `docs/plans/migrated/`, and project-local `docs/superpowers/plans/` locations are no longer active authoring paths.

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
├── projects/                         # Django monorepo and product projects
├── applications/                     # Infrastructure and tooling
├── tests/                            # Integration and E2E tests
└── docs/                             # This documentation project
    ├── recommendations.md            # Read first: priorities and decisions
    ├── plans/                        # Single active plan registry
    │   ├── editions/                 # Formint edition execution chain
    │   └── legacy/                   # Read-only historical evidence
    ├── projects/                     # Current per-project references
    ├── infrastructure/               # Proxy, DB, deployment, workers
    ├── ai/                           # Agents, prompts, MCP
    └── guides/                       # Step-by-step workflows
```

## Platform Documentation

| Platform | Directory | Covers |
|---|---|---|
| 🦀 **Rust** | [`docs/rust/`](rust/) | POS auth, operations, database schema, email |
| ⚛️ **TypeScript** | [`docs/typescript/`](typescript/) | POS API layer, components, contexts, hooks |
| 🐍 **Python/Django** | [`docs/python/`](python/) | Django sites, libs, templates, fusion components |
| 🏗️ **Infrastructure** | [`docs/infrastructure/`](infrastructure/) | Proxy, databases, workers, Docker Compose, deployment |
| 🌐 **Server** | [`docs/server/`](server/) | Sanic sidecar, REST endpoints, WebSocket |

## Sites & Projects at a Glance

| Project | Directory | Port | Stack | Domain |
|---|---|:---:|---|---|
| **CTC Research** | `projects/ctc-research/` | 5070 | Django + Wagtail | ctc-research.com |
| **LMS** | `projects/lms/` | 5071 | Django + Wagtail + LMS | structa.cloud |
| **VResume** | `projects/portfolio/` | 5072 | Django + Wagtail | vresume.structa.cloud |
| **Cypercloud** | `projects/cypercloud/` | 5073 | Django + AI Chat | localhost |
| **POS** | `projects/pos/` | — | Tauri 2 + React + Rust | Desktop app |
| **WWW (Shared Core)** | `projects/www/` | 5080 | Celery + Dramatiq | sentinel site |
| **Libs** | `libs/` | — | Python packages | submodules |

Each project has a dedicated documentation page in [`docs/projects/`](projects/) with development, configuration, and deployment references where available.

## Quick Links

- [⭐ Recommendations first](recommendations.md)
- [📚 Guides](guides/) — step-by-step tutorials
- [🗺️ Canonical plans](plans/README.md) — all active plans and historical evidence
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
- [🏢 Sites & Projects](projects/)
- [🏛️ Core Architecture](core/)
- [📦 Publishing](publish/) — marketplace & distribution
- [🤖 Agents](ai/) — AI agent instructions
- [📐 Best Practices](best-practices/) — Markdown conventions & usage

## Related

- [`../README.md`](../README.md) — repository overview and quick start
- [`recommendations.md`](recommendations.md) — recommended priorities
- [`plans/README.md`](plans/README.md) — canonical plan registry
- [`plans/document-lifecycle.md`](plans/document-lifecycle.md) — archive/delete policy
