# Loop-CRM — Wagtail Landing, Subscription/Billing, and Webapp Enhancement Plan

> **Status:** Phases 0–4 shipped (2026-08-18) · Phases 5–8 planned
> **Date:** 2026-08-18
> **Canonical path:** [`projects/loop-crm/`](../../../projects/loop-crm/)
> **Related:** [`merge-plan.md`](merge-plan.md) · [`projects/loop-crm/docs/DESIGN_SYSTEM.md`](../../../projects/loop-crm/docs/DESIGN_SYSTEM.md) · [`docs/plans/editions/08-tenant-schemas.md`](../editions/08-tenant-schemas.md) · [`libs/django-fusion/docs/06-forms-and-tables.md`](../../../libs/django-fusion/docs/06-forms-and-tables.md)

<!-- AI-generated: review needed -->

---

## 1. Context

Loop-CRM is the unified sales + marketing platform (Twenty DNA + Postiz DNA) on
Django + django-fusion. Today it has two surfaces:

1. **Public landing (Astro):** `frontend/src/pages/index.astro` is a fully
   hard-coded marketing page. `terms.astro` / `privacy.astro` are static.
   Content changes require code edits — there is no editor path.
2. **Authenticated webapp (Astro + Bolt):** `frontend/src/pages/[...path].astro`
   is the app shell (31 routes). It reads the canonical **Bolt API** (`/bolt/`,
   JWT bearer via `BoltApiClient`) with a `/api/v1/` session-cookie fallback.
   Login is allauth at `/accounts/login/`; `LOGIN_REDIRECT_URL = /overview/`.

The backend has **no Wagtail**. `INSTALLED_APPS` in
`backend/configs/default/__init__.py` lists Django, Channels, django-fusion,
allauth, tables2, dramatiq and the domain apps (`core`, `crm`, `marketing`,
`attribution`, `finance`, `pos`). Wagtail is already available in the workspace
(`projects/pyproject.toml` pins `wagtail>=7.4.2`); **django-tenants is not**
(present nowhere in `projects/pyproject.toml`).

Tenancy today is **row-level**: `core.Workspace` is the multi-tenant root and
`apps/core/tenancy.py` (`current_workspace_id`) scopes every read/write path.
Billing/subscriptions do not exist yet — `apps/finance` (`Invoice`, `Payment`,
`RevenueEvent`) models the CRM product's own finance ledger, not SaaS billing
for the workspace itself.

The repo reference for a Wagtail-managed public site with an Astro shell is
**precis-landing** (`projects/precis/precis-landing/`): Wagtail page models in
`backend/apps/pages/`, StreamField blocks in `backend/apps/content/blocks.py`,
a `/apis/pages/<slug>/` JSON road consumed by Astro, and `seed_pages.py`.

## 2. Page flow check (current routes)

| # | Step | Route | Surface | Auth | Source |
|---|---|---|---|---|---|
| 1 | Landing | `/` (`index.astro`) | Astro public | none | hard-coded copy |
| 2 | Legal | `/privacy/`, `/terms/` | Astro public | none | static copy |
| 3 | Login/signup | `/accounts/login|signup|logout/` | Django (allauth) via Astro proxy | — |
| 4 | Profile | `/account/profile/` | Django | session | allauth + RBAC |
| 5 | Webapp | `/overview/`, `/crm/*`, `/marketing/*`, `/finance/*`, `/attribution/*`, `/settings/*`, `/tasks/` | Astro shell | session → JWT | `/bolt/*` (BoltApiClient) or `/api/v1` |
| 6 | Data tables | `/bolt/tables/{resource}` · `/api/v1/tables/{resource}/` | JSON API | JWT / cookie | `resource_tables.py` |
| 7 | HTMX fragments | `/fragments/navigation/`, `/fragments/workflows/*`, `/fragments/posts/*`, `/fragments/crm/*`, `/fragments/finance/*`, `/fragments/marketing/*` | Django HTML | session | fusion components |
| 8 | Admin | `/admin/` (Django) | Django | staff | model admins |

**Gaps found by the check:**
- The landing has no editor path (Wagtail absent) and pricing tiers are
  hard-coded while the webapp has no plan/subscription surface.
- Public landing CTAs point at `/accounts/*` only; there is no
  "pricing tier → checkout" flow.
- No `/apis/*` road exists on the backend for the public pages.
- `/settings/*` covers members/integrations/workflows but not
  billing/subscription, employee/report surfaces, or a report catalog.

## 3. Target architecture

```text
Public road (no auth)                          Authenticated road (login required)
─────────────────────────                      ────────────────────────────────────
Astro (frontend/)                              Astro app shell ([...path].astro)
├─ index.astro    → /apis/pages/home/          ├─ BoltApiClient → /bolt/* (JWT bearer)
├─ pricing.astro  → /apis/pages/pricing/ +     └─ fallback      → /api/v1/* (cookie)
│                    /apis/billing/plans/          ↓
├─ faq.astro      → /apis/pages/faq/          Django backend (:8001 dev)
├─ privacy/terms  → /apis/pages/…               ├─ /bolt/  django-bolt (canonical)
        ↓ proxy (/apis → backend)               ├─ /api/v1/* compatibility road
Django backend                                  ├─ /accounts/* allauth
├─ Wagtail admin  /cms/  (editors)              └─ /billing/* checkout + webhooks
├─ apps/pages (LandingPage, HomePage, …)           after login → /overview/ webapp
├─ apps/content (StreamField blocks)              webapp side: /settings/plan,
├─ /apis/pages/<slug>/  public JSON road          /reports/*, /employees/*
└─ /apis/billing/plans/  tier catalog             → Stripe (checkout + webhook)
```

Two roads, one product — the precis-landing "render-first/data-API" contract.
The **public** road is Wagtail-managed content + a billing plan catalog served
as JSON and rendered by Astro; the **authenticated** road is the webapp driven
by Bolt with a new billing/subscription + reports + employees surface. Astro
keeps owning every public URL; Wagtail never serves HTML at `/` or the app
paths, so there is no routing conflict with `[...path].astro` or the
django-fusion `LoopCrmModule` route tree.

## 4. Options considered

1. **Full precis-landing clone — Wagtail serves HTML directly (fusion road) too.**
   Rejected: would duplicate the existing django-fusion module routes and
   complicate the Astro proxy. The public road only needs editor-managed
   *content*, not server-rendered public HTML.
2. **Keep hard-coded Astro landing + Wagtail snippets for copy.**
   Rejected: leaves page *structure* uneditable; doesn't match the ask.
3. **Wagtail page models + `/apis/pages/` JSON road + Astro renders.**
   **Accepted** — mirrors precis-landing, keeps Astro as the single public
   renderer, leaves the Bolt webapp untouched.
4. **Schema-per-tenant via django-tenants for subscriptions.**
   Evaluated — see §6. Not required for billing; deferred as an optional
   enterprise phase.
5. **SaaS billing on the existing `apps/finance` models.**
   Rejected — `finance` is the product's revenue ledger (invoices issued by
   customers). SaaS billing gets a dedicated `apps/billing` with a
   subscription model and Stripe sync (§7).

## 5. License removal (do first, independent)

The product advertises **AGPL-3.0** in four places:

| Location | Content |
|---|---|
| `frontend/src/pages/index.astro` (DNA band) | `License / AGPL-3.0` item |
| `frontend/src/pages/index.astro` (hero note) | `Open source (AGPL-3.0) · built from the Twenty and Postiz DNA` |
| `frontend/src/pages/index.astro` (footer) | `<span>AGPL-3.0</span>` under Legal |
| `frontend/src/pages/terms.astro` | Three license paragraphs |
| `docs/plans/loop-crm/merge-plan.md` (header) | `**License:** AGPL-3.0` — consistency update |

**Decision:** remove every license claim from product pages and terms; replace
the terms copy with plain SaaS terms (lawful use, credentials, tenant
responsibility, no warranty) without any license grant. No `LICENSE` file
exists inside `projects/loop-crm/` — nothing to delete there.

## 6. Tenancy analysis: row-level workspaces vs django-tenants

**Checked:** django-tenants is **not** in the workspace deps. The only
tenant-schemas plan in the repo is `docs/plans/editions/08-tenant-schemas.md`,
and it belongs to the **Formints editions** (`Organization` + `Branch` +
`BranchSettings`), not Loop-CRM.

**Loop-CRM today:** row-level tenancy — `Workspace` on every domain record,
scoped through `apps/core/tenancy.py`, enforced on all three roads
(render-first screens, `/api/v1/`, `/bolt/`). This works and is verified by
tests; switching to PostgreSQL schema-per-tenant would require:

- `django-tenants` added to `projects/pyproject.toml` (new dependency),
- `SHARED_APPS` / `TENANT_APPS` split and `django_tenants.postgresql_backend`,
- `migrate_schemas --shared` / `--tenant`, a public-schema seed + domain model,
- data backfill from row-scoped records into per-schema copies,
- reworking `tenancy.py`, allauth adapters, Bolt auth, and every query that
  currently filters `workspace_id=`,
- **PostgreSQL required** — SQLite dev default breaks, and the Redis-free /
  SQLite dev story (README notes) goes away.

**Recommendation:** keep row-level `Workspace` tenancy as the architecture.
Billing/subscriptions need a subscription *model* and a payment provider, not
schema isolation — a `BillingAccount` per `Workspace` with plan + status
delivers the same gate. Schema-per-tenant is **deferred** to an optional
enterprise phase: adopt only if a paying customer requires hard isolation or
regulatory segmentation, and then follow the Formints edition plan
(`08-tenant-schemas.md`) as the migration reference (Tenant 6–7 pattern:
registry → backfill → `migrate_schemas` → per-tenant queries), with Loop-CRM's
`Workspace` playing the `Organization` anchor role.

## 7. Payment & subscription architecture (landing → checkout → workspace)

**Goal:** the landing's pricing tiers (Wagtail-managed, §9) drive a real
checkout; a purchased plan activates the workspace and gates seat/feature
limits in the webapp.

**Provider:** **Stripe** (industry standard for SaaS billing; Python SDK,
webhooks, trials, seat-based pricing). Alternative: LemonSqueezy when a
Merchant of Record (auto VAT/sales-tax) is preferred. Integration reference
from the Gravity Index search `f6a2366e-3274-49b8-860d-bee6ab0e9eb3`.

**New app `apps/billing`:**

- **Models** (all workspace-scoped, mirroring `core` patterns):
  - `Plan` — slug, name, price_cents, period (`monthly|annual`), seat_limit,
    feature flags (attribution, finance ledger, workflow automation, …),
    Stripe price IDs per period, `is_active`. Seeded from a catalog; the
    Wagtail pricing page stays editorial (marketing copy) while `Plan` is the
    source of truth for limits (the "relative data" contract: pricing copy in
    Wagtail, enforceable limits in `apps/billing`).
  - `BillingAccount` — 1:1 with `Workspace`; `plan` FK, `status`
    (`trial|active|past_due|canceled`), `stripe_customer_id`,
    `stripe_subscription_id`, trial end.
  - `Seat` — user ↔ workspace seat count for seat-limited plans.
- **Roads:**
  - `POST /billing/checkout/` — authenticated; creates a Stripe Checkout
    Session for the selected plan (`mode=subscription`, per-seat quantity);
    returns the session URL. Landing "Start free"/tier CTAs route here after
    login (anonymous → `/accounts/signup/` → checkout).
  - `POST /billing/webhook/stripe/` — `csrf_exempt`, verifies
    `STRIPE_WEBHOOK_SECRET`, handles `customer.subscription.updated`,
    `invoice.payment_succeeded`, `customer.subscription.deleted` → updates
    `BillingAccount.status` + seats; on `payment_succeeded` also writes a
    `finance.RevenueEvent` (recognized SaaS revenue — bridges SaaS billing to
    the existing ledger without reusing Invoice/Payment).
  - `GET /billing/portal/` — Stripe Billing Portal session for self-service
    plan change / cancellation.
  - `GET /apis/billing/plans/` — public tier catalog for the landing
    (prices, cadence, feature bullets, `checkout` href) so the Wagtail pricing
    copy and the plan data render together.
  - Webapp: new `/settings/plan/` page (current plan, seats, usage, upgrade /
    cancel via portal) — added to `[...path].astro` route catalog.
- **Env contract:** `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`,
  `STRIPE_WEBHOOK_SECRET` added to `configs/env.py` (the 56-var catalog) and
  `.env.example`; empty values disable checkout with an honest
  "billing not configured" state.
- **Feature gating:** `BillingAccount.status == active|trial` gates
  `settings/` features; seat limits checked on member invite; over-limit
  requests surface the upgrade CTA. Keep gates in one module
  (`apps/billing/gates.py`) so every road shares them.
- **Seed:** demo workspace gets a trial `BillingAccount` so the webapp works
  before any Stripe keys exist.

## 8. Design decision (visual system + precis-landing theme)

The repo's `structa-industrial-ui` skill (Swiss Industrial Print, light paper
substrate) applies to `projects/precis/*/frontend`. **Loop-CRM has its own
active design system** — `projects/loop-crm/docs/DESIGN_SYSTEM.md` (Tactical
Telemetry / CRT terminal: dark substrate, mono-led, hazard red, zero radius,
ASCII framing). This plan **keeps the Loop-CRM design system** for the landing
and the webapp. Documented drift: Loop-CRM deliberately overrides the light
substrate of `structa-industrial-ui`.

**"Theme of precis-landing" = structural parity, not visual parity.** Adopt
precis-landing's *pattern*: Wagtail page models + StreamField section blocks +
`/apis/pages/<slug>/` road + `seed_pages` + a slim Home page that hands off to
fuller pages. Reuse precis-landing's block *shapes* (`HeroBlock`, `CtaBlock`,
`FeaturesSectionBlock`, `PricingSectionBlock`, `FaqSectionBlock`,
`StatsSectionBlock`, `ButtonBlock`/`LinkBlock` with page-chooser resolution)
but render them with the existing `loop-*` BEM classes and CRT tokens, so the
public road and the app shell look identical.

## 9. Landing theme parity with precis-landing (public pages)

| precis-landing pattern | Loop-CRM adoption |
|---|---|
| `apps/pages/models.py` — `LandingPage` (hero+cta) abstract base | Same, trimmed to Loop-CRM sections |
| `HomePage` slim (hero + CTA) → `AboutPage` full document | `HomePage` (hero, DNA band, modules, steps, pricing, CTA) — single page for now; About/pricing/faq pages follow |
| `apps/content/blocks.py` StreamField blocks | Same block shapes, `loop-*` classes, CRT tokens |
| `/apis/pages/<slug>/` JSON road + `_stream_to_plain`/`_button_to_dict` | Port the helpers; flatten section items for Astro |
| `seed_pages.py` management command | `apps/pages/management/commands/seed_pages.py` + `make backend-seed-pages` |
| Wagtail admin at `/admin/` vs Django `/django-admin/` | Wagtail at **`/cms/`**, Django admin stays at `/admin/` (no collision) |
| Astro proxy `/apis` → backend | Add `/apis` to `frontend/astro.config.mjs` proxy table |
| No hard-coded fallback when API is down | Skeleton/empty state, never resurrect hard-coded copy |

Wagtail-managed pages: **Home**, **Pricing** (editorial copy + `/apis/billing/plans/` data), **FAQ**, **Privacy**, **Terms** — the pages that exist today. `index.astro`/`pricing.astro`/`faq.astro` become data-driven renderers.

## 10. Webapp sidenav enhancements

Current: `AppShell.astro` loads `/fragments/navigation/` (HTMX), caches in
sessionStorage, updates active state; groups come from `apps/core/navigation.py`
+ `frontend/src/lib/navigation.ts`.

Enhancements (all respecting the CRT design system):

1. **Collapsible groups** — chevron toggle per module group, persisted to
   sessionStorage (matches the existing cache pattern).
2. **Workspace switcher** — top block listing the user's workspaces (from
   `/bolt/workspaces` or the profile API), current workspace highlighted.
3. **Command palette (Ctrl/Cmd+K)** — fuzzy search over the 31 routes + quick
   actions (create company/deal/post), keyboard-driven, `dropdown-menu`/`sheet`
   primitives reused.
4. **Badge counts** — pending approvals (`/marketing/approvals/`), open
   invoices, running tasks from the real APIs (Bolt), rendered as hazard-red
   mono counters; refreshed via `useWorkspaceRealtime`/SSE.
5. **Active-section auto-expand** — the module containing the current path
   expands by default.
6. **Footer user card** — avatar (exists in `ui/`), name/role, "Sign out",
   "Profile", and the plan chip (`BillingAccount.plan`) with an upgrade link
   when on trial.
7. **"Launch app" affordance on the landing** — the public nav keeps
   "Sign in/Start free"; logged-in users hitting `/` see a "Open workspace →"
   link (server-driven via `/apis/auth/status/` or allauth session).

## 11. Backend admin panels + frontend full APIs (animated, guided)

**Backend — two admin panels unfold:**
- **`/admin/` (Django admin, unchanged):** domain models, users, RBAC, audit —
  existing surface.
- **`/cms/` (Wagtail admin, new):** editors manage landing pages, pricing copy,
  FAQ, legal pages, navigation labels. Wagtail `Site` + root `HomePage` wired
  on migrate/seed. Everything Wagtail exports is also exposed through
  `/apis/pages/<slug>/`, so the two roads never diverge.

**Frontend — full APIs with animated + guided UX:**
- **Guided onboarding tour** — first login (after `/overview/`): a step overlay
  (backed by `sheet` + `tooltip` primitives) walking through nav, the resource
  table, and the first-create flows; progress stored per user (a `core`
  profile flag or local preference API). Respects `prefers-reduced-motion`.
- **Animated empty/loading states** — `skeleton.tsx` + `loop-*` shimmer for
  Bolt-loaded tables; `htmx-indicator` for fragment swaps; reveal transitions
  reuse the existing mechanical motion law (opacity/translate, 0.15–0.25s).
- **Guided create flows** — the existing `/fragments/*/create/` forms get a
  stepped, animated modal flow (django-fusion form → fragment swap into a
  `sheet`), with validation errors inline.
- **Command palette** doubles as the guided index (routes + actions).
- Keep every animated layer SSR-safe and a11y-correct (focus trap in the tour,
  ARIA live regions for badge updates).

## 12. Astro interactivity & interactive components (inventory + gaps)

**Current inventory (from `frontend/src/components/`):**

| Component | File | Type | Feature status |
|---|---|---|---|
| AppShell | `AppShell.astro` | shell + HTMX nav | ✅ shipped |
| PipelineBoard (kanban) | `board/PipelineBoard.tsx` | React + Redux | ✅ shipped (move mutation CSRF-protected) |
| RevOpsDashboard | `dashboard/RevOpsDashboard.tsx` | React | ✅ shipped (revenue-trend + funnel links) |
| ResourceTable | `dashboard/ResourceTable.tsx` | React, bolt-first | ✅ shipped (schema-aware tables) |
| PipelineDemo | `demo/PipelineDemo.tsx` | React (landing) | ✅ shipped (hard-coded demo data) |
| StoreProvider | `StoreProvider.tsx` | Redux root | ✅ shipped |
| `ui/` primitives | avatar, badge, button, card, dropdown-menu, input, label, separator, sheet, skeleton, tooltip | shadcn-style | ✅ shipped, **underused** |
| lib: boltApi, navigation, useLiveSync, useWorkspaceRealtime, icons, utils | `lib/` | clients/helpers | ✅ shipped |

**Gaps (components missing / not yet feature-wired):**
- **No command palette / search** component (add — routes + records search via
  Bolt).
- **No onboarding tour / guided overlay** component (add).
- **No report catalog UI** (add — see §14).
- **No billing/plan UI** (add — `/settings/plan/`).
- **`ui/` primitives underused** — kanban/dashboard/tables mostly hand-rolled
  `loop-*` CSS; adopt primitives for dropdowns, tooltips, sheets in new
  surfaces (keep the CRT token contract).
- **No employee directory** component (add — see §14).
- PipelineDemo is the only landing interactivity; move it to a data-driven
  component once `/apis/pages/home/` exists (or keep as a self-contained
  animation — decide in Phase 3).

## 13. Feature/component analysis: what has integrations, what could

| Surface | Data source | Integration today | Integration candidate |
|---|---|---|---|
| Resource tables | `/bolt/tables/{resource}` | Bolt + `/api/v1` | ✅ none needed |
| Kanban move | `/bolt/deals/...` + CSRF fragment | Bolt | ✅ — |
| Publishing calendar | `Post` records | provider-neutral connector surface (`apps/marketing`) | LinkedIn/X/Gmail/Outlook OAuth adapters (already planned in merge-plan; credential-blocked) |
| Payments (product ledger) | `apps/finance` | — | Stripe **SaaS** billing webhook → `RevenueEvent` (§7) |
| Workflows | `core.WorkflowDefinition/Run` | Dramatiq + Slack webhook | Email notify, webhook actions (partial) |
| Realtime | SSE/WS (`apps.core.realtime`) | Channels + Redis/InMemory | Live badge counts + collaborative presence |
| Members/RBAC | `core.UserProfile` + roles | — | Seat enforcement from `BillingAccount` (§7) |
| Custom objects/fields | `custom_attributes` + catalog | — | Employee records (§14) |
| Audit | `core.AuditLog` | — | Report: audit trail export (CSV exists) |
| Search | none (no search surface) | — | **Cmd+K** global search over companies/contacts/deals/posts/employees via Bolt |

**User-created data** already exists (`custom_attributes`, custom-object
catalog, saved views, CSV import). The employee/report surfaces below are the
primary new consumers of user-created data.

## 14. Employee search + employee reports + report catalog

Loop-CRM has no `Employee` model; members live on `core.UserProfile` and
people records on `crm.Contact`. The request: **user-created data → search
employees → track employee reports → a list of reports.**

**Decision — model employees as a **custom object** (`settings/custom-objects`
already ships the runtime schema): a workspace can create an `Employee` record
type (name, department, manager, join date, KPI fields) without a migration.
This is the fastest path and reuses the existing custom-field validation.

- **Employee directory surface:** `/employees/` route in `[...path].astro`
  (new module group "People" or under Workspace), rendered with
  `ResourceTable`-style schema-aware tables from `/bolt/tables/employees/`.
- **Employee search:** Cmd+K palette searches employees (plus companies,
  contacts, deals, posts) through a new `/bolt/search/?q=` endpoint that
  federates registered resources with the tenancy scope; results open the
  record page.
- **Employee reports:** per-employee report page `/employees/<pk>/report/`
  aggregating from user-created fields + existing activity data: activities
  logged, deals touched (from `crm.Activity`/`Deal` ownership), posts approved,
  invoices created — a "performance dossier" per member.
- **Report catalog — a list of reports** at `/reports/`:

| Report | Source data | Road |
|---|---|---|
| Revenue trend | `finance.RevenueEvent` (already on `/bolt/revenue/trend`) | ✅ exists |
| Attribution models | `attribution` engines | ✅ exists (`/attribution/reports/`) |
| Audit trail | `core.AuditLog` (CSV export exists) | ✅ exists |
| Pipeline forecast | `crm.Deal` stage × probability | new page (data ready) |
| Publishing analytics | `marketing.PostAnalytics` | new page (data ready) |
| Employee activity/performance | activities + deals + posts + custom KPI fields | new (§14) |
| SaaS billing / seats | `apps/billing` | new (§7) |

- `/reports/` lists all of the above with a description, owner module, and
  export affordance (CSV); each report is a route in the Astro catalog.

## 15. django-fusion forms & tables — docs to complete

The framework already documents forms/tables:
`libs/django-fusion/docs/06-forms-and-tables.md` and
`COMPONENT_FORMS_TABLES.md`. What's missing is **product-level documentation
for Loop-CRM's usage**. Add `projects/loop-crm/docs/FUSION_FORMS_TABLES.md`
covering:

- The `{% comp %}` form/table component overrides in
  `backend/templates/fusion/components/form.html` + `table.html` and why
  DIRS-before-APP_DIRS shadowing matters; single-line `{% comp %}` tag rule.
- `apps/core/resource_tables.py` — `RowGenerator` + `resource_table()` contract
  (headers with type metadata `text|money|date|pill|link`, formatted rows,
  count) consumed by the Django screens and both API roads.
- The Bolt road (`GET /bolt/tables/{resource}`, JWT, workspace-scoped) and the
  compat road (`/api/v1/tables/{resource}/`, session cookie).
- The frontend `ResourceTable.tsx` renderer (bolt-first, `/api/v1` fallback,
  per-road path shape) and how a new resource (employees, §14) is added:
  model → `tables.py` → `resource_tables.py` → `/bolt/tables/` → page map in
  `[...path].astro`.
- Form flows: `create` fragments (companies/contacts/deals/invoices/payments/
  posts), CSRF cookie contract (`X-CSRFToken`), HTMX swap targets.
- Link, don't duplicate — point at the framework docs for component API
  reference and keep Loop-CRM specifics here.

## 16. Translations & shared locale (i18n)

**Current state (audited 2026-08-18, excluding `.venv` / `node_modules`):**

- **Loop-CRM has no `locale/` dir.** `LANGUAGES` (en/ar), `LocaleMiddleware`
  and `LOCALE_PATHS` are already configured in
  `backend/configs/default/__init__.py`, but no catalogs exist and `make i18n`
  has never produced them. The frontend has no i18n layer (`src/i18n` and
  `src/locales` do not exist) — matching the remaining todo list in
  `docs/changelogs/session-2026-08-18.md`.
- The monorepo keeps **per-project catalogs in two different layouts**:
  - LC_MESSAGES dirs: `projects/precis/precis-main/backend/locale/<lang>/LC_MESSAGES/django.{po,mo}`
    (en, ar, de, es, fr, pt, sv) and `projects/precis/precis-landing/backend/locale/<lang>/LC_MESSAGES/`
    (ar, de, pt, sv, …).
  - **Mixed flat + dir (messy):** `projects/precis/precis-lms/assets/locale/`
    and `projects/precis/precis-ctc/assets/locale/` hold flat `<lang>.po`
    files **and** `<lang>/LC_MESSAGES/django.{po,mo}` dirs (duplicated
    catalogs in one tree).
- **`projects/assets/locale/` already exists as the shared target** (only a
  `.gitkeep` today). Per the repo map in the root `AGENTS.md`, `projects/assets/`
  is the monorepo-level shared assets dir — a shared catalog belongs there.

**Decision — consolidate into one shared catalog:**

1. **Merge target:** `projects/assets/locale/<lang>/LC_MESSAGES/django.{po,mo}`
   — one canonical layout for every language across the monorepo.
2. **Merge sources:** every per-project catalog found above plus any
   archived/legacy project locale dirs in the repo — **excluding `.venv`,
   `node_modules`, `dist`, collected static, and vendored deps**. Reconcile the
   mixed flat/`LC_MESSAGES` layouts (flat `<lang>.po` →
   `<lang>/LC_MESSAGES/django.po`); merge duplicate msgids per language across
   sources (later project wins, then manual review of conflicts).
3. **Change `LOCALE_PATHS` at each Django backend project** to the shared dir.
   Loop-CRM: `LOCALE_PATHS = [BASE_DIR.parents[2] / "assets" / "locale"]`
   (`BASE_DIR` = `projects/loop-crm/backend` → `parents[2]` = `projects/`,
   so the path resolves to `projects/assets/locale`). Keep each backend's
   `LANGUAGES` as its advertised set; the shared dir holds the merged catalogs.
4. **Complete compilation:** one `python manage.py compilemessages` pass (or
   `django-admin compilemessages -l …`) against `projects/assets/locale/` so
   **all languages compile** — no backend left without a compiled `.mo` for
   its advertised `LANGUAGES`. This completes the locale task repo-wide.
5. **Loop-CRM translations (scope of this plan):**
   - Backend `gettext_lazy` sweep: remaining models (`attribution`, `core`,
     `pos`), forms labels/help_text, view messages, `fusion.py` page
     titles/kickers/descriptions, templates `{% trans %}` (`crm`/`marketing`/
     `finance` models are already converted per the session changelog).
   - `make i18n` = makemessages against the shared dir + compilemessages for
     en/ar (extend the backend Makefile `i18n` target to target
     `projects/assets/locale`).
   - Frontend i18next layer: `src/i18n/` en/ar catalogs, route hardcoded UI
     strings through `t()`, a locale switcher — mirror the translation flow in
     `docs/ai/templates-and-request-flows.md`.
   - Wagtail landing blocks use `gettext_lazy` labels; block content is
     translatable through the `/apis/pages/<slug>/?lang=` overlay pattern
     (precis-landing `PageTranslation` reference, §9).

## 17. Implementation steps (phases)

### Phase 0 — Remove license (small, first PR) — ✅ shipped
- `index.astro`: delete DNA `License` item, `AGPL-3.0` hero note, footer
  `<span>AGPL-3.0</span>`; `terms.astro` + `privacy.astro`: SaaS copy;
  `merge-plan.md` header line; grep clean (excludes `package-lock.json`
  third-party metadata + `dist/` artifacts). Verified with `npm run check`.
  New seed copy carries a test guard (`apps/pages/tests.py`).

### Phase 1 — Add Wagtail to the backend — ✅ shipped
- `INSTALLED_APPS` += `wagtail*` apps + `apps.pages` + `apps.content`;
  `WAGTAIL_SITE_NAME` + `WAGTAILADMIN_BASE_URL`; `urls.py` mounts `/cms/`
  (admin + documents + images), trailing Wagtail catch-all for editor
  previews only; `migrate` + `make backend-check` green.

### Phase 2 — Wagtail page models + content blocks — ✅ shipped
- `apps/content/blocks.py` (Hero, DNA band, CTA, Features, Steps, Stats,
  Pricing, FAQ, Button/Link with page chooser); `apps/pages/models.py`
  (`LandingPage` abstract, `HomePage`, `PricingPage`, `FaqPage`, `PrivacyPage`,
  `TermsPage`); migration `apps/pages/0001_initial`; Wagtail preview templates
  `backend/templates/pages/{base,home,pricing,faq,privacy,terms}.html` +
  `partials/`.

### Phase 3 — Public JSON data road + Astro landing — ✅ shipped
- `apps/pages/api.py` — `page_data_api` + `page_list_api` (port
  `_stream_to_plain`, `_button_to_dict`, `_normalize_page_links`,
  `_page_to_dict`; sections also expose `<field>_head` = editor-managed
  section headings); mounted at `/apis/pages/<slug>/` + `/apis/pages/`;
  `astro.config.mjs` proxy += `/apis` `/cms` `/documents` `/images` and
  `PUBLIC_BACKEND_URL` define; `index.astro` + new `pricing.astro`/
  `faq.astro` + `privacy.astro`/`terms.astro` fetch and render from JSON via
  `src/lib/landing.ts` + shared `LandingLayout.astro` and landing section
  components; explicit empty state (no hard-coded fallback).

### Phase 4 — Seed + Makefile — ✅ shipped
- `apps/pages/management/commands/seed_pages.py` (idempotent, replaces the
  Wagtail default placeholder HomePage, `--refresh` restores seeded copy
  without clobbering editor edits); backend Makefile `seed-pages` + project
  Makefile `backend-seed-pages`; `apps/pages/tests.py` pins seed + API contract.

### Phase 5 — Billing & subscriptions (Stripe)
- `apps/billing` (Plan, BillingAccount, Seat); `configs/env.py` +=
  STRIPE_* vars; checkout/portal/webhook views; `/apis/billing/plans/`;
  `/settings/plan/` route in the app catalog; feature gates in
  `apps/billing/gates.py`; demo workspace trial seed; write `payment_succeeded`
  → `finance.RevenueEvent`.

### Phase 6 — Webapp enhancements
- Sidenav (collapsible groups, workspace switcher, Cmd+K palette, badge
  counts, user card + plan chip); `/bolt/search/` federated search; onboarding
  tour component + first-login trigger; animated empty/loading states +
  guided create flows; `/employees/` directory + `/employees/<pk>/report/` via
  custom-object schema + `/reports/` catalog pages.

### Phase 7 — Translations & shared locale (i18n)
- **Merge catalogs:** move/reconcile every per-project catalog (§16) into
  `projects/assets/locale/<lang>/LC_MESSAGES/` — `precis-main/backend/locale`,
  `precis-landing/backend/locale`, `precis-lms/assets/locale`,
  `precis-ctc/assets/locale`, plus archived/legacy project dirs; normalize the
  mixed flat/`LC_MESSAGES` layouts; exclude `.venv`/`node_modules`/`dist`.
- **Change `LOCALE_PATHS` at each Django backend project** to the shared dir
  (Loop-CRM first: `backend/configs/default/__init__.py` →
  `BASE_DIR.parents[2] / "assets" / "locale"`).
- **Loop-CRM backend sweep:** `gettext_lazy` on remaining models, forms, view
  messages, `fusion.py`, templates; extend `make i18n` to makemessages into
  the shared dir + compilemessages en/ar.
- **Frontend i18next layer:** `src/i18n/` en/ar catalogs, `t()` everywhere,
  locale switcher; Wagtail block labels `gettext_lazy`.
- **Complete compilation:** one `compilemessages` pass over the shared dir for
  all languages; verify `make check` + `make backend-check` stay green.

### Phase 8 — Docs + validation
- `projects/loop-crm/docs/FUSION_FORMS_TABLES.md` (§15); `docs/loop-crm/`
  README/setup-and-build + `projects/loop-crm/README.md`,
  `DESIGN_SYSTEM.md`, `merge-plan.md` sync (routes, `/cms/`, `/apis/`,
  `/billing/`, reports, shared locale).
- Validation (narrowest first):
  ```bash
  cd projects/loop-crm/backend && make check
  cd projects/loop-crm && make check                # astro check
  make backend-test                                  # manage.py test apps
  make backend-seed-pages && make backend-seed
  # manual: /cms/ edit → /apis/pages/home/ reflects → / renders; login →
  # /overview/ → tables via /bolt/; checkout (test mode) → plan active;
  # locale switcher → ar renders translated UI
  ```

## 18. Consequences

- **Positive:** editor-changeable marketing content; landing pricing drives a
  real Stripe subscription flow; a report catalog + employee surface turn
  user-created data into reports; sidenav/guided UX modernize the webapp;
  fusion forms/tables usage documented; one shared locale catalog with all
  languages compiled; license claims gone; the Bolt webapp architecture is
  preserved.
- **Trade-offs:** landing requires the backend reachable for full content
  (empty state by design); a second admin surface (`/cms/`) alongside
  `/admin/`; Stripe adds an external dependency with test-mode-only dev
  defaults; schema-per-tenant is explicitly deferred (SQLite dev + row-level
  tenancy stay).
- **Risks:** Wagtail `Page` tree vs `django.contrib.sites` (SITE_ID already
  set) — low, gated by seed + checks; `/apis` proxy missing would break dev
  landing (Phase 3); custom-object employees have no dedicated model
  relationships — acceptable for v1, revisit if reports need joins beyond
  activity/deal/post ownership; Stripe webhook idempotency must be handled
  (event `id` dedupe).

## 19. Recommendations (analysis summary)

1. Execute Phase 0 (license) and Phase 1–4 (Wagtail landing) first — they are
   independent of billing and unblock editor content.
2. Adopt Stripe for billing (LemonSqueezy only if MoR/VAT handling wins);
   keep `apps/billing` separate from `apps/finance`; gate features by plan
   from day one.
3. **Do not adopt django-tenants now** — row-level workspaces + `BillingAccount`
   cover the subscription requirement; revisit only for an enterprise hard-
   isolation ask (reference `08-tenant-schemas.md`).
4. Employees as a custom object (not a new model) — fastest, reuses shipped
   schema machinery; add a dedicated model only when report joins demand it.
5. Reuse the `ui/` primitives for all new surfaces (palette, tour, plan page,
   reports) instead of hand-rolling `loop-*` CSS.
6. Keep Loop-CRM's dark CRT design system; treat precis-landing as structural
   reference only.
7. Wire live data everywhere (badge counts, search, reports from real Bolt
   endpoints) — never mock; empty states are explicit.
8. Consolidate all backend locale catalogs into `projects/assets/locale/`
   (one canonical `LC_MESSAGES` layout) and point every Django backend's
   `LOCALE_PATHS` at it — one complete `compilemessages` pass, no backend left
   uncompiled; do this in the same release as the Loop-CRM i18n sweep.

## 20. Open questions

1. Wagtail scope: Home + Pricing + FAQ + Privacy + Terms (recommended) or
   Home-only first?
2. Billing go-live: test-mode Stripe keys OK for dev, or keep billing disabled
   until keys are set (recommended)?
3. Employees: custom object (recommended) or a dedicated `core.Employee`
   model?
4. Should the report catalog ship in the same release as employees, or
   employees first then reports?
5. Confirm the `merge-plan.md` license header edit is wanted.
6. Advertised languages for Loop-CRM: en/ar only (recommended minimum) or the
   full merged set (en, ar, de, es, fr, pt/sv from the shared catalog)?
7. Shared-locale merge conflicts: later-project-wins is the default — confirm
   who reviews the merged msgids (a repo owner, not per-product).

## 21. Skill captions & which skills to use (from the agent catalog)

Skills are captioned from `docs/ai/skills-catalog.md`; the design skills are
constrained by the Loop-CRM CRT pattern (§8) — they inform review, they never
override the user's design system.

| Skill | Caption (what it provides) | Used in |
|---|---|---|
| `structa-backend` | Django/Wagtail/django-fusion conventions: app layout, `{% comp %}`, fragments, dual rendering, imports, validation | Phases 1–3, 5–7 (all backend work) |
| `structa-docs` | Repo docs conventions: ADR format, Remarks & Notes, AI-review markers, doc-sync obligations | This plan + Phase 7 docs |
| `structa-industrial-ui` | Swiss Industrial Print law/tokens — **read to confirm drift**, Loop-CRM keeps dark CRT | §8–9 design review |
| `container-arch-scaling` | Full-stack architecture, proxy/Compose, request lifecycles, MCP discovery | Phase 5 (billing webhooks), `/apis` proxy, deploy |
| `webapp-testing` / `agent-browser` | Playwright + browser automation for the guided tour, sidenav, checkout flow | Phase 6 verification, E2E |
| `tdd` / `verification-before-completion` | Test-first for `apps/billing` + evidence before claiming done | Phases 5–7 |
| `systematic-debugging` | Root-cause discipline for Stripe webhook / Bolt auth failures | Phase 5–6 |
| `writing-plans` / `executing-plans` | Plan execution with checkpoints | Executing this plan |
| `design-taste-frontend` / `frontend-design` | Design-direction review for the landing/tour components (against the CRT system) | Phases 3, 6 |
| `api-design-principles` | REST contract review for `/bolt/search/`, `/billing/*`, `/apis/pages/*` | Phases 3, 5–6 |
| `explore-data` | Profile the seeded/demo dataset for report correctness (revenue, employee KPIs) | Phase 6 reports |
| `structa-docs` + `documentation` | Completing `FUSION_FORMS_TABLES.md` and product docs | Phase 8 |
| `industrial-brutalist-ui` | The archetype skill behind the Loop-CRM design system (Tactical Telemetry): dark substrate, mono telemetry, hazard red, zero radius, ASCII framing — use to review any new surface | Phases 3, 6, 8 (design guardrail) |
| `shadcn-ui` / `shadcn` | The `ui/` primitives (avatar, button, sheet, tooltip, skeleton, …) are shadcn-style — use for palette, tour overlay, plan page, report UI | Phases 6, 8 |
| `tailwind-design-system` | Design tokens in `globals.css` (`loop-*` vars); keep token law when extending | Phases 3, 6 |
| `high-end-visual-design` / `redesign-existing-projects` | Anti-pattern audit so new landing/tour components never look generic AI | Phases 3, 6 (review only) |
| `extract-design-system` | Reverse-check for token drift between Django templates and Astro tokens | Phase 8 |
| `web-design-guidelines` | Accessibility/UX review of the tour, sidenav, tables (focus traps, ARIA live) | Phase 6 |
| `vercel-react-best-practices` | React island perf for ResourceTable/PipelineBoard additions | Phase 6 |

## 22. References

| Reference | Why it is linked |
|---|---|
| `docs/plans/README.md` | Canonical plan registry — register this plan (Loop-CRM scope row + recent updates) |
| `docs/_sidebar.md` | MkDocs sidebar — add this plan under the Loop-CRM section |
| `docs/ai/skills-catalog.md` | Source of the skill captions in §21 |
| `docs/ai/templates-and-request-flows.md` | The translation flow (backend + frontend) the i18n section mirrors |
| `libs/django-fusion/docs/06-forms-and-tables.md` + `COMPONENT_FORMS_TABLES.md` | Framework forms/tables reference for §15 |
| `libs/django-fusion/docs/10-wagtail-integration.md` + `18-render-contract.md` | Wagtail integration + render contract for Phases 1–3 |
| `docs/plans/landing-fusion/README.md` | Landing plan pattern (checks-before-blocks, plan dir conventions) |
| `docs/plans/loop-crm/merge-plan.md` | The Loop-CRM merge roadmap this plan extends (license header, adapters, AI hub) |
| `docs/plans/loop-crm/formint-integration-finance-workflows.md` | Formint↔Loop-CRM finance + workflow expansion — related surface |
| `docs/plans/editions/08-tenant-schemas.md` | django-tenants migration pattern reference (§6) |
| `docs/plans/repository/locale-fixture-audit-2026-07-31.md` | Wagtail content-locale audit (distinct from `.po` catalogs; both matter for §16) |
| `docs/plans/repository/active-monorepo-consolidation-2026-08-14.md` | Monorepo consolidation context (workers, Nx, dev-workspace) |
| `docs/plans/DJANGO_BOLT_FUSION_CASE_STUDY.md` | Bolt API case study — `/bolt/` canonical road context |
| `projects/loop-crm/docs/DESIGN_SYSTEM.md` + `SETUP_AND_BUILD.md` | The CRT design system (§8) and setup/build commands |
| `docs/changelogs/session-2026-08-18.md` | Remaining i18n todo list (§16 scope) + this plan's changelog entry |

## Remarks & Notes

- Watch out: Wagtail admin (`wagtailadmin`) and Django admin (`admin`) must
  stay on different prefixes (`/cms/` vs `/admin/`); keep the Wagtail catch-all
  last in `urls.py`.
- The workspace `uv` env already installs Wagtail — no new dependency; verify
  with `uv run python -c "import wagtail"`. **django-tenants is NOT installed
  and is deferred by this plan.**
- The frontend dev proxy forwards `/api`, `/bolt`, `/accounts`, `/account`,
  `/connect`, `/static`, `/media`, `/admin`, `/fragment(s)`, `/ws` to
  `BACKEND_URL` (`.env.local` → `http://127.0.0.1:8001`). `/apis` and
  `/billing` must be added there.
- Stripe integration reference: Gravity Index search
  `f6a2366e-3274-49b8-860d-bee6ab0e9eb3` (Stripe recommended; LemonSqueezy
  alternative). Env vars: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`,
  `STRIPE_WEBHOOK_SECRET`; webhook events `customer.subscription.updated`,
  `invoice.payment_succeeded`, `customer.subscription.deleted` with event-id
  idempotency.
- Loop-CRM's dark CRT design intentionally overrides the light
  `structa-industrial-ui` substrate — do not "fix" the landing to light.
- Do not run migrations/seeds against shared or production databases; the
  `backend-seed-pages`/`backend-seed` targets are local dev only.
- Keep the `loop-*` BEM class contract intact across landing and webapp; new
  surfaces (palette, plan page, reports) may adopt `ui/` primitives but must
  keep zero radius and the mono/hazard-red token law.
- The report catalog and employee surfaces consume user-created data
  (custom objects/fields, saved views) — never fabricate placeholder
  aggregates; empty states are explicit.
- The existing `08-tenant-schemas.md` plan belongs to Formints editions —
  reference it as a pattern for a future Loop-CRM schema-per-tenant phase, do
  not apply its `Organization`/`Branch` models to Loop-CRM.
- **Locale audit evidence (2026-08-18):** catalogs live at
  `precis-main/backend/locale` (en/ar/de/es/fr/pt/sv), `precis-landing/backend/locale`
  (LC_MESSAGES), `precis-lms/assets/locale` and `precis-ctc/assets/locale`
  (mixed flat `.po` + `LC_MESSAGES` — duplicated and inconsistent).
  `projects/assets/locale/` already exists (`.gitkeep` only) and is the merge
  target. Loop-CRM has no catalog yet.
- When merging, exclude `.venv`, `node_modules`, `dist`, collected static and
  vendored dependency catalogs — merge only first-party project/archived
  project sources, then run ONE complete `compilemessages`.
- Loop-CRM `LOCALE_PATHS` math: `BASE_DIR` = `projects/loop-crm/backend`;
  `BASE_DIR.parents[2] / "assets" / "locale"` resolves to
  `projects/assets/locale`.
- `docs/plans/repository/locale-fixture-audit-2026-07-31.md` is a Wagtail
  *content* locale audit (page fixtures), a different layer from `.po`/`.mo`
  catalogs — both are in scope for a complete i18n story.
- Plan registration (structa-docs sync obligation): this plan must be added to
  `docs/plans/README.md` (Loop-CRM scope) and `docs/_sidebar.md` (Loop-CRM
  section) when it moves to Accepted.
