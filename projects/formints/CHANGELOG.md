# Formints changelog

> All notable changes to the POS restaurant point-of-sale desktop app.

## Unreleased — edition completion

### Frontend (Formint Pro — Astro)
- **`SectionHeading` component** (`src/components/ui/SectionHeading.astro`)
  replaces the per-page eyebrow + `h1`/`h2` + `.section-heading` markup and
  styles across all 11 pages (heroes and section headers, actions via the
  `actions` slot). Centralizes the eyebrow style, the heading size scale
  (`sm`/`md`/`lg`, `hero`/`hero-xl`), and the `divider` variant, and enforces
  the one-eyebrow-per-page audit rule at render time: any eyebrow after the
  first per request is dropped with a dev-only `console.warn`.

### Community version (formint-community)
- Bundle generator + rename contract (Formints Community, `com.mammhoud.formint-community`) and landing seed sync (offline-first badge, refund flow) are complete; GitHub publish remains an external operator action.

### Added (pos-client — formint-client)
- Shop API contract tests — catalog, auth status, cart-count fragment (D1), plus the existing orders/checkout/promo/editorial suite.
- `my_orders_fragment` — HTMX fragment for the signed-in customer's recent orders (D5), mirroring `products_fragment`.

### Added (Formint Cloud — tenant identity layer)
- `Tenant.settings` JSON column + migration (per-tenant signup gate, social provider keys, login redirect).
- `TenantAwareAccountAdapter`, `tenant` context processor, `tenant_provider_settings` helper, and `branch_database_aliases` — all SQLite-safe and tenant-inert without `DB_ENGINE=django_tenants`.

### Added (Formint Pro — fusion dual-mode views + settings)
- **`/fusion/views/*` dual-mode endpoints** — `fusion_dual_views.py`
  reuses the read-only services (forecast, customer display, kiosk,
  purchase orders, tables floor, delivery stats, gift cards) behind
  django-fusion's `fusion_view` decorator: the same endpoint answers as a
  **render-first component** (`django_templates/fusion/*.html`) or a
  **codec-encoded data API** (`X-Fusion-Render-First: false`), per the
  canonical fusion contract. Existing raw JSON views are untouched.
- **Fusion asset-pipeline settings** — `FUSION_PIPELINE` (webpack off,
  components on), `FUSION_ASSET_PIPELINE` legacy alias,
  `FUSION_COMPONENTS` enable flag, and `STATICFILES_DIRS` that picks up
  the Astro `frontend/dist` build when present.

### Added (Formint Pro — navigation + frontend coverage)
- **Navigation modules for all shipped features** — the `fusionNavigation`
  contract in `formint/core.py` (and the `Layout.astro` offline fallback)
  now exposes every completed module: Restaurants (tables,
  reservations, deliveries), Gift Cards, Gaming Center, Forecast,
  Purchase Orders, Kiosk, Customer Display, plus the existing ops,
  menu, sales, loyalty, and profile entries.
- **Frontend pages for every nav route** — new Alpine-driven pages for
  `/tables`, `/reservations`, `/deliveries`, `/gift-cards`,
  `/purchase-orders`, `/forecast/report`, and `/gaming` (stations /
  tokens / sessions tabs), all calling the existing JSON endpoints.

### Added (Formint Pro)
- **Barcode Scanner** — `/barcode/<value>` resolves a scanned code to a product (exact `barcode` match with `sku` fallback) and `/barcode/<value>/label` renders a Code128 SVG label; `python-barcode` is lazy-imported so the server runs without it.
- **POS-KO Gaming Center** — `/gaming/*` token-based sessions: `GamingStation`/`GamingToken`/`GamingSession`/`GamingQueueEntry` models + service (start/pause/resume/stop with duration × hourly-rate billing, per-started-minute token decrement, and a waitlist queue with estimated wait).
- **Gift Cards** — `/gift-cards*` digital gift cards: `GiftCard`/`GiftCardTransaction` models + service (issue, case-insensitive balance lookup, atomic redeem with `used`/expiry/disabled guards, reload, disable) and an immutable signed-amount ledger.
- **Table Management** — `/tables*` + `/reservations*` floor layouts and order tracking: `RestaurantTable` (section/capacity/shape, floor-plan position, status lifecycle) and `TableReservation` models + service (`occupy_table`/`clear_table` seat the live sale and sync the sale's `SaleGroup.table_number`; reservations create → seat → complete with cancel/no-show branches; `floor_summary` occupancy stats).
- **Delivery Integration** — `/deliveries*` platform connectors: `DeliveryProvider` (Talabat/HungerStation/Careem/manual registry) and `DeliveryOrder` models + service (zone-based fee computation, full status lifecycle with transition guards, provider webhook ingestion on `order_id`, delivery KPIs).
- **AI Forecasting** — `/forecast*` read-only advisory analytics (`services/forecast.py`): per-product demand projection (moving average + clamped trend factor), stock/reorder recommendations over lead time, waste aggregation with estimated cost, and sales movers/growth insights with plain-language recommendations. Purely advisory — never mutates POS data (per the django-fusion LLM/MCP plan).
- **Employee Scheduling** — `/scheduling*` shift planning + time clock: weekly shift upsert + concrete week roster from `EmployeeSchedule`, staffing coverage, and the new `TimeClockEntry` model + service (`services/scheduling.py`) with clock in/out/break, single-active-punch guard, and worked-hours/overtime/pay estimate.
- **Customer Display** — `/customer-display*` read-only order-confirmation screens (`services/customer_display.py`): per-sale display envelope (order #, table, order type, item rows, totals, kitchen-ticket status + elapsed/remaining/overdue ETA) and an active-orders board feed with per-status summary; plus a polling wall-screen page (`frontend/src/pages/customer-display/index.astro`, `?sale=<id>` focuses one confirmation). Purely read-only — no new models or migration.
- **Self-checkout Kiosk** — `/kiosk*` self-service kiosk mode: `KioskSession` + `KioskCartItem` models + service (`services/kiosk.py`) with a catalog feed, session lifecycle, stock-guarded cart ops, and totals (subtotal + 8% tax). Checkout reuses the canonical `sale_checkout` surface (atomic Sale/SaleItem/KitchenTicket + stock deduction) by forwarding the exact `POST /sales/` payload, then links the sale and closes the session. Touchscreen UI at `frontend/src/pages/kiosk/index.astro` (`?kiosk=` labels the device). Migration `0016`.
- **Inventory Forecasting** — `/forecast/inventory*` reorder-point planning (`services/forecast.py`): per-product safety stock, reorder point (lead demand + safety), projected stock-out date, needs-reorder flags with reasons, and suggested order quantities — the roadmap's final P3 item, superseding the AI Forecasting stock advisory. `POST /forecast/inventory/reorder` is the explicit operator action that materializes the plan into `PurchaseOrder` drafts (`RF-YYYYMMDD-###`, cost from product, no stock movement until ordered/received); no new models or migration.
- **Purchase Order Workflow** — `/purchase-orders*` procurement lifecycle (`services/purchase_orders.py`): create draft POs (`PO-YYYYMMDD-###`), mark ordered, receive with `in` `InventoryTransaction` stock-in (product stock + `received_quantity` bump, partial receipt defaults to remaining balance, over-receipt rejected), and cancel with transition guards. `GET /purchase-orders/alerts` reuses the forecast plan to surface at/below-reorder-point products plus open drafts; `GET /purchase-orders/stats` reports status counts + outstanding value. No new models or migration.

### Added (Formint Cloud)
- **Cloud Dashboard** — `/cloud-dashboard` multi-branch management page over the full `/api/dashboard/*` contract: sync-queue retry/cancel, conflict resolve (local/remote/merge) + dismiss, and the recent-activity feed. `api/dashboard.ts` now types every dashboard endpoint (health, queue, conflicts, activity) with retry/cancel/resolve/dismiss mutations.

### Changed (Formint Pro)
- Canonical documentation now points to `formint-pro/server/` and describes Django as the primary API boundary.
- Added Pro Standard-parity currency and tax-profile models, admin/API routes, and read-only CSV/JSON exports.
- Retained the Robyn/django-bolt runner as an explicitly optional compatibility path rather than claiming it was removed.

### Changed (Formint Cloud and SDK)
- Added the missing Cloud `src/AppIsland.tsx` entry point so the Astro frontend hydrates its existing provider stack.
- `@formints/client` resource modules are built and consumed by the Cloud monitor surface.

### Verification
- `@formints/client`: 6 Vitest tests, typecheck, and ESM build pass.
- Cloud frontend: Astro check passes with 0 errors.
- Pro frontend: Astro check passes with 0 errors; backend gates require the absent local `server/.venv`.

## 2026-08-11 — Formint Pro: sync + admin + components enhancement

### Added (formint-pos)
- **Sync API** — `SyncController` under `/api/v1/sync/` exposing the merged
  `ProductSyncEngine` (push products/config/catalog, receive sales/reports/
  inventory, approve/reject pending changes, approvals list, ledger stats,
  connectivity status) so the desktop app drives cloud server sync over HTTP
- **Components API** — `ComponentsController` under `/api/v1/components/`
  serving django-fusion tables, forms, and fragments (branch summary) as JSON
  data the Astro shell renders directly
- **Unified transport** — `frontend/src/lib/fusion-api.ts`: API-first with
  Tauri-invoke fallback (auto-restart server) and offline snapshot cache;
  registered as `$store.api` in `Layout.astro`; nav fetch now goes through it
- **Reusable UI components** — `FusionTable` (data-driven tables + skeleton +
  pagination), `FusionForm` (schema-driven fields + validation), `WizardForm`
  (multi-step wizard with progress rail/bar, per-step validation, keyboard
  nav), new `wizard-step` skeleton variant
- **Sync Center page** — `/ops/sync/` (transport status, sync stats, product
  catalog via Components API, supplier onboarding wizard); enabled in nav as
  "Sync Center" with NEW badge
- **Admin palette alignment** — Unfold `UNFOLD["COLORS"]` switched from
  emerald to the POS app's blue (#2563eb) scale so admin and app share one
  identity
- **Tests** — 15 new backend tests (sync API + components API) and 17 new
  frontend contract tests; fixed stale navigation-contract tests and the
  `PageHandler` nav flattening bug

### Changed (formint-pos)
- All `/api/v1/*` routes normalised to trailing-slash form (SystemController
  included) for a single URL contract

### Verification
- Server: `make check` + `manage.py test formint` (108 tests, OK)
- Frontend: `npm run check` (0 errors) + `npm test` (80 tests, OK)


> Follows [Semantic Versioning](https://semver.org/).

---

## 2026-08-11 - Active project closeout

### Changed

- Confirmed `projects/formints/` as the canonical POS product workspace.
- Kept edition-specific implementation in the owning Formint/POS project and
  preserved the active edition plans without marking unfinished cloud or tenant
  work complete.
- Added a root POS changelog at `projects/pos/CHANGELOG.md` and an edition
  changelog at `projects/pos/forge-pos/CHANGELOG.md` for cross-boundary release
  traceability.

### Verification

- Use each edition's documented frontend, server, and native test commands.
- Keep generated native targets, bundles, databases, and screenshots ignored.


> Follows [Semantic Versioning](https://semver.org/).

---

## Unreleased — 3 August 2026

> **Per-edition changelogs:** forge-pos merged into formint-community/standard (see `docs/plans/legacy/pos/`)

### Added (formint-pos — merged package)
- **Merged edition** — `pos-full` + `pos-solo` consolidated into `formint-pos/` (Astro frontend + Django Ninja backend + Robyn server + Unfold admin); legacy React UIs archived under `formint-pos/legacy-react/`
- **Robyn server** — Merged from the former Full/Solo servers (streams, ws_client, sync signals, services, middleware, routes) into `formint-pos/server/`
- **Server test fixes** — `bolt_api` collection crash fixed (removed stale `namespace` kwarg); `test_bolt_api` gracefully skips when `AsyncTestClient` is unavailable
- **Screenshots** — Unfold admin screenshots consolidated into Landing-Fusion `related/formints/`

### Added (formint-cloud — cloud backups + monitoring)
- **Automatic backups** — `BackupRun` model + `manage.py backup_db` management command (online SQLite backup with `sqlite3.Connection.backup()`, timestamped filenames, per-run status tracking)
- **Scheduled backup task** — `@task(schedule="0 2 * * *")` wrapping `backup_db` via django-fusion's APScheduler integration (runs nightly at 02:00 UTC)
- **Monitoring endpoint** — `GET /monitor/status` JSON endpoint reporting database reachability, latest backup details, and sync queue depth
- **Backup + monitor tests** — `apps/test_backup.py` (7 tests: model + command), `apps/test_monitor.py` (3 tests: endpoint contract)

### Removed (repository)
- **`pos-solo/` and `pos-full/` editions deleted** — fully merged into `formint-pos/` (content preserved in `legacy-react/` archive and git history)
- **`make editions`** — edition generation target removed; each edition is now canonical in its own directory

---

## v1.3.0 — 30 July 2026

> **Per-edition changelogs:** forge-pos merged into formint-community/standard (see `docs/plans/legacy/pos/`)

### Added (forge-pos)
- **Settings → Theme tab** — New tab with Theme Studio link, "Preview Theme Components" modal, and active theme info
- **ThemePreviewModal** — Modal previewing all components across 5 theme variants
- **Email-based Support Chat** — Using `VITE_SUPPORT_EMAIL` env var with mailto links; removed WebSocket/server/ticket deps

### Changed (forge-pos)
- **ThemeShowcase page deleted** — Merged into ThemePreviewModal (Settings → Theme)
- **Dashboard text dimming** — Menu labels, descriptions, and accent strips use reduced opacity
- **SupportChat simplified** — No longer depends on server health check or ticket system

### Changed (formint-pos)
- **Django Bolt API** — `bolt_api.py` server module with BoltAPI integration (carried into the merged server)
- **Bolt tests** — `test_bolt_api.py` and `bolt_urlconf.py` for URL routing verification

---

## v1.2.0 — 20 July 2026

### Added
- **Server v2 Documentation** — Comprehensive [`docs/SERVER_V2.md`](docs/SERVER_V2.md) with full architecture, 70+ API catalog, WebSocket streams, Django signals, and cloud bridge plan
- **`docs/README.md` updated** — Modernised edition overview (Solo→Robyn, Full→Cloud Master), shared module map, and new whatʼ s new section
- **`README.md` updated** — `SERVER_V2.md` added as top entry in documentation table

### Changed
- **Server Sanic→Robyn migration documented** — All editions now use Robyn async Python server with Django ORM
- **Solo edition** replaces Extended (Sanic→Robyn, unified models, approval workflow, product sync)
- **Full edition** upgraded (Robyn + Cloud Master + Rust-backed posapp + django-bolt)

---

## v1.1.0 — 19 July 2026

### Added
- **3 Edition System** — Minimal, Solo (Extended), and Full editions with shared codebase
- **Django Portal** — Shared Django portal with django-fusion viewsets (all editions)
- **Cloud CRM Master** — Full edition includes standalone Cloud CRM server (Sanic, port 8766)
- **Cloud Sync Client** — Solo edition includes sync client for pushing POS data to Cloud CRM
- **Cloud Sync Proxy** — Full edition sync proxy routes generic entity pushes from Solo
- **Change Signals** — Full edition Rust broadcast channel for settings/product/CRM entity changes
- **POS-KO Gaming Center** — Gaming center module with token management and session tracking
- **Profile/Logout Button** — User avatar + dropdown in top bar with sign out
- **Inactivity Warning** — Toast warning with "Stay" button for session timeout
- **i18n Arabic** — Full Arabic translation support (ar locale)
- **Scripts Reorganization** — Scripts moved to `dev/` and `github/` subdirectories
- **Auth System Tests** — 23 Rust unit tests for auth operations

### Changed
- **WebSocket fixed** — Persistent connection with auto-reconnect (no longer creates new WS per message)
- **TypeScript API layer** — New `api/` module with `server.ts`, `chat.ts`, `tickets.ts`, `data.ts`
- **Server API expanded** — 9 new endpoints (sales, products, settings, invoice, support tickets, chat WS)
- **Makefile** — `make editions` generates all 3 editions from canonical `pos-full/` source
- **Scripts paths** — Internal `__dirname`/`SCRIPT_DIR` paths updated for new directory structure

### Fixed
- Chat support WebSocket creating new connection for every message
- `make build-server` path in Makefile
- `make screenshots` capture script for 6 marketplace screenshots
- i18n diff script path in GitHub Actions workflow

---

## v1.0.0 — 10 June 2026

### Initial Release

- **Core POS** — Tauri 2 + React 19 + Rust + SQLite
- **29 Database Tables** — Products, categories, sales, customers, employees, inventory, suppliers, purchase orders, recipes, kitchen display, payroll, scheduling, tax, analytics
- **22 Page Components** — Dashboard, POS terminal, inventory, reports, settings, employees, suppliers, kitchen, recipes, analytics, tax, payroll, schedules, customers, chat, profile
- **15 UI Components** — Buttons, cards, tables, forms, modals, dropdowns, toasts, sidebar, topbar, search, pagination, tabs, badges, charts, layout
- **25 CRUD Modules** — Auth, sales, products, inventory, customers, employees, categories, taxes, payment methods, tables, orders, payments, tips, discounts, recipes, suppliers, purchase orders, kitchen display, payroll, scheduling, analytics, settings, loyalty, chat, backup
- **i18n** — English and French translations (i18next)
- **SCSS Design System** — Utilities, base styles, component styles
- **Diesel Migrations** — 6 SQLite migrations
- **SMTP Email** — Configurable email sending for receipts and reports
- **Auth System** — Optional superuser-based authentication with env vars
- **Server API** — Python/Sanic REST API (26 endpoints) for Full edition
- **Invoice PDF** — Tax, commercial, proforma, credit, receipt invoice types
- **PDF & Excel Export** — Report generation in PDF and Excel formats
- **Dark & Light Mode** — Theme switching with CSS custom properties
- **Responsive Layout** — Works on desktop, tablet, and mobile viewports
