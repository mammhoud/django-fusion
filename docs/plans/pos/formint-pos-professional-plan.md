# Formint POS — Professional Edition Plan

> **Status:** Active planning  
> **Updated:** 2026-08-04  
> **Tags:** `#formint-pos` `#pos` `#professional` `#restaurant` `#product` `#business` `#roadmap`  
> **Canonical plan:** This is the single source of truth for the Professional Edition business scope, feature priorities, delivery gates, and launch strategy.

## Executive recommendation

Make **Formint POS Professional** the commercial successor to POS Full and the feature-complete restaurant edition built on the POS Solo foundation. Do not delete or rename implementation directories until parity, migration, release, and rollback gates have passed. Keep POS Cloud as the optional SaaS control plane while Formint owns the local restaurant operation.

The recommended product architecture is:

- **Formint desktop:** Tauri 2 shell with offline-first local storage and native printer/scanner support.
- **Web UI:** Astro static shell with reusable components, Alpine.js for local state, and HTMX for server interactions.
- **Application backend:** Django + Django ORM and django-fusion components, forms, tables, routing, and fragment rendering; no Wagtail dependency for the POS application.
- **Data contract:** Astro owns the full page shell; the same domain action can return a lean HTMX data fragment or a versioned JSON response.
- **Cloud:** POS Cloud remains the multi-branch, SaaS, backup, analytics, and tenant control plane.

The Professional Edition should be sold on operational value—multi-branch control, kitchen throughput, customer retention, developer access, and waiter mobility—not on a long list of disconnected screens.

---

## 1. Vision

بناء منصة إدارة مطاعم عربية متكاملة تستهدف:

- المطاعم الفردية
- سلاسل المطاعم
- الكافيهات
- مطابخ السحابة (Cloud Kitchens)
- شركات الامتياز (Franchise)

Formint POS should be **Arabic-first**, offline-capable, restaurant-focused, and extensible enough to grow from one branch to a managed franchise network.

### Product principles

1. **Service continuity first:** checkout, kitchen, and inventory must continue during network outages.
2. **Arabic-first, not Arabic-added-later:** RTL, Arabic invoices, tax presentation, number/date formatting, and translations are release criteria.
3. **One source of truth per concern:** Django is authoritative for business rules; local SQLite is authoritative for offline branch operations; cloud PostgreSQL is authoritative for tenant and cross-branch coordination.
4. **Composable UI:** Astro owns the page and loading UI; django-fusion provides reusable routing, forms, tables, and lean data fragments for HTMX and other clients.
5. **Progressive complexity:** Community is useful on day one; Professional adds measurable restaurant operations; SaaS adds scale and managed services.
6. **Safe extensibility:** versioned APIs, audit trails, permissions, idempotent sync, and migration scripts are part of the product—not post-launch cleanup.

---

## 2. Product editions and positioning

### Community Edition — free / self-hosted

For a single small operator, developer, or evaluation deployment.

- POS checkout and orders
- Products and categories
- Basic inventory
- Basic reports
- Local/offline operation
- Arabic, English, and RTL foundations
- Community documentation and support

Community must remain genuinely useful, but branch management, premium integrations, advanced loyalty, and commercial support belong in paid tiers.

### Professional Edition — target: $49–$99 per installation or annual license

For growing restaurants, cafés, cloud kitchens, and operators with multiple terminals or branches.

- Everything in Community
- Multi-branch management
- Kitchen Display System
- QR menu and menu publishing
- Loyalty and customer profiles
- Versioned API access and API keys
- Mobile waiter workflows
- Advanced reports and branch analytics
- Recipes, ingredient costing, waste tracking, and purchasing
- Roles, approvals, audit history, and device management
- Offline queue, conflict-safe synchronization, and backup/restore
- Priority support and commercial deployment documentation

**Pricing decision to validate:** treat $49–$99 as the initial self-hosted license price range, with `$79` as the reference scenario below. Decide before launch whether the license is one-time with paid updates, annual, or subscription-based. Avoid promising unlimited branches or unlimited support at this price; use a branch/device allowance and clear support boundaries.

### SaaS Edition — monthly subscription

POS Cloud provides tenant management, hosted PostgreSQL, central analytics, backups, billing, integrations, and managed updates.

| Plan | Branches | Suggested price | Best for |
|------|----------|-----------------|----------|
| Starter | 1 | $15/month | One location testing hosted POS |
| Growth | 5 | $49/month | Small restaurant group |
| Business | 20 | $149/month | Regional operator |
| Enterprise | Unlimited | Custom | Franchise and high-volume groups |

SaaS pricing is a hypothesis until validated. Track payment processing, support, storage, and messaging costs before committing to margins.

### Edition boundary

| Capability | Community | Professional | SaaS |
|------------|:---------:|:------------:|:----:|
| Core POS and orders | ✅ | ✅ | ✅ |
| Products, categories, inventory | ✅ | ✅ | ✅ |
| Basic reports | ✅ | ✅ | ✅ |
| Offline checkout | ✅ | ✅ | ✅ |
| Multi-terminal local operation | — | ✅ | ✅ |
| Multi-branch dashboard | — | ✅ | ✅ |
| Kitchen Display | — | ✅ | ✅ |
| QR Menu | — | ✅ | ✅ |
| Loyalty | — | ✅ | ✅ |
| Public API access | — | ✅ | ✅ |
| Mobile waiter | — | ✅ | ✅ |
| Central cloud analytics | — | Optional | ✅ |
| Hosted backups and managed updates | — | Optional | ✅ |
| Tenant isolation and billing | — | — | ✅ |
| Priority/commercial support | — | ✅ | ✅ |

---

## 3. Professional Edition feature contract

The following six features are the Professional Edition launch differentiators. Each feature has a minimum viable contract and an enhancement track so the release cannot be blocked by unlimited scope.

### 3.1 Multi-branch management — P0

**Customer outcome:** An operator can manage branches, terminals, catalogs, stock, staff, and reports centrally while each branch continues operating offline.

**Launch contract:**

- Branch and terminal registry with stable IDs and health/last-seen state.
- Branch-specific price lists, tax settings, menus, warehouses, and printer configuration.
- Role and permission scopes for organization, branch, and terminal.
- Central product/category/configuration publishing with approval workflow.
- Branch sales, inventory, and cash summaries.
- Stock transfers and receiving between branches.
- Idempotent offline queue with retry, conflict visibility, and manual resolution.
- Audit log for every cross-branch change.

**Enhancements:** central purchasing, franchise-specific catalog inheritance, branch benchmarking, scheduled publishing, regional tax rules, and branch-level budgets.

**Acceptance targets:** no duplicate order on retry; branch can complete core sales for at least 24 hours offline; sync success and conflict rates are visible; permissions prevent cross-branch data leakage.

### 3.2 Kitchen Display System (KDS) — P0

**Customer outcome:** Orders reach the right preparation station quickly and staff can manage preparation status without returning to the cashier.

**Launch contract:**

- Station routing by product/category/modifier.
- Ticket states: queued → preparing → ready → served/cancelled.
- Elapsed-time and overdue indicators with configurable thresholds.
- Prioritization, bump/recall, notes, modifiers, and ticket grouping.
- Multi-screen support for kitchen, bar, bakery, and expo stations.
- Offline-safe local queue and reconnect reconciliation.
- Sound/visual notification preferences and accessibility-friendly contrast.
- Kitchen performance metrics: preparation time, overdue rate, and throughput.

**Enhancements:** customer-facing order status, printer fallback, station load balancing, Arabic kitchen labels, and predictive prep-time alerts.

### 3.3 QR Menu — P0

**Customer outcome:** A guest can scan a branch/table QR code and view an accurate, localized menu without staff intervention.

**Launch contract:**

- Public, mobile-first menu route per branch and menu version.
- QR codes scoped to branch, dining area, and table where required.
- Availability, schedule, category, modifier, allergen, and tax display.
- Arabic/English language selection and RTL layout.
- Item images, descriptions, dietary/allergen labels, and price versioning.
- Safe preview/publish workflow; unpublished edits never leak publicly.
- Optional order-request handoff to waiter/POS without requiring online payment.

**Enhancements:** online ordering, payments, promotions, customer feedback, branded domains, and delivery menus. Public menu endpoints must be rate limited and cacheable.

### 3.4 Loyalty system — P1

**Customer outcome:** Restaurants can identify returning customers and reward visits without creating accounting ambiguity.

**Launch contract:**

- Customer profile with consent and communication preferences.
- Earn/redeem rules based on amount, item, visit, or campaign.
- Points ledger with immutable entries, expiry, reversals, and reason codes.
- Reward catalog, coupons, manual adjustment permissions, and audit trail.
- Branch-aware customer lookup with privacy controls.
- Arabic-friendly customer enrollment and receipt messaging.

**Enhancements:** tiers, referrals, birthday campaigns, WhatsApp/SMS connectors, segmentation, and churn/repeat-visit analytics.

Never model loyalty as a mutable balance alone; the ledger is the source of truth and redemptions must be idempotent.

### 3.5 API access — P1

**Customer outcome:** Operators and partners can integrate reporting, menus, orders, loyalty, and inventory without database access.

**Launch contract:**

- Versioned `/api/v1/` contract with OpenAPI documentation.
- Scoped API keys or OAuth-compatible tokens; never share staff passwords.
- Read access for products, categories, branches, sales summaries, customers (consent-aware), inventory, and KDS metrics.
- Controlled write actions for orders, menu publishing, loyalty redemption, and stock operations.
- Pagination, filtering, idempotency keys, request IDs, and consistent errors.
- Per-tenant/branch scopes, rate limits, rotation, revocation, and audit logs.
- Webhooks for order, payment, inventory, loyalty, sync, and branch status events.

**Enhancements:** partner app marketplace, SDKs, webhooks replay, signed payloads, and per-integration usage analytics.

Do not expose internal Django models as the public contract. Define serializers/schemas and compatibility tests first.

### 3.6 Mobile waiter — P1

**Customer outcome:** Waiters can open tables, add items, send tickets, split bills, and see status from a phone or tablet.

**Launch contract:**

- Responsive/PWA workflow usable on current iOS and Android browsers.
- PIN/QR/device sign-in with branch and role scope.
- Table map, open tabs, modifiers, notes, discounts requiring permission, and send-to-kitchen.
- Draft order saved locally and safely retried.
- Table transfer, merge/split checks, service charges, and payment handoff to POS.
- Clear order status and offline/online indicator.
- Large touch targets, low-bandwidth assets, Arabic RTL support, and accessibility labels.

**Enhancements:** native wrapper, handheld printer, tableside payment, guest self-order handoff, and waiter performance analytics.

---

## 4. Full restaurant operations included in Professional

The following capabilities are mandatory Formint contracts. They must be implemented and covered by compatibility tests before any corresponding Forge POS implementation, screen, table, fixture, or asset is removed.

### Menu composition, modifiers, extras, and notes — P0/P1

Formint must preserve the restaurant-specific item model that is easy to lose during edition consolidation:

- **Composite/combo items:** a sellable parent item with required or optional component choices, quantities, substitutions, pricing rules, availability, and tax behavior.
- **Modifiers and item extras:** add-ons, toppings, removals, cooking choices, size upgrades, and priced/unpriced extras attached to an order line; preserve the selected snapshot on the sale and KDS ticket.
- **Notes:** line notes, kitchen notes, waiter notes, customer notes, and internal operational notes with explicit visibility and permission rules. Notes must not be silently copied between customer-facing receipts and kitchen tickets.
- **Templates:** preparation-step, chef-tip, allergen, plating, receipt, and service-note templates with localization and branch scope.
- **Auditability:** record who changed a combo definition, modifier price, extra, or note; historical orders retain immutable item/price/note snapshots.
- **Offline safety:** combo expansion and extra pricing are deterministic from the locally published catalog version and reconcile by stable IDs/idempotency keys.

**Acceptance gate:** create a combo with required choices and extras, add line and kitchen notes, send it to KDS, split/refund it, print the receipt, and reconcile it offline without losing component snapshots or charging an extra twice.

### Forge feature-transfer rule

KDS, loyalty, combo/composite items, modifiers/extras, notes, receipts, responsive tables, theme tokens, and native desktop workflows are **Formint-owned requirements** after migration. Forge is an implementation source during parity, not a second product authority. A Forge feature may be removed only after its Formint replacement, migration notes, tests, screenshots, and rollback/archive entry are complete.

| Formint contract | Status before Forge removal | Required evidence |
|---|---|---|
| KDS: stations, timers, overdue-first, bump/recall, notes, modifiers/extras | 🟡 Must implement | KDS workflow, offline/reconnect, notification, and visual tests |
| Loyalty ledger, rewards, consent, refunds/reversals | 🟡 Must implement | Ledger idempotency, branch, privacy, and reconciliation tests |
| Combo/composite items and immutable component snapshots | 🟡 Must implement | Catalog, order, KDS, receipt, refund, and migration fixtures |
| Modifiers and item extras | 🟡 Must implement | Pricing, quantity, tax, offline retry, and duplicate-prevention tests |
| Line/kitchen/customer/internal notes and templates | 🟡 Must implement | Visibility, localization, receipt/KDS separation, and audit tests |
| Semantic colors, RTL, responsive layouts, skeletons, and empty/error states | 🟡 Must implement | Light/dark/RTL phone/tablet/desktop/second-screen visual matrix |
| Tauri desktop plugin capabilities | 🟡 Must implement selectively | Capability audit, platform smoke tests, and rollback release |

The statuses are intentionally not marked complete merely because the source
behavior exists in Forge documentation. Update them only when the Formint
implementation and evidence are available.


The Professional Edition should consolidate the strongest existing POS Full and Forge POS capabilities without introducing a second data authority.

### Operations

- Orders, sales, returns, voids, discounts, taxes, payments, receipts, and cash sessions.
- Products, categories, modifiers, recipes, ingredients, units, suppliers, purchase orders, and stock counts.
- Ingredient costing, waste reasons, expiry/batch tracking, low-stock alerts, and reorder suggestions.
- Tables, reservations, dining areas, open tabs, split/merge bills, and service charges.
- KDS stations, ticket lifecycle, kitchen notes, and preparation analytics.
- Customer profiles, consent, loyalty ledger, and purchase history.
- Employee roles, shifts, approvals, device registration, and audit history.
- Reports for sales, gross margin, tax, inventory, waste, branch comparison, and staff performance.

### Forge POS enhancements to port

Port the reusable patterns, not the Forge database layer. The latest Forge design baseline is the reference for responsive density, semantic colors, and interaction polish:

- Dense responsive data tables with filtering, sorting, pagination, bulk actions, export, and mobile stacking.
- Reusable form primitives, validation summaries, modal workflows, search, keyboard navigation, and focus management.
- Currency context, dashboard deltas, skeleton/loading states, notification patterns, and visual regression coverage.
- Native printer/file integration and Tauri operations where they improve offline restaurant workflows.
- KDS elapsed-time progress, overdue-first sorting, mute/chime controls, second-screen behavior, station routing, ticket notes, modifiers, and bump/recall.
- Combo/composite item editing, modifier groups, extras pricing, kitchen-note visibility, receipt-note templates, and immutable order-line snapshots.
- Semantic theme tokens rather than hardcoded colors; consistent borders/buttons, high-contrast status colors, dark/light modes, and Arabic RTL variants.
- Responsive breakpoints for dense product grids, tables, cards, KDS columns, waiter touch targets, and mobile stacking; test narrow phone, tablet, desktop, and second-screen layouts.

Django ORM and the Formint sync contract remain authoritative. Do not run Rust/Diesel and Django as competing business data stores.

### Arabic-first and compliance readiness

- Arabic and English translations with RTL layout coverage.
- Arabic invoices, configurable VAT/tax numbers, tax-inclusive/exclusive display, and localized date/number formatting.
- Configurable invoice numbering, refunds, credit notes, and audit history.
- Data retention, export, deletion, consent, and role restrictions suitable for target-market review.
- Market-specific compliance must be verified with local accounting/tax specialists before being marketed as compliant.

---

## 5. Target architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│ Formint POS Professional                                        │
│                                                                  │
│  Tauri 2 shell / browser PWA                                    │
│    └─ Astro static UI                                           │
│       ├─ Alpine.js: local state, dialogs, table/cart behavior   │
│       └─ HTMX: actions, partial updates, live status            │
│                                                                  │
│  Django application + django-fusion                             │
│    ├─ domain models, services, permissions, migrations          │
│    ├─ lean HTMX data fragments and versioned JSON/data API       │
│    ├─ forms, tables, routing helpers, audit and API schemas      │
│    └─ optional Django Ninja adapter after API contract review   │
│                                                                  │
│  Local SQLite / queue  ── sync broker ── POS Cloud PostgreSQL    │
│    ├─ offline sales and inventory                                │
│    ├─ idempotent events and conflict records                     │
│    └─ branch, tenant, analytics, backup, billing, integrations   │
└──────────────────────────────────────────────────────────────────┘
```

### Response modes and rendering boundary

The browser-facing application must be **Astro-shell-first**. Backend responses for dynamic sections contain data or a small semantic fragment only; they must never re-render the page layout, navigation, full component tree, or loading state.

1. **Initial page:** Astro renders the page shell, section structure, accessibility landmarks, and initial preloader/skeleton markup.
2. **HTMX data section:** HTMX requests a narrowly scoped Django endpoint and swaps only the target data region. The response is a data-only HTML fragment (rows, cards, ticket items, status text, or form result), not a full django-fusion component or document.
3. **JSON/data API:** A versioned serializer serves external integrations, Tauri-native operations, reports, and non-browser clients. JSON is not a replacement for the normal browser HTMX path.
4. **Errors and empty states:** The Astro target owns error, retry, empty, offline, and timeout UI; Django returns stable status codes and machine-readable metadata in headers or a minimal fragment.

Business services, validation, permissions, transactions, and audit behavior are shared by every mode. Presentation ownership is not: Astro owns layout, skeletons, preloaders, transitions, and client interaction; Django owns domain data and rules; django-fusion supplies routing, request detection, forms/tables primitives, and lean fragment helpers where needed.

**Explicit non-goal:** Do not use backend-rendered full pages or backend skeleton templates for Formint dynamic sections. Existing full-component responses are migration-era compatibility paths and must be removed after their HTMX data-section replacements pass acceptance tests.

### Frontend-owned loading and preloader contract

Follow the proven `landing-fusion` pattern:

- `frontend/src/components/ui/Skeleton.astro` owns component-shaped placeholders for dashboard cards, tables, KDS tickets, branch lists, QR menus, loyalty balances, and waiter tables.
- `frontend/src/components/ui/PageLoader.astro` or the shared layout owns the first-paint/preloader state.
- `frontend/src/lib/htmx-bootstrap.ts` owns request counters, global progress, slow-request messaging, timeout safety, retry signaling, and response-error handling.
- Each HTMX target provides a local skeleton with `aria-hidden="true"`, a stable target ID, `aria-live="polite"`, and an accessible label. The skeleton is replaced or hidden only after a successful swap.
- `prefers-reduced-motion`, offline mode, slow connections, and keyboard/screen-reader behavior are first-class states.
- No backend response may contain a duplicate global header, layout, full-page loader, or skeleton wrapper.

A data section should follow this contract:

```html
<section id="branch-summary"
         data-skeleton-label="Branch summary"
         aria-live="polite"
         hx-get="/htmx/branches/summary/"
         hx-trigger="load, refresh-branch-summary from:body"
         hx-target="#branch-summary-content"
         hx-swap="innerHTML">
  <div id="branch-summary-content">
    <div data-skeleton="stats-row" aria-hidden="true"><!-- Astro skeleton --></div>
  </div>
</section>
```

Django returns only the contents of `#branch-summary-content`, for example a list of KPI values or a `data-empty` state. It does not return `<html>`, `<body>`, page chrome, or loading markup.

### Shared project assets

Create a single project-level assets workspace beside `frontend/` and `backend/`, following `projects/landing-fusion/assets/`:

```text
projects/pos/formint-pos/
├── assets/                    # shared source assets; no duplicate frontend/backend copies
│   ├── images/                # menu, product, branch, and marketing imagery
│   ├── icons/                 # UI, status, kitchen, payment, and PWA icons
│   ├── fonts/                 # approved Arabic/Latin font files and licenses
│   ├── styles/                # tokens, base, components, layout, RTL, print
│   ├── scripts/               # small shared browser utilities only
│   ├── static/                # files copied or collected for deployment
│   ├── manifests/             # asset manifest, PWA, icon and cache metadata
│   └── fixtures/              # visual-regression and representative UI data only
├── frontend/                  # Astro pages/components; imports source assets via aliases
├── backend/                   # Django data/API/HTMX endpoints; no duplicated UI assets
└── docs/
```

The Astro/Vite configuration should expose stable aliases such as `@assets/images`, `@assets/styles`, and `@assets/static`. Django should reference the same `assets/static` through `STATICFILES_DIRS` and expose a versioned manifest only when a client needs asset metadata. Do not put page templates or backend-owned full UI components in `assets/`; the shared directory is for source assets and static build inputs, while Astro owns the UI markup.

Asset acceptance criteria: one canonical file per image/font/icon, hashed production output, license metadata for fonts/images, no broken imports, RTL/print assets covered, and no asset is removed until the usage scan and visual tests pass.

### Technology stack contract

| Layer | Recommended technology | Responsibility |
|-------|------------------------|----------------|
| Desktop/native | Tauri 2 + Rust | Shell, printer/scanner/file integration, offline device capabilities |
| Web UI | Astro + Alpine.js + HTMX + Tailwind CSS | Static shell, local state, progressive enhancement, responsive styling |
| Application | Django + Django ORM + django-fusion | Domain rules, migrations, permissions, SSR, fragments, forms, tables |
| API | Versioned Django endpoints; evaluate Django Ninja after schema review | Public JSON contract, OpenAPI, webhooks, integrations |
| Async jobs | Celery + Redis, or the existing project worker conventions | Sync retries, reports, notifications, scheduled maintenance |
| Storage | PostgreSQL + S3-compatible object storage in hosted environments | Durable cloud data, backups, exports, media |
| Local data | SQLite with durable queue/WAL strategy | Offline checkout and branch operation |
| Infrastructure | Docker + Traefik | Repeatable deployment, routing, TLS, service boundaries |
| AI | Ollama and OpenAI-compatible providers behind an adapter | Forecasting and recommendations, advisory only |

These are target capabilities, not permission to add dependencies immediately. Confirm established repository support and operational cost before implementation.

### django-fusion integration contract

- Register the POS app, component roots, template roots, middleware, and fragment behavior explicitly.
- Use django-fusion routing, forms, tables, and lean fragment helpers for data sections; do not use it to re-render Astro layout or loading UI.
- Keep POS-specific models/services in the Formint project; upstream only generic, proven capabilities into django-fusion.
- Make Wagtail optional and out of the Formint dependency graph.
- Add health, readiness, request ID, metrics, and structured error responses.
- Prefer PostgreSQL in hosted environments and SQLite for local/offline operation where supported by the sync design.

### Data ownership and synchronization

| Data | Local branch | Cloud |
|------|:------------:|:-----:|
| Open carts, local sessions, printer state | authoritative | not stored as operational truth |
| Completed branch sales | queued/authoritative offline | aggregated and reconciled |
| Global catalog and policies | cached | authoritative |
| Branch inventory movements | created offline/queued | reconciled ledger |
| Loyalty ledger | queued with idempotency key | authoritative after reconciliation |
| Branch/tenant identity and billing | cached | authoritative |

Sync requirements: stable IDs, event version, source device, idempotency key, created/updated timestamps, retry count, conflict status, and an audit reference.

---

## 6. Delivery roadmap

Dates are relative release gates, not promises. A phase is complete only when its acceptance criteria and rollback path are documented.

### Product version map

The business roadmap supplied for the restaurant product maps to the technical gates below:

| Product version | Product outcome | Technical alignment |
|-----------------|-----------------|---------------------|
| Version 1.0 | Core POS: orders, products, categories, inventory, purchases, sales, reports | Phase 1 core parity |
| Version 2.0 | Restaurant operations: tables, reservations, KDS, recipes, ingredients | Phase 2 KDS plus restaurant operations |
| Version 3.0 | Multi-branch: branch dashboard, stock transfer, central purchasing, branch reports | Phase 2 multi-branch |
| Version 4.0 | Customer experience: QR Menu, online-order handoff, loyalty, mobile waiter | Phase 3 customer/staff experience |
| Version 5.0 | Integrations: WhatsApp, Telegram, SMS, payments, delivery providers | Phase 4 API and ecosystem |
| Version 6.0 | AI suite: sales, inventory, waste forecasting, recommendations, RAG analytics | Phase 6 AI expansion |
| Version 7.0 | Enterprise: multi-tenant, franchise, monitoring, warehouse, BI | Phase 6 enterprise expansion plus POS Cloud |

### Phase 0 — Product and architecture foundation

- Confirm edition boundaries, license, pricing, supported platforms, and target-market compliance assumptions.
- Freeze the domain vocabulary: organization, branch, terminal, station, table, menu, order, sale, customer, loyalty ledger, sync event.
- Inventory POS Solo, POS Full, Forge POS, and POS Cloud; classify each capability as keep, port, replace, or retire.
- Preserve `pos-full` while parity work is underway; no destructive rename.
- Define API schemas, event envelopes, permissions, migration format, observability, and backup policy.
- Create `formint-pos/assets/` beside `frontend/` and `backend/`; move shared assets before moving UI code.
- Define the Astro/HTMX rendering boundary: Astro shell and skeletons; Django data-only HTMX responses; JSON only for external/client contracts.
- Establish a baseline dead-code report before deleting or consolidating any POS Full, Solo, or React/Fusion paths.

**Gate:** signed feature matrix, architecture decision, data ownership map, rendering contract, asset manifest, dead-code baseline, and test strategy.

### Phase 1 — Formint foundation and core parity

- Import the latest Forge UI baseline: semantic color tokens, responsive grid/table rules, RTL alignment, compact/skeleton states, notes/receipt categories, currency context, and keyboard/focus behavior.
- Implement the Formint domain contracts for combo/composite items, modifiers, extras, line/kitchen/customer notes, and immutable order snapshots before deleting their Forge counterparts.

- Normalize POS Solo branding/configuration and establish the Formint product identity.
- Port missing Full capabilities: roles, employees, approvals, sync scheduler, node registry, audit, purchasing, recipes, reports, and cloud linkage.
- Port Forge UI primitives, tables, forms, keyboard interactions, export, printer, and KDS UX patterns.
- Build Astro page shells and frontend-owned skeleton/preloader states before converting dynamic sections.
- Convert one vertical slice from backend full-component rendering to an HTMX data-only response and document the pattern.
- Complete core POS, inventory, purchasing, cash, reports, Arabic/RTL, and offline test coverage.

**Gate:** Community and Professional core flows pass desktop, browser, API, offline, and migration tests; the reference slice has no backend layout or skeleton response.

### Phase 2 — Professional differentiators

- Complete the Formint KDS contract, including ticket notes, modifiers/extras, combo component visibility, station routing, elapsed/overdue state, bump/recall, and notification behavior.

- Multi-branch registry, permissions, publishing, transfers, dashboard, and conflict management.
- KDS stations, ticket lifecycle, timers, notifications, printer fallback, and kitchen metrics.
- QR menu versioning, localization, QR generation, preview, publish, cache, and public security controls.

**Gate:** two branches and multiple terminals can operate offline, reconnect, reconcile, and produce matching reports; KDS and QR menu pass a restaurant pilot.

### Phase 3 — Customer and staff experience

- Complete the Formint loyalty ledger and customer-note/privacy contract; migrate Forge customer and receipt-note behavior only after ledger and consent tests pass.

- Loyalty ledger, rewards, consent, customer lookup, and branch-aware reporting.
- Mobile waiter PWA with tables, drafts, modifiers, kitchen handoff, split/merge, and offline retry.
- Performance, accessibility, RTL, low-bandwidth, and device compatibility hardening.

**Gate:** waiter pilot completes representative service without cashier intervention for normal table orders; loyalty balances remain correct across retries/refunds.

### Phase 4 — API and ecosystem

- Release `/api/v1/`, API key lifecycle, scopes, rate limiting, schemas, webhooks, docs, and SDK examples.
- Add payment, messaging, delivery, accounting, storage, and printer integrations behind adapters.
- Create integration sandbox, webhook replay, audit tooling, and support diagnostics.

**Gate:** external integration can be built from documentation without database access; security review and abuse-rate tests pass.

### Phase 5 — SaaS and market launch

- POS Cloud tenant/branch controls, hosted backups, billing, usage limits, central analytics, and managed updates.
- Prepare demo server, landing page, onboarding, migration assistant, support playbooks, screenshots, and marketplace package.
- Run a controlled pilot in Egypt before expanding to Saudi Arabia, UAE, then Kuwait, Qatar, and Bahrain.

**Gate:** operational runbook, backup restore test, support SLA, billing reconciliation, and rollback release are complete.

### Phase 6 — AI and enterprise expansion

- Demand forecasting, stock prediction, sales analytics, waste prediction, and smart recommendations.
- RAG analytics over permission-scoped sales, inventory, recipe, waste, and branch documents with citations and freshness indicators.
- Ollama and OpenAI-compatible providers behind an adapter; forecast models evaluated against historical holdout data before release.
- Multi-tenant/franchise controls, central monitoring, data warehouse, BI dashboards, and enterprise governance.
- AI features must be advisory, explainable, permission-aware, privacy-preserving, and never silently alter prices, stock, or orders.

---

## 7. Dead-code analysis and removal workstream

Dead-code removal is a gated migration activity, not a broad delete pass. The objective is to remove obsolete full-component rendering, duplicate frontend bridges, unused assets, and retired POS Full paths without removing compatibility contracts prematurely.

### Analysis sequence

1. **Inventory:** enumerate Python modules, Django routes, templates, django-fusion components, Astro pages/components, TypeScript exports, Rust commands, CSS classes, assets, package scripts, environment variables, fixtures, and tests.
2. **Static analysis:** run the repository typo/dead-code checker, Ruff `F401/F841/I001`, TypeScript/Astro checks, Rust `cargo check` where applicable, import/export graph analysis, and template/reference scans. Evaluate Vulture for Python and Knip/ts-prune only after verifying they are available for the project.
3. **Runtime evidence:** combine route smoke tests, HTMX endpoint tests, browser coverage, API contract tests, and production-like logs. Static “unused” does not prove dead when a template tag, dynamic import, URL name, migration, or plugin loads it indirectly.
4. **Classify findings:** `remove-now`, `migrate-then-remove`, `keep-compatibility`, `archive`, or `false-positive`. Record owner, evidence, replacement, and rollback impact for every finding.
5. **Quarantine first:** stop new references, mark deprecated paths, and move candidates to a dated migration inventory before deletion.
6. **Delete in small batches:** remove only after tests pass, asset/build manifests are regenerated, and the before/after report is reviewed.

### Initial Formint candidates

- Backend full-page/layout templates and backend skeleton/preloader templates replaced by Astro-owned markup.
- Duplicate `FragmentComponent`/React `FusionPage` paths after the equivalent HTMX data section is proven.
- Unused POS Full-only routes, imports, environment variables, fixtures, and admin widgets after parity migration.
- Duplicate images, fonts, icons, CSS tokens, and compiled assets after consolidation into `assets/`.
- Unused Astro exports, TypeScript helpers, Rust commands, and package scripts identified by static analysis and runtime coverage.
- Wagtail-only POS imports and template loaders once Formint's no-Wagtail boundary is verified.

### Safety gates

- No deletion of persisted identifiers, migrations, sync event schemas, public API routes, or release scripts until compatibility ownership is explicitly transferred.
- A candidate must have zero static references, zero dynamic/template references, zero required migration history, and no runtime coverage evidence for two validation cycles—or an approved archive decision.
- Run frontend build/check/test, backend checks/tests, API/HTMX contract tests, sync/reconciliation tests, and a clean-install smoke test after each batch.
- Keep a deletion manifest with commit, evidence, replacement path, and rollback/archive location.

### Deliverables

- `dead-code-baseline.md` with counts and classifications.
- `asset-usage-report.json` or equivalent machine-readable inventory.
- `deprecated-routes.md` and compatibility expiry dates.
- CI checks preventing new references to retired full-component paths.
- Final deletion report attached to the POS Full retirement release.

### Recommended cleanup enhancements

- Add a shared `make audit-formint` command that runs the Python, TypeScript/Astro, template, asset, and route scans.
- Add coverage thresholds for HTMX data endpoints and Astro target states, including loading, empty, error, offline, and retry paths.
- Generate a route/component/asset graph in CI and fail only on newly introduced unreferenced nodes, allowing a controlled baseline.
- Add visual regression snapshots for skeleton-to-content swaps, Arabic RTL, KDS density, mobile waiter, print, and dark mode.
- Add an API/HTMX deprecation header and request ID so old clients can be measured before removal.

## 8. Migration and retirement policy

Formint is a product rename and consolidation, not a directory rename only.

1. Keep POS Solo and POS Full builds reproducible during the parity period.
2. Introduce `formint-pos` as the canonical product identifier while accepting legacy `pos-solo` and `pos-full` identifiers at boundaries.
3. Migrate persisted node/edition identifiers with an explicit versioned migration and rollback command.
4. Run dual compatibility tests for database fixtures, sync envelopes, API clients, environment variables, and release artifacts.
5. Publish a deprecation release for POS Full; block new feature work there.
6. Delete POS Full only after two successful release cycles, restore verification, migration sign-off, and no active customer depends on its artifact.
7. Retain an immutable archive of source, schema, fixtures, changelog, and migration notes even after deleting the active directory.

**Rollback:** retain the prior installer, database backup, schema migration reverse path where safe, and a feature flag to stop cloud writes before reverting. Never roll back by copying an active database over a newer database without a tested procedure.

---

## 9. Marketplace and go-to-market strategy

### Objective

Fund development by selling a self-hosted Professional Edition while converting successful operators to managed SaaS.

### Channels

| Channel | Strength | Risk | Recommended use |
|---------|----------|------|------------------|
| CodeCanyon | Existing traffic and buyer intent | High commission and support burden | Validate demand with a constrained listing |
| Gumroad | Fast launch and lower platform friction | Licensing/update workflows need ownership | Early direct-license experiments |
| Freemius | Licensing, subscriptions, updates | Vendor dependency and integration cost | Evaluate after license model is stable |
| Direct website | Customer ownership, margin, branding, SaaS conversion | Requires traffic and support funnel | Long-term primary channel |

### Funnel

```text
Visitor → interactive demo → trial/pilot → Professional purchase
        → onboarding/email education → cloud migration → SaaS subscription
```

### Launch sequence

| Month | Deliverable |
|------:|-------------|
| 1 | MVP scope, architecture, documentation, pricing interviews |
| 2 | Demo server, screenshots, landing page, pilot onboarding |
| 3 | Marketplace candidate release and self-hosted installation package |
| 4 | Content, Arabic-first campaigns, partner outreach, support workflow |
| 5 | SaaS beta with selected branches |
| 6 | First paid SaaS customers and conversion review |

Do not promise a marketplace launch until installation, upgrades, licensing, backups, API security, and support boundaries are tested on a clean machine.

---

## 10. Revenue scenarios and metrics

### Illustrative source-code sales

| Sales | Price | Gross revenue |
|------:|------:|--------------:|
| 50 | $79 | $3,950 |
| 200 | $79 | $15,800 |
| 500 | $79 | $39,500 |

### Illustrative SaaS revenue

| Managed branches | Price assumption | Monthly gross revenue |
|-----------------:|------------------:|----------------------:|
| 100 | $15/branch | $1,500 |
| 500 | $15/branch | $7,500 |
| 1,000 | $15/branch | $15,000 |

These are scenarios, not forecasts. The `$79` reference price is a one-time self-hosted-license hypothesis until the pricing decision is validated. Report net revenue after marketplace fees, taxes, payment fees, support, hosting, messaging, storage, and refunds.

### Product metrics

- Checkout success rate while offline and after reconnect.
- Sync success, retry, conflict, and duplicate-prevention rates.
- KDS median preparation time and overdue-ticket rate.
- QR menu views, menu-to-order conversion, and stale-menu incidents.
- Loyalty enrollment, repeat visits, redemption rate, and ledger correction count.
- Mobile waiter order-entry time, draft loss rate, and kitchen handoff latency.
- API error rate, p95 latency, rate-limit events, webhook delivery/replay rate.
- Backup success and restore time; recovery point and recovery time objectives.

### Business metrics

- Marketplace conversion and refund rate.
- Trial-to-paid and Professional-to-SaaS conversion.
- Monthly recurring revenue, gross margin, churn, and expansion revenue.
- Active branches, active terminals, orders per branch, and support tickets per customer.
- Net promoter/customer satisfaction score and time to first successful sale.

Five-year directional goal: 500+ branches, 100+ corporate customers, and annual revenue above $1M USD, subject to validated unit economics and market research.

---

## 11. Target markets and localization

1. **Phase 1:** Egypt — Arabic-first validation, VAT/tax and invoice requirements verified locally.
2. **Phase 2:** Saudi Arabia — localization, payment, tax, and operational partnerships.
3. **Phase 3:** UAE — multi-language, multi-currency, hospitality and franchise workflows.
4. **Phase 4:** Kuwait, Qatar, and Bahrain — local compliance and payment validation per market.

Market expansion requires translated onboarding, local invoice/tax review, payment/delivery integrations, support coverage, and pilot evidence. Translation alone is not market readiness.

---

## 12. Risks and mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sync conflicts or duplicate sales | Critical | Stable IDs, idempotency, event versions, conflict UI, reconciliation tests |
| Scope expansion across six flagship features | High | Launch contracts, phase gates, pilot acceptance, explicit out-of-scope list |
| POS Solo/Full architectural drift | High | Formint canonical interfaces, parity matrix, frozen Full during migration |
| Two competing data stores | Critical | Django/domain service authority; Rust only for native/offline operations |
| API/security abuse | High | Scoped keys, rate limits, rotation, audit logs, schema validation, security tests |
| Offline data loss | Critical | Durable queue, WAL/transactions, export, backup/restore drills, crash tests |
| Wagtail coupling | Medium | Keep Wagtail outside Formint dependencies; use django-fusion components |
| Marketplace support overload | High | Installation checks, version policy, paid support boundary, diagnostics bundle |
| False compliance claims | High | Local legal/accounting review before market-specific claims |
| AI recommendations harm operations | Medium | Explainability, human approval, read-only launch, feature flags |

---

## 13. Recommended immediate actions

1. Approve this document as the canonical Professional Edition scope.
2. Build a capability matrix mapping every POS Full and Forge feature to `keep`, `port`, `replace`, or `retire`.
3. Freeze POS Full feature work and preserve its build/install path until the parity gate passes.
4. Normalize the POS Solo foundation under the Formint product identity without deleting legacy compatibility values.
5. Implement one vertical slice end to end: **branch → order → KDS → offline queue → sync → report**, using an Astro shell, frontend skeleton/preloader, HTMX data-only sections, and JSON only where an external contract requires it.
6. Create the shared `assets/` directory and migrate one asset family with aliases, manifest generation, cache headers, and usage tests.
7. Implement the multi-branch identity, audit, and idempotency primitives before building loyalty or public API features.
8. Produce the dead-code baseline, remove the first approved batch, and publish the deletion manifest before retiring any POS Full directory.
9. Run a two-restaurant pilot before committing to marketplace pricing or SaaS limits.
10. Add this plan to Anytype and link it from the root plan index, POS feature roadmap, and POS edition documentation.

---

## Related implementation documents

- [`../../../projects/pos/README.md`](../../../projects/pos/README.md) — current POS editions and architecture
- [`../../../docs/features/feature-roadmap.md`](../../../docs/features/feature-roadmap.md) — Formint Professional feature priorities
- [`cloud-plan.md`](cloud-plan.md) — cloud/multi-branch integration details and the isolated cloud transport boundary
- [`tauri-plugins-enhancement-plan.md`](tauri-plugins-enhancement-plan.md) — Formint desktop plugin candidates and rollout
- [`forge-pos-plan.md`](forge-pos-plan.md) — Forge parity source, current status, and retirement gates
- [`../legacy/pos/forge-pos-ui-enhancement-master.md`](../legacy/pos/forge-pos-ui-enhancement-master.md) — archived Forge design baseline for colors, responsive UI, RTL, notes, and KDS
- [`django-fusion-enhancements.md`](django-fusion-enhancements.md) — django-fusion component and sync integration
- [`pos-solo-enhancement.md`](pos-solo-enhancement.md) — legacy Solo enhancement plan; superseded by this plan for Professional scope
- [`../../features/feature-roadmap.md`](../../features/feature-roadmap.md) — cross-project feature roadmap
- [`../../publish/pos-release.md`](../../publish/pos-release.md) — release and publishing guidance
- [`../../../docs/Anytype/plans/formint-pos-professional-plan.md`](../../../docs/Anytype/plans/formint-pos-professional-plan.md) — Anytype knowledge-graph object

## Decision record

This plan supersedes the commercial/product scope scattered across the older POS Solo enhancement, POS Full, cloud, and marketplace notes. Those documents remain useful implementation references until their content is migrated, but new Professional Edition work should be tracked here.
