# POS Solo — AI Agent Instructions

> **Project:** `projects/pos/pos-solo/`  
> **Type:** Tauri desktop app + Robyn sidecar + Django ORM  
> **Stack:** React 18 + TypeScript + Vite + Tailwind CSS + Rust (Tauri) + Python (Robyn/Django ORM)

---

## Project Overview

POS Solo is the single-user edition of the Structa POS system. It shares the
same core architecture as POS Full (Tauri + React + Robyn sidecar) but has a
simplified feature set focused on solo operators. No multi-store sync, no
employee management, no role system.

---

## Key Differences from POS Full

| Feature | POS Full | POS Solo |
|---------|:--------:|:--------:|
| Multi-store sync | ✅ | ❌ |
| Employee management | ✅ | ❌ |
| Payroll | ✅ | ❌ |
| Role-based access | ✅ | ❌ |
| Inventory management | ✅ | ✅ (simplified) |
| Point of sale | ✅ | ✅ |
| Customer management | ✅ | ✅ |
| Reports | ✅ | ✅ (basic) |

---

## Directory Structure

```
pos-solo/
├── src/                          # React frontend
│   ├── components/               # Shared UI components
│   │   ├── ui/                   # ⬜ PLANNED — UI primitives (Modal, Skeleton, etc.)
│   │   └── layout/               # ⬜ PLANNED — Layout components (PageLayout, SideNav)
│   │   (Currently flat — restructure pending)
│   ├── pages/                    # Route-level page components (currently flat)
│   ├── store/                    # Redux store (RTK Query)
│   ├── hooks/                    # Custom React hooks
│   ├── contexts/                 # React contexts
│   ├── lib/                      # Core libraries (fusion-decoder, fusion-store)
│   ├── api/                      # API client layer
│   ├── utils/                    # Utility functions
│   ├── i18n/                     # Internationalization
│   ├── config/                   # App configuration (pos-solo only)
│   ├── test/                     # Vitest tests
│   └── types.ts                  # Shared TypeScript types
├── src-tauri/                    # Rust/Tauri backend
│   ├── src/
│   │   ├── db/                   # Database models + schema (Diesel)
│   │   ├── commands/             # Tauri command handlers
│   │   └── main.rs
│   └── migrations/               # SQLite migrations
├── sidecar/                      # Python sidecar (Robyn)
│   ├── models/                   # Django ORM models
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

Same conventions as POS Full. See `../pos-full/AGENTS.md` for full reference.

### Key Differences
- **Config module** (`src/config/`) — POS Solo loads configuration from `config/` (not present in POS Full)
- **Simplified store** — Fewer API endpoints; no sync middleware
- **No WebSocket** — POS Solo does not connect to cloud sync

---

## Testing

```bash
# Frontend unit tests (Vitest)
npm run test

# E2E tests (Playwright — from pos-e2e project)
cd ../pos-e2e && npx playwright test --project=pos-solo

# Sidecar tests (pytest)
cd sidecar && python -m pytest tests/ -v

# TypeScript typecheck
npx tsc --noEmit

# Desktop dev (Tauri hot-reload)
make dev-desktop
# or
make desktop-dev      # alias
```

---

## Documentation References

| Topic | File |
|-------|------|
| POS architecture | `../docs/POS_ARCHITECTURE.md` |
| Sidecar integration | `../docs/SIDECAR_V2.md` |
| Getting started | `../docs/GETTING_STARTED.md` |
| Theme system | `../docs/THEME_SYSTEM.md` |
| Implementation plan | `./plan/` |
| Prompt variations | `./PROMPTS.md` |
