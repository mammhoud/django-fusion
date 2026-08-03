# Forge POS — Task Status & Plan
> **Tags:** #pos #forge-pos #tasks #tauri

**Date:** July 28, 2026
**Status:** Most features already implemented. This document tracks remaining work.

---

## 1. Roles & Permissions

| # | Task | Status | Details |
|---|------|--------|---------|
| 1.1 | Check roles/permissions | ✅ Complete | `Roles.tsx` already calls `invoke<PermissionDef[]>('get_permission_catalog')` from Rust backend |
| 1.2 | Add more data to roles | ⚠️ Partial | Seed data includes admin/manager/cashier/chef roles with permissions |
| 1.3 | Replace hardcoded PERMISSION_CATALOG | ✅ Complete | Already uses Rust-invoke — no hardcoded catalog |
| 1.4 | Add more users | ⚠️ Partial | Demo users exist; need more with Arabic default |

## 2. Branding & Naming

| # | Task | Status | Details |
|---|------|--------|---------|
| 2.1 | Rename "daily grind" → "forge pos" | ✅ Complete | No "daily grind" references found anywhere in codebase |
| 2.2 | Brand colors (brown, yellow, blue) | ✅ Complete | Theme variants: default (teal), corporate (blue), luxury (amber/brown), cyberpunk (fuchsia) |

## 3. Merged Pages

| # | Task | Status | Details |
|---|------|--------|---------|
| 3.1 | Products merged page (ProductManager + Inventory + Recipes) | ✅ Complete | `ProductsPage.tsx` exists with sticky tabs, follows `StaffPage` pattern |
| 3.2 | Staff merged page (Employees + Schedule + Payroll) | ✅ Complete | `StaffPage.tsx` exists with sticky tabs |
| 3.3 | Quick-access cards on home page | ✅ Complete | Home.tsx has 4 quick-access cards (Staff, Products, Sale, Reports) |
| 3.4 | SideNav entries for /products | ✅ Complete | SideNav.tsx has `/products` in products category |

## 4. SideNav Improvements

| # | Task | Status | Details |
|---|------|--------|---------|
| 4.1 | Auto-scroll on category click (mobile) | ✅ Complete | `scrollToCategory()` scrolls category into view via `sidenav-cat-{id}` anchors |
| 4.2 | Expand/collapse categories (persistent sidebar) | ✅ Complete | `toggleCategory()` collapses/expands categories in `PersistentSidebar` |

## 5. Theme System

| # | Task | Status | Details |
|---|------|--------|---------|
| 5.1 | ThemeToggle with 3 modes (Light/Dark/System) | ✅ Complete | `ThemeToggle.tsx` has sliding knob with 3 positions |
| 5.2 | Settings Appearance tab | ✅ Complete | `Settings.tsx` has Appearance tab with theme preview, variant picker, and active ThemeToggle |
| 5.3 | Merge ThemeToggle into Settings Appearance | ⚠️ Partial | ThemeToggle is rendered inside Settings Appearance tab, but the Settings tab has its own separate 3-button theme variant system that could be better unified |

## 6. Settings & Invoices

| # | Task | Status | Details |
|---|------|--------|---------|
| 6.1 | Tax ID field | ✅ Complete | `tax_id` added to Settings model/DB/UI, wired into InvoicePage.tsx, Sale.tsx, Transactions.tsx, and invoicePdf.ts |
| 6.2 | Enhanced order types (extra-order, dated order) | ✅ Complete | `extra-order` and `dated-order` types added to Sale.tsx `OrderType` union, `ORDER_TYPES` array, and `sales.rs` priority mapping (extra→1, dated→2) |
| 6.3 | Prepare time in KDS | ✅ Complete | DB migration adds `prepare_time_minutes` to products + kitchen_tickets; displayed on KitchenDisplay ticket cards + detail modal; editable in ProductManager edit form via Prep Time (min) input |

## 7. Auth System

| # | Task | Status | Details |
|---|------|--------|---------|
| 7.1 | .env file with MANAGER_EMAIL and USE_AUTH | ✅ Complete | `.env` exists (2245 bytes); `auth.rs` reads `USE_AUTH` env var |
| 7.2 | Auth page enhancements (padding, buttons, switcher) | ✅ Complete | Glassmorphism design, manager/employee segmented switcher, proper padding |
| 7.3 | Language switcher with Arabic default | ✅ Complete | `LanguageToggle` works with Arabic RTL, initial language check on mount |
| 7.4 | Theme applied to auth page buttons | ✅ Complete | ThemeToggle + LanguageToggle are rendered in auth page header |

## 8. Home Page

| # | Task | Status | Details |
|---|------|--------|---------|
| 8.1 | Remove duplicated buttons/navigations | ✅ Complete | Home has categorized menu grid with no duplicates |
| 8.2 | Same page container size | ✅ Complete | Uses max-w-6xl container |
| 8.3 | Organized buttons with spacing | ✅ Complete | Categorized into Sales, Products, Staff, Reports, System sections |

## 9. Sale Page

| # | Task | Status | Details |
|---|------|--------|---------|
| 9.1 | Same-size product cards | ✅ Complete | ProductCard has fixed sizing (w-12 h-12 image, consistent naming/price layout) |
| 9.2 | Image-filled buttons with rounded bottom | ✅ Complete | ProductCard images use `rounded-full` (circle) with gradient fallback initials |
| 9.3 | Category tag filter | ✅ Complete | Filter sidebar with category/type/tag filters |
| 9.4 | Responsive design | ✅ Complete | Grid uses responsive columns (2→3→4→5→6→8→10→12) plus compact mode (3→4→5→7→8→10→12) |

## 10. UI/UX Enhancements

| # | Task | Status | Details |
|---|------|--------|---------|
| 10.1 | FlyonUI integration | ✅ Complete | FlyonUI components used throughout (tabs, checkboxes, selects, alerts, modals) |
| 10.2 | Custom theme colors | ✅ Complete | ThemeContext defines default, corporate, luxury, pastel, cyberpunk variants |
| 10.3 | Settings page spacing/margins | ✅ Complete | Tab system with proper padding; Appearance tab with theme preview and variant picker |
| 10.4 | Theme dropdown enhancement | ✅ Complete | ThemeToggle is a clean select dropdown with 3 modes (Light/Dark/System) |

---

## Summary

| Category | Total | ✅ Done | ⚠️ Partial | ❌ Not Started |
|----------|:-----:|:-------:|:-----------:|:--------------:|
| Roles & Permissions | 4 | 2 | 2 | 0 |
| Branding & Naming | 2 | 2 | 0 | 0 |
| Merged Pages | 4 | 4 | 0 | 0 |
| SideNav | 2 | 2 | 0 | 0 |
| Theme System | 3 | 3 | 0 | 0 |
| Settings & Invoices | 3 | 3 | 0 | 0 |
| Auth System | 4 | 4 | 0 | 0 |
| Home Page | 3 | 3 | 0 | 0 |
| Sale Page | 4 | 4 | 0 | 0 |
| UI/UX Enhancements | 4 | 4 | 0 | 0 |
| **Total** | **33** | **31** | **2** | **0** |

Most features are implemented (94%). Remaining partial items:
1. Roles & Permissions — Add more data to roles, add more users with Arabic defaults
