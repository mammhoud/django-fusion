# Structa Cloud — Documentation

> ⭐ **Start here:** read [Recommendations first](recommendations.md), then open the relevant guide, project reference, or implementation plan.

> ⚡ **New here?** Start with [Guides](guides/) — numbered walkthroughs for setup, auth, dev, deployment, and customization.

## Current Products

| Product | Canonical Path | Main Responsibility | Domain |
|---|---|---|---|
| **Precis LMS** | `projects/precis/precis-lms/` | Django/Wagtail learning platform: courses, enrollment, progress, profiles, content | structa.cloud |
| **Landing-Fusion** | `projects/precis/precis-landing/` | Public marketing/catalog site; Astro frontend and Django/Wagtail backend | structa.cloud |
| **Syntara** (Cypercloud) | `projects/syntara/` | AI chat, template discovery, code customization, streaming responses | — |
| **Formint POS** | `projects/formints/` | Multi-edition restaurant POS: Community, Professional, Cloud, Client | — |
| **django-fusion** | `libs/django-fusion/` | Shared Django/Wagtail components, routing, fragments, forms, tables | submodule |
| **Infrastructure** | `applications/` | PostgreSQL, Redis, Traefik/Nginx, Compose, deployment and MCP tooling | structa.cloud |
| **Workspace tests** | `tests/` | Cross-project validation, fixtures, browser tests, deployment checks | — |

## Documentation ownership

| Need | Canonical location |
|---|---|
| Recommended priorities and sequencing | [`recommendations.md`](recommendations.md) |
| Engineering plans and implementation tasks | [`plans/`](plans/README.md) |
| Product decisions and knowledge-graph objects | `Anytype/` when present |
| Current project, architecture, development, and deployment references | The topic/project sections below |

All new plans must be added under `docs/plans/<scope>/` and linked from the canonical plan registry. The old `docs/dev/plans/`, `docs/plans/migrated/`, and project-local `docs/superpowers/plans/` locations are no longer active authoring paths.

## Repository Structure

```
structa.cloud/
├── projects/                         # Product code, shared Django config, and assets
│   ├── precis/                       # Product grouping: LMS, research, marketing
│   │   ├── main/                     # Precis LMS — learning platform
│   │   │   ├── backend/              # Django + Wagtail backend
│   │   │   ├── assets/               # Templates, static, SCSS, media
│   │   │   └── frontend/             # Astro frontend shell
│   │   ├── precis-ctc/             # Medical research center site
│   │   └── landi/                    # Astro marketing site + Django/Wagtail CMS
│   │       ├── backend/              # Django + Wagtail backend
│   │       ├── frontend/             # Astro frontend
│   │       └── assets/               # Project assets
│   ├── syntara/                      # Cypercloud AI chat/customizer runtime
│   ├── formints/                     # Multi-edition POS platform
│   │   ├── formint-community/        # Community (Tauri + React + Rust)
│   │   ├── formint-pro/              # Professional (Astro + Django + Tauri)
│   │   ├── formint-cloud/            # Cloud master (Django + Channels)
│   │   ├── formint-standard/         # Standard edition (Astro + Tauri)
│   │   ├── formint-client/           # POS Client (Tauri + Vue 3)
│   │   ├── tests/                    # Shared POS tests
│   │   └── docs/                     # POS architecture docs
│   ├── configs/                      # Shared Django settings and workers
│   ├── assets/                       # Monorepo-level shared assets
│   ├── scripts/                      # Project-local automation
│   ├── Makefile                      # Canonical project dispatcher
│   └── pyproject.toml                # Python workspace dependencies
├── libs/                             # Reusable libraries
│   └── django-fusion/                # Shared Django/Wagtail components (submodule)
├── applications/                     # Databases, proxy, Compose, scripts, Kilo/MCP
│   ├── proxy/                        # Traefik reverse proxy configs
│   ├── databases/                    # PostgreSQL + Redis compose
│   ├── agents/                       # Kilo MCP server
│   ├── templates/                    # Coder/Terraform templates
│   └── scripts/                      # Automation scripts
├── tests/                            # Workspace integration, HTTP, browser, fixtures
├── docs/                             # This documentation project
│   ├── assets/                       # Screenshots, previews, diagrams
│   │   ├── screenshots/formints/     # Formint admin + frontend screenshots
│   │   └── previews/formints/        # Formint product preview images
│   ├── guides/                       # Step-by-step numbered walkthroughs
│   ├── plans/                        # Single active plan registry
│   ├── projects/                     # Current per-project references
│   ├── ai/                           # Agents, prompts, MCP
│   └── design/                       # Design system and branding
├── .agents/                          # AI agent skills and configuration
│   ├── skills/                       # Reusable skill definitions (21 skills)
│   └── kiro/settings/                # MCP server configuration
├── .github/                          # CI workflows and composite actions
├── Makefile                          # Root deployment and delegation entry point
└── pyproject.toml                    # Root Python/tooling configuration
```

## Quick Links

- [⭐ Recommendations first](recommendations.md)
- [🛠️ Project Setup & Build Guides](setup-guides.md) — per-project setup/build indexes
- [📚 Guides](guides/) — step-by-step tutorials
- [🗺️ Canonical plans](plans/README.md) — all active plans and historical evidence
- [🔄 Recent Changes](recent-changes.md)
- [🎯 Features Index](features/) — capabilities by project
- [🏗️ Infrastructure & Deployment](dev/infrastructure/)
- [🗄️ Databases](dev/databases/)
- [🧪 Testing](tests/)
- [🤖 AI & Agents](ai/) — agent instructions and prompts
- [🏛️ Project Architecture](dev/technical/architecture/)
- [📐 Customization](dev/customization/)
- [📦 Publishing](publish/) — marketplace & distribution
- [🎨 Design](design/)

## Project Documentation

| Product | Directory | Key Docs |
|---|---|---|
| **Precis LMS** | [`precis/`](precis/) | Configuration, Courses, Deployment |
| **Landing-Fusion** | [`precis-landing/`](precis-landing/) | Frontend, Backend API, Deployment |
| **Syntara/Cypercloud** | [`cypercloud/`](cypercloud/) | Infrastructure, Configuration, Features |
| **Formint POS** | [`pos/`](pos/) | Editions, Backend (Rust), Sidecar (Django), Cloud |
| **django-fusion** | [`libs/`](libs/) | Component guide, Viewsets, Templates |
| **Shared Config** | [`dev/back-env/`](dev/back-env/) | Settings reference, Environment variables |

## Related

- [`../AGENTS.md`](../AGENTS.md) — repository-wide AI agent instructions
- [`recommendations.md`](recommendations.md) — recommended priorities
- [`plans/README.md`](plans/README.md) — canonical plan registry
- [`plans/document-lifecycle.md`](plans/document-lifecycle.md) — archive/delete policy
