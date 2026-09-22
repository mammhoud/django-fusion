# Community Edition — Design, Architecture & Implementation Plan

> Tags: `#formints` `#pos` `#community` `#tauri` `#rust` `#diesel` `#sqlite` `#offline-first` — status ✅ done (21 Aug 2026).

> **Status (21 Aug 2026): ✅ DONE.** Tasks A1–A5 are implemented and verified —
> Rust `refund_sale`, the refund UI + confirm dialog, `useOfflineMode`, the
> Playwright refund spec, and the editions.md API-surface note. Frontend suite
> green (427 tests); Rust suite green.
>
> **Canonical source:** `projects/formints/formint-community/` — offline-first
> desktop POS (Astro 5 + React 19 over Tauri 2 + Rust/Diesel/SQLite). No
> sidecar, no cloud, no Django.

## Verified features (code-backed)

- **Offline-first mode** — `src/hooks/useOfflineMode.ts` + banner in
  `src/components/AppShell.tsx` ("Offline mode — data stays on this device");
  unit-tested in `src/test/hooks/useOfflineMode.test.ts`.
- **Refunds & returns** — Rust `refund_sale` (`src-tauri/src/operations/sales.rs`)
  flips a completed sale to `refunded` (once only), with UI in
  `src/app/pages/pos/Transactions.tsx` + confirm dialog; tested in
  `Transactions.test.tsx` and Rust tests.
- **Rust/Diesel command surface** — 30+ `#[command]` functions across
  `src-tauri/src/operations/`: sales, products, categories, customers,
  employees, employee types, ingredients, recipes, inventory transactions,
  suppliers, purchase orders, delivery types/zones, tax reports, shifts,
  coupons, notes, support messages, analytics, reports, auth, roles,
  user actions, hardware (ESC/POS printer + cash drawer), dump.
- **KDS (Kitchen Display System)** — ticket lifecycle with timers, overdue
  sort, mute + chime variants.
- **Payments** — cash, card, split; **invoices** — PDF generation + advanced
  receipt templates (tax/commercial/proforma/credit); **email** — SMTP via
  `src-tauri/src/email.rs`.
- **i18n** — en/fr/ar via react-i18next; **themes** — 5 variants with Theme
  Studio + preview modal; **roles** — 5 default roles with granular JSON
  permissions; **support chat** — email-based (`VITE_SUPPORT_EMAIL`).

## Remaining work

No open code tasks. The only remaining item is the external **publish** of the
standalone `formint-community` repo ([07-community-version.md](07-community-version.md)).
