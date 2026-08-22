---
title: Formint POS — Cross-Edition Audit & Reconciliation Plan
description: Evidence-backed audit of every Formint frontend, backend, design system, color contract, feature claim, and remaining delivery work.
navigation:
  title: Formint audit plan
  icon: i-lucide-clipboard-check
object:
  type: "reference"
  id: "docs.plans.editions.formint-audit-2026-08-22"
attributes:
  source_path: "plans/editions/10-formint-audit-and-reconciliation-2026-08-22.md"
  canonical_route: "/docs/en/plans/editions/10-formint-audit-and-reconciliation-2026-08-22"
  source_of_truth: "repository-markdown"
  owner: "formints"
  status: "proposed"
  audited_at: "2026-08-22"
tags:
  - structa-cloud
  - formints
  - pos
  - audit
  - roadmap
  - design-system
links:
  - label: "Formint edition plans"
    to: "/docs/en/plans/editions"
    icon: "i-lucide-layers"
  - label: "Feature comparison"
    to: "/docs/en/plans/editions/comparison"
    icon: "i-lucide-table-2"
  - label: "Formint product docs"
    to: "/docs/en/pos"
    icon: "i-lucide-store"
---

# 🧭 Formint POS — Cross-Edition Audit & Reconciliation Plan

<!-- AI-generated: review needed -->

> **Audit date:** 22 August 2026  ·  **Product boundary:** `projects/formints/`
>  ·  **Canonical runtime names:** Community, Standard, Pro, Cloud, and
> pos-client. This document is an engineering truth pass, not a release
> approval or a live production certification.
>
> **Phase 0 status (22 Aug 2026):** executed — landing-page claims, edition
> messaging, placeholder imagery, and the release-process checklist are
> reconciled (see Phase 0 checkboxes below).

## 🎯 Executive verdict

The Formint codebase is a five-edition product family with three different
runtime shapes, not one shared application:

```mermaid
graph LR
    C[Community<br/>Astro + React<br/>Tauri + Rust + SQLite]
    S[Standard<br/>Astro + React<br/>Tauri + Rust + SQLite]
    P[Pro<br/>Astro + Alpine + HTMX<br/>Django + Tauri]
    CL[Cloud<br/>Astro + React UI<br/>Django + Channels]
    PC[pos-client<br/>Vue + Pinia + Tauri<br/>Django shop + Astro storefront]
    DS[@formints/design-system<br/>tokens + React components]
    AR[assets/<br/>shared registry]

    C --> S --> P --> CL
    PC -. separate branch .-> CL
    DS -. partial adoption .-> C
    DS -. partial adoption .-> S
    AR --> C
    AR --> S
    AR --> P
    AR --> CL
    AR --> PC
```

### Current status at a glance

| Area | Finding | Decision implied |
|---|---|---|
| Community | Core offline POS and documented enhancement work are code-backed and locally verified | Treat as done in code; publish remains an operator action |
| Standard | Rust/Diesel-first parity layer is present: currency, tax, permissions, exports, queue, loyalty | Treat as done in code; run browser/E2E when a desktop runtime is available |
| Pro | Django-first feature surface is broad and tested: API, Fusion, KDS, CRM, vertical modules, forecasting, procurement | Treat as done in code; provision the product-local environment before final release sign-off |
| Cloud | Backup, monitor, tenant identity, queue/conflict, dashboard, and WebSocket contracts exist | Keep staging status until live `verify-stack` and PostgreSQL schema flip-on pass |
| pos-client | Shop APIs/fragments and the Vue shell exist; browser cart/checkout completion is still open | Keep in active development; do not market it as done |
| Design system | Package exists and is a dependency in Community/Standard, but product code mostly uses local components and CSS | Finish adoption or explicitly narrow the package contract; do not call it universal yet |
| Public claims | Cloud landing page claims shipped Pro/Cloud features, but uses a `picsum.photos` marketing image and advertises only three editions | Replace external placeholder imagery and reconcile edition messaging before launch |
| Documentation | Several active references still describe Robyn, RTK Query, old paths, or conflicting palettes | Perform a docs truth pass before adding more features |

The public website was not treated as live production evidence in this audit.
The website claim surface was checked from the repository-owned Cloud landing page
(`projects/formints/formint-cloud/frontend/src/pages/index.astro`) and package
metadata pointing to `https://structa.cloud`. Live DNS, deployment health,
analytics, and production browser behavior still require an operator/staging
check.

## 🧱 Edition-by-edition audit

### 🟢 Community — `projects/formints/formint-community/`

**Frontend.** Astro 5 provides the page shell and React 19 renders the POS
islands. The UI has dedicated pages for sales, products, transactions,
customers, suppliers, kitchen, inventory, recipes, analytics, reports, staff,
employees, payroll, roles, schedules, coupons, notes, support, settings, auth,
and about. Shared frontend behavior lives under `src/components/`, `src/hooks/`,
`src/contexts/`, `src/api/`, and `src/app/pages/`.

**Backend.** There is deliberately no Django or Python backend. Tauri commands
cross into Rust/Diesel and an embedded SQLite database. The native surface owns
sales, products, inventory, employees, auth, roles, receipts/invoices, hardware,
analytics, support, and local settings.

**Done and evidenced.** Offline-first mode, refund/return flow, KDS, cash/card/
split payments, invoices and receipt templates, ESC/POS support, i18n (English,
French, Arabic), role permissions, five theme variants, loyalty, scheduling,
coupons, notes, and support are represented in the React/Rust code and tests.
The refund path is explicitly idempotent: only completed sales can be refunded,
and the sale remains in the transaction history.

**Design/color state.** The local FlyonUI theme layer is the active visual
contract. `perplexity` uses warm paper, verdigris, and amber; corporate, luxury,
pastel, light, and dark variants remain selectable. Local BEM/CSS tokens also
provide surface, semantic, spacing, motion, RTL, and compact-widget aliases.
The parent asset registry now supplies shared brand/font/icon files.

**Remaining.** No known product-code blocker. Standalone repository creation,
release signing, packaging, and the final browser/desktop E2E run remain
operator/environment gates.

### 🟢 Standard — `projects/formints/formint-standard/`

**Frontend.** Standard follows the Community Astro 5 + React 19 surface and adds
Alpine-compatible patterns where required. It has the same broad local POS page
surface plus currency, tax-profile, and enterprise administration pages.

**Backend.** Rust/Diesel + SQLite is primary. Standard does not require a Python
server. Its native operations include currency, tax profiles, role/permission
resolution, CSV/JSON export, reconnect/flush behavior, and local sync queue
support. The optional Django sidecar is additive and must not be presented as a
requirement for the local product contract.

**Done and evidenced.** Community parity plus multi-currency, tax profiles,
custom roles/permissions, exports, node/heartbeat registry, sync approvals,
offline queue/reconnect, and loyalty are code-backed. The employee suites passed
after preserving the payroll fields in the add/edit payload contract.

**Design/color state.** Standard mirrors the Community FlyonUI token vocabulary
and theme variants, with local style files for its build. It has received the
shared asset aliases and compact CRUD/double-bezel styling, but it does not
currently consume the React component exports from `@formints/design-system`.

**Remaining.** Run the full browser/desktop E2E matrix in an environment with a
working desktop/browser runtime. Optional sidecar sync and large-dataset async
export work is additive, not a release blocker.

### 🟢 Pro — `projects/formints/formint-pro/`

**Frontend.** Astro 5 + Alpine.js + HTMX is the canonical web shell. The shell
supports full-page responses, HTMX fragments, and data responses through the
Fusion render-mode contract. Tauri remains the desktop wrapper, but Pro's
business boundary is Django-first.

**Backend.** The canonical server boundary is Django ASGI with Django Ninja,
django-fusion, django-bolt when installed, Unfold admin, ORM models, services,
fragments, and WebSocket support. The `server/routes/` and Robyn-era material are
legacy compatibility/history surfaces, not the architecture to extend.

**Done and evidenced.** The code and focused tests cover Standard parity, a
45-resource typed API, Fusion dual-mode views, Unfold admin, CRM, KDS station
routing, QR menu versioning/publish, loyalty/reversal, API keys and rate limits,
mobile waiter split/merge, multi-terminal sync, offline outbox, barcode lookup,
gaming center, gift cards, table management/reservations, delivery connectors,
advisory forecasting, employee scheduling/time clock, customer display, kiosk,
inventory forecasting, and purchase orders.

The advisory features are intentionally read-only until an explicit operator
action: forecasting must not change prices, stock authority, refunds, or sync
state on its own.

**Design/color state.** Pro has a local canonical-looking `tokens.css` and
`global.css`, while the product family documentation says the design language is
warm paper + ink + verdigris + amber. The actual Cloud marketing surface instead
uses a dark ink + copper + amber identity. These can coexist as product contexts,
but the semantic token names and brand guidance must be made explicit so “primary”
does not silently mean blue in one edition and copper in another.

**Remaining.** Product-local `server/.venv` validation is still an environment
gate. Release approval must not rely only on another edition's virtualenv.

### 🟡 Cloud — `projects/formints/formint-cloud/`

**Frontend.** The Cloud frontend is an Astro + React UI derived from the Community
surface, with Cloud dashboard/telemetry and a static public marketing page. The
landing page has a dark copper-crest visual system and advertises Pro/Cloud
operational capabilities.

**Backend.** Django is the complete API/admin boundary. `apps/core/` owns models,
viewsets, reports, admin, and dashboard settings. `apps/domain/` owns the sync
broker, queue, and conflict resolver. `apps/handlers/` owns sync receivers,
Channels consumers, Fusion contracts, fragments, and the server surface. The
configured architecture is Django + Channels; Robyn must not be reintroduced.

**Done and evidenced.** Organization → Branch identity, branch settings, device
tokens, sync queue, conflict resolution, branch reports, dashboard contracts,
WebSocket sync-event frames, automatic `BackupRun`/`backup_db`, `/monitor/status`,
Unfold admin, and SDK monitor wiring are locally tested.

**Remaining.** Cloud stays staging until a running staging master passes
`make verify-stack`, including HTTP, queue, and WebSocket behavior. PostgreSQL
schema-per-tenant is still a flip-on operation: configure `DB_ENGINE`, run shared
and tenant migrations, seed a Tenant/Domain, and execute the gated integration
suite. Do not describe SQLite-safe tenant identity tests as proof of production
schema isolation.

### 🔵 pos-client — `projects/formints/formint-client/`

**Frontend.** The client has two frontend roads: a Vue 3 + Pinia + Tauri desktop
register in `src/`, and an Astro storefront in `frontend/`. The desktop route
surface currently includes dashboard, menu, orders, and settings. The storefront
has catalog, editorial/featured products, cart drawer, login, HTMX fragments,
and Alpine interactions.

**Backend.** `backend/` is a plain Django shop/employee/CMS application. It owns
catalog, products, cart, checkout, orders, promotions, auth status, employee
inbox/KPIs, and Fusion/HTMX fragments. This is not the same backend as Cloud and
must not inherit Cloud tenant assumptions automatically.

**Done and evidenced.** Shop API contract tests, catalog/auth/cart-count
contracts, checkout/order/promo/editorial API coverage, and the My Orders HTMX
fragment are present. Vue shell, i18n (English and Simplified Chinese), Pinia,
Tauri plugins, and storefront motion are present.

**Remaining.** The browser-level cart/checkout journey, Playwright coverage on
port 1433, feature-inheritance review, and release packaging are open. This is
the only edition whose plan explicitly identifies unfinished product flows,
rather than only promotion or environment gates.

## 🎨 Design, color, and asset audit

### What is already implemented

- `projects/formints/assets/` is the shared source for brand files, fonts, icons,
  public files, and Django static assets; duplicate frontend asset roots were
  delegated to it.
- Community, Standard, Cloud, Pro, and Client configs expose the parent asset
  layer through aliases, `publicDir`, Vite/Astro roots, or Django staticfiles.
- Local edition styles remain separate where the build contracts differ. This is
  correct: a Rust desktop theme, Django admin surface, Astro landing page, and
  Vue storefront do not need one compiled CSS file.
- The shared CSS/TypeScript package contains spacing, radius, shadow, motion,
  semantic color, BezelCard, Bento, compact form, and reveal primitives.
- Community/Standard use a FlyonUI theme matrix; Client uses its own `fu-*`
  semantic aliases and daisyUI/shadcn-vue-compatible tokens; Cloud marketing
  uses an intentionally dark copper treatment.

### Problems to resolve

1. **Token source is described as universal but is not universal in code.** The
   design-system package is listed as a dependency in Community/Standard, yet
   production imports mostly use local `Card`, `Button`, and form components.
   `@formints/design-system` currently has tests/examples and partial CSS usage,
   not complete cross-edition adoption.
2. **Brand palette and UI palette are mixed in documentation.** The product docs
   describe verdigris/amber, the brand plan describes copper/orange/gold/teal,
   and the Cloud landing page hard-codes copper/amber. Select a semantic contract:
   brand accent may be copper while the default operational action may be
   verdigris, but each surface must document which role it uses.
3. **Typography names drift.** The shared package token source names Inter while
   the asset registry and active styles use Outfit/Roboto in several editions.
   Pick `Outfit` as display/brand, `Roboto` or a documented UI body face, and
   JetBrains Mono for telemetry; remove undocumented aliases after migration.
4. **Motion is duplicated.** Local CSS, the shared package, and page-level
   scripts define overlapping reveal/easing utilities. Keep one shared primitive
   for React, one documented CSS contract for non-React surfaces, and delete
   aliases only after a consumer scan.
5. **Public imagery is not launch-ready.** The Cloud landing page uses
   `https://picsum.photos/seed/formint-floor/1200/900` despite describing the page
   as a real product surface. Replace it with an approved local image or remove
   the photo card; do not ship an external placeholder as brand media.

## ✅ What is done, planned, and blocked

### Done in code

- Parent Formint asset registry and edition wiring.
- Community refund/return flow and offline indicator.
- Standard money, tax, permissions, export, queue, and loyalty layer.
- Pro's Django/Fusion/Unfold foundation and listed vertical modules.
- Cloud backup, monitoring, dashboard, queue/conflict, WebSocket, and tenant
  identity layer.
- Client shop APIs, Fusion/HTMX fragments, Vue shell, and storefront foundation.
- Focused frontend checks, Vue typecheck, Django checks, asset registry checks,
  employee tests, and whitespace validation from the preceding implementation
  work.

### Planned or still required

- Cloud staging deployment and live `verify-stack`.
- PostgreSQL schema-per-tenant flip-on and integration verification.
- Client cart/checkout browser flow and Playwright suite.
- Standard/Community desktop browser E2E when the runtime is available.
- Pro validation in its own provisioned `server/.venv`.
- Community standalone repository/release and SDK registry publication.
- Design-system adoption decision and semantic token consolidation.
- Docs and legacy-path reconciliation (Phase 4). Public claims and the
  placeholder image are reconciled (Phase 0, done 22 Aug 2026).

### Environment/operator gates, not missing features

- GitHub repository creation, commits, tags, signing keys, and registry publish.
- Staging boot, database credentials, PostgreSQL migration, and live health checks.
- Browser/desktop runtime availability for full E2E.
- Product-local Python environment for Pro.

## 🧹 Removal and consolidation register

No additional deletion should happen automatically from this audit. The current
worktree already contains a large asset-centralization change and unrelated
`application/` modifications; those must remain untouched. Proposed removals are
separated by confidence:

### Remove or rewrite now, after reference confirmation

- Rewrite `projects/formints/CONTEXT.md`, which still describes an embedded
  Robyn server and an older four-edition vocabulary.
- Rewrite active architecture/Makefile comments that say Pro still uses Robyn,
  RTK Query, or the retired `formintA`/`formintB`/`pos-full` paths.
- Update stale test/page-object comments and docs under
  `projects/formints/tests/pos-e2e/` to canonical edition paths and ports.
- Correct the package documentation typo “Formin” and examples that imply
  Astro can directly render React components without an island/integration.
- Remove the Cloud landing page's `picsum.photos` URL before public launch; use
  an approved asset or remove that card.

### Consolidate later, only after a consumer scan

- Robyn-era `server/routes/`, `.robyn-backup/`, and `server.py` compatibility
  surfaces in Pro. First prove they are not used by Make targets, deployment,
  tests, or external contracts; then archive or delete under the deletion
  manifest.
- Duplicate legacy CSS aliases (`forge-*`, old animation names, and repeated
  glass/reveal utilities). Preserve a compatibility layer for one migration
  window, measure consumers, then remove unused aliases.
- Unused `@formints/design-system` dependency entries if the team chooses not
  to adopt the package. The preferred path is the opposite: adopt the package
  in shared React surfaces and keep local CSS only for edition overlays.
- Superseded historical docs such as `docs/pos/features.md` and
  `docs/pos/cloud-edition.md` should remain as redirects/pointers until the docs
  owner confirms no external links depend on their routes; do not delete them
  merely because they are marked superseded.

### Keep

- Edition-owned platform icons, Tauri shell configuration, Django admin styling,
  Cloud tactical SCSS, and Client storefront styling where runtime contracts or
  visual context differ.
- Runtime aliases required by external integrations. Document them as aliases;
  do not recreate duplicate source trees.
- The shared parent asset registry and its validation target.

## 🗺️ Prioritized implementation plan

### Phase 0 — Claims and architecture truth gate

- [x] Make `docs/plans/editions/README.md`, `comparison.md`,
      `projects/formints/README.md`, and the Cloud landing page agree on whether
      the public product story presents three editions (Community/Pro/Cloud) or
      all five (including Standard/Client).
      **Done (22 Aug 2026):** the landing page now presents all five editions
      (Community · Standard · Pro · Cloud · pos-client) with status chips;
      the four surfaces agree on the five-edition story. The docs surfaces
      (editions index, comparison, product README) already listed five and
      were left as the canonical record.
- [x] Mark every feature as **implemented**, **locally tested**, **staging
      verified**, or **planned**. Do not use “live” for code that has not been
      deployed.
      **Done (22 Aug 2026):** feature copy now reads “implemented and locally
      tested in the Cloud master” with Cloud explicitly marked 🟡 staging;
      the CTA no longer says “The app is live”. Edition cards carry
      done/staging/dev status chips from the finish board.
- [x] Replace the external placeholder image on the Cloud landing page.
      **Done (22 Aug 2026):** the `picsum.photos` URL was replaced with the
      local `pos-crest-enhanced.svg` from the shared asset registry
      (`projects/formints/assets/shared/static/`). No external placeholder
      media remains on the page.
- [x] Add a lightweight claim-evidence checklist to the release process.
      **Done (22 Aug 2026):** `projects/formints/PUBLISH.md` gained a
      Claim-Evidence Checklist (truth gate) section covering canonical
      edition names, status accuracy, code-path citations, no external
      placeholder media, and stack-claim accuracy; its stale edition table
      (Mini/merged, Robyn, Sanic) was corrected to the five canonical
      editions.

**Exit criteria:** every public claim links to a code path and a test or is
explicitly labelled roadmap/operator work.

### Phase 1 — Design system and color contract

- [ ] Choose the semantic brand contract: document copper/amber for the Cloud
      public identity and verdigris/amber for operational themes, or choose one
      family-wide action palette.
- [ ] Align TypeScript token typography with the actual self-hosted font files.
- [ ] Add a small integration surface for the shared React primitives in
      Community and Standard; do not replace every component in one pass.
- [ ] Define a CSS-only adapter for Pro/Cloud and a Vue adapter for Client,
      mapping the same semantic roles without forcing React into those builds.
- [ ] Remove duplicate motion/token aliases only after TypeScript/CSS consumer
      scans and visual checks.

**Exit criteria:** each edition documents its token entrypoint, brand palette,
font source, reduced-motion behavior, and whether it consumes shared components
or only shared semantic tokens.

### Phase 2 — Cloud promotion and tenant safety

- [ ] Deploy a disposable staging Cloud master with the existing Django/Channels
      topology.
- [ ] Run `make verify-stack` and record health, dashboard, queue, conflict, and
      WebSocket results.
- [ ] Set PostgreSQL `DB_ENGINE`, run `migrate_schemas --shared` and
      `migrate_schemas --tenant`, seed Tenant/Domain, and execute the gated
      tenant integration suite.
- [ ] Verify backup output, monitoring status, broker behavior, and rollback to
      SQLite configuration without destructive production operations.
- [ ] Only then change Cloud and tenant status from staging/pending to done.

**Exit criteria:** live staging checks pass and tenant isolation is verified on
PostgreSQL, not only SQLite.

### Phase 3 — pos-client completion

- [ ] Trace the full user path: catalog → category filter → cart drawer → login
      state → promo → checkout → order confirmation → My Orders.
- [ ] Add browser tests for authenticated and anonymous states, invalid stock,
      promo failure, CSRF failure, and retry/error recovery.
- [ ] Run the `formint-client` Playwright project on port 1433 and update the
      client plan only from observed results.
- [ ] Verify that Client remains a separate shop product and does not inherit
      Cloud-only branch/tenant claims accidentally.

**Exit criteria:** browser checkout is green with the Django shop backend and
release packaging has a documented path.

### Phase 4 — Documentation and legacy cleanup

- [ ] Rewrite active stale architecture docs and comments to canonical paths.
- [ ] Keep historical pages as pointers or move them through the lifecycle and
      deletion manifest; do not silently delete externally linked routes.
- [ ] Remove or archive Pro Robyn compatibility material only after the consumer
      scan and owner approval.
- [ ] Refresh edition counts, feature matrices, ports, commands, and status dates.
- [ ] Add this audit to the plan registry and link it from the edition index.

**Exit criteria:** an engineer can choose an edition, start its documented
frontend/backend path, and find no contradictory active architecture claim.

### Phase 5 — Release and operational readiness

- [ ] Publish the standalone Community repository and signing metadata.
- [ ] Publish `@formints/client` only after its package checks and release files
      are verified.
- [ ] Run the edition-specific checks, focused tests, desktop/browser E2E, and
      asset registry check from a clean checkout.
- [ ] Capture release screenshots from the current canonical frontends; do not
      reuse retired path references.
- [ ] Update the finish board only after evidence is attached to each status.

## 🧪 Verification matrix

| Scope | Narrow check | Release-level evidence |
|---|---|---|
| Shared assets | `cd projects/formints && make assets-check` | No duplicate roots; registry files resolve in every edition |
| Community | `make -C projects/formints/formint-community check` and focused Vitest | Desktop/Rust suite + Community Playwright project |
| Standard | `make -C projects/formints/formint-standard check` and focused Vitest | Desktop/Rust suite + Standard Playwright project |
| Pro | `make -C projects/formints/formint-pro check` and `make test` | Product-local Django environment, frontend tests, API/Fusion/admin coverage |
| Cloud | `make -C projects/formints/formint-cloud check` and `make test` | Live staging `verify-stack`, dashboard, WebSocket, backup, PostgreSQL tenancy |
| Client | `make -C projects/formints/formint-client build` and `vue-tsc --noEmit` | Shop API + browser cart/checkout + port-1433 Playwright project |
| SDK | `make -C projects/formints sdk-typecheck sdk-test` | Published package with ESM/types and consumer smoke test |
| Documentation | `cd docs && npm run prepare-content && npm run validate-content` | Links, frontmatter, status labels, and canonical paths stay synchronized |

The preceding asset-wiring session verified the asset registry, whitespace,
focused employee tests, four Astro checks, Client Vue typecheck, and three Django
checks. Rust `cargo check` was unavailable because Cargo was not installed, and
the broad frontend suite encountered the environment's pre-existing `kill-port`
/`lsof` limitation. Those are recorded as verification limits, not silently
converted into product failures.

## Remarks & Notes

- This audit intentionally does not change product code beyond documentation
  registry links. It records the next work so asset-centralization changes and
  unrelated `application/` worktree modifications remain isolated.
- “Done” means code-backed and locally verified; “staging” means promotion is
  still required; “dev” means a user-facing flow or E2E gate is incomplete.
- The canonical product path is `projects/formints/`. Retired names such as
  `formintA`, `formintB`, `pos-full`, `pos-solo`, and Robyn-era server names are
  compatibility/history references only.
- Do not run migrations, staging deploys, release signing, database resets, or
  deletion operations from this document without explicit operator direction.
