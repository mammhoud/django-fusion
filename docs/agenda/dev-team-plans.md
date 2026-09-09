---
Object type: Plan
Tags: development, engineering, roadmap
Status: Published
---

# Development Team Plans

> **Scope:** All engineering plans across Structa Cloud products
> **Updated:** 2026-09-06

---

## Active vertical slices (priority order)

### 1. Formint Edition Chain — P0
**Owner:** Formint team
**Path:** projects/formints/

| Edition | Status | Next Gate |
|---------|--------|-----------|
| Community | Complete | — |
| Standard | Complete | — |
| Professional | In Progress | Backend sync and invoicing |
| Cloud | Planned | Multi-tenant SaaS |
| Client | Complete | Cloud API integration |

**Key Plans:**
- `docs/plans/editions/10-formint-audit-and-reconciliation-2026-08-22.md` — Cross-edition audit
- `docs/plans/django-fusion/django-fusion-tasks-mcp-plan.md` — Unified task API, MCP tooling
- `docs/plans/django-fusion/config-cascade-plan.md` — Config cascade (active, baseline implemented)

### 2. Precis Landing — **P0**
**Canonical:** `docs/plans/precis-landing.md`
**Owner:** Precis team
**Path:** `projects/precis/precis-landing/`
**Contract:** Post-only code-rendering (server HTML / HTMX fragment / JSON for Astro)
**Verification:** `make backend-test` + `npm run check`

### 3. Precis LMS (unified) — **P1**
**Canonical:** `projects/precis/precis-main/` (merged LMS + Landing)
**Owner:** Precis team
**Dispatcher:** `WEBSITE=precis-main` (aliases: `precis-lms`, `precis-landing`)
**Key Areas:** Frontend build, deployment gates, Wagtail CMS integration

### 4. CTC Research — **Active**
**Canonical:** `docs/plans/repository/ctc-research-publish-2026-08-18.md`
**Owner:** CTC team
**Path:** `projects/precis/precis-ctc/`
**Workstreams:** Content/component audit, multi-lang catalogs (es/sv/pt-br), media proxy, email parity, `make redeploy`, cross-module workflows

### 5. Syntara (Cypercloud) — **Active**
**Canonical:** `projects/syntara/`
**Owner:** AI team
**Runtime alias:** `cypercloud` preserved for external contracts
**Stack:** Django + Webpack + HTMX + Monaco Editor + Ollama/OpenAI/Claude/Gemini

### 6. Loop-CRM — **Active (merge complete at feature level)**
**Canonical:** `docs/plans/loop-crm/merge-plan.md`
**Owner:** CRM team
**Path:** `projects/loop-crm/`
**Status:** Merge milestones shipped end-to-end (tenancy/auth → tenant-scoped CRUD → channels/adapters → allauth → finance ledger → AI hub → en/ar locale → billing/Wagtail landing). Remaining gates are operational, not feature code: live OAuth provider credentials, realtime/WebSocket hardening on the deployed stack, and the demo-state server-half verification.
**Milestones:** Tenancy/auth → tenant-scoped CRUD → channels/adapters → allauth → finance/POS ingestion → AI hub + locale → billing/landing

### 7. django-fusion (Shared Framework) — **P2**
**Canonical:** `docs/plans/django-fusion/`
**Owner:** Framework team
**Path:** `libs/django-fusion/`
**Active Plans:**
- Tasks & MCP: unified background task API, Celery removal, MCP tooling
- LLM & AI MCP Enhancement: provider-neutral routing, model levels, caching, streaming
- Webpack Enhancement: project-customizable webpack, env configs
- Analyzer + Skeleton + Asset APIs: dynamic skeletons, per-page components, Astro bridge

---

## ✅ Implementation status truth (backend × frontend) — 2026-09-06

> Reconciliation pass run 2026-09-06 across the Django products. "Implemented"
> means code-backed in the current tree; "Not yet" is planned/missing;
> "Couldn't add" records work intentionally deferred or blocked. Cross-product
> component evidence lives in
> [`docs/audit/frontend-components-2026-09-06.md`](../../audit/frontend-components-2026-09-06.md).

| Product | Backend — implemented | Backend — not yet / couldn't add | Frontend — implemented | Frontend — not yet / flagged |
|---------|-----------------------|---------------------------------|------------------------|------------------------------|
| **Loop-CRM** | Tenancy+RBAC, CRM pipeline/deals/board, marketing posts + 12-platform catalog connectors + OAuth (incl. Google/Meta/TikTok/Reddit), attribution, finance/POS ledger, billing/Stripe, Wagtail landing road, workflows, Dramatiq tasks, realtime events, AI Hub (consent-gated), en/ar locale | Live OAuth credentials + publish E2E on deployed stack; realtime/WebSocket hardening on deploy; demo-state server-half verify (all need a real deploy, not code) | Astro shell, RevOps dashboard, PipelineBoard (real `/apis/core/` data, GSAP drag, CSRF move), AiHub, CommandPalette, LocaleSwitcher, EmployeeDirectory, BillingPlan, ReportCatalog, Task Center — no placeholder components | `PipelineDemo` is an inert marketing demo island (fake deals) — landing-preview only, not app code; live-provider config remains env-gated |
| **Precis LMS (precis-main)** | Wagtail content/pages + LMS backend + django-fusion routing | Deployment/CI gates per plan; builder/data surfaces | Astro/marketing shell shipped | `frontend/src/lib/brand.ts` carries a stale "CRM + social scheduling · coming soon" tagline — flagged copy, see audit |
| **Precis Landing** | Render-first Django contract (HTML/HTMX/JSON) | — | Astro front-end live | — |
| **CTC Research** | Multi-lang catalogs (es/sv/pt-br), media proxy, i18n fixtures, containerized deploy | Publish gates (email parity E2E, redeploy validation) still open | Backend-rendered pages live | `blog/*-details*.html` demo templates still carry hard-coded Lorem-ipsum/2018 theme markup — not view-referenced, should be removed or quarantined |
| **Syntara (Cypercloud)** | Django `chat` app, config cascade, model routing, token tracking | Provider keys + OAuth for live AI calls (local Ollama works) | Webpack/HTMX + Monaco customizer shipped | — |
| **Formint Pro** | Django `server/` backend + sync; finance ledger groundwork | Invoicing/reports APIs, client onboarding funnel (next gates) | Astro + Vue shells shipped; create/edit modals + delete wired for suppliers, HR roles, schedules, payroll, admin notes, kitchen recipes (2026-09-06) | — |
| **Formint Cloud** | Django `backend/` (core/domain/handlers) + Channels API road | Multi-tenant SaaS, KDS, realtime sync scale-out | Astro frontend + shared client | — |
| **Formint Community / Standard / Client** | SQLite/Rust (Community/Standard), Vue+Tauri (Client) | — (Cloud API integration for Client) | Rust/Tauri + Vue | — |
| **django-fusion** | Component/fragment/task/config systems; bolt bridge | Celery removal + MCP tooling + LLM routing consolidation (P2) | Astro bridge + skeleton APIs in flight | — |

**What couldn't be added (deferred or blocked, with reason):**
- **Loop-CRM live provider publishing** — connectors + OAuth exist and are tested, but no real provider credentials are configured anywhere; verification requires the deployed stack (`crm.structa.cloud`) and secrets. Not a code gap.
- **Loop-CRM realtime on deploy** — Channels/SSE path is dev-verified; production Redis/channel-layer hardening is a deploy gate.
- **CTC publish gates** — content/component audit + i18n + media proxy shipped; email parity + `make redeploy` validation remain deploy-blocked.
- ~~Formint Pro create forms~~ — resolved 2026-09-06: suppliers, HR roles/schedules/payroll, admin notes and kitchen recipes/ingredients now open real create/edit modals wired to the Django server API (see [`docs/audit/frontend-components-2026-09-06.md`](../../audit/frontend-components-2026-09-06.md) § 2.3).
- **ERD PNGs for Loop-CRM** — tooling added (2026-09-06); DOT graphs generated and PNGs rendered after installing `graphviz` locally. PNGs stay git-ignored derived assets (repo convention); the committed contract is the `docs/erd` README + DOT. Formint-cloud re-render remains blocked in this sandbox by the missing optional `django_bolt` package (present in its Docker image).

---

## 🔧 Key Commands by Product

| Product | Check | Test | Build/Run |
|---------|-------|------|-----------|
| Formint Pro | `cd projects/formints/formint-pro && make check` | `make test` | `make run-dev` |
| Formint Cloud | `cd projects/formints/formint-cloud && make check` | `make test` | `make run-dev` |
| Formint Community | `cd projects/formints/formint-community && pnpm run check` | `pnpm test` | `pnpm tauri dev` |
| Precis Main | `cd projects/precis/precis-main/backend && make check` | `make test` | `make run-dev` |
| Precis Landing | `cd projects/precis/precis-landing && make check` | `make backend-test` | `make build` |
| Precis CTC | `cd projects/precis/precis-ctc && make check` | `make test` | `make build` |
| Syntara | `cd projects/syntara && make check` | `make test` | `make dev` |
| django-fusion | `cd libs/django-fusion && uv run pytest` | — | — |

---

## 📐 Architecture Patterns (Reference)

| Pattern | Location | Description |
|---------|----------|-------------|
| **Dual rendering** | Precis Landing, Formint | Server HTML / HTMX fragment / JSON API contract |
| **Config cascade** | `django_fusion.config.project` | Layered YAML: site → admin → defaults |
| **Component system** | `django_fusion.comp` | `{% comp "name" %}` registered components |
| **Fragment routing** | `django_fusion.routes` | Named fragment endpoints for HTMX/Astro |
| **Background tasks** | `django_fusion.tasks` | Dramatiq-based, Redis broker (prod) |
| **Wagtail pages** | Product `models.py` | StreamField + django-fusion blocks |

---

## 📋 Current Engineering Priorities (from recommendations.md)

| Priority | Action | Verification |
|----------|--------|--------------|
| P0 | Formint edition extension chain — next executable task | Edition-specific tests |
| P0 | Precis Landing content work — preserve rendering contract | Backend tests + `npm run check` |
| P1 | Precis LMS — close frontend/deployment gates | Site checks, tests, builds |
| P1 | Repository cleanup — don't delete compatibility sources prematurely | Reference scan |
| P2 | django-fusion tasks & MCP — unified bg task API, Celery removal, MCP tooling | `uv run pytest libs/django-fusion/` |
| P2 | Docs maintenance — link validation, stale ref removal | Link checker |

---

## 🔗 Cross-References

- **Plan Registry:** `docs/plans/README.md` — all active/superseded plans
- **Recommendations:** `docs/recommendations.md` — prioritized next actions
- **Project Awareness:** `docs/guides/00-project-awareness.md` — object graph, commands
- **Architecture:** `docs/ARCHITECTURE.md` — full system architecture
- **Config Cascade:** `docs/plans/django-fusion/config-cascade-plan.md`
- **Marketing Claims:** `docs/plans/marketing-claims.md` — evidence requirements for feature claims

---

## Remarks & Notes

- Use `projects/Makefile` dispatcher (`make check WEBSITE=<target>`) for canonical commands
- Product `AGENTS.md` files are the local source of truth for conventions
- Do not create plans in `docs/dev/plans/`, `projects/*/docs/`, or `docs/plans/migrated/`
- Completed plans are deleted once superseded; git history is the archive

<!-- AI-generated: review needed -->