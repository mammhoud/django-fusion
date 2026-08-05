# POS Full — AI Agent Instructions

> **Project:** `projects/pos/pos-full/`  
> **Type:** Tauri desktop app + Robyn sidecar + Django ORM  
> **Stack:** React 18 + TypeScript + Vite + Tailwind CSS + RTK Query + Rust (Tauri) + Python (Robyn/Django ORM)

---

## Project Overview

POS Full is the flagship point-of-sale desktop application. It runs as a Tauri
app with a React frontend, a Rust backend (Tauri invoke), and a Python sidecar
(Robyn web server with Django ORM for data persistence). It targets restaurant
and retail environments with full inventory, employee, customer, and reporting
modules.

---

## Directory Structure

```
pos-full/
├── src/                          # React frontend
│   ├── components/               # Shared UI components
│   │   ├── ui/                   # ⬜ PLANNED — UI primitives (Modal, Skeleton, DataTable, etc.)
│   │   └── layout/               # ⬜ PLANNED — Layout components (PageLayout, SideNav)
│   │   (Currently flat — restructure pending)
│   ├── pages/                    # Route-level page components
│   │   ├── pos/                   # ⬜ PLANNED — Point-of-sale (Sale, KitchenDisplay, ProductManager)
│   │   ├── inventory/            # ⬜ PLANNED — Inventory, Suppliers, Recipes
│   │   ├── employees/            # ⬜ PLANNED — Employees, Payroll, Schedule, Roles
│   │   ├── customers/            # ⬜ PLANNED — Customers, Transactions
│   │   ├── reports/              # ⬜ PLANNED — Reports, Analytics, TaxReports
│   │   ├── admin/                # ⬜ PLANNED — Settings, SupportChat, Notes, ReceiptTemplates
│   │   └── auth/                 # ⬜ PLANNED — Auth
│   │   (Currently flat — restructure pending)
│   ├── store/                    # Redux store (RTK Query)
│   │   ├── api/                  # API endpoints
│   │   └── middleware/           # WebSocket middleware
│   ├── hooks/                    # Custom React hooks
│   ├── contexts/                 # React contexts (Auth, Theme, Language)
│   ├── lib/                      # Core libraries (fusion-decoder, fusion-store, fusion-types)
│   ├── api/                      # API client layer (sidecar, data, chat, tickets)
│   ├── utils/                    # Utility functions (export, invoicePdf, tauri)
│   ├── i18n/                     # Internationalization
│   ├── test/                     # Vitest tests (mirrors src/ structure)
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── mocks/                # Tauri mock helpers
│   └── types.ts                  # Shared TypeScript types
├── src-tauri/                    # Rust/Tauri backend
│   ├── src/
│   │   ├── db/                   # Database models + schema (Diesel)
│   │   ├── commands/             # Tauri command handlers
│   │   └── main.rs               # Entry point
│   └── migrations/               # SQLite migrations
├── sidecar/                      # Python sidecar (Robyn)
│   ├── models/                   # Django ORM models (pos.py, extra.py)
│   ├── routes/                   # Robyn route handlers
│   ├── services/                 # Business logic services
│   ├── configs/                  # Django admin config
│   ├── middleware/                # Fusion, auth middleware
│   ├── fragments/                # HTMX fragment components
│   └── tests/                    # Pytest tests
├── public/                       # Static assets
├── docs/                         # Project documentation
│   ├── typescript/               # TypeScript/React docs
│   ├── rust/                     # Rust/Tauri docs
│   ├── python/                   # Python/sidecar docs
│   └── sql/                      # SQL/migration docs
└── plan/                         # Implementation plans
```

---

## Code Style & Standards

### TypeScript / React
- **Component naming:** `PascalCase` for components, `camelCase` for hooks/utils
- **File naming:** `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Props interfaces:** Named `ComponentNameProps`, colocated in the same file
- **State management:** Redux Toolkit + RTK Query for server state; React context for UI state
- **Styling:** Tailwind CSS with CTC teal theme variables (`--ctc-*`)
- **Testing:** Vitest + @testing-library/react. Tests mirror `src/` directory structure.

### Rust / Tauri
- **Crate naming:** `snake_case`
- **Module structure:** `db/` for database, `commands/` for Tauri commands
- **Migrations:** Diesel migrations in `src-tauri/migrations/`

### Python / Sidecar
- **Framework:** Robyn web server with Django ORM (standalone)
- **Import style:** Follow `django_fusion` canonical paths
- **Testing:** pytest with `django_setup.py` bootstrap

---

## Component Conventions

### Page Components (`src/pages/`)
- Each page is a standalone route component
- Pages use `PageLayout` wrapper for consistent chrome
- Data fetching via RTK Query hooks
- All four states handled: loading, error, empty, normal

### Shared Components (`src/components/`)
- `ui/` — Pure presentational components (Modal, Skeleton, DataTable, ConfirmDialog)
- `layout/` — Layout wrappers (PageLayout, SideNav)
- `Fusion*` components — Fragment rendering bridge with sidecar

---

## Key Libraries

| Library | Path | Purpose |
|---------|------|---------|
| FusionDecoder (TS) | `src/lib/fusion-decoder.ts` | Decode sidecar fragment payloads |
| FusionStore | `src/lib/fusion-store.ts` | Tauri-compatible session storage |
| FusionMiddleware | `src/components/FusionMiddleware.tsx` | Fragment-vs-data mode context |
| FusionProxy | `src/components/FusionProxy.tsx` | HTML fragment fetcher/renderer |
| fusion-types | `src/lib/fusion-types.ts` | Shared TypeScript interfaces |

---

## Import Conventions

```typescript
// Local imports (use @/ alias)
import { ProductCard } from '@/components/ProductCard';
import { useGetProductsQuery } from '@/store/api/baseApi';

// Library imports
import { fusionDecoder } from '@/lib/fusion-decoder';

// Tauri imports
import { invoke } from '@tauri-apps/api/core';
```

---

## Testing

```bash
# Frontend unit tests (Vitest)
npm run test

# E2E tests (Playwright — from pos-e2e project)
cd ../pos-e2e && npx playwright test --project=pos-full

# Sidecar tests (pytest)
cd sidecar && python -m pytest tests/ -v

# TypeScript typecheck
npx tsc --noEmit
```

---

## Documentation References

| Topic | File |
|-------|------|
| POS architecture | `../docs/POS_ARCHITECTURE.md` |
| Sidecar integration | `../docs/SIDECAR_V2.md` |
| Sync architecture | `../docs/SYNC_ARCHITECTURE.md` |
| Role system | `../docs/ROLE_SYSTEM.md` |
| Theme system | `../docs/THEME_SYSTEM.md` |
| Getting started | `../docs/GETTING_STARTED.md` |
| Bolt integration | `../docs/BOLT_INTEGRATION.md` |
| Fusion integration plan | `../docs/DJANGO_FUSION_ENHANCEMENTS_PLAN.md` |
| Implementation plan | `./plan/` |
| Prompt variations | `./PROMPTS.md` |
