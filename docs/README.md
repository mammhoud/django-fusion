---
title: Structa Cloud Documentation
description: Canonical engineering, product, and operations documentation for the Structa Cloud monorepo.
navigation:
  title: Documentation home
  icon: i-lucide-house
object:
  type: "reference"
  id: "docs.home"
attributes:
  source_path: "README.md"
  canonical_route: "/docs/en/"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
tags:
  - structa-cloud
  - documentation
  - onboarding
  - docus
links:
  - label: "Project awareness"
    to: "/docs/en/guides/00-project-awareness"
    icon: "i-lucide-compass"
  - label: "Architecture"
    to: "/docs/en/architecture"
    icon: "i-lucide-landmark"
---

# Structa Cloud — Documentation

> ⭐ **Start here:** read [Project awareness](guides/00-project-awareness.md), then open the relevant architecture, product, or implementation guide.

> ⚡ **New here?** Start with [Guides](guides/) — numbered walkthroughs for setup, auth, development, deployment, and customization.

> 📚 **Docus:** this Markdown tree is the single authored source. `docs/content/` is generated and ignored; build it with `make -C docs build`.

## Current Products

| Product | Canonical Path | Main Responsibility | Domain |
|---|---|---|---|
| **Precis LMS** | `projects/precis/precis-main/` | Django/Wagtail learning platform: courses, enrollment, progress, profiles, content | structa.cloud |
| **Landing-Fusion** | `projects/precis/precis-landing/` | Public marketing/catalog site; Astro frontend and Django/Wagtail backend | structa.cloud |
| **Syntara** (Cypercloud) | `projects/syntara/` | AI chat, template discovery, code customization, streaming responses | — |
| **Formint POS** | `projects/formints/` | Multi-edition restaurant POS: Community, Professional, Cloud, Client | — |
| **django-fusion** | `libs/django-fusion/` | Shared Django/Wagtail components, routing, fragments, forms, tables | submodule |
| **Infrastructure** | `application/` | PostgreSQL, Redis, Traefik/Nginx, Compose, deployment and MCP tooling | structa.cloud |
| **Workspace tests** | `tests/` | Cross-project validation, fixtures, browser tests, deployment checks | — |

## Documentation ownership

| Need | Canonical location |
|---|---|
| Recommended priorities and sequencing | [`recommendations.md`](recommendations.md) |
| Engineering plans and implementation tasks | [`plans/`](plans/README.md) |
| Product decisions and architecture context | [`plans/`](plans/) and the relevant product section |
| Document objects, attributes, tags, and links | [`guides/00-project-awareness.md`](guides/00-project-awareness.md) |
| Current project, architecture, development, and deployment references | The topic/project sections below |

All new plans must be added under `docs/plans/<scope>/` and linked from the canonical plan registry. The old `docs/dev/plans/`, `docs/plans/migrated/`, and project-local `docs/superpowers/plans/` locations are no longer active authoring paths.

## Repository Structure

```
structa.cloud/
├── projects/                         # Product code, shared Django config, and assets
│   ├── precis/                       # Product grouping: LMS, research, marketing
│   │   ├── precis-main/              # Precis LMS — learning platform
│   │   │   ├── backend/              # Django + Wagtail backend
│   │   │   ├── assets/               # Templates, static, SCSS, media
│   │   │   └── frontend/             # Astro frontend shell
│   │   ├── precis-landing/           # Landing-Fusion marketing/catalog site
│   │   │   ├── backend/              # Django + Wagtail backend
│   │   │   ├── frontend/             # Astro frontend
│   │   │   └── assets/               # Project assets
│   │   └── precis-ctc/               # Medical research center site
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
├── application/                     # Databases, proxy, Compose, scripts, Kilo/MCP
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
│   ├── plans/                        # Single active plan registry + legacy archive
│   ├── precis/  loop-crm/  syntara/  pos/  precis-ctc/   # Per-product references
│   ├── libs/                         # Shared library docs (django-fusion)
│   ├── startup/                      # Private market strategy per product
│   ├── ai/                           # Agents, prompts, MCP
│   └── dev/                          # Infrastructure, databases, customization
├── .agents/                          # AI agent skills and configuration
│   ├── skills/                       # Reusable skill definitions (21 skills)
│   └── kiro/settings/                # MCP server configuration
├── .github/                          # CI workflows and composite actions
├── Makefile                          # Root deployment and delegation entry point
└── pyproject.toml                    # Root Python/tooling configuration
```

## Quick Links

- [🧭 Project awareness and computation guide](guides/00-project-awareness.md)
- [⭐ Recommendations first](recommendations.md)
- [🛠️ Project Setup & Build Guides](setup-guides.md) — per-project setup/build indexes
- [📚 Guides](guides/) — step-by-step tutorials
- [🗺️ Reference map](REFERENCE.md) — every docs dir/subdir, its owning project, and what each file references
- [🛠️ Commands & delegation](COMMANDS.md) — unified verb naming, delegation chain, and the deploy cascade
- [🗺️ Canonical plans](plans/README.md) — all active plans and historical evidence
- [🔄 Recent Changes](recent-changes.md)
- [🎯 Features Index](features/) — capabilities by project
- [🏗️ Infrastructure & Deployment](dev/infrastructure/)
- [🗄️ Databases](dev/databases/)
- [🧪 Testing](tests/)
- [🏛️ Architecture](ARCHITECTURE.md) — request lifecycle, components, tasks, MCP, Docus
- [🏗️ Infrastructure & Deployment](dev/infrastructure/) — proxy, workers, troubleshooting
- [📐 Customization](dev/customization/) — methods and design system
- [📦 Publishing](publish/) — marketplace & distribution
- [🤖 AI & Agents](ai/) — agent instructions, prompts, and skills
- [✍️ Documentation authoring prompt](ai/documentation-authoring.md) — the powerful doc-generation prompt (emoji, diagrams, ERD, previews, EN/AR)
- [🚀 Startup & Market Strategy](startup/README.md) — 🔒 private: MVP canvas, TAM/SAM/SOM, ideal clients per product; [full portfolio master](startup/STRATEGY.md)
- [📚 Docus implementation](guides/09-docus.md) — source generation, metadata, locales, build, and deployment

## Project Documentation

| Product | Directory | Key Docs |
|---|---|---|
| **Precis** (LMS + landing) | [`precis/`](precis/README.md) | Architecture, Configuration, Courses, Landing (frontend/API/deployment) |
| **CTC Research** | [`precis-ctc/`](precis-ctc/) | Content strategy, Publishing & production |
| **Syntara** (Cypercloud) | [`syntara/`](syntara/) | Configuration, Features, Infrastructure |
| **Loop-CRM** | [`loop-crm/`](loop-crm/) | Design system, Setup & build |
| **Formint POS** | [`pos/`](pos/) | Editions, Backend (Rust), Sidecar, Cloud edition |
| **django-fusion** | [`libs/`](libs/README.md) | Package guide, Where & how used, Component system |
| **Shared Config** | [`dev/back-env/`](dev/back-env/) | Settings reference, Environment variables |
| **Startup strategy** 🔒 | [`startup/`](startup/README.md) | MVP canvas, TAM/SAM/SOM, SaaS services, ideal clients, research |

## Canonical source and Docus

`docs/**/*.md` and `docs/**/*.mdx` are authored documentation. The Docus app
lives at the root of `docs/` and runs `scripts/prepare-content.mjs` to
generate the ignored English content tree and copy the authored Arabic
translations. There is one content source, one set of links, and one
validation path; generated files are not edited or committed.

Use `object`, `attributes`, `tags`, and `links` frontmatter for new documents.
The preparation script adds the same graph metadata to legacy pages that do not
yet define it. See [Project awareness](guides/00-project-awareness.md).

## Related

- [`../AGENTS.md`](../AGENTS.md) — repository-wide AI agent instructions
- [`recommendations.md`](recommendations.md) — recommended priorities
- [`plans/README.md`](plans/README.md) — canonical plan registry
- [`plans/document-lifecycle.md`](plans/document-lifecycle.md) — archive/delete policy

## Remarks & Notes

- `docs/**/*.md` and `docs/**/*.mdx` are the only authored documentation sources.
- `docs/content/` is disposable generated output; never edit it or add a second copy there.
- New pages should carry `object`, `attributes`, `tags`, and Docus-native `links` metadata.
- Prefer one canonical page plus links to it over repeated product explanations.








# Structa Cloud Docus application

This directory contains the Nuxt/Docus application that serves the authored
repository documentation. The canonical reader-facing implementation guide is
[`../guides/09-docus.md`](../guides/09-docus.md); keep operational detail there
instead of maintaining a second documentation copy in this package README.

## Local development

```bash
cd docs
npm install
npm run prepare-content
npm run validate-content
npm run dev
```

Open `http://localhost:3000/docs/en/`. The application also exposes the Arabic
locale at `/docs/ar/` and uses `/docs/` as its configured base path.

## Build and preview

```bash
npm run build
npm run build:static
npm run preview
```

`prepare-content.mjs` generates the ignored `content/en/` and `content/ar/`
trees before development and build. Do not edit or commit `content/`, `.nuxt/`,
`.output/`, `dist/`, or `node_modules/`.

## Deployment

The production image is built from `docs/Dockerfile`, runs the Docus Nuxt SSR
server on `docus:3000`, and is routed by the shared proxy. See the canonical
[Docus implementation guide](../guides/09-docus.md) for the proxy contract,
metadata model, validation commands, and source-of-truth rules.

## Remarks & Notes

- This README describes the application package; `docs/guides/09-docus.md` is the single published Docus guide.
- A Docus build does not validate product backend health; run the owning project checks separately.
