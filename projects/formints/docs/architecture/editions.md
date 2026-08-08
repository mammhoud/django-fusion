# POS Editions

> **Canonical naming (ADR 0001):** Community · Standard · Pro · Cloud — the
> legacy names (Minimal/Solo/Full, pos-mini/pos-solo/pos-full, forge-pos) are
> deprecated but kept below as a mapping aid.

## Comparison at a glance

| Feature | Community (`formintA/`) | Pro (`formint/`, merged) | Cloud (`formintB/`, pos-cloud) | pos-client (`formintC/`) |
|---------|-------------------------|--------------------------|--------------------------------|--------------------------|
| **Tauri shell** | ✅ | ✅ | ❌ (hosted) | ✅ (Vue 3) |
| **Astro frontend** | ❌ | ✅ | ❌ | ❌ |
| **Rust backend** | ✅ | ✅ (minimal shell) | ❌ | ✅ |
| **Django Ninja backend** | ❌ | ✅ | ✅ | ❌ |
| **Robyn sidecar** | ❌ | ✅ | ✅ (pos-cloud-sidecar) | ❌ |
| **Unfold admin** | ❌ | ✅ | ✅ | ❌ |
| **WebSocket streams** | ❌ | ✅ | ✅ (channels + sidecar) | ❌ |
| **Cloud sync** | ❌ (sync client target) | ✅ | ✅ (cloud master) | ❌ |
| **Port** | 1420 | 8767 (backend) / 4321 (frontend) | 8767 (sidecar) | 1420 |

> **Note**: The former `pos-full` (Cloud Master) and `pos-solo` (Standalone)
> editions were merged into the Pro package at `formint/` — the merged package
> owns the Pro Robyn sidecar (`formint/sidecar/`) and both legacy React UIs
> were removed (the Astro + Alpine + HTMX frontend is canonical). The Cloud
> master lives in `formintB/` and now ships two packages: the Django backend
> (`backend/`, `pos-cloud`) plus its own Robyn sidecar (`sidecar/`,
> `pos-cloud-sidecar`); `formintA/` is the Community tier (formerly
> forge-pos / pos-mini).

## Version matrix

| Edition | Directory | Package | Version | Tauri product | Tauri identifier |
|---------|-----------|---------|---------|---------------|------------------|
| **Community** | [`formintA/`](../../formintA/) | `formint-pos` | **0.1.0** | Formint | `com.mammhoud.pos` |
| **Standard** | *(merged into `formint/`)* | `formint-pos-sidecar` / `formint-pos-backend` | **0.1.0** | — | — |
| **Pro** | [`formint/`](../../formint/) | `formint-pos` (frontend `formint-pos-frontend` 0.1.0 · backend `formint-pos-backend` 0.1.0 · sidecar `formint-pos-sidecar` 0.1.0) | **0.1.0** | Formint POS Professional | `cloud.structa.formint.pos` |
| **Cloud** | [`formintB/`](../../formintB/) | `pos-cloud` + `pos-cloud-sidecar` | **0.1.0** | — | — |
| **pos-client** | [`formintC/`](../../formintC/) | `pos-client` | **1.0.0** (package) / **0.1.0** (Cargo + Tauri) | POS Client | `com.pos-client.app` |

### Edition → directory mapping (canonical names)

| Canonical edition | Product tier | Directory / package | Legacy names |
|-------------------|--------------|---------------------|--------------|
| **Community** | Free, offline-first desktop POS (Rust/Diesel, no sidecar) | `formintA/` (`forge-pos`/`pos-mini`) | Minimal, Mini |
| **Standard** | Standalone + embedded Robyn sidecar + cloud sync client | merged into `formint/` | Solo |
| **Pro** | Multi-terminal + cloud master + django-bolt API | `formint/` (merged `formint-pos`) | Full |
| **Cloud** | Hosted multi-terminal SaaS cloud master | `formintB/` (`pos-cloud`) | Cloud Server |

---

## Per-edition components & features

### Community — `formintA/` (formerly forge-pos / pos-mini)

> Lightweight Tauri + React + Rust/Diesel desktop app. No sidecar. Product
> slug on the landing site: `/products/formint-pos/`.

#### Added components (frontend — React 19)

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

**Pages (23):** `Sale`, `ProductsPage`, `ProductManager`, `Transactions`, `Customers`, `Suppliers`, `KitchenDisplay`, `Inventory`, `Recipes`, `Home` (dashboard), `Analytics`, `Reports`, `Auth`, `About`, `Settings`, `StaffPage`, `Employees`, `Payroll`, `Roles`, `EmployeeSchedule`, `Coupons`, `Notes`, `SupportChat`.

#### Features

- Offline-first mode + refunds & returns (Community capability, landing sync Aug 2026)
- 30+ Tauri `#[command]` functions (Diesel ORM) — products, customers, sales, employees, settings
- ESC/POS thermal printer support (direct, only edition with hardware printing)
- Invoice PDF generation (jspdf + Tauri file dialog) + advanced receipt templates
- Product image support (Tauri file picker + base64)
- i18n (English / French / Arabic) via react-i18next
- Role-based access control — 5 default roles with granular JSON permissions
- Theme system — 5 variants (default, corporate, luxury, pastel, cyberpunk) with Theme Studio
- Remix Icon system (~600+ `ri-*` tokens) + vendored Inter/Roboto fonts
- KDS (Kitchen Display System) — time-elapsed bar, overdue sort, mute, chime variants
- Email-based Support Chat (`VITE_SUPPORT_EMAIL`)

---

### Standard — merged into `formint/`

> Standalone tier: everything in Community's data model **plus** the embedded
> Robyn sidecar (REST API, inventory, analytics, WebSocket streams) and the
> cloud sync client that pushes products/sales/nodes to a cloud master.
> Since the `pos-solo` merge this tier shares the `formint/` codebase with Pro;
> it is gated by configuration, not a separate directory.

#### Added components & features (over Community)

- **Robyn sidecar** (`formint/sidecar/`) — REST + WebSocket on `:8766`, Django ORM as data authority
- **Django ORM models** — `full_` / `pos_crm_` / `pos_sync_` tables (30 models)
- **Node registry + heartbeats** — `Node`, `Heartbeat`, `NodeEvent`, `DeviceConfig`, `MasterDevice`
- **Cloud sync client** — pushes products, sales, nodes to a cloud master
- **Loyalty & rewards program** — loyalty transactions, points issued/redeemed
- **Multi-currency & tax profiles** (Standard capability, landing sync Aug 2026)
- **Custom roles & permissions** (Standard capability)
- **Data export CSV/JSON** (Standard capability)
- **Approval workflow** — `SyncApproval` moderation queue

---

### Pro — `formint/` (merged formint-pos, recommended)

> **Phase 2 status:** merge complete — `pos-full` + `pos-solo` consolidated.
> Astro + Alpine + HTMX frontend · Django Ninja backend · Robyn sidecar ·
> Unfold admin · Tauri v2 shell.

#### Added components — backend (`sidecar/`)

| Layer | Components |
|-------|-----------|
| **API** | `formint/api.py` (NinjaAPI + fusion encoder), `controllers.py` (45 ModelController CRUD resources), `schemas.py` (ninja_schema Out + writable/patch factories) |
| **HTMX fragments** | `components.py` (TableMixin tables + FormMixin forms), `handlers.py` (BranchSummaryHandler, TableFragmentHandler, FormFragmentHandler), `fusion_components.py` (FusionDualModeMixin + FragmentComponent) |
| **Fusion render-mode** | `fusion.py` (encode_fragment_pointer, render-mode/nav/assets contract), `core.py` (FormintSite nav source of truth), `views.py` (/fusion/* endpoints) |
| **Admin** | `admin.py` (canonical Unfold ModelAdmin superset), `dashboard.py` (10 KPI cards · 5 charts · 3 tables) |
| **Robyn sidecar routes** | `admin.py`, `apikeys.py`, `approvals.py`, `config.py`, `crm.py`, `data.py`, `fusion_fragments.py`, `htmx_fragments.py`, `info.py`, `kds.py`, `nodes.py`, `reports.py`, `state.py`, `sync.py`, `webhooks.py` |

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
- **Robyn sidecar** — WebSocket streams, data sync, webhooks, scheduler (`:8766`)
- **Cloud sync** — multi-terminal push to a cloud master; sync approval + conflict handling
- **Cloud CRM** — companies, pipelines, stages, contacts, deals, activities, notes
- **Node registry** — `Node`/`Heartbeat`/`NodeEvent`/`DeviceConfig`/`MasterDevice`/`CloudLink`/`SyncLog`
- **Fusion §12 enhancement surface** — include-path component bridge, block attrs, `{% comp %}` tags, `contrib.api` health/branding/layouts, PageHandler full-page pipeline
- Operator-facing render-mode setting (`UserSettings.fusion_render_mode`) + `/fusion/session-mode/` toggle
- **Wagtail-free** Django boundary — models `full_*` preserved for migration compatibility

---

### Cloud — `formintB/` (pos-cloud)

> Hosted multi-terminal SaaS. Two cooperating packages under one tree: the
> **Django backend** (`backend/`, package `pos-cloud`) for the hosted server +
> admin, and a **Robyn sidecar** (`sidecar/`, package `pos-cloud-sidecar`)
> exposing the same models over a fast async REST API. Both share
> `pos_cloud.db`. Cloud master that terminals push their data to; automatic
> backups + monitoring (Cloud capability, landing sync Aug 2026).

#### Added components — backend (`backend/`)

| Layer | App | Components |
|-------|-----|-----------|
| **Models** | `apps/core/` | `Organization`, `Branch`, `Lead`, `Contact`, `Deal`, `InventoryReport`, `BranchReport`, `BranchSyncLog`, `BranchProduct`, `BranchSale`, `BranchInventory`, `DeviceToken`, `SyncConflict`, `SyncQueueItem` |
| **API / viewsets** | `apps/core/` | `api.py` — `/stats`, `/products`, `/sales`, `/inventory`, `/branches`, `/sync-logs` (Ninja, Pydantic-typed); `views.py` — Organization/Branch/Lead/Contact/Deal/InventoryReport/BranchReport `ModelViewset`s with filtersets + report generation |
| **Domain services** | `apps/domain/` | `sync_broker.py`, `sync_queue.py`, `conflict_resolver.py` |
| **Request handlers** | `apps/handlers/` | `sync_api.py` (sync_receive_products/sales/inventory/heartbeat + broadcast), `sync_dashboard.py` (branch health, queue summary/by-branch/list/retry/cancel, conflict list/resolve/dismiss/stats, recent activity), `consumers.py` (channels ASGI), `middleware.py`, `fragments/{layouts, modals, reports, skeletons, tables}.py` (django-fusion) |
| **Config** | `configs/` | `asgi.py`, `wsgi.py`, `urls.py`, `dashboard.py` (django-bolt) + `manage.py` |

#### Added components — sidecar (`sidecar/`, package `pos-cloud-sidecar`)

> Robyn async server that bootstraps the pos-cloud Django ORM (shared
> `pos_cloud.db`), mirrors the Pro sidecar's `handlers.py` pattern, and serves
> the same models + django-fusion contract over REST. Default port `:8767`.

| File | Role |
|------|------|
| `server.py` | Robyn bootstrap — Django ORM setup, CORS middleware, `/`, `/health`, `/stats`, generic CRUD registration for all 14 core models (`/organizations`, `/branches`, `/leads`, `/contacts`, `/deals`, `/inventory-reports`, `/branch-reports`, `/sync/logs`, `/sync/products`, `/sync/sales`, `/sync/inventory`, `/device-tokens`, `/conflicts`, `/queue`) |
| `handlers.py` | JSON-safe serialization + generic CRUD helpers (mirrors `formint/sidecar/handlers.py`) |
| `about.py` | version metadata (dunder-free so PyInstaller bundles it) |
| `routes/fusion.py` | django-fusion API-first contract over the sidecar — `/fusion/health`, `/fusion/render-mode`, `/fusion/nav`, `/fusion/session-mode`, `/fusion/assets` |
| `tests/test_server.py` | smoke test (pytest, `asyncio_mode = auto`) |

Entry point: `pos-cloud-sidecar` (via `[project.scripts]`). Dependencies mirror
the backend (`robyn`, `django`, `django-fusion`, `django-bolt`, `channels`, …)
plus `Jinja2` + `wagtail` for the fusion component renderer.

#### Features added (Cloud tier)

- Multi-tenant cloud master (`Organization` → `Branch` hierarchy)
- **Async sync pipeline** — receive endpoint → `SyncQueueItem` → broker → conflict detection/resolution → WebSocket broadcast back to branches
- **Branch reporting** — `BranchReport` / `InventoryReport` generation + filtersets
- **CRM SaaS** — Leads, Contacts, Deals pipelines
- Device token auth (`DeviceToken` → BaseDeviceToken) for terminal registration
- django-bolt + django-fusion dashboard on ASGI (channels/daphne), PostgreSQL via psycopg2
- **Robyn sidecar** (`pos-cloud-sidecar`, `:8767`) — same Django ORM + `/fusion/*` render-mode contract exposed over a fast async REST API
- Automatic cloud backups + monitoring (Cloud capability, landing sync Aug 2026)

---

### pos-client — `formintC/` (Vue 3 desktop)

> Separate Vue 3 + Tauri desktop client app (not an upgrade of formint-pos).

#### Added components

| Area | Components |
|------|-----------|
| **views/** | `DashboardView.vue`, `MenuView.vue`, `OrdersView.vue`, `SettingsView.vue` |
| **components/** | `TitleBar.vue` |
| **layouts/** | `MainLayout.vue` |
| **router/** | `index.ts` (vue-router) |
| **locales/** | `en-US.ts`, `zh-CN.ts` (vue-i18n) |
| **api/** | `index.ts` |
| **state** | Pinia stores · daisyUI + Tailwind v4 · Tauri plugins (fs, log, opener, store) |

#### Features

- Dashboard (quick actions), Menu catalog, Orders (sale list), Settings (connection)
- Bilingual i18n (EN / zh-CN), custom title bar, Pinia state management

---

## Architecture per edition

### Pro — `formint/` (merged formint-pos — recommended)
```
Astro → HTMX/JSON → Django Ninja backend → Django ORM → SQLite
  └── /api/v1 (45 paginated resources, django-fusion encoder/decoder)
  └── /htmx   (django-fusion tables + forms fragments)
  └── /fusion (render-mode / navigation / assets)
  └── /admin  (Unfold dashboard + KPI cards + charts)
  └── Robyn Sidecar (:8766) → WebSocket streams + data sync + webhooks
```

### Community — `formintA/` (formerly forge-pos / pos-mini)
```
React → Tauri Commands → Rust/Diesel → SQLite
```

### pos-cloud (Cloud)
```
Branches → sync push → Django ASGI (channels/daphne)   [backend/]
  └── SyncQueue → SyncBroker → ConflictResolver → Broadcast to branches
  └── Unfold admin + Bolt dashboard (CRM + reports)
  └── SQLite (pos_cloud.db) — PostgreSQL in production via psycopg2
  └── Robyn sidecar (:8767)  [sidecar/] — same Django ORM + /fusion/* contract
```

### pos-client (Vue 3 desktop)
```
Vue 3 → Tauri Commands → Rust → SQLite
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
