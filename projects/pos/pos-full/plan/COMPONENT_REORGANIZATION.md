# POS Full — Component Reorganization Plan

> **Plan file:** `projects/pos/pos-full/plan/COMPONENT_REORGANIZATION.md`
> **Created:** 2026-07-25 | **Branch:** `generic`
> **Parent:** `README.md` — Plan #1

---

## Overview

POS Full's `src/` directory is currently flat — all components, pages, hooks,
and utilities sit in single-level directories. This plan reorganizes them into
a structured, scalable hierarchy matching the LMS front-end pattern with proper
subdirectories and clear separation of concerns.

---

## Current State vs Target

### Current (Flat)

```
src/
  components/          # 19 files, no subdirs
  pages/               # 23 files, no subdirs
  hooks/               # 2 files
  contexts/            # 3 files
  store/               # Redux, RTK Query
  api/                 # API client layer
  lib/                 # Fusion utilities
  utils/               # General utilities
  test/                # 18 test files
```

### Target (Organized)

```
src/
  components/
    ui/                 # UI primitives: Modal, Skeleton, DataTable, ConfirmDialog, BackButton
    layout/             # Layout: PageLayout, SideNav
    fusion/             # Fusion: FusionPage, FusionProxy, FusionMiddleware
    pos/                # POS-specific: ProductCard, Receipt, Invoice, StatusToast
    shared/             # Shared: DatePicker, LanguageToggle, ThemeToggle, KeyboardShortcutsModal
  pages/
    pos/                # Sale, KitchenDisplay, ProductManager
    inventory/          # Inventory, Suppliers, Recipes
    employees/          # Employees, Payroll, EmployeeSchedule, Roles
    customers/          # Customers, Transactions
    reports/            # Reports, Analytics, TaxReports
    admin/              # Settings, SupportChat, Notes, ReceiptTemplates, InvoicePage
    auth/               # Auth
    root/               # Home, About
  hooks/
    useStatusToast.ts
    useDebouncedSearch.ts
    useResponsiveVariant.ts     # NEW — breakpoint detection
  contexts/
    AuthContext.tsx
    ThemeContext.tsx
    LanguageContext.tsx
  store/
    api/
      endpoints/        # NEW — split baseApi into per-resource endpoints
    middleware/
      websocket.ts
  docs/                 # Language-specific docs
    typescript/
    python/
    rust/
    sql/
  plan/                 # Implementation plans
```

---

## Implementation Steps

### Step 1 — Create Target Directories (1 hour)

```bash
mkdir -p src/components/{ui,layout,fusion,pos,shared}
mkdir -p src/pages/{pos,inventory,employees,customers,reports,admin,auth,root}
mkdir -p src/store/api/endpoints
```

### Step 2 — Move Components (2 hours)

| Source | Destination | Component |
|--------|-------------|-----------|
| `components/Modal.tsx` | `components/ui/Modal.tsx` | Modal |
| `components/Skeleton.tsx` | `components/ui/Skeleton.tsx` | Skeleton |
| `components/DataTable.tsx` | `components/ui/DataTable.tsx` | DataTable |
| `components/ConfirmDialog.tsx` | `components/ui/ConfirmDialog.tsx` | ConfirmDialog |
| `components/BackButton.tsx` | `components/ui/BackButton.tsx` | BackButton |
| `components/PageLayout.tsx` | `components/layout/PageLayout.tsx` | PageLayout |
| `components/SideNav.tsx` | `components/layout/SideNav.tsx` | SideNav |
| `components/FusionPage.tsx` | `components/fusion/FusionPage.tsx` | FusionPage |
| `components/FusionProxy.tsx` | `components/fusion/FusionProxy.tsx` | FusionProxy |
| `components/FusionMiddleware.tsx` | `components/fusion/FusionMiddleware.tsx` | FusionMiddleware |
| `components/ProductCard.tsx` | `components/pos/ProductCard.tsx` | ProductCard |
| `components/Receipt.tsx` | `components/pos/Receipt.tsx` | Receipt |
| `components/Invoice.tsx` | `components/pos/Invoice.tsx` | Invoice |
| `components/StatusToast.tsx` | `components/pos/StatusToast.tsx` | StatusToast |
| `components/ChatSupport.tsx` | `components/pos/ChatSupport.tsx` | ChatSupport (POS context) |
| `components/DatePicker.tsx` | `components/shared/DatePicker.tsx` | DatePicker |
| `components/LanguageToggle.tsx` | `components/shared/LanguageToggle.tsx` | LanguageToggle |
| `components/ThemeToggle.tsx` | `components/shared/ThemeToggle.tsx` | ThemeToggle |
| `components/KeyboardShortcutsModal.tsx` | `components/shared/KeyboardShortcutsModal.tsx` | KeyboardShortcutsModal |
| `components/ChatSupport.tsx` | `components/shared/ChatSupport.tsx` | ChatSupport |

### Step 3 — Move Pages (1.5 hours)

| Source | Destination |
|--------|-------------|
| `pages/Sale.tsx` | `pages/pos/Sale.tsx` |
| `pages/KitchenDisplay.tsx` | `pages/pos/KitchenDisplay.tsx` |
| `pages/ProductManager.tsx` | `pages/pos/ProductManager.tsx` |
| `pages/Inventory.tsx` | `pages/inventory/Inventory.tsx` |
| `pages/Suppliers.tsx` | `pages/inventory/Suppliers.tsx` |
| `pages/Recipes.tsx` | `pages/inventory/Recipes.tsx` |
| `pages/Employees.tsx` | `pages/employees/Employees.tsx` |
| `pages/Payroll.tsx` | `pages/employees/Payroll.tsx` |
| `pages/EmployeeSchedule.tsx` | `pages/employees/EmployeeSchedule.tsx` |
| `pages/Roles.tsx` | `pages/employees/Roles.tsx` |
| `pages/Customers.tsx` | `pages/customers/Customers.tsx` |
| `pages/Transactions.tsx` | `pages/customers/Transactions.tsx` |
| `pages/Reports.tsx` | `pages/reports/Reports.tsx` |
| `pages/Analytics.tsx` | `pages/reports/Analytics.tsx` |
| `pages/TaxReports.tsx` | `pages/reports/TaxReports.tsx` |
| `pages/Settings.tsx` | `pages/admin/Settings.tsx` |
| `pages/SupportChat.tsx` | `pages/admin/SupportChat.tsx` |
| `pages/Notes.tsx` | `pages/admin/Notes.tsx` |
| `pages/ReceiptTemplates.tsx` | `pages/admin/ReceiptTemplates.tsx` |
| `pages/InvoicePage.tsx` | `pages/admin/InvoicePage.tsx` |
| `pages/Auth.tsx` | `pages/auth/Auth.tsx` |
| `pages/Home.tsx` | `pages/root/Home.tsx` |
| `pages/About.tsx` | `pages/root/About.tsx` |

### Step 4 — Update Import Paths (2 hours)

Every file that imports from moved files needs updating:

```bash
# Find all import references and update
rg "from '\.\./components/" src/ --files-with-matches | while read f; do
  # Replace: '../components/Modal' → '../components/ui/Modal'
  # Replace: '../pages/Sale' → '../pages/pos/Sale'
done
```

### Step 5 — Split RTK Query Base API (2 hours)

Split `src/store/api/baseApi.ts` into per-resource endpoint files:

```
src/store/api/endpoints/
  core.ts         # Settings, Employees, DeliveryTypes
  products.ts     # Products, Categories
  customers.ts    # Customers
  sales.ts        # Sales, SaleItems
  inventory.ts    # Ingredients, InventoryTransactions
  legacy.ts       # Analytics, Transactions, Recipes
  chat.ts         # Support chat, tickets
```

### Step 6 — Update Route Imports (1 hour)

The router (React Router or Tauri routing) must point to new page paths:

```typescript
// Before:
{ path: '/sale', component: () => import('../pages/Sale') }

// After:
{ path: '/sale', component: () => import('../pages/pos/Sale') }
```

### Step 7 — Update Test Imports (1 hour)

All `src/test/` files reference moved components:

```bash
rg "from '\.\./components/|from '\.\./pages/" src/test/ --files-with-matches
```

### Step 8 — Verify (1 hour)

```bash
npm run build          # Vite build must succeed
npx tsc --noEmit       # TypeScript must pass
npm run test           # All Vitest tests must pass
```

---

## Documentation Updates

After reorganization, update these docs:

| Doc | Update |
|-----|--------|
| `AGENTS.md` | Remove ⬜ markers from directory tree, mark current |
| `PROMPTS.md` | Update import paths in code examples |
| `../pos-e2e/pages/*.ts` | Verify POM import paths still work |
| `docs/typescript/index.md` | Update component paths table |

---

## Progress

| Step | Status | Effort |
|:----:|:------:|:------:|
| 1 — Create directories | ⬜ | 1h |
| 2 — Move components | ⬜ | 2h |
| 3 — Move pages | ⬜ | 1.5h |
| 4 — Update imports | ⬜ | 2h |
| 5 — Split RTK Query API | ✅ | 2h |
| 6 — Update routes | ⬜ | 1h |
| 7 — Update tests | ⬜ | 1h |
| 8 — Verify | ⬜ | 1h |

**Total:** ~11.5 hours