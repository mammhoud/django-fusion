---
Object type: Plan
Tags: planning, objectives
Status: Published
Type: Roadmap
Related Plans: product-development, market-research, business-model
Related Goals: business-goal, growth-goal
---

# Startup Planner — Product & Business Strategy

> **Type:** Plan 📋
> **Emoji:** 🚀
> **Description:** Strategic planning overview — product creation, project scopes, scalability planning, and milestone mapping for the Structa Cloud platform.

---

## 1. Product Creation

### Web Applications & Sites

> Paths normalized 2026-09-10 to the current tree — see `AGENTS.md` name-migration rules.

| Project | Path | Domain | Purpose |
|---------|------|--------|---------|
| **Precis (LMS + landing, unified)** | `projects/precis/precis-main/` | structa.cloud | Learning management + marketing catalog |
| **CTC Research** | `projects/precis/precis-ctc/` | ctc-research.com | Research publishing |
| **Syntara (Cypercloud)** | `projects/syntara/` | — | AI chat customizer (runtime alias `cypercloud`) |
| **Loop-CRM** | `projects/loop-crm/` | crm.structa.cloud | CRM + social scheduling |

> Retired legacy projects — `projects/lms` (merged into precis-main),
> `projects/portfolio` / VResume (not in checkout; resume builder not pursued),
> `projects/tinker` (superseded by Syntara's customizer) — remain in git
> history only.

### Shared Libraries

| Library | Path | Purpose |
|---------|------|---------|
| **django-fusion** | `libs/django-fusion/` | Component system, routing, CBVs |
| **ceptor-ai** | `libs/ceptor-ai/` | AI chat client, MCP server |

---

## 2. Focus Areas

| Focus | Description | Status |
|-------|-------------|--------|
| **Product Creation** | Build and launch all web applications | ✅ Active |
| **Future Technology** | AI integration, scalable architecture | 🚧 Ongoing |
| **Projects Investigations** | Research new features and integrations | 📋 Ongoing |
| **Sales Process** | Go-to-market strategy, pricing | 📋 Planned |
| **Project Versions** | Edition scoping (mini, solo, full, cloud) | 🚧 In Progress |

---

## 3. Project Scopes

### POS Desktop Suite
Full enhanced POS with AI compatibility:
- **CRM** — Customer relationship management
- **Resume/Portfolio** — Professional identity tools
- **LMS** — Learning management system
- **CMS** — Content management system

### Integration Features
- **Project Adding** — Add new sites/applications to the platform
- **Project Generating** — AI-assisted project customization
- **Background Tasks** — Celery worker infrastructure
- **Shared Media Server** — Nginx-based static/media serving
- **Multi/Single Domain** — Flexible domain routing via Traefik

---

## 4. Scalability Planning

| Area | Current State | Target |
|------|:------------:|:------:|
| Sites | 5 sites | 20+ sites |
| Users | Single-tenant | Multi-tenant SaaS |
| Database | SQLite per site | Shared PostgreSQL |
| Deployment | Docker Compose | Kubernetes |
| AI Integration | Ceptor AI MVP | Full AI pipeline |

---

## 5. Business & Pricing Strategy

| Tier | Price | Features | Target |
|------|-------|----------|--------|
| **Community** | Free | Self-hosted, full source | Developers |
| **Professional** | Subscription | Premium features, support | Agencies |
| **Enterprise** | Custom | Dedicated support, SLA | Enterprises |
| **Educational** | Discounted | All features | Schools, universities |

---

## 6. Collaborators & Team

The platform aims to attract contributors through:
- Open source codebase (MIT license)
- Comprehensive documentation
- Active community via GitHub and Discord
- Clear contribution guidelines
- Recognition and roles for active contributors

---

## Related Docs

- → `business-model.md` — Business Model Canvas
- → `product-development.md` — Development lifecycle
- → `market-research.md` — Market analysis
- → `project-guide.md` — Repository navigation
- → `../tasks/tasks-and-backlog.md` — Implementation tasks
- → `../stories/starting-the-project.md` — Founder journey (how it started)
- → `../goals/achievement-board.md` — Achievements by phase
- → `../README.md` — Master index
