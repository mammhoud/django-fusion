# Forge POS — Changelog

> All notable changes to the Forge POS desktop application (Tauri 2 + Rust + React).
> Follows [Semantic Versioning](https://semver.org/).
> See also: [`../CHANGELOG.md`](../CHANGELOG.md) for POS-wide changes.

---

## [Unreleased] — July 30, 2026

### Added
- **Settings → Theme tab** — New "Theme" tab in Settings with Theme Studio link, "Preview Theme Components" modal, and active theme info display
- **ThemePreviewModal** — Modal component showing buttons, forms, alerts, badges, tabs, stats, cards, tables, and progress bars across all 5 theme variants (default, corporate, luxury, pastel, cyberpunk)
- **Email-based Support Chat** — Floating support widget using `VITE_SUPPORT_EMAIL` env var with mailto: links; hides entirely when email not configured; removed WebSocket/sidecar/ticket system dependency

### Changed
- **ThemeShowcase page deleted** — Merged into `ThemePreviewModal`, accessible from Settings → Theme tab
- **Dashboard text dimming** — Menu item labels dimmed (`text-base-content/80`), descriptions dimmed (`text-base-content/40`), category accent strips reduced opacity (`60%`)
- **Removed routes** — `/theme-showcase` route removed from App.tsx, SideNav.tsx, Home.tsx, and preloadRoutes.ts

---

## v1.2.0 — July 28, 2026

### Added
- **Branding rename** — "Daily Grind" → "Forge POS" across all code + UI
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
