---
Object type: Plan
Tags: backend, api, database
Status: Published
---

# Backend Plans

> **Scope:** Backend engineering plans across Structa Cloud products, with focus on Formint POS versions
> **Updated:** 2026-09-06

---

## Active backend vertical slices (priority order)

### 1. Formint POS Backend — P0

**Owner:** Formint team

| Version | Stack | Status | Next Gate |
|---------|-------|--------|-----------|
| Community | SQLite + Tauri (Rust) | Complete | — |
| Standard | SQLite + Tauri (Rust) | Complete | — |
| Professional | Django + PostgreSQL | In Progress | Invoicing API, reports, sync |
| Cloud | Django + PostgreSQL + Channels | Planned | Multi-tenant, real-time sync |
| Client | Vue 3 + Tauri | Complete | Cloud API integration |

### 1a. Formint Invoicing & Reports Backend — P1

**Owner:** Formint team

| Task | Target Version | Status |
|------|---------------|--------|
| Invoicing API — wizard form backend | Pro, Cloud | Planned |
| Invoice editing and choices API | Pro, Cloud | Planned |
| Reports API — sales, tax, inventory | Pro, Cloud | Planned |
| Unified theme attributes API | All versions | Planned |
| Cross-team data change coordination | All versions | Planned |
| Client onboarding funnel API | Standard, Pro, Cloud | Planned |
| Payment gateway integration (Stripe/PayPal) | Pro, Cloud | Planned |

### 2. Precis LMS Backend — P0

**Owner:** Precis team
**Stack:** Django + Wagtail + PostgreSQL
**Key areas:** API design, CMS integration, enrollment models, contact collection, workspace provisioning

### 2a. Precis AI Design Chat Backend — P1

**Owner:** Precis team
**Stack:** Django + PostgreSQL + AI providers
**Key areas:** Token billing, multi-model routing, usage monitoring

### 3. CTC Research Backend — Active

**Owner:** CTC team
**Stack:** Django + Wagtail + PostgreSQL
**Workstreams:** Multi-lang catalogs, media proxy, email parity

### 4. Syntara Backend — Active

**Owner:** AI team
**Stack:** Django + PostgreSQL + AI providers
**Key areas:** Chat sessions, template customization, provider routing, token tracking

### 5. Loop-CRM Backend — Active (code-complete; deploy gates open)

**Owner:** CRM team
**Milestones:** Tenancy/auth → tenant CRUD → channels/adapters → feature parity
**Status (2026-09-06):** Domain apps (core/crm/marketing/attribution/finance/pos/billing/pages) ship 42 models across sales, marketing, finance/RevOps, POS-ingest, SaaS-billing and landing domains; `graph_models` ERD targets (`make erd`/`erd-all`) now match the repo convention. Remaining work is deploy-gated: live OAuth provider credentials + publish E2E, realtime/Channels hardening on the deployed stack, and the demo-state server-half verification.

### 6. django-fusion (Shared Backend Framework) — P2

**Owner:** Framework team
**Active plans:** Tasks API, LLM integration, skeleton APIs

---

## Cross-team data coordination

### Design & Data Change Requests

- **Trigger:** Another team requests design or data changes affecting backend models or APIs
- **Process:** Receiving team reviews schema impact, migration path, API contract changes
- **Scope:** Theme attributes, invoice schemas, report data models, cross-product data flows
- **Verification:** Schema migration plan + API contract update + backward compatibility check + sign-off

---

## Current backend priorities

| Priority | Action | Verification |
|----------|--------|--------------|
| P0 | Formint edition extension chain — next executable task | Edition-specific tests |
| P0 | Precis Landing content work — preserve rendering contract | Backend tests |
| P1 | Formint invoicing and reports backend — wizard, editing, reports, theme API | API contract tests |
| P1 | Formint POS client acquisition — 60 Standard / 30 Pro / 5 Cloud | Client onboarding funnel metrics |
| P1 | Precis LMS contact collection backend | Contact API tests |
| P1 | Precis LMS workspace provisioning and billing | Workspace creation tests |
| P1 | Precis AI Design Chat token billing backend | Token metering tests |
| P1 | Loop-CRM feature parity backend | Feature gap audit |
| P1 | Cross-team data change coordination | Impact assessment + migration plan |
| P2 | django-fusion tasks and MCP | Test suite |
| P2 | Documentation maintenance | Link checker |
| P2 | Repository cleanup | Reference scan |

---

## Backend architecture patterns

| Pattern | Location | Description |
|---------|----------|-------------|
| Dual rendering | Precis Landing, Formint | Server HTML / HTMX fragment / JSON API |
| Config cascade | django_fusion.config.project | Layered configuration: site → admin → defaults |
| Component system | django_fusion.comp | Registered reusable components |
| Fragment routing | django_fusion.routes | Named fragment endpoints for HTMX/Astro |
| Background tasks | django_fusion.tasks | Task queue with Redis broker |
| Wagtail pages | Product models.py | StreamField + django-fusion blocks |
| POS versions | projects/formints/ | Separate codebases per edition |

---

## Periodic backend tasks

| Task | Cadence | Team |
|------|---------|------|
| API contract review | Weekly | Backend |
| Database migration review | Weekly | Backend |
| Schema backward compatibility check | Bi-weekly | Backend |
| Performance and query review | Bi-weekly | Backend |
| Security dependency audit | Weekly | Engineering |
| Cross-team data impact review | Monthly | Backend + Product |

---

## Remarks

- Use the Makefile dispatcher for canonical commands
- Product AGENTS.md files are the local source of truth for conventions
- POS versions share django-fusion but maintain separate codebases per edition

<!-- AI-generated: review needed -->
