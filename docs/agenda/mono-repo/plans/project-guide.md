---
Object type: Guide
Status: Published
Category: Setup
Target Audience: Developer
Related Plans: product-development, startup-planner
Related Architecture: architecture-overview
Tags: guide, navigation, repository
---

# Project Guide — Repository Navigation

> **Description:** Navigation guide mapping the Structa Cloud monorepo — how to find files, understand the directory structure, and move from ideas in Anytype to working code.

---

## Repository layout

### Projects (Django sites + POS editions)

| Path | Purpose |
|------|---------|
| projects/configs/ | Shared Django configuration |
| projects/assets/ | Shared templates, static files |
| projects/www/ | Shared Django code |
| projects/lms/ | LMS Demo |
| projects/ctc-research/ | CTC Research |
| projects/portfolio/ | VResume |
| projects/cypercloud/ | CyperCloud |
| projects/pos/ | POS editions (mini, solo, full) |

### Libraries and infrastructure

| Path | Purpose |
|------|---------|
| libs/django-fusion/ | Component system |
| libs/ceptor-ai/ | AI chat client + MCP |
| applications/proxy/ | Traefik + Nginx |
| applications/databases/ | PostgreSQL + Redis |
| applications/compose/ | Docker Compose orchestration |
| docs/ | MkDocs documentation |
| tests/ | Workspace test suite |
| Build scripts | Root dispatcher |
| docker-compose.yml | Root orchestration |

---

## How to navigate

1. **Start with the big picture** — architecture overview, startup planner
2. **Understand each product** — website descriptions, feature documentation
3. **See what's being worked on** — tasks and backlog, goals, milestones
4. **Technical deep dive** — overview, references
5. **From idea to code** — setup guide, development workflow, product lifecycle

---

## Key directories reference

| Directory | Contains | How to Use |
|-----------|----------|------------|
| projects/configs/ | Base settings, environment configs | Add shared settings here |
| projects/assets/ | Shared templates, static files, locale | Add cross-site assets here |
| projects/www/ | Core Django code, workers | Add shared services here |
| projects/<site>/ | Site-specific code | Add site logic in its directory |
| libs/ | Reusable Python packages | Add framework-level code here |
| applications/ | Infrastructure services | Add Docker, proxy config here |

---

## Operating targets

| Task | Target | Purpose |
|------|--------|---------|
| Development | Run site dev server | Local development |
| Check | Run system checks | Validate configuration |
| Test | Run tests | Verify behavior |
| Deployment | Full stack deployment | Release to production |
| POS | POS development targets | Build POS editions |

---

## Related

- → `../architecture/overview.md` — Architecture overview
- → `../guides/_index.md` — Development setup
- → `../guides/development-workflow.md` — Development workflow
- → `product-development.md` — Development lifecycle
- → `startup-planner.md` — Startup planning
- → `../README.md` — Master index
