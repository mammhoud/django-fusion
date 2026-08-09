# POS Editions

> **Last Updated:** 9 August 2026
>
> **Canonical naming (ADR 0001):** Community · Standard · Pro · Cloud — the
> legacy names (Minimal/Solo/Full, pos-mini/pos-solo/pos-full, forge-pos) are
> deprecated but kept below as a mapping aid.
>
> **Restructure (Aug 2026):** the monorepo layout is now `formintA/`
> (Community), `formint/` (Pro, merged Standard), `formintB/` (Cloud,
> `pos-cloud`), and `formintC/` (pos-client). `formintA` runs an **Astro 5 +
> React 19** shell and `formintC` ships a **Vue 3 client + Django purchase-app
> backend + Astro (django-fusion) storefront**. The former `forge-pos`,
> `formint-pos`, `pos-client` and `pos-cloud` directory names no longer exist.

## Comparison at a glance

| Feature | Community (`formintA/`) | Pro (`formint/`, merged) | Cloud (`formintB/`, pos-cloud) | pos-client (`formintC/`) |
|---------|-------------------------|--------------------------|--------------------------------|--------------------------|
| **Tauri shell** | ✅ | ✅ | ❌ (hosted) | ✅ (Vue 3) |
| **Astro frontend** | ✅ (Astro 5 + React 19) | ✅ (Astro + Alpine + HTMX) | ✅ (Astro + React 19) | ✅ (storefront, django-fusion) |
| **Rust backend** | ✅ (Diesel) | ✅ (minimal shell) | ❌ | ✅ |
| **Django backend** | ❌ | ✅ (Ninja + sidecar) | ✅ (viewsets + fusion) | ✅ (shop, plain Django) |
| **django-bolt API** | ❌ | ✅ | ✅ (bolt + fusion) | ❌ |
| **Unfold admin** | ❌ | ✅ | ✅ | ❌ |
| **WebSocket streams** | ❌ | ✅ (channels) | ✅ (channels) | ❌ |
| **Cloud sync** | ❌ (sync client target) | ✅ | ✅ (cloud master) | ❌ |
| **Port** | 1420 | 8767 (backend) / 4321 (frontend) / 8766 (bolt) | 8767 (API) / 8082 (admin) | 1420 |

> **Note**: The former `pos-full` (Cloud Master) and `pos-solo` (Standalone)
> editions were merged into the Pro package at `formint/` — the merged package
> runs a **full Django setup** (`formint/sidecar/`: Django + Channels WebSockets
> + django-bolt + django-fusion; the Robyn server was removed) and the legacy
> React UIs were removed (the Astro + Alpine + HTMX frontend is canonical).
> The Cloud master lives in `formintB/` as a **full Django setup** — the Django
> backend (`backend/`, `pos-cloud`) serves the whole API surface (viewsets,
> fusion contract, bolt analytics) on `:8767`. `formintA/` is the Community
> tier (formerly forge-pos / pos-mini), now running an Astro 5 + React 19
> shell over the same Tauri + Rust/Diesel core.

## Version matrix

| Edition | Directory | Package | Version | Tauri product | Tauri identifier |
|---------|-----------|---------|---------|---------------|------------------|
| **Community** | [`formintA/`](../../formintA/) | `formint-pos` | **0.1.0** | Formint | `com.mammhoud.pos` |
| **Standard** | *(merged into `formint/`)* | `formint-pos-sidecar` / `formint-pos-backend` | **0.1.0** | — | — |
| **Pro** | [`formint/`](../../formint/) | `formint-pos` (frontend `formint-pos-frontend` 0.1.0 · backend `formint-pos-backend` 0.1.0 · sidecar `formint-pos-sidecar` 0.1.0) | **0.1.0** | Formint POS Professional | `cloud.structa.formint.pos` |
| **Cloud** | [`formintB/`](../../formintB/) | `pos-cloud` | **0.1.0** | — | — |
| **pos-client** | [`formintC/`](../../formintC/) | `pos-client` (package **1.0.0** · Cargo **0.1.0** · shop backend `purchase-app` 0.1.0) | **1.0.0** (package) / **0.1.0** (Cargo) | POS Client | `com.pos-client.app` |

### Edition → directory mapping (canonical names)

| Canonical edition | Product tier | Directory / package | Legacy names |
|-------------------|--------------|---------------------|--------------|
| **Community** | Free, offline-first desktop POS (Astro + React + Rust/Diesel, no sidecar) | `formintA/` (`formint-pos`) | Minimal, Mini, forge-pos |
| **Standard** | Standalone + embedded Django sidecar + cloud sync client | merged into `formint/` | Solo |
| **Pro** | Multi-terminal + cloud master + django-bolt API | `formint/` (merged `formint-pos`) | Full |
| **Cloud** | Hosted multi-terminal SaaS cloud master | `formintB/` (`pos-cloud`) | Cloud Server |
| **pos-client** | Separate Vue 3 client + Django purchase-app + Astro storefront | `formintC/` (`pos-client`) | — |

---

## Edition scope — what is mini vs what is large

> Measured from the current tree (Aug 2026); file counts exclude
> `node_modules`, `target`, `.venv`, `dist`, and SQLite artifacts.

| Edition | Source files | UI surface | Data layer | Scale tier |
|---------|:-----------:|------------|------------|------------|
| **pos-client** (`formintC/`) | ~120 | 4 Vue views + 8-file Astro storefront | 6 Django models (shop) + Rust/Diesel | **Smallest footprint** — lightweight client + purchase app |
| **Community** (`formintA/`) | ~480 | 25 Astro pages + React 19 components | Rust/Diesel tables | **Mini desktop tier** — offline-first, no Python at all |
| **Cloud** (`formintB/`) | ~450 | 26 Astro pages (Community UI + telemetry) | 13 core models + sync domain | **Server-scale** — hosted, no desktop |
| **Pro** (`formint/`) | ~275 | 32 Astro pages | **48 Django models** + sync/CRM | **Largest / flagship** — desktop + cloud + admin |

**Reading:** *mini* is the **Community** edition — the offline-first desktop
app (Tauri + Rust/Diesel, Astro + React 19) with **no Django, no sidecar, no
cloud**: everything runs locally on the terminal. The *smallest* codebase is
actually **pos-client**, a separate Vue 3 client bundled with a Django
purchase-app backend and an Astro storefront. *More large* is the **Pro**
edition — the flagship that keeps the desktop shell but adds the full Django
sidecar (48 models), Channels WebSockets, django-bolt, django-fusion, Unfold
admin, CRM, and multi-terminal cloud sync. **Cloud** is the hosted-scale
variant: no desktop app, but the deepest server side (multi-tenant
Organization → Branch sync pipeline, conflict resolution, branch reporting).

---

## Per-edition components & features

### Community — `formintA/` (formerly forge-pos / pos-mini)

> Lightweight Tauri + Astro 5 + React 19 + Rust/Diesel desktop app. No
> sidecar, no Django — offline-first. Product slug on the landing site:
> `/products/formint-pos/`.

#### Frontend — Astro 5 + React 19 (`src/`)

**Pages (25 Astro routes):** `index` (dashboard), `sale`, `products`,
`customers`, `suppliers`, `inventory`, `kitchen`, `recipes`, `analytics`,
`tax-reports`, `reports`, `transactions`, `employees`, `payroll`, `roles`,
`schedule`, `staff`, `coupons`, `notes`, `manager`, `settings`, `about`,
`support-chat`, `404`.

**Added components (React 19):**

| Area | Components |
|------|-----------|
| **ui/** | `Modal`, `FormModal`, `ModalProvider`, `ConfirmDialog`, `PasswordConfirmModal`, `DataTable`, `Button`, `Card`, `StatCard`, `StatusToast`, `Skeleton`, `SearchInput`, `DatePicker`, `Badge`, `Tabs`, `Tooltip`, `Avatar`, `Separator`, `BrandLoader`, `BackButton`, `ScrollToTopButton`, `ComparisonTable`, `AnimatePresence` |
| **layout/** | `SideNav`, `PageLayout`, `AnimatedBackground` |
| **display/** | `ThemeToggle`, `ThemeStudio`, `ThemePreviewModal`, `LanguageToggle` |
| **forms/** | `EmployeeForm`, `EmployeeTypeForm` |
| **pos/** | `ProductCard`, `CategoryFilterPills`, `Invoice`, `Receipt`, `ChatSupport` |
| **analytics/** | `TaxReportsPanel` |
| **notes/** | `PrepStepsEditor` |
| **shared/** | `KeyboardShortcutsModal`, `ProductFilterBar` |
| **shell** | `AppShell` |

#### Features

- Offline-first mode + refunds & returns (Community capability, landing sync Aug 2026)
- 30+ Tauri `#[command]` functions (Rust/Diesel) — products, customers, sales, employees, settings
- ESC/POS thermal printer support (direct, only edition with hardware printing)
- Invoice PDF generation (jspdf + Tauri file dialog) + advanced receipt templates
- Product image support (Tauri file picker + base64)
- i18n (English / French / Arabic) via react-i18next
- Role-based access control — 5 default roles with granular JSON permissions
- Theme system — 5 variants (default, corporate, luxury, pastel, cyberpunk) with Theme Studio
- Tailwind v4 + shadcn/ui + flyonui + GSAP + zustand + recharts
- KDS (Kitchen Display System) — time-elapsed bar, overdue sort, mute, chime variants
- Email-based Support Chat (`VITE_SUPPORT_EMAIL`)
- Vitest + Playwright test suites (unit + e2e)

---

### Standard — merged into `formint/`

> Standalone tier: everything in Community's data model **plus** the embedded
> Django sidecar (Django REST + Channels WebSocket streams + django-bolt) and
> the cloud sync client that pushes products/sales/nodes to a cloud master.
> Since the `pos-solo` merge this tier shares the `formint/` codebase with Pro;
> it is gated by configuration, not a separate directory.

#### Added components & features (over Community)

- **Django sidecar** (`formint/sidecar/`) — Django + Channels WS + django-bolt + fusion, Django ORM as data authority
- **Django ORM models** — `full_` / `pos_crm_` / `pos_sync_` tables (**48 models**)
- **Node registry + heartbeats** — `Node`, `Heartbeat`, `NodeEvent`, `DeviceConfig`, `MasterDevice`
- **Cloud sync client** — pushes products, sales, nodes to a cloud master
- **Loyalty & rewards program** — loyalty transactions, points issued/redeemed
- **Multi-currency & tax profiles** (Standard capability, landing sync Aug 2026)
- **Custom roles & permissions** (Standard capability)
- **Data export CSV/JSON** (Standard capability)
- **Approval workflow** — `SyncApproval` moderation queue

---

### Pro — `formint/` (merged formint-pos, recommended)

> **Phase 2 status:** merge complete — `pos-full` + `pos-solo` consolidated;
> the Robyn server was replaced by a full Django setup (django-bolt + Channels
> + django-fusion). Astro + Alpine + HTMX frontend · Django Ninja backend ·
> django-bolt API · Unfold admin · Tauri v2 shell.

#### Added components — backend (`sidecar/`)

| Layer | Components |
|-------|-----------|
| **API** | `formint/api.py` (NinjaAPI + fusion encoder), `controllers.py` (45 ModelController CRUD resources), `schemas.py` (ninja_schema Out + writable/patch factories) |
| **HTMX fragments** | `components.py` (TableMixin tables + FormMixin forms), `handlers.py` (BranchSummaryHandler, TableFragmentHandler, FormFragmentHandler), `fusion_components.py` (FusionDualModeMixin + FragmentComponent) |
| **Fusion render-mode** | `fusion.py` (encode_fragment_pointer, render-mode/nav/assets contract), `core.py` (FormintSite nav source of truth), `views.py` (/fusion/* endpoints) |
| **Admin** | `admin.py` (canonical Unfold ModelAdmin superset), `dashboard.py` (10 KPI cards · 5 charts · 3 tables) |
| **django-bolt API** | `bolt_api.py` (BoltAPI core REST endpoints; served natively by `manage.py runbolt` via `BOLT_API`) — replaces the removed Robyn `server.py`/`routes/` |
| **Channels WebSockets** | `consumers.py` (`ws/nodes`, `ws/entities`, `ws/config`) + `asgi.py` (ProtocolTypeRouter) — replaces Robyn WS streams |
| **Django-native surface** | `views_django.py`, `htmx_views.py`, `api_keys_views.py`, `fusion_views.py`, `configs/urls.py` (full HTTP surface served by daphne / runserver) |
| **Signal receivers** | `sync_signals.py`, `signal_handlers.py`, `ws_sync_signals.py` — registered via `PosFullConfig.ready()` (no Robyn bootstrapping) |

#### Added components — frontend (`frontend/`)

| Area | Components |
|------|-----------|
| **ui/** | `Icon.astro`, `Skeleton.astro`, `ui/icons/Sprite.astro` |
| **layouts/** | `Layout.astro` (global HTMX indicator + skeleton loading) |
| **lib/** | `htmx-bootstrap.ts`, `fusion-decoder.ts` + `fusion-types.ts` (TS FusionCodec counterpart), `session-sync.ts` (cross-tab BroadcastChannel sync), `alpine-stores.ts`, `sparkline.ts`, `admin-settings-poll.ts` |

**Pages (32 Astro routes):** `index`, `data`, `fusion`, `pos/{sale, products, inventory, customers, suppliers, transactions}`, `kitchen/{index, recipes}`, `hr/{employees, payroll, roles, schedules}`, `ops/{coupons, delivery-types, delivery-zones, shifts, vertical-slice}`, `crm/{dashboard, companies, contacts, deals, pipelines, activities, notes}`, `admin/{about, notes, reports, settings, support}`.

#### Features added (Pro tier)

- Django Ninja + ninja-extra typed REST API — **45 paginated resources** with fusion envelope `{ status, message, data }`
- django-fusion **data components** — server-rendered tables + forms over HTMX (render-first / data-API dual mode)
- **Unfold admin** — KPI dashboard, charts, loyalty & settings management, 2FA
- **Django sidecar** — full Django on `:8767` (daphne) + django-bolt `/bolt/*` on `:8766` (`runbolt`); Channels WebSocket streams `ws/{nodes,entities,config}`
- **Signal receivers** — audit trail, outbound webhooks, and cloud WS push wired through Django signals (`PosFullConfig.ready()`)
- **Cloud sync** — multi-terminal push to a cloud master; sync approval + conflict handling
- **Cloud CRM** — companies, pipelines, stages, contacts, deals, activities, notes
- **Node registry** — `Node`/`Heartbeat`/`NodeEvent`/`DeviceConfig`/`MasterDevice`/`CloudLink`/`SyncLog`
- **Fusion §12 enhancement surface** — include-path component bridge, block attrs, `{% comp %}` tags, `contrib.api` health/branding/layouts, PageHandler full-page pipeline
- Operator-facing render-mode setting (`UserSettings.fusion_render_mode`) + `/fusion/session-mode/` toggle
- **Wagtail-free** Django boundary — models `full_*` preserved for migration compatibility

---

### Cloud — `formintB/` (pos-cloud)

> Hosted multi-terminal SaaS as a **full Django setup**: the Django backend
> (`backend/`, package `pos-cloud`) serves the entire API surface —
> django-fusion viewsets, the `/fusion/*` render-mode contract, the
> Community-UI bridges, and the BoltAPI analytics dashboard — sharing
> `pos_cloud.db`. The Robyn sidecar that previously served the REST surface
> has been **removed**; a second Django dev server on `:8767` now answers the
> sidecar-compatible paths the frontend expects. Cloud master that terminals
> push their data to; automatic backups + monitoring (Cloud capability, landing sync Aug 2026).

#### Added components — backend (`backend/`)

| Layer | App | Components |
|-------|-----|-----------|
| **Models** | `apps/core/` | `Organization`, `Branch`, `Lead`, `Contact`, `Deal`, `InventoryReport`, `BranchReport`, `BranchSyncLog`, `BranchProduct`, `BranchSale`, `BranchInventory`, `DeviceToken`, `SyncConflict`, `SyncQueueItem` |
| **API / viewsets** | `apps/core/` | `views.py` — Organization/Branch/Lead/Contact/Deal/InventoryReport/BranchReport/DeviceToken/SyncConflict/SyncQueueItem `ModelViewset`s with filtersets + report generation; `api.py` — BoltAPI analytics (`/stats`, `/products`, `/sales`, `/inventory`, `/branches`, `/sync-logs`) |
| **Domain services** | `apps/domain/` | `sync_broker.py`, `sync_queue.py`, `conflict_resolver.py` |
| **Request handlers** | `apps/handlers/` | `sync_api.py` (sync_receive_products/sales/inventory/heartbeat + broadcast), `sync_dashboard.py` (branch health, queue summary/by-branch/list/retry/cancel, conflict list/resolve/dismiss/stats, recent activity), `consumers.py` (channels ASGI), `middleware.py`, `fragments/{layouts, modals, reports, skeletons, tables}.py` (django-fusion), `fusion.py` (render-mode contract), `surface.py` (root CRUD + bridges) |
| **Config** | `configs/` | `asgi.py`, `wsgi.py`, `urls.py`, `dashboard.py` (django-bolt) + `manage.py` |

#### Frontend — `frontend/` (Astro 5 + React 19)

**Pages (26 Astro routes):** the Community UI surface (dashboard, sale,
products, customers, suppliers, inventory, kitchen, recipes, analytics,
tax-reports, reports, transactions, employees, payroll, roles, schedule,
staff, coupons, notes, manager, settings, about, support-chat, 404) **plus**
`telemetry` — the cloud telemetry dashboard.

#### Sidecar surface — served by Django (`apps/handlers/surface.py` + `fusion.py`)

> The Robyn sidecar is gone; Django answers the same paths on `:8767`.

| Area | Django module | Paths |
|------|---------------|-------|
| **Root CRUD** | `apps/handlers/surface.py` | `/organizations`, `/branches`, `/leads`, `/contacts`, `/deals`, `/inventory-reports`, `/branch-reports`, `/sync/{logs,products,sales,inventory}`, `/device-tokens`, `/conflicts`, `/queue` (generic JSON CRUD, `{count, items}` sidecar shape; JSON 401 for anonymous, staff-only token role/is_active writes, `token_hash` never serialized) |
| **Community-UI bridges** | `apps/handlers/surface.py` | `/api/sales`, `/api/products`, `/api/settings` (anonymous, read-only) |
| **Fusion contract** | `apps/handlers/fusion.py` | `/fusion/health`, `/fusion/render-mode`, `/fusion/nav`, `/fusion/session-mode` (GET/POST/DELETE), `/fusion/assets` |
| **System** | `configs/urls.py` | `/stats`, `/health` |

#### Features added (Cloud tier)

- Multi-tenant cloud master (`Organization` → `Branch` hierarchy)
- **Async sync pipeline** — receive endpoint → `SyncQueueItem` → broker → conflict detection/resolution → WebSocket broadcast back to branches
- **Branch reporting** — `BranchReport` / `InventoryReport` generation + filtersets
- **CRM SaaS** — Leads, Contacts, Deals pipelines
- Device token auth (`DeviceToken` → BaseDeviceToken) for terminal registration
- django-bolt + django-fusion dashboard on ASGI (channels/daphne), PostgreSQL via psycopg2
- **Full Django API surface** — all CRUD, fusion contract, and Community-UI bridges served by Django (`:8767` API / `:8082` admin) with the Robyn sidecar removed
- Automatic cloud backups + monitoring (Cloud capability, landing sync Aug 2026)

---

### pos-client — `formintC/` (Vue 3 desktop + Django shop)

> Separate Vue 3 + Tauri desktop client app, **bundled since Aug 2026 with a
> Django purchase-app backend and an Astro (django-fusion) storefront** — a
> full client-to-shop stack, not an upgrade of formint-pos.

#### Components — desktop client (`src/`, Vue 3)

| Area | Components |
|------|-----------|
| **views/** | `DashboardView.vue`, `MenuView.vue`, `OrdersView.vue`, `SettingsView.vue` |
| **components/** | `TitleBar.vue` |
| **layouts/** | `MainLayout.vue` |
| **router/** | `index.ts` (vue-router) |
| **locales/** | `en-US.ts`, `zh-CN.ts` (vue-i18n) |
| **api/** | `index.ts` |
| **state** | Pinia stores · daisyUI + Tailwind v4 · Tauri plugins (fs, log, opener, store) |

#### Components — purchase-app backend (`backend/`, plain Django)

| App | Models | Notes |
|-----|--------|-------|
| `employee` | — | staff/auth support (`Employee`), fusion components + templates |
| `shop` | `Category`, `Product`, `Cart`, `CartItem`, `Order`, `OrderItem` | catalog + cart + order lifecycle; `admin.py`, `handlers.py`, `services.py`, `fusion.py`, `auth_adapters.py` |

#### Components — storefront (`frontend/`, Astro + django-fusion)

| File | Role |
|------|------|
| `pages/index.astro` | storefront home |
| `layouts/Layout.astro` | global layout |
| `components/HtmxBootstrap.astro` | django-fusion HTMX bootstrap |
| `components/ui/{CartDrawer, LoginModal, Toast}.astro` | cart, auth, feedback |
| `components/layout/{Header, Footer}.astro` | shell |

#### Features

- Desktop client: Dashboard (quick actions), Menu catalog, Orders (sale list), Settings (connection)
- Bilingual i18n (EN / zh-CN), custom title bar, Pinia state management
- Django purchase app: catalog + cart + orders with admin (`backend/`), storefront served over django-fusion (`frontend/`)

---

## Architecture per edition

### Pro — `formint/` (merged formint-pos — recommended)
```
Astro → HTMX/JSON → Django Ninja backend → Django ORM → SQLite
  └── /api/v1 (45 paginated resources, django-fusion encoder/decoder)
  └── /htmx   (django-fusion tables + forms fragments)
  └── /fusion (render-mode / navigation / assets)
  └── /admin  (Unfold dashboard + KPI cards + charts)
  └── django-bolt (:8766, runbolt) + Channels WS streams + signals
```

### Community — `formintA/` (formerly forge-pos / pos-mini)
```
Astro 5 (25 pages) + React 19 → Tauri Commands → Rust/Diesel → SQLite
```

### pos-cloud (Cloud)
```
Branches → sync push → Django ASGI (channels/daphne)   [backend/]
  └── SyncQueue → SyncBroker → ConflictResolver → Broadcast to branches
  └── Unfold admin + Bolt dashboard (CRM + reports)
  └── SQLite (pos_cloud.db) — PostgreSQL in production via psycopg2
  └── Django API server (:8767) — same project; full CRUD + /fusion/* + bridges
  └── Astro + React 19 frontend (:8082 admin, Community UI + telemetry)
```

### pos-client (Vue 3 desktop + Django shop)
```
Vue 3 → Tauri Commands → Rust → SQLite          [src/ + src-tauri/]
Django purchase-app (shop + employee) → SQLite  [backend/]
Astro storefront → django-fusion fragments       [frontend/]
```

## Preset Configurations (formint-pos)

| Preset | Brand | Products |
|--------|-------|----------|
| `all` | Level Up Gaming Center | base + gaming + coffee |
| `base` | POS KO | Core POS products |
| `gaming` | Level Up Gaming Center | Gaming station products |
| `coffee` | The Daily Grind | Coffee shop products |

## Related docs

- [Canonical edition naming (ADR 0001)](../adr/0001-pos-editions-naming.md)
- [Table & column comparison across editions](table-column-comparison.md)
- [Sidecar migration guide](sidecar-migration-guide.md)
- [POS architecture (all editions)](pos-architecture.md)
