# Formints Editions — Feature Comparison

> Tags: `#formints` `#pos` `#editions` `#comparison` `#matrix` `#buyer-guide` — statuses: Community/Standard/Pro ✅ done · Cloud 🟡 staging · pos-client 🔵 dev (21 Aug 2026).

> **Canonical source of edition facts:** [`README.md`](README.md) (extension
> chain, data model, E2E matrix). This page is the at-a-glance **buyer and
> capability comparison** across all editions — keep it in sync with the
> edition plans when features move between tiers.

**Date:** 2026-08-20 · **Product home:** `projects/formints/` (Community ·
Standard · Pro · Cloud · Client)

## 1. Editions at a glance

| Edition | Directory | Frontend | Backend (primary) | Sidecar | Status |
|---------|-----------|----------|-------------------|---------|--------|
| **Community** | `formint-community/` | Astro 5 + React 19 | Rust/Diesel + SQLite | None | ✅ done |
| **Standard** | `formint-standard/` | Astro 5 + React 19 + Alpine | Rust/Diesel + SQLite | Django (optional) | ✅ done |
| **Pro** | `formint-pro/` | Astro 5 + Alpine + HTMX | Django + django-fusion + django-bolt + Unfold | Required | ✅ done |
| **Cloud** | `formint-cloud/` | Astro 5 + Alpine | Django (multi-tenant, Channels) | Required | 🟡 staging |
| **pos-client** | `formint-client/` | Vue 3 (Vite) | Django shop + Astro storefront | Required | 🔵 dev |

> **Feature inheritance (hard rule):** every higher edition MUST include every
> feature of the tiers below it. Each edition plan's final task runs a parity
> sweep that verifies the inheritance and fixes gaps.

## 2. Capability matrix

| Capability | Community | Standard | Pro | Cloud | Client |
|------------|:---------:|:--------:|:---:|:-----:|:------:|
| **Core POS** (sales, sale items, products, categories, customers, employees) | ✅ | ✅ | ✅ | ✅ | ✅ (shop) |
| Refunds & returns | ✅ | ✅ | ✅ | ✅ | — |
| Offline-first operation | ✅ | ✅ | ✅ (WS sync) | — | — |
| Multi-currency | — | ✅ | ✅ | ✅ | — |
| Tax profiles | — | ✅ | ✅ | ✅ | — |
| Custom roles / permissions | — | ✅ | ✅ | ✅ | — |
| CSV/JSON export | — | ✅ | ✅ | ✅ | — |
| Offline sync queue | — | ✅ | ✅ (multi-terminal) | — | — |
| Ingredients / recipes | ✅ | ✅ | ✅ | ✅ | — |
| Kitchen Display System (KDS) | — | — | ✅ | ✅ | — |
| QR menu | — | — | ✅ | ✅ | — |
| Loyalty system | — | — | ✅ (P1) | ✅ | — |
| API access | — | — | ✅ (P1) | ✅ | ✅ (shop API) |
| Mobile waiter | — | — | ✅ (P1) | ✅ | — |
| Multi-terminal sync | — | — | ✅ (P1) | ✅ | — |
| Offline queue (server-backed) | — | — | ✅ (P1) | ✅ | — |
| Barcode scanner | — | — | ✅ (P1) | ✅ | — |
| POS-KO gaming center | — | — | ✅ (P0) | ✅ | — |
| Gift cards | — | — | ✅ (P2) | ✅ | — |
| Table management + reservations | — | — | ✅ (P2) | ✅ | — |
| Delivery integration | — | — | ✅ (P2) | ✅ | — |
| AI forecasting | — | — | ✅ (P2) | ✅ | — |
| Employee scheduling | — | — | ✅ (P3) | ✅ | — |
| Customer display | — | — | ✅ (P3) | ✅ | — |
| Self-checkout kiosk | — | — | ✅ (P3) | ✅ | — |
| Inventory forecasting | — | — | ✅ (P3) | ✅ | — |
| Purchase order workflow | — | — | ✅ | ✅ | — |
| CRM (Company, Pipeline, Deal, Contact, Activity) | — | — | ✅ | ✅ | — |
| Cloud sync (Organization → Branch, async) | — | — | — | ✅ | — |
| Schema-per-tenant (`django-tenants`) | — | — | — | ✅ (flip-on) | — |
| Backups + monitoring | — | — | — | ✅ | — |
| Vue client + Django shop + storefront | — | — | — | — | ✅ |
| Modular TS/JS SDK (`@formints/client`) | ✅ | ✅ | ✅ | ✅ | ✅ |

> **Legend:** ✅ included · — not included at this tier · (Pn) = planned phase
> in the Pro plan (P0 shipped, P1–P3 phased). Cloud inherits Pro's surface and
> adds multi-tenant sync; verify per-phase status in [`03-pro.md`](03-pro.md)
> and [`04-cloud.md`](04-cloud.md) before marketing a feature as shipped.

## 3. Data model at each extension

| Edition | Schema | Core entities added at this tier |
|---------|--------|----------------------------------|
| Community | Diesel/SQLite `restaurant.db` | `sales`, `sale_items`, `products`, `categories`, `customers`, `employees`, `ingredients`, `recipes`, `settings`, … |
| Standard | `restaurant.db` + optional Django `full_*` | Rust `Currency`, `TaxProfile`, `Role`, export engine; optional sidecar `Node`, `Heartbeat`, `DeviceConfig`, `SyncApproval`, `SyncLog` |
| Pro | Django `full_*` (48 models) | CRM + KDS/QR/loyalty/gaming/gift cards/tables/delivery/time clock/kiosk (see §2) |
| Cloud | `pos_cloud.db` + PostgreSQL schemas | `Organization`, `Branch`, sync/branch models, `Tenant`/`Domain` registry, `BranchSettings` |
| Client | Vue client + Django shop | `Category`, `Product`, `Cart`, `CartItem`, `Order`, `OrderItem`, `Employee` |

## 4. Deployment & runtime

| Aspect | Community / Standard | Pro | Cloud | Client |
|--------|----------------------|-----|-------|--------|
| Deployment | Desktop (Tauri), local SQLite | Desktop + optional server; Django required | Hosted SaaS master | Desktop + Django shop |
| Server dependency | None (offline-first) | Required Django backend | Required (multi-tenant) | Required shop backend |
| Sync surface | Offline queue (Standard) | Multi-terminal WS | `/sync/push` + `/ws/sync-events/` broadcast | Shop REST API |
| Background tasks | None | Dramatiq via django-fusion | Dramatiq (backups, reports) | Dramatiq |
| Auth stack | Local | allauth + fusion | allauth + workspace/tenant scoping | allauth |

## 5. E2E & sync coverage

Canonical Playwright suite: `projects/formints/tests/pos-e2e/` — one project per
edition (ports 1420–1433) + `formint-cloud-sync` backend project. See the
[E2E & sync matrix](README.md#e2e--sync-matrix) in the editions index.

## 6. Which edition for whom (buyer guide)

| Buyer | Edition | Why |
|-------|---------|-----|
| Single café / small restaurant, no server | **Community** | Offline-first, free, no dependencies |
| Multi-currency / tax / role needs, local-first | **Standard** | Adds money, tax, roles, export on the same Rust core |
| Full-service restaurant (KDS, tables, delivery, loyalty) | **Pro** | Required Django backend unlocks CRM + Pro modules |
| Multi-branch chain wanting hosted sync + monitoring | **Cloud** | Organization → Branch hierarchy, async sync, backups |
| Retail shop with its own catalog + online storefront | **Client** | Vue client + Django shop + Astro storefront |

## Remarks & Notes

- The editions index [`README.md`](README.md) is the canonical extension chain;
  this comparison is derived from it and the per-edition plans
  ([`01`](01-community.md) → [`05`](05-pos-client.md), [`08`](08-tenant-schemas.md)).
- (Pn) phase markers are roadmap intent, not shipped features — check the plan
  file and the repo before claiming capability in sales material.
- Feature inheritance means Pro/Cloud rows implicitly include every
  Community/Standard capability marked ✅ above.
