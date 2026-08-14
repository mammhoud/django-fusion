# Formint — Changelog

> All notable changes to the Formint desktop application (Tauri 2 + Rust + React).
> Follows [Semantic Versioning](https://semver.org/).
> See also: [`../CHANGELOG.md`](../CHANGELOG.md) for POS-wide changes.

---

## [Unreleased] — August 3, 2026

### Added
- **Landing-site sync (Formints / `formint-pos`)** — Project branding aligned
  with the published product page at `/products/formint-pos/` (formerly
  pos-mini / forge-pos). Docs now carry the site slug + edition identity so
  the repo and the landing page cannot drift.
- **Expanded feature-comparison table** — New capability rows across
  Community · Standard · Pro · Cloud: offline-first mode, refunds & returns,
  loyalty & rewards program, multi-currency & tax profiles, custom roles &
  permissions, data export (CSV/JSON), and automatic cloud backups.
- **Edition capability updates** — Community gained offline-first mode +
  refunds; Standard gained loyalty, multi-currency, roles and data export;
  Cloud gained automatic backups + monitoring.
- **New reference snippets** — `Diesel migration (up.sql)` (loyalty points +
  refunds tables) and a `Tauri command (invoice PDF)` example added to the
  product page reference material.
- **Product roadmap band** — Loyalty engine, multi-currency & tax profiles,
  and automatic cloud backups published as the roadmap on the product page.
- **Modal system + shared form components** — Unified add/edit flows across modules via reusable `Modal` + form components (Employee module converted first)
- **Plan cleanup** — All completed plans archived to `docs/plans/legacy/pos/` (UI Enhancement Master Plan, Task Status, Enhancement Plan); `forge-pos-plan.md` rewritten to track only pending work
- **Remix Icon system** — Full icon-set migration from Iconify (`icon-[tabler--…]`, lucide, heroicons, mdi, ph, carbon, solar) and `react-icons/hi2` to the Remix Icon font (`ri-*` classes). Vendored the Remix Icon package (2,950 icons) plus Inter & Roboto font families from CMS Fusion; rewrote `src/lib/icons.tsx` (`Ic`/`ic`/`iconClass`) to emit `ri-*` classes; ~600+ icon tokens replaced across all pages
- **Assets reorganization** — `public/` merged into `assets/` with organized layout: icon fonts → `assets/icons/remix/`, font families → `assets/fonts/inter/` + `assets/fonts/roboto/`, CSS → `assets/styles/fonts/`; all asset paths fixed in `index.html`, `vite.config.ts`, `tauri.conf.json`, and source imports

### Changed
- **Icon system** — Remaining Iconify utility icons in SideNav (pin, logout, close, help-circle, user-check) + Analytics/Reports/Tax modules replaced with Heroicons (`react-icons/hi2`) — *superseded by the Remix Icon migration above; Iconify + `react-icons` deps and `@iconify/tailwind4` plugin removed*
- **Auth page** — Sign In submit arrow now flips for RTL (`rtl:rotate-180`), password show/hide toggle fixed, back-to-login arrows RTL-aware, leftover framer-motion `whileHover` removed, gradient class migrated to Tailwind v4 `bg-linear-to-r`
- **Dead framer-motion props cleanup** — `initial/animate/exit/transition/whileHover/variants/layoutId` props stripped across ~20 files; 22 frozen `animate={{ rotate: 360 }}` spinners converted to Tailwind `animate-spin`; deleted `framer-legacy.d.ts` shim
- **Behavior fixes from dead props** — Recipes cost bar now fills by percentage, Sale mobile checkout bar collapses when cart empty, Sale order-details sidebar collapses, Home icon spins on hover
- **Product cards** — Unified single-color theme-adaptive styling; modals fixed on Products and Kitchen pages (FlyonUI opacity override)

### Removed
- **MCP Support toggle** — Removed from Settings; ChatSupport no longer gates on MCP; the never-applied `mcp_enabled` migration was deleted
- **Unique Card Colors toggle** — Backend `unique_card_colors` column dropped (migration `2026-10-03-000000_remove_unique_card_colors`); Settings toggle + i18n keys removed; product cards always use the single uniform theme color (Sale/ProductManager simplified)

### Fixed
- **Sale page layout** — Order-type component uses `flex gap-2` (removed wrap), total amount container simplified
- **Sale status-toast test flake** — Load-error toast assertion given an explicit `waitFor` timeout (8s) for the slow CI test environment

### Status
All 17 sections of the UI Enhancement Master Plan complete; remaining work tracked in `docs/plans/pos/forge-pos-plan.md` (useApiMutation, DataTable bulk actions, events extension, preloading, Tauri notifications).

---

## [Unreleased] — July 30, 2026

### Added
- **KDS enhancements (from P2/P3 plan)** — Time-elapsed progress bar (green→yellow→red), overdue badge, 'overdue-first' sort, mute-30-min, and chime-variant dropdown
- **Settings → Theme tab** — New "Theme" tab in Settings with Theme Studio link, "Preview Theme Components" modal, and active theme info display
- **ThemePreviewModal** — Modal component showing buttons, forms, alerts, badges, tabs, stats, cards, tables, and progress bars across all 5 theme variants (default, corporate, luxury, pastel, cyberpunk)
- **Email-based Support Chat** — Floating support widget using `VITE_SUPPORT_EMAIL` env var with mailto: links; hides entirely when email not configured; removed WebSocket/server/ticket system dependency

### Changed
- **Framer-motion removed** — Dependency dropped; components migrated to FlyonUI CSS animations
- **ThemeShowcase page deleted** — Merged into `ThemePreviewModal`, accessible from Settings → Theme tab
- **Dashboard text dimming** — Menu item labels dimmed (`text-base-content/80`), descriptions dimmed (`text-base-content/40`), category accent strips reduced opacity (`60%`)
- **Removed routes** — `/theme-showcase` route removed from App.tsx, SideNav.tsx, Home.tsx, and preloadRoutes.ts

---

## v1.2.0 — July 29, 2026

### Added
- **Branding rename** — "Daily Grind" → "Formint" across all code + UI
- **Tax ID field** — Added to Settings model/DB/UI, wired into InvoicePage, Sale, Transactions, and invoicePdf
- **Enhanced order types** — `extra-order` and `dated-order` added to Sale.tsx, `ORDER_TYPES`, and Rust priority mapping
- **Prepare time in KDS** — DB migration adds `prepare_time_minutes` to products + kitchen_tickets; displayed on KitchenDisplay ticket cards + detail modal
- **Merged pages** — `ProductsPage.tsx` (ProductManager + Inventory + Recipes) and `StaffPage.tsx` (Employees + Schedule + Payroll) with sticky tabs
- **Quick-access cards** — 4-card grid on Home page (Staff, Products, Sale, Reports)
- **SideNav expand/collapse** — `toggleCategory()` for persistent sidebar categories
- **Auth page design** — Glassmorphism design, manager/employee segmented switcher

### Changed
- **FlyonUI integration** — Tabs, checkboxes, selects, alerts, modals now use FlyonUI components throughout
- **Theme system** — `ThemeContext` with 5 variants (default, corporate, luxury, pastel, cyberpunk) × 2 modes (light/dark); ThemeToggle with 3-position sliding knob
- **Language system** — `LanguageToggle` with Arabic RTL; 5 language files (en, ar, fr, de, es)
- **SideNav improvements** — Auto-scroll on category click (mobile), role-based filtering (manager/employee)
- **Settings** — Appearance tab with theme preview, variant picker, currency selector (150+ currencies)
- **Roles.tsx** — Fallback removed; uses `invoke<PermissionDef[]>('get_permission_catalog')` from Rust

### Fixed
- **Sale page** — Category tag filter sidebar, responsive grid columns
- **Home page** — Removed duplicate buttons/navigations, consistent container size

### Status
26/33 tasks complete (79%). Remaining: Sale page product card sizing, ThemeToggle tighter integration with Settings Appearance tab.

---

## v1.1.0 — July 2026

### Added
- **Initial POS release** — Tauri 2 desktop app with Rust backend (SQLite) + React frontend (TypeScript/Tailwind v4)
- **POS features** — Sale, Kitchen Display System, Transactions, Inventory, Recipes, Product Manager
- **Staff management** — Employees, Employee Schedule, Payroll, Roles & Permissions
- **Reporting** — Analytics, Reports, Tax Reports, Invoice generation (PDF)
- **Settings** — Restaurant profile, Business hours, Tax configuration, Delivery zones
- **Keybindings** — Global keyboard shortcuts (`G` Dashboard, `S` Sale, `T` Theme, `?` Help)
- **Route preloading** — Lazy-loaded pages with hover/focus preload for instant navigation
- **Vitest test suite** — 25+ page-level tests with Tauri mock infrastructure
