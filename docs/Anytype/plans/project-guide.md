---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Guide
Tags: navigation, repository, onboarding
Status: Published
Category: Setup
Target Audience: Developer
Related Plans: product-development, startup-planner
Related Architecture: architecture-overview
---

# Project Guide — Repository Navigation

> **Type:** Guide 📘
> **Emoji:** 🗺️
> **Description:** Navigation guide mapping the Structa Cloud monorepo — how to find files, understand the directory structure, and move from ideas in Anytype to working code.

---

## Repository Layout

```
structa.cloud/
├── projects/              # Django sites + POS editions
│   ├── configs/           # Shared Django configuration
│   ├── assets/            # Shared templates, static files
│   ├── www/               # Shared Django code
│   ├── lms/               # LMS Demo (port 5071)
│   ├── ctc-research/      # CTC Research (port 5070)
│   ├── portfolio/         # VResume (port 5072)
│   ├── cypercloud/        # CyperCloud (port 5073)
│   └── pos/               # POS editions (mini, solo, full)
├── libs/                  # Reusable Python libraries
│   ├── django-fusion/     # Component system
│   └── ceptor-ai/         # AI chat client + MCP
├── applications/          # Infrastructure
│   ├── proxy/             # Traefik + Nginx
│   ├── databases/         # PostgreSQL + Redis
│   └── compose/           # Docker Compose orchestration
├── docs/                  # MkDocs documentation
├── tests/                 # Workspace test suite
├── Makefile               # Root dispatcher
└── docker-compose.yml     # Root orchestration
```

---

## How to Navigate

### 1. Start with the Big Picture
- → `architecture/overview.md` — High-level architecture
- → `plans/startup-planner.md` — Product and business strategy

### 2. Understand Each Product
- → `architecture/website-descriptions.md` — Full site descriptions
- → `features/` — Feature documentation per site

### 3. See What's Being Worked On
- → `tasks/tasks-and-backlog.md` — Current tasks and priorities
- → `goals/` — Strategic goals and OKRs
- → `milestones/` — Delivery milestones

### 4. Technical Deep Dive
- → `architecture/overview.md` — Technology stack
- → `references/` — API, database, command references

### 5. From Idea to Code
- → `guides/setup.md` — Development setup
- → `guides/development.md` — Development workflow
- → `plans/product-development.md` — Product lifecycle

---

## Key Directories Reference

| Directory | Contains | How to Use |
|-----------|----------|------------|
| `projects/configs/` | Base settings, environment configs | Add shared settings here |
| `projects/assets/` | Shared templates, static files, locale | Add cross-site assets here |
| `projects/www/` | Core Django code, workers | Add shared services here |
| `projects/<site>/` | Site-specific code | Add site logic in its directory |
| `libs/` | Reusable Python packages | Add framework-level code here |
| `applications/` | Infrastructure services | Add Docker, proxy config here |

---

## Working with the Makefile

The Makefile system delegates across layers:

```bash
# Development
cd projects && make dev WEBSITE=lms           # Run LMS dev server
cd projects && make check WEBSITE=lms         # Django system checks
cd projects && make test WEBSITE=lms          # Run tests

# Deployment
make deploy              # Full stack deployment
make deploy-databases    # Deploy databases
make deploy-app          # Deploy applications
make deploy-proxy        # Deploy proxy

# POS
make pos                 # POS dev targets
make pos-build           # Build POS editions
```

---

## Related Docs

- → `architecture/overview.md` — Architecture overview
- → `architecture/makefile.md` — Makefile reference
- → `guides/setup.md` — Development setup
- → `guides/development.md` — Development workflow
- → `plans/product-development.md` — Development lifecycle
- → `plans/startup-planner.md` — Startup planning
- → `../README.md` — Master index
