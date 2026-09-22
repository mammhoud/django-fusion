---
title: Product Audit — Full Report
description: Detailed audit of CRM, POS, LMS, and Landing Builder — completed features, planned roadmap, missing features, technical debt, gap analysis, risk analysis, and recommendations.
object:
  type: "report"
  id: "docs.audit.product-audit"
attributes:
  source_path: "audit/product-audit.md"
  canonical_route: "/docs/en/audit/product-audit"
  section: "audit"
  owner: "workspace"
  status: "maintained"
  source_of_truth: "repository-markdown"
tags:
  - structa-cloud
  - audit
  - gap-analysis
  - risk-analysis
  - recommendations
  - crm
  - pos
  - lms
  - landing-builder
links:
  - label: "Audit home"
    to: "/audit"
    icon: "i-lucide-clipboard-check"
  - label: "Plan registry"
    to: "/plans"
    icon: "i-lucide-map"
---

# 🔍 Product Audit — Full Report

> **Audit date:** 22 August 2026 · **Method:** code-tree + plan-registry truth
> pass. **Scope:** CRM, POS, LMS, Landing Builder. This is not a release
> approval or a live production certification.

<!-- AI-generated: review needed -->

## How to read this report

Each product section lists **Completed features** (code-backed), **Planned
features** (registry roadmap), **Missing features** (gaps vs. the product
profiles/vision), and **Technical debt** (refactoring opportunities). The
report closes with **Gap analysis**, **Risk analysis**, and
**Recommendations** in priority order.

Sources: `docs/plans/README.md`, `docs/plans/loop-crm/merge-plan.md`,
`docs/plans/editions/README.md`,
`docs/plans/editions/10-formint-audit-and-reconciliation-2026-08-22.md`,
`docs/startup/product-profiles.md`, `docs/startup/PRICING.md`, and the product
READMEs.

---

# 1. CRM — Loop-CRM (`projects/loop-crm/`) 🟢 live

> Product boundary: `projects/loop-crm/backend/apps/*` (core, crm, marketing,
> attribution, finance, pos, billing, pages, content, tasks) + Astro frontend.

## Completed features

| Area | What is shipped |
|---|---|
| Foundation | Domain models, django-fusion `Site`/`Application` registry, shared module/sidebar navigation, responsive Astro shell |
| Tenancy & auth | Workspace-scoped reads/mutations end-to-end (`apps/core/tenancy.py`), login-gated pages/APIs, CSRF-protected kanban move, allauth flows, RBAC roles |
| CRM core | Companies, contacts, pipelines, deals, activities, custom fields (`CustomFieldDefinition`, 9 types), custom objects (runtime schema, no migrations per object), saved views, CSV import/export |
| Marketing | Campaigns, social channels, posts with draft → approval → scheduled → published states, content calendar, approval queue, analytics (X metrics real) |
| Automation | No-code **step** workflow editor, workflow catalog, cross-module actions, Dramatiq actors (publish, aggregate, attribute) |
| Real-time & integrations | SSE/WebSocket pipeline/board sync, webhooks (deal-won, post-published), email sync (Gmail/Outlook OAuth + incremental sync), 6 real social publishers (LinkedIn, X, Mastodon, Bluesky, Discord, Slack) |
| Finance | Invoices, payments, revenue events, revenue-trend aggregate, Formint POS ingestion ledger (`apps/pos`) |
| Billing | Stripe-backed SaaS billing: checkout/portal/webhook, `/settings/plan/`, public `/apis/billing/plans/` |
| Landing | Wagtail-managed public landing: `/cms/` editor → `/apis/pages/<slug>/` JSON → Astro |
| API | Optional django-bolt road (`/bolt/`, JWT + API keys) with per-resource OpenAPI tags; `/api/v1/` compatibility road; pagination/filtering on both |
| Tasks | Task Center merging shared `django_fusion.BackgroundTaskLog` + `core.TaskExecution` |
| Tests | 28 backend test files; Playwright covers navigation shell, workflow lifecycle, content lifecycle |

## Planned features

- **AI hub (Phase 4)** — lead scoring, sales-email drafting, social post
  generation behind provider adapters with workspace consent + `AuditLog`.
- **6 remaining catalog adapters** — Instagram/Facebook/TikTok/YouTube/Reddit/
  WhatsApp promoted from honest `CatalogOnlyConnector` stubs to real
  publishers + OAuth connect flows (Bluesky app-password, Mastodon instance
  OAuth).
- **Visual DAG workflow editor** — trigger-rooted node/edge canvas with
  branching/merging, cycle rejection, topological action order.
- **Formint finance ingestion** — `pos_sales` push, data mapping, `apps/pos`
  model expansion, workflow action/template growth (✅ completed — see
  [`docs/agenda/feature-tracking/loop-crm.md`](../agenda/feature-tracking/loop-crm.md);
  the plan file was deleted, git history is the archive).
- **Wagtail landing Phases 5–8** — sidenav/guided UX, employees + report
  catalog, shared-locale i18n, license removal (`wagtail-landing-plan.md`).
- **Full per-resource Bolt OpenAPI** (partial today).

## Missing features

| Gap | vs. profile | Evidence |
|---|---|---|
| AI agents (sales/marketing/support) | product profile lists 4 AI agents | none shipped — Phase 4 |
| Support / Projects / HR module families | profile: ticketing, knowledge base, projects, HR | unshipped (only sales/marketing/finance cores) |
| 30+ social channels | Postiz DNA | 12 cataloged, 6 real |
| GraphQL road | CMS/API profile | REST only (deliberate, documented) |
| Notes/tasks/favorites as first-class | Twenty DNA | folded into `Activity` types only |
| Postiz extras | Canva editor, RSS, marketplace | absent |
| Social analytics breadth | per-network metrics | `{}` honestly for non-X networks |

## Technical debt

- **Two API roads** — `/bolt/` (canonical) + `/api/v1/` (compatibility):
  dual maintenance; plan a sunset of the compatibility road once consumers
  migrate.
- **Dual task logs** — shared `BackgroundTaskLog` + `core.TaskExecution` with
  idempotent mirroring; merge or accept as permanent boundary.
- **Dual rendering roads** — render-first (HTMX) + data (Astro islands):
  documented contract, but each screen must consciously choose; drift risk.
- **Demo-state complexity** — the demo state + auth gap fixes shipped (see
  [`docs/agenda/feature-tracking/loop-crm.md`](../agenda/feature-tracking/loop-crm.md));
  the demo credential contract must never leak into production paths.
- **Test skew** — 28 test files, but Playwright coverage is scoped to nav/
  workflow/content; finance, billing, and landing flows lack browser coverage.
- **Committed dev artifacts** — `projects/db.sqlite3`, `dev_db.sqlite3`, and
  `formints/restaurant.db` are present in the tree (gitignored but shipped in
  checkouts); confirm the deletion register covers them.

---

# 2. POS — Formints (`projects/formints/`) 🟢 core / 🟡 cloud

> Editions: Community ✅ · Standard ✅ · Pro ✅ · Cloud 🟡 staging ·
> pos-client 🔵 dev · JS/TS SDK ✅ · Tenant schemas 🟡 pending.

## Completed features

| Edition | What is shipped |
|---|---|
| **Community** | Offline-first POS, refunds/returns (idempotent), KDS, ESC/POS, invoices/receipts, cash/card/split payments, i18n (en/fr/ar), 5 theme variants + Theme Studio, roles, loyalty, scheduling, coupons, notes, support — 427 frontend tests + Rust suite green |
| **Standard** | Currencies, tax profiles, roles/permissions, CSV/JSON export, offline sync queue, node registry, loyalty — Rust/Diesel-first, optional Django sidecar |
| **Pro** | 45-resource Django Ninja API, fusion render-mode (HTMX/data dual contract), Unfold admin, KDS, QR menu, API keys + rate limits, mobile waiter, multi-terminal sync, offline queue, barcode, gaming (POS-KO), gift cards, tables, delivery, AI/inventory forecasting, scheduling, customer display, kiosk, purchase orders, CRM module |
| **Cloud** | BackupRun + `backup_db`, `/monitor/status`, cloud dashboard, tenant layer (Tenant/Domain/BranchSettings), sync queue/broker/conflicts, WebSocket parity contract — locally verified |
| **SDK** | `@formints/client` modular TypeScript fetch SDK: build + typecheck + tests green |
| **Testing** | Shared Playwright suite (`tests/pos-e2e/`, one project per edition), `tests/sync/` REST+WS+SDK contract suite, pytest/Vitest/cargo layers |

## Planned features

- **Cloud promotion** — staging deployment, `make verify-stack`, PostgreSQL
  schema-per-tenant flip-on (`django-tenants`, `08-tenant-schemas.md`).
- **pos-client completion** — cart/checkout UI end-to-end flows, E2E browser
  suite, publish.
- **Standalone Community repo** — bundle generator done; GitHub creation +
  push + release are owner actions.
- **SDK registry release** — owner action.
- **Cross-edition reconciliation** (`10-formint-audit…`) — claims truth gate,
  design-system contract, cloud promotion, pos-client completion, docs
  cleanup, release readiness (Phases 0–5).

## Missing features

| Gap | Evidence |
|---|---|
| pos-client browser cart/checkout | `05-pos-client.md` — dev status |
| Schema-per-tenant on PostgreSQL | `08-tenant-schemas.md` — SQLite-verified only (14 tests), flip-on pending |
| Standard browser/E2E suite | environment gate (desktop runtime) |
| Pro `make check`/`make test` gate | requires local `server/.venv` absent in checkout |
| Design-system adoption in Community/Standard | audit: package is a dependency but product code mostly uses local components/CSS |
| Public claims parity | Cloud landing uses `picsum.photos` placeholder and advertises only 3 editions |

## Technical debt

- **Three runtime shapes, five editions** — React+Rust desktop, Astro+Django
  web, Vue desktop: duplicated UI logic across stacks; the audit plan calls
  for narrowing the design-system contract or explicitly narrowing its claim.
- **Partial design-system adoption** — `@formints/design-system` vs local
  components/CSS; pick one contract per edition.
- **Stale documentation** — references to Robyn, RTK Query, old paths, and
  conflicting palettes remain; a docs truth pass is planned (audit Phase 4).
- **Theme fragmentation** — local FlyonUI theme layer + `perplexity` palette
  vs. the shared `projects/assets/theme` system; the POS theme (`fu-pos-*`)
  exists but editions have not migrated to it.
- **Hardcoded example credentials** — `.env.example` files carry generated
  defaults (documented as fresh-cluster-only); rotate before any public
  deployment.

---

# 3. LMS — Precis (`projects/structa.cloud/`) 🟢 live

> Unified product: marketing/catalog shell + learning platform on one Astro
> frontend and one Django 5.2 + Wagtail 7.4 + django-fusion backend.

## Completed features

| Area | What is shipped |
|---|---|
| Marketing/catalog shell | Landing, company, services, products, blog, pricing, brand, FAQ, privacy, AI-agents, contact pages |
| Learning | Course catalog + detail, enrollment, progress, profile, certificates (`backend/apps/learning`) |
| Content | Wagtail StreamFields on every editable section; `seed_pages`; `PageTranslation` EN/AR editorial overlays |
| Rendering | django-fusion `PageHandler` (full HTML + HTMX fragments), skeleton loading on both roads |
| Assistant | `AssistantPanel` wired through HTMX (assistant.astro) |
| Frontend quality | Dark mode (persisted, FOUC-free, cross-tab sync), minimal client JS (~30KB), multilingual |
| Backend tests | `apps.pages` tests green; `make e2e` smoke |

## Planned features

- **Full Playwright E2E** across learning + assistant flows.
- **Docker/Traefik production rollout gates** — explicitly listed as "not yet
  ported".
- **CMS/builder direction** (🟡) — multi-site path, site scaffolding, tenant
  isolation productization (`docs/precis/cms-builder.md`).

## Missing features

| Gap | vs. vision (product profile / PRICING) |
|---|---|
| Assessments (quizzes, exams, assignments, question banks) | partially shipped — verify per feature before claiming |
| Learning paths, discussions, AI tutor, advanced analytics | Professional tier |
| Communities, events, digital badges, CRM integration | Business tier |
| SCORM/xAPI, on-premise, dedicated support | Enterprise tier |
| Full browser E2E + production deploy path | "Not yet ported / next" |
| Syntara merge (AI assistant consolidation) | not started |

## Technical debt

- **Three marketing codebases** — `precis-main` shell, legacy
  `precis-landing/` copy (kept for the dispatcher alias), and Loop-CRM's
  Wagtail landing: consolidation candidate.
- **Dual CSS pipelines** — Tailwind `globals.css` + webpack/SCSS `fusion.css`
  (`make css` + `make build-assets`); two pipelines to keep in sync.
- **Stale plan paths** — resolved: Syntara merge plan deleted; Precis canonical
  is `projects/structa.cloud/`.
- **Theme engine not adopted** — `projects/assets/theme/lms/` exists
  (fu-lms-* tokens/components) but precis-main still styles locally via
  Tailwind + Fusion tokens; migration pending.
- **`@import` SCSS deprecation** — repo-wide convention, flagged by Dart Sass.

---

# 4. Landing Builder — Precis Builder vision 🔴 / building blocks 🟡

> Scope: the "Landing builder" capability sold in PRICING (Precis Builder
> Professional tier) and its live building blocks: Wagtail page system,
> theme engine, component library, dynamic template fields.

## Completed features (building blocks)

| Block | What exists |
|---|---|
| Content CMS core | Wagtail StreamField pages + `PageTranslation` in `precis-main`, `precis-ctc`, Loop-CRM `apps/pages` |
| Managed landing pipeline | Loop-CRM: `/cms/` editor → `/apis/pages/<slug>/` JSON → Astro render (shipped) |
| Reference deployments | structa.cloud (flagship), ctc-research.com (client site, EN/AR parity, publishing workflow) |
| Theme system | `projects/assets/theme/` — 13 themes, `fu-*` tokens, theme engine (`data-theme`/`data-brand`/dark mode), interactive `preview.html` |
| Component catalog | 40+ BEM components (`fu-*`) across default/lms/crm/pos themes + design-system variations |
| Dynamic templates | `django_fusion.template_fields` — **implemented** sandboxed `{{ variable }}` engine (parse/resolve/validate/escape/filter/preview, 14 filters) |
| Framework | django-fusion `{% comp %}`, fragments, `PageHandler`, render-first contract |
| **Landing Builder MVP** | `django_fusion.builder` — abstract `BuilderPage` (theme/brand/dark + `template_context` + section StreamField), `BuilderRenderer`, `/apis/builder/` JSON road, fu-* section templates, preview issue bar; reference mount in Loop-CRM (`apps.pages.BuilderPage`, `seed_builder`) |
| CMS direction | assets-based model documented (`docs/precis/cms-builder.md`); Solo/Business editions sold |

## Planned features

- **Precis Builder productization** — site scaffolding, theme switching UI,
  tenant isolation (`cms-builder.md`; wagtail-landing-plan Phases 5–8).
- **Vision modules** (PRICING Professional/Business): portal builder, dynamic
  forms, drag-and-drop, AI generation, SEO optimization, reusable components.

## Missing features

| Gap | Notes |
|---|---|
| Drag-and-drop / visual page assembly | no visual canvas — MVP is Wagtail StreamField assembly (thin by design) |
| Site scaffolding + tenant isolation | multi-site path documented, not shipped |
| Theme switching UI | **shipped in MVP** — per-page `theme`/`brand`/`dark_mode` fields render `data-theme`/`data-brand`/`.dark` |
| Dynamic forms | vision only |
| Front-end editing | Wagtail admin only; no in-page editor |
| Versioning/scheduling/review workflows | partial via Wagtail |
| Content API breadth | REST `/apis/pages/` + `/apis/builder/` only; no GraphQL |

## Technical debt

- **Fragmented landing codebases** — three Astro landing shells with
  duplicated sections; the builder targets one assembly layer, not three
  (adoption pending).
- **Theme system adoption gap** — the builder MVP is the first consumer
  (`django_fusion.builder` templates + `builder-theme.css`); CRM/POS/LMS
  product adoption still pending.
- **Claims/price book ahead of code** — PRICING sells builder tiers; the
  thin MVP now exists, but visual canvas, tenant isolation, and site
  scaffolding remain before the Professional-tier claims are honest.

---

# 5. Gap analysis

## Capability matrix (shipped vs. vision)

| Capability | CRM | POS | LMS | Landing Builder |
|---|:---:|:---:|:---:|:---:|
| Core domain CRUD | ✅ | ✅ | ✅ | ✅ |
| Multi-tenant isolation | ✅ | 🟡 (Postgres flip-on) | ❌ | ❌ |
| Billing/subscriptions | ✅ Stripe | 🟡 cloud | ❌ | ❌ |
| AI features | ❌ Phase 4 | 🟡 forecasting only | 🟡 assistant panel | ❌ |
| Real integrations | 🟡 6/12 social | 🟡 sync | ❌ | ❌ |
| Background tasks | ✅ Dramatiq | ✅ (Pro/Cloud) | ✅ tasks app | n/a |
| Theme engine adoption | ❌ | ❌ | ❌ | ✅ (library) |
| Dynamic template fields | ❌ | ❌ | ❌ | ✅ (spec only) |
| E2E browser coverage | 🟡 scoped | 🟡 env-gated | ❌ | ❌ |
| Production deployment evidence | 🟡 demo-level | 🟡 staging | ❌ gates open | 🟡 CTC live |

## The single biggest gap

**The theme engine + component library + dynamic template system are
complete and unused by products.** Wiring CRM, POS, and LMS onto
`projects/assets/theme` would simultaneously fix the POS design-system
fragmentation, the LMS dual-CSS pipelines, and give Landing Builder its
first real consumer.

---

# 6. Risk analysis

## Risk register

| # | Risk | L | I | Level | Mitigation |
|---|---|:---:|:---:|:---:|---|
| R1 | Marketing claims ahead of code (pricing pages sell vision tiers; POS landing uses placeholder imagery, advertises 3 editions) | High | High | 🔴 | Claims truth gate in Formint audit Phase 0; gate PRICING on shipped features |
| R2 | Production deploy evidence thin (LMS rollout gates open, Cloud staging-only, CRM verified at demo level) | Med | High | 🔴 | LMS Docker/Traefik gates; Cloud `verify-stack` + staging deploy; CRM staging environment |
| R3 | Multi-stack POS divergence (3 runtimes, 5 editions) raises maintenance cost and bug drift | High | Med | 🟠 | Narrow design-system contract per edition; feature inheritance parity sweeps |
| R4 | Duplicated surfaces (two API roads, dual task logs, dual CSS, three landing shells) | Med | Med | 🟠 | Consolidation plan: deprecate `/api/v1` compat, single task log, one landing shell |
| R5 | Secrets hygiene (example credentials in `.env.example`, dev DBs in checkout) | Med | Med | 🟠 | Rotate before any public deploy; enforce no-commit of artifacts |
| R6 | AI features promised but absent (CRM Phase 4, LMS tutor, builder AI generation) | Med | Med | 🟠 | Sequence AI behind provider-neutral layer (`django-fusion LLM & AI MCP plan`) |
| R7 | Syntara merge stalls → two AI chat runtimes persist | Med | Low | 🟡 | Prioritize the planned merge; single Assistant surface |
| R8 | Tenant/schema work blocks SaaS ambitions (CRM multi-tenant OK; LMS/Builder none; POS pending) | Med | Med | 🟠 | POS flip-on first; reuse pattern for LMS/Builder |

**L** = likelihood, **I** = impact (of the unmitigated risk).

---

# 7. Recommendations

## P0 — do first (blocker class)

1. **Claims truth pass (R1).** Execute Formint audit Phase 0–1: reconcile
   every public claim (pricing, POS landing, product profiles) with shipped
   code; remove placeholder imagery; tag vision tiers as "planned" in public
   copy.
2. **LMS production gates (R2).** Ship the Playwright E2E suite and the
   Docker/Traefik rollout so the flagship product has a deployable path and a
   rollout checklist (mirror `docs/guides/04-deploy.md`).
3. **Secrets/artifacts hygiene (R5).** Rotate example credentials, remove
   committed dev databases from checkouts, and enforce `.gitignore` rules in
   CI.

## P1 — next quarter

4. **POS Cloud promotion.** Postgres schema-per-tenant flip-on →
   `make verify-stack` → staging deploy; finish pos-client cart/checkout
   flows (closes the 🟡 finish board).
5. **CRM AI hub + adapters.** Implement Phase 4 (lead scoring, drafting,
   generation) behind provider adapters; promote the 6 catalog adapters as
   credentials land.
6. **Landing Builder MVP (R8/R4 lever).** ✅ **Shipped** — `django_fusion.builder`
   (abstract `BuilderPage`, `BuilderRenderer`, `/apis/builder/` JSON road,
   fu-* section templates, preview bar) + `django_fusion.template_fields`
   engine, mounted in Loop-CRM (`apps.pages.BuilderPage`, `seed_builder`).
   Next: visual canvas, tenant isolation, and adoption by the other landing
   shells.

## P2 — consolidation (debt paydown)

7. **Theme engine adoption.** Wire CRM, POS, and LMS onto
   `projects/assets/theme` (per `migration-guide.md` in `docs/design/`) —
   retires POS local themes, LMS dual CSS, and CRM's Tactical Telemetry
   drift in one move.
8. **Single API road + single task log.** Deprecate `/api/v1` compatibility
   once Bolt consumers migrate; merge the dual task storage or document it as
   a permanent boundary.
9. **One landing shell.** Decommission the legacy `precis-landing` copy and
   fold Loop-CRM's landing into the shared assembly layer.
10. **Docs truth pass.** Fix stale paths (`precis-lms` references), POS
    legacy mentions (Robyn/RTK Query), and sync the audit statuses with
    `docs/plans/README.md` and `docs/startup/product-profiles.md`.

## Suggested tracking

| Initiative | Owner | Plan link |
|---|---|---|
| Claims truth gate | Product + engineering | `docs/plans/editions/10-formint-audit-and-reconciliation-2026-08-22.md` |
| LMS rollout gates | Precis | `docs/plans/precis-landing.md` (extension) |
| POS Cloud promotion | Formints | `docs/plans/editions/04-cloud.md`, `08-tenant-schemas.md`, `09-completion-plan.md` |
| CRM AI + adapters | Loop-CRM | `docs/plans/loop-crm/merge-plan.md` §12 |
| Landing Builder MVP | Precis/Builder | `docs/precis/cms-builder.md` (direction) |
| Theme adoption | Workspace | `docs/design/migration-guide.md` |

---

# 8. Verdict

| Product | Verdict |
|---|---|
| CRM | Strong foundation, honest partials, clear roadmap — ship AI + adapters before selling AI |
| POS | Best-tested product family; finish Cloud promotion + claims parity |
| LMS | Solid core; production readiness and the Syntara merge are the gates |
| Landing Builder | 🟢 Thin MVP shipped (Wagtail assembly + theme picker + dynamic fields + JSON road, Loop-CRM reference). Next: visual canvas, tenant isolation, shell adoption |

## Remarks & Notes

- Statuses follow the legend in `docs/startup/product-profiles.md` (🟢 live ·
  🟡 beta/partial · 🔴 vision).
- Audit findings that change a plan or claim must be recorded in
  `docs/plans/README.md` and this report updated in the same change.
- Live DNS, deployment health, analytics, and production browser behavior
  require operator/staging checks; this report certifies the repository, not
  production.
