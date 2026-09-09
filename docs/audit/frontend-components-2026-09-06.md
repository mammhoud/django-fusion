---
title: Frontend Component Audit — Placeholders & Design/Interactivity Gaps
description: Cross-product frontend component audit — components that still carry placeholder content or stub interactions, what is implemented against real backend use cases, and component design + interactivity recommendations.
object:
  type: "report"
  id: "docs.audit.frontend-components-2026-09-06"
attributes:
  source_path: "audit/frontend-components-2026-09-06.md"
  canonical_route: "/docs/en/audit/frontend-components-2026-09-06"
  section: "audit"
  owner: "workspace"
  status: "maintained"
  source_of_truth: "repository-markdown"
tags:
  - structa-cloud
  - audit
  - components
  - frontend
  - placeholders
  - design
  - interactivity
links:
  - label: "Audit home"
    to: "/audit"
    icon: "i-lucide-clipboard-check"
  - label: "Product audit"
    to: "/audit/product-audit"
    icon: "i-lucide-clipboard-check"
  - label: "Dev team plans"
    to: "/agenda/dev-team-plans"
    icon: "i-lucide-code-2"
---

# 🧩 Frontend Component Audit — Placeholders & Design/Interactivity Gaps

> **Audit date:** 2026-09-06 · **Method:** source scan for placeholder markers
> (`TODO`/`lorem`/`coming soon`/`not implemented`/mock data) across every
> product frontend, followed by a data-road trace of the components that hit.
> **Scope:** loop-crm, precis-main, precis-landing, precis-ctc, syntara,
> formint (community/standard/pro/cloud/client). This is a report — no
> component code was changed.
>
> Outcome requested: confirm implemented components have no placeholders,
> list what still does, and say what should be customized per backend use case
> and what the component design/interactivity should become.

<!-- AI-generated: review needed -->

## 1. Verdict summary

| Product | Placeholder-free components? | Genuine placeholders found |
|---------|------------------------------|----------------------------|
| **Loop-CRM** | ✅ Yes — every app island reads a real `/apis/core/` endpoint; empty states are explicit, pending reports are labeled `pending` not faked | `PipelineDemo` is an inert marketing demo island (fake deals) — landing-preview only, never used inside the app shell |
| **Precis Landing** | ✅ Yes | — |
| **Syntara** | ✅ Yes | — |
| **Formint Client** | ✅ Yes | — |
| **Precis LMS (precis-main)** | ⚠️ Copy | `frontend/src/lib/brand.ts:58` — `role: 'CRM + social scheduling · Twenty + Postiz merged · coming soon'` is stale teaser copy for Loop-CRM, which is live |
| **CTC Research** | ⚠️ Demo assets | `apps/pages/blog/templates/blog/blog-details*.html` + variants — hard-coded 2018/`lorem ipsum` theme pages, no Django template tags, no view references them |
| **Formint Pro** | ✅ Resolved 2026-09-06 | Previously several **Add** actions only toasted `"Add … coming soon"`; real create/edit modals + delete are now wired to the `/suppliers/`, `/roles/`, `/employee-schedules/`, `/payroll/`, `/notes/`, `/recipes/` + `/ingredients/` APIs (see § 2.3) |
| **Formint Community / Standard / Cloud** | ✅ Yes (code) | Only a jsdom test TODO comment (not runtime) |

Sources scanned (marker terms): every `src|frontend/src|assets` tree —
`.astro/.tsx/.ts/.vue/.html` — excluding `node_modules`, `dist`, `.astro`,
`test-results`, locale catalogs and `.min.*`. Input `placeholder=` attributes
were excluded as legitimate UI affordances (loop-crm forms, CRM form widgets).

## 2. Genuine placeholders to act on

### 2.1 CTC Research — Lorem-ipsum demo blog templates
**Where:** `projects/precis/precis-ctc/backend/apps/pages/blog/templates/blog/`
(`blog-details.html`, `blog-details-left.html`, `blog-details-audio.html`,
`blog-details-video.html`, `blog-details-gallery.html`, …).
**Evidence:** content is a 2018 premium-theme demo (dates, fake authors,
`assets/img/blog/...`, links back to `blog-details.html`). No Django template
tags and **no `.py` view references any of them**, so they cannot render for
real pages today.
**Recommendation:** quarantine or delete. If kept as a visual reference, move
under a `docs/` or `theme-preview/` path outside `templates/` so a future
Wagtail template-name collision cannot surface them; then confirm the real
blog-detail template the Wagtail `BlogDetailPage` actually renders is
placeholder-free.

### 2.2 Precis Main (unified) — stale brand teaser
**Where:** `projects/precis/precis-main/frontend/src/lib/brand.ts:58`.
**Evidence:** a product/role list still advertises the merged CRM as
"coming soon", which Loop-CRM (live at `crm.structa.cloud`) no longer is.
**Recommendation:** refresh the copy to the live Loop-CRM positioning or drop
the row; do not ship teaser wording for a shipped product.

### 2.3 Formint Pro — "Add … coming soon" stub actions (resolved 2026-09-06)
**Where they were (each a real list/table page whose create action was a stub toast):**
- `frontend/src/pages/pos/suppliers/index.astro`
- `frontend/src/pages/hr/roles/index.astro`
- `frontend/src/pages/hr/schedules/index.astro`
- `frontend/src/pages/hr/payroll/index.astro`
- `frontend/src/pages/admin/notes/index.astro`
- `frontend/src/pages/kitchen/recipes/index.astro`

**Resolution (2026-09-06):** each page now ships a create/edit modal (same
pattern as the working CRM/ops pages) backed by the existing Django
`ModelControllerBase` CRUD endpoints — `/suppliers/`, `/roles/`,
`/employee-schedules/`, `/payroll/`, `/notes/`, and the dual-tab
`/recipes/` + `/ingredients/`. Delete confirmations were wired where they were
still toasts (roles, schedules, payroll, notes, recipes). Employee/product
selects load from `/employees/` and `/products/`. `astro check` passes for all
71 frontend files; no backend change was required.

**Follow-up verification (2026-09-06):**
- **Stale display fields removed** — list tables bind to real serializer
  fields only. FK display names now resolve client-side from the reference
  lists the pages already load: `empName(item.employee)` (schedules,
  payroll, ops/shifts) and `prodName(item.product)` (recipes);
  ops/shifts duration is derived from `opened_at`/`closed_at` instead of the
  never-serialized `duration_hours` property. No `item.*_name` bindings
  remain on any of the seven pages.
- **Contract tests added** — `frontend/src/tests/create-forms.contract.test.ts`
  asserts each modal POSTs/PUTs/DELETEs the expected payload key set to its
  endpoint (`/suppliers/`, `/roles/`, `/employee-schedules/`, `/payroll/`,
  `/notes/`, `/recipes/`, `/ingredients/`). `vitest run` → **86 passed**
  (8 files). `astro check` → **0 errors, 0 warnings** (99 hints, all
  pre-existing implicit-any style notes).
- Backend suite: not runnable in the sandbox — `server/` lockfile requires
  `libs/django-bolt`, which is not present in this checkout (only
  `libs/django-fusion/` is); no server venv can be synced here. Run
  `make test` inside the product Docker image on the host.

### 2.4 Loop-CRM — `PipelineDemo` (inert by design)
**Where:** `projects/loop-crm/frontend/src/components/demo/PipelineDemo.tsx`.
**Evidence:** canned `Deal[]` data (Halcyon Labs, …) advanced on a timer — it
is a motion showcase for the public landing, not the app. The production
board is `board/PipelineBoard.tsx`, which loads `/apis/core/board/`, is
realtime-synced, and persists drags through a CSRF-protected move endpoint.
**Recommendation:** keep it but clearly gate it to landing preview routes; it
must never be mounted inside the authenticated shell (verified — it is not).

## 3. Loop-CRM — component → backend data road (all real)

| Component | Backend road | Interaction today | Notes |
|-----------|--------------|-------------------|-------|
| `RevOpsDashboard` | `/apis/core/dashboard/`, `/board/`, `/revenue/trend/` + workspace-realtime refresh | KPI stat cards, funnel with stage deep-links, stacked deal/POS trend bars, live-sync chip, skeleton/error states | Reads counts incl. marketing (`posts`/`channels`/`campaigns`) and sales (`deals`/`touchpoints`) domains |
| `PipelineBoard` | `/apis/core/board/` + POST `/apis/core/deals/<id>/stage/` | GSAP `Draggable` with elastic snap-back, per-card prev/next steppers, `prefers-reduced-motion` fallback, optimistic move with rollback, deep-link `?pipeline=&stage=` | Sales (crm) core surface |
| `AiHub` | `/apis/core/ai/` catalog + consent + `/apis/core/ai/<op>/` | Consent toggle before any context leaves; operation select + brief → result panel with human-review notice | Marketing/sales assist; provider row shows configured state |
| `CommandPalette` | `/apis/core/search/` (+ client route index) | `Cmd/Ctrl+K` + `/`, escape, keyboard-free click, top-12 results, aria dialog | Global shell |
| `LocaleSwitcher` | `/apis/core/locale/` GET/POST | Writes language, applies `dir`, reloads; RTL-ready | en/ar |
| `EmployeeDirectory` | `/apis/core/people/` | Toolbar + search input + member list | People shell |
| `ReportCatalog` | `/apis/reports/` | Cards with `live`/`pending` state; pending never fake | Honest status pattern |
| `BillingPlan` / `ProfileCard` / `OnboardingTour` / `ResourceTable` | `/settings/`, account/plan roads | Plan catalog, plan change, profile, tour | Billing surface |
| `ui/*` (card, badge, skeleton, tooltip, dropdown…) | — | Radix/shadcn primitives restyled to the Tactical Telemetry system | Reusable primitives |
| `landing/*` (Hero, Pricing, FAQ, CTA, EmptyState) | Wagtail `/apis/pages/<slug>/` JSON via Astro | Public marketing pages | No app-data claims |

No component inside the authenticated shell uses mock aggregates; empty
states are explicit ("No pipeline yet", "No revenue events yet") and the
report catalog renders `pending` instead of fake numbers — both are the
design contract the rest of the repo should copy.

## 4. What should be customized per backend use case (design + interactivity)

Backend use cases exist for **two audiences** — marketing (plan → approve →
schedule → publish → attribute) and sales (lead → stage → deal → invoice →
recognize) — plus finance/RevOps cross-domain views. The components that serve
them should be customized as follows:

1. **Domain-coded, not generic tables.** `ResourceTable`/fusion tables serve
   CRUD generically; the moment a row has domain behavior (a `Post` with
   publish-state guards, a `Deal` with stage probability) the component should
   render a domain action cluster — approve/queue/publish for marketing,
   advance/close/won for sales — driven by the same permission + state model
   the backend already returns. Don't bolt these onto generic row actions.
2. **Consent- and permission-aware AI surfaces.** The AI Hub pattern (explicit
   workspace consent, provider-configured badge, human-review result footer)
   should be the template for every future AI-assisted action so the
   "no record changed without review" promise is visible in the UI, not just
   the API.
3. **Live-sync discipline.** Loop-CRM's `live/synced` chip + silent realtime
   refreshes (no skeleton flash on mutation events) should apply to every
   shared board/dashboard; single-user pages can stay request/response.
4. **Empty ≠ fake.** Keep the `pending`/explicit-empty contract everywhere a
   report or metric is not yet backed by data; replace placeholders with
   states, never mock numbers.
5. **Accessibility + motion parity.** Components already honour
   `prefers-reduced-motion`, keyboard steppers, `role=dialog`/`aria-live` and
   focus chips. Extend the same to any new board/drop target (drag is only an
   enhancement; keyboard move must always exist).
6. **Custom-object / custom-field surfaces.** Backend supports
   `CustomFieldDefinition` + custom-object catalog (Twenty-style). Any new
   record editor should render fields from that catalog instead of a fixed
   form, so tenant-specific fields stay a configuration, not a fork.
7. **RTL/locale.** LocaleSwitcher applies `dir` at the document level; new
   components must be tested under `dir=rtl` (the design system is LTR-first
   today — AR parity is an explicit contract).

## 5. Cross-product component work queue

| Priority | Item | Product | Evidence |
|:--:|---|---|---|
| P1 | Real create-forms behind the "Add … coming soon" toasts | Formint Pro | ✅ Done 2026-09-06 — § 2.3 |
| P2 | Remove/quarantine lorem blog-demo templates | CTC | § 2.1 |
| P2 | Refresh `brand.ts` "coming soon" Loop-CRM copy | Precis LMS | § 2.2 |
| P2 | Gate `PipelineDemo` to landing previews with a code comment contract | Loop-CRM | § 2.4 |
| P1 | Reconcile formint-pro + loop-crm entry rows in dev-team plans | Workspace | dev-team-plans.md status truth table |

## 6. Related

- [`docs/agenda/dev-team-plans.md`](../agenda/dev-team-plans.md) — status-truth matrix and "couldn't add" register
- [`docs/agenda/feature-tracking.md`](../agenda/feature-tracking.md) § Loop-CRM — AI hub/locale/connectors milestone
- [`docs/loop-crm/README.md`](../loop-crm/README.md) — Loop-CRM data roads
- [`projects/loop-crm/frontend/DESIGN.md`](../../projects/loop-crm/frontend/DESIGN.md) — Tactical Telemetry token map

<!-- AI-generated: review needed -->
