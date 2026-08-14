# POS Editions

> **Canonical naming (ADR 0001):** Community · Standard · Pro · Cloud — the
> legacy names (Minimal/Solo/Full, pos-mini/pos-solo/pos-full, forge-pos) are
> deprecated but kept below as a mapping aid.

## Comparison at a glance

| Feature | Community (`formint-community/`) | Pro (`formint-pro/`, merged) | Cloud (`formint-cloud/`, formint-cloud) | pos-client (`formint-client/`) |
|---------|-------------------------|--------------------------|--------------------------------|--------------------------|
| **Tauri shell** | ✅ | ✅ | ❌ (hosted) | ✅ (Vue 3) |
| **Astro frontend** | ❌ | ✅ | ❌ | ❌ |
| **Rust backend** | ✅ | ✅ (minimal shell) | ❌ | ✅ |
| **Django Ninja backend** | ❌ | ✅ | ✅ | ❌ |
| **Robyn server** | ❌ | ✅ | ❌ (full Django setup) | ❌ |
| **Unfold admin** | ❌ | ✅ | ✅ | ❌ |
| **WebSocket streams** | ❌ | ✅ | ✅ (channels) | ❌ |
| **Cloud sync** | ❌ (sync client target) | ✅ | ✅ (cloud master) | ❌ |
| **Port** | 1420 | 8767 (backend) / 4321 (frontend) | 8767 (API) / 8082 (admin) | 1420 |

> **Note**: The former `pos-full` and `pos-solo` products were merged into
> `formint-pro/`; its Django server is canonical and its Robyn/django-bolt
> runner is retained only for compatibility packaging. The legacy React UIs
> were removed in favour of the Astro + Alpine + HTMX frontend. `formint-cloud/`
> is a separate full-Django hosted master; Django serves its API, fusion
> contract, and bolt analytics on the documented ports. `formint-community/`
> is the standalone Community tier, while `formint-standard/` is the separate
> local-first Standard tier.

## Version matrix

| Edition | Directory | Package | Version | Tauri product | Tauri identifier |
|---------|-----------|---------|---------|---------------|------------------|
| **Community** | [`formint-community/`](../../formint-community/) | `formint-pos` | **0.1.0** | Formint | `com.mammhoud.pos` |
| **Standard** | [`formint-standard/`](../../formint-standard/) | `formint-standard` | **0.1.0** | Formint Standard | `com.mammhoud.formint-standard` |
| **Pro** | [`formint-pro/`](../../formint-pro/) | `formint-pos` (frontend `formint-pos-frontend` 0.1.0 · backend `formint-pos-backend` 0.1.0 · server `formint-pos-server` 0.1.0) | **0.1.0** | Formint POS Professional | `cloud.structa.formint.pos` |
| **Cloud** | [`formint-cloud/`](../../formint-cloud/) | `formint-cloud` | **0.1.0** | — | — |
| **pos-client** | [`formint-client/`](../../formint-client/) | `pos-client` | **1.0.0** (package) / **0.1.0** (Cargo + Tauri) | POS Client | `com.pos-client.app` |

> **Standalone community version:** published as `github.com/mammhoud/formint-community` —
> package `formint-community`, product **Formints Community**, identifier
> `com.mammhoud.formint-community`. Refreshed from `formint-community/` via `make community-bundle`.

### Edition → directory mapping (canonical names)

| Canonical edition | Product tier | Directory / package | Legacy names |
|-------------------|--------------|---------------------|--------------|
| **Community** | Free, offline-first desktop POS (Rust/Diesel, no server) | `formint-community/` | Minimal, Mini |
| **Standard** | Standalone Rust/Diesel POS with money, tax, permissions, export, and sync queue | `formint-standard/` | Solo |
| **Pro** | Django-first multi-terminal POS with CRM, fusion, sync, and optional legacy runner | `formint-pro/` | Full |
| **Cloud** | Hosted multi-terminal SaaS cloud master | `formint-cloud/` (`formint-cloud`) | Cloud Server |

---

## Per-edition components & features

### Community — `formint-community/` (formerly forge-pos / pos-mini)

> Lightweight Tauri + React + Rust/Diesel desktop app. No server. Product
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

- **Offline-first mode + offline-first badge** — no server, no sidecar, local
  SQLite only. The **"Offline-first · open source" badge** (`offer_label`)
  marks the Community edition on the landing edition + home product cards, and
  in-app a calm banner ("Offline mode — data stays on this device") shows
  whenever the OS reports the device offline (`useOfflineMode` hook).
  (Community capability, landing sync Aug 2026)
- **Refunds & returns** — Transactions → Refund on a completed sale → confirm
  dialog → `invoke('refund_sale', { saleId })` → Rust `sales::refund_sale`
  flips `sales.status` to `"refunded"`. Only `completed` sales, once only;
  the transaction trail is preserved (no data deleted).
- **API surface:** Tauri `invoke` commands (Rust/Diesel) — the `@formints/client` TS bundle applies to the Django-backed editions (Standard/Cloud), not this edition
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

### Standard — `formint-standard/`

> Standalone tier: everything in Community's local-first workflow plus the
> Rust/Diesel money, tax-profile, permissions, export, and sync-queue surfaces.
> Standard is a maintained canonical package at `formint-standard/`; it is not
> an alias for the Pro Django server.

#### Added components & features (over Community)

- **Standard local data layer** (`formint-standard/src-tauri/`) — Rust/Diesel SQLite with offline queue and reconnect support
- **Standard reference data** — currencies, tax profiles, permission resolution, and CSV/JSON export surfaces
- **Node registry + heartbeats** — `Node`, `Heartbeat`, `NodeEvent`, `DeviceConfig`, `MasterDevice`
- **Cloud sync client** — pushes products, sales, nodes to a cloud master
- **Loyalty & rewards program** — loyalty transactions, points issued/redeemed
- **Multi-currency & tax profiles** (Standard capability, landing sync Aug 2026)
- **Custom roles & permissions** (Standard capability)
- **Data export CSV/JSON** (Standard capability)
- **Approval workflow** — `SyncApproval` moderation queue

---

### Pro — `formint-pro/` (merged formint-pos, recommended)

> **Phase 2 status:** merge complete — `pos-full` + `pos-solo` consolidated.
> Astro + Alpine + HTMX frontend · Django Ninja backend · optional legacy
> Robyn/django-bolt compatibility runner · Unfold admin · Tauri v2 shell.

#### Added components — backend (`server/`)

| Layer | Components |
|-------|-----------|
| **API** | `server/formint/api.py` (NinjaAPI + fusion encoder), `server/formint/controllers.py` (45+ ModelController CRUD resources), `server/formint/schemas.py` (fusion Out + writable/patch factories) |
| **HTMX fragments** | `components.py` (TableMixin tables + FormMixin forms), `handlers.py` (BranchSummaryHandler, TableFragmentHandler, FormFragmentHandler), `fusion_components.py` (FusionDualModeMixin + FragmentComponent) |
| **Fusion render-mode** | `fusion.py` (encode_fragment_pointer, render-mode/nav/assets contract), `core.py` (FormintModule nav source of truth), `views.py` (/fusion/* endpoints) |
| **Admin** | `admin.py` (canonical Unfold ModelAdmin superset), `dashboard.py` (10 KPI cards · 5 charts · 3 tables) |
| **Compatibility routes** | `server/server.py`, `server/bolt_api.py`, and `server/routes/` — optional legacy Robyn/django-bolt packaging path |

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
- **Optional legacy runner** — Robyn WebSocket/data-sync compatibility path (`:8766`); Django remains the primary server API
- **Standard parity** — currency/tax-profile models and admin, `/api/v1/currencies/`, `/api/v1/tax-profiles/`, and read-only CSV/JSON exports
- **Cloud sync** — multi-terminal push to a cloud master; sync approval + conflict handling
- **Cloud CRM** — companies, pipelines, stages, contacts, deals, activities, notes
- **Node registry** — `Node`/`Heartbeat`/`NodeEvent`/`DeviceConfig`/`MasterDevice`/`CloudLink`/`SyncLog`
- **Fusion §12 enhancement surface** — include-path component bridge, block attrs, `{% comp %}` tags, `contrib.api` health/branding/layouts, PageHandler full-page pipeline
- Operator-facing render-mode setting (`UserSettings.fusion_render_mode`) + `/fusion/session-mode/` toggle
- **Wagtail-free** Django boundary — models `full_*` preserved for migration compatibility

---

### Cloud — `formint-cloud/` (formint-cloud)

> Hosted multi-terminal SaaS as a **full Django setup**: the Django backend
> (`backend/`, package `formint-cloud`) serves the entire API surface —
> django-fusion viewsets, the `/fusion/*` render-mode contract, the
> Community-UI bridges, and the BoltAPI analytics dashboard — sharing
> `formint_cloud.db`. The Robyn server that previously served the REST surface
> has been **removed**; a second Django dev server on `:8767` now answers the
> server-compatible paths the frontend expects. Cloud master that terminals
> push their data to; automatic backups + monitoring (Cloud capability).

#### Added components — backend (`backend/`)

| Layer | App | Components |
|-------|-----|-----------|
| **Models** | `apps/core/` | `Organization`, `Branch`, `Lead`, `Contact`, `Deal`, `InventoryReport`, `BranchReport`, `BranchSyncLog`, `BranchProduct`, `BranchSale`, `BranchInventory`, `DeviceToken`, `SyncConflict`, `SyncQueueItem` |
| **API / viewsets** | `apps/core/` | `views.py` — Organization/Branch/Lead/Contact/Deal/InventoryReport/BranchReport/DeviceToken/SyncConflict/SyncQueueItem `ModelViewset`s with filtersets + report generation; `api.py` — BoltAPI analytics (`/stats`, `/products`, `/sales`, `/inventory`, `/branches`, `/sync-logs`) |
| **Domain services** | `apps/domain/` | `sync_broker.py`, `sync_queue.py`, `conflict_resolver.py` |
| **Request handlers** | `apps/handlers/` | `sync_api.py` (sync_receive_products/sales/inventory/heartbeat + broadcast), `sync_dashboard.py` (branch health, queue summary/by-branch/list/retry/cancel, conflict list/resolve/dismiss/stats, recent activity), `consumers.py` (channels ASGI), `middleware.py`, `fragments/{layouts, modals, reports, skeletons, tables}.py` (django-fusion), `fusion.py` (render-mode contract), `surface.py` (root CRUD + bridges) |
| **Config** | `configs/` | `asgi.py`, `wsgi.py`, `urls.py`, `dashboard.py` (django-bolt) + `manage.py` |

#### Server surface — served by Django (`apps/handlers/surface.py` + `fusion.py`)

> The Robyn server is gone; Django answers the same paths on `:8767`.

| Area | Django module | Paths |
|------|---------------|-------|
| **Root CRUD** | `apps/handlers/surface.py` | `/organizations`, `/branches`, `/leads`, `/contacts`, `/deals`, `/inventory-reports`, `/branch-reports`, `/sync/{logs,products,sales,inventory}`, `/device-tokens`, `/conflicts`, `/queue` (generic JSON CRUD, `{count, items}` server shape; JSON 401 for anonymous, staff-only token role/is_active writes, `token_hash` never serialized) |
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
- **Full Django API surface** — all CRUD, fusion contract, and Community-UI bridges served by Django (`:8767` API / `:8082` admin) with the Robyn server removed
- Automatic cloud backups + monitoring (Cloud capability)

---

### pos-client — `formint-client/` (Vue 3 desktop)

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
- **Django shop backend** — `catalog_api` / `orders_api` JSON, auth-status API,
  cart/checkout flow, `place_order`, and the django-fusion dual-mode fragments
  (`products_fragment`, `cart_count_fragment`, `cart_drawer_fragment`,
  `my_orders_fragment` — the signed-in customer's recent orders, D5)
- **Shop API contract tests** — catalog, auth status, and cart-count fragment
  (D1) plus the orders/checkout/promo/editorial suite under `backend/tests/`


---

## Architecture per edition

### Pro — `formint-pro/` (merged formint-pos — recommended)
```
Astro → HTMX/JSON → Django Ninja backend → Django ORM → SQLite
  └── /api/v1 (45 paginated resources, django-fusion encoder/decoder)
  └── /htmx   (django-fusion tables + forms fragments)
  └── /fusion (render-mode / navigation / assets)
  └── /admin  (Unfold dashboard + KPI cards + charts)
  └── optional Robyn compatibility runner (:8766) → legacy WebSocket/data-sync contract
```

### Community — `formint-community/` (formerly forge-pos / pos-mini)
```
React → Tauri Commands → Rust/Diesel → SQLite
```

### Formint Cloud (Cloud)
```
Branches → sync push → Django ASGI (channels/daphne)   [backend/]
  └── SyncQueue → SyncBroker → ConflictResolver → Broadcast to branches
  └── Unfold admin + Bolt dashboard (CRM + reports)
  └── SQLite (formint_cloud.db) — PostgreSQL in production via psycopg2
  └── Django API server (:8767) — same project; full CRUD + /fusion/* + bridges
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
- [Pro ↔ Cloud Sync Contract](pro-cloud-sync-contract.md)
- [Table & column comparison across editions](table-column-comparison.md)
- [Server migration guide](server-migration-guide.md)
- [POS architecture (all editions)](pos-architecture.md)
