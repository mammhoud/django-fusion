# POS Solo — Enhancement Plan
> **Tags:** #pos #pos-solo #enhancement

> **Plan file:** `projects/pos/pos-solo/plan/ENHANCEMENT_PLAN.md`
> **Created:** 2026-07-25 | **Branch:** `generic`

---

## Overview

POS Solo shares the same core architecture as POS Full but with a simplified
feature set. This plan covers Solo-specific enhancements and references the
POS Full plans where applicable.

---

## Plan 1 — Component Reorganization

**Reference:** `../pos-full/plan/COMPONENT_REORGANIZATION.md`

Same reorganization pattern as POS Full, but fewer components:

```
src/components/
  ui/         # Modal, Skeleton, DataTable (from POS Full, minus fusion/)
  layout/     # PageLayout, SideNav
  pos/        # ProductCard, StatusToast
  shared/     # DatePicker, ThemeToggle

src/pages/
  pos/        # Sale, ProductManager
  inventory/  # Inventory, Recipes
  customers/  # Customers, Transactions
  reports/    # Reports, Analytics
  admin/      # Settings, Notes, About
  auth/       # Auth
```

### Solo-Specific Differences

- **No `fusion/` directory** — fusion-decoder.ts and fusion-store.ts stay in `lib/`
- **No `employees/` pages** — solo operators, no employee management
- **`config/` directory** — POS Solo loads configuration from `src/config/` (unique to Solo)

---

## Plan 2 — Desktop Dev Workflow

### Issue

Users run `make desktop-dev` but the Makefile only has `dev-desktop`. An alias
was added (see [CHANGES_MADE.md](../../CHANGES_MADE.md)) but the workflow can
be further improved.

### Improvements

- [ ] Add `make dev-web` for browser-only development (no Tauri window)
- [ ] Add `make dev-api` to run only the sidecar (for API testing)
- [ ] Add `make build-release` for production Tauri build
- [ ] Document the port differences: sidecar on `8766`, Tauri webview on `1420`
- [ ] Add `.env.example` for sidecar configuration

### Commands

```bash
# Full Tauri desktop with hot-reload
make dev-desktop
# or
make desktop-dev   # alias

# Browser-only (sidecar + Vite dev server, no Tauri window)
make dev-web

# API testing (sidecar only, no Vite)
make dev-api

# Production build
make build-release
```

---

## Plan 3 — CTC Teal Theme Migration

**Reference:** `../pos-full/plan/FLYONUI_THEME_MIGRATION.md`

Same indigo→teal migration as POS Full, but fewer pages to migrate (no
Employees, no Payroll, no Roles, no EmployeeSchedule).

| Page | Has indigo/purple | Priority |
|------|:------------:|:--------:|
| Analytics | Yes | P0 |
| Recipes | Yes | P1 |
| Inventory | Yes | P1 |
| Reports | Yes | P1 |
| About | Yes | P2 |

---

## Plan 4 — Sidecar Port Unification (Future)

Currently POS Full sidecar runs on `8765` and POS Solo on `8766`. Consider
unifying to a single port with edition detection via environment variable.

```python
# sidecar/config.py
EDITION = os.environ.get('POS_EDITION', 'solo')
PORT = 8765 if EDITION == 'full' else 8766
```

---

## Documentation

| Doc | Content |
|-----|---------|
| `AGENTS.md` | Solo-specific conventions, no employees, port 8766 |
| `PROMPTS.md` | Code generation templates for solo edition |
| `docs/typescript/index.md` | References POS Full conventions |
| `docs/python/index.md` | Sidecar differences (no roles, no sync) |
| `docs/rust/index.md` | No WebSocket sync |
| `docs/sql/index.md` | Subset of POS Full tables |

---

## Progress

| Plan | Status | Effort |
|------|:------:|:------:|
| 1 — Component Reorganization | ⬜ | 6h |
| 2 — Desktop Dev Workflow | 🟡 | 2h |
| 3 — CTC Teal Theme Migration | ⬜ | 3h |
| 4 — Sidecar Port Unification | ⬜ | 2h |