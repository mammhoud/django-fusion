# POS — Changelog

> All notable changes to the POS restaurant point-of-sale desktop app.
> Follows [Semantic Versioning](https://semver.org/).

---

## v1.3.0 — 30 July 2026

> **Per-edition changelogs:** [forge-pos](forge-pos/CHANGELOG.md) · [pos-solo](pos-solo/CHANGELOG.md) · [pos-full](pos-full/CHANGELOG.md)

### Added (forge-pos)
- **Settings → Theme tab** — New tab with Theme Studio link, "Preview Theme Components" modal, and active theme info
- **ThemePreviewModal** — Modal previewing all components across 5 theme variants
- **Email-based Support Chat** — Using `VITE_SUPPORT_EMAIL` env var with mailto links; removed WebSocket/sidecar/ticket deps
- **Per-edition CHANGELOGs** — `forge-pos/`, `pos-solo/`, `pos-full/` each with edition-specific history

### Changed (forge-pos)
- **ThemeShowcase page deleted** — Merged into ThemePreviewModal (Settings → Theme)
- **Dashboard text dimming** — Menu labels, descriptions, and accent strips use reduced opacity
- **SupportChat simplified** — No longer depends on sidecar health check or ticket system

### Changed (pos-full)
- **Django Bolt API** — `bolt_api.py` sidecar module with BoltAPI integration
- **Bolt tests** — `test_bolt_api.py` and `bolt_urlconf.py` for URL routing verification

### Changed (pos-solo)
- **Plans documented** — Django Fusion enhancements and solo enhancement plans in `docs/plans/pos/`

---

## v1.2.0 — 20 July 2026

### Added
- **Sidecar v2 Documentation** — Comprehensive [`docs/SIDECAR_V2.md`](docs/SIDECAR_V2.md) with full architecture, 70+ API catalog, WebSocket streams, Django signals, and cloud bridge plan
- **`docs/README.md` updated** — Modernised edition overview (Solo→Robyn, Full→Cloud Master), shared module map, and new whatʼ s new section
- **`README.md` updated** — `SIDECAR_V2.md` added as top entry in documentation table

### Changed
- **Sidecar Sanic→Robyn migration documented** — All editions now use Robyn async Python server with Django ORM
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
- **TypeScript API layer** — New `api/` module with `sidecar.ts`, `chat.ts`, `tickets.ts`, `data.ts`
- **Sidecar API expanded** — 9 new endpoints (sales, products, settings, invoice, support tickets, chat WS)
- **Makefile** — `make editions` generates all 3 editions from canonical `pos-full/` source
- **Scripts paths** — Internal `__dirname`/`SCRIPT_DIR` paths updated for new directory structure

### Fixed
- Chat support WebSocket creating new connection for every message
- `make build-sidecar` path in Makefile
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
- **Sidecar API** — Python/Sanic REST API (26 endpoints) for Full edition
- **Invoice PDF** — Tax, commercial, proforma, credit, receipt invoice types
- **PDF & Excel Export** — Report generation in PDF and Excel formats
- **Dark & Light Mode** — Theme switching with CSS custom properties
- **Responsive Layout** — Works on desktop, tablet, and mobile viewports
