# POS Mini — AI Agent Instructions

> **Project:** `projects/pos/pos-mini/`  
> **Type:** Tauri desktop app (no sidecar)  
> **Stack:** React 18 + TypeScript + Vite + Tailwind CSS + Rust (Tauri) + SQLite (direct)

---

## Project Overview

POS Mini is the lightweight edition. It uses Tauri with a React frontend and
a Rust backend that talks directly to SQLite via Diesel ORM — **no Python
sidecar**. This makes it the simplest and fastest to deploy.

---

## Key Differences

| Feature | POS Full | POS Solo | POS Mini |
|---------|:--------:|:--------:|:--------:|
| Python sidecar | ✅ | ✅ | ❌ |
| Django ORM | ✅ | ✅ | ❌ (Diesel direct) |
| Multi-store sync | ✅ | ❌ | ❌ |
| Employee management | ✅ | ❌ | ❌ |
| Fusion fragments | ✅ | ✅ | ❌ |
| Point of sale | ✅ | ✅ | ✅ |
| Product management | ✅ | ✅ | ✅ |
| Customer management | ✅ | ✅ | ✅ |

---

## Directory Structure

```
pos-mini/
├── src/                          # React frontend
│   ├── components/               # ✅ Shared UI components (currently flat)
│   │   ├── ui/                   # ⬜ PLANNED — UI primitives
│   │   └── layout/               # ⬜ PLANNED — Layout components
│   ├── pages/                    # ✅ Route-level page components (currently flat)
│   ├── stores/                   # ✅ Redux stores (note: plural — existing convention)
│   ├── hooks/                    # Custom React hooks
│   ├── contexts/                 # React contexts
│   ├── utils/                    # Utility functions
│   ├── i18n/                     # Internationalization
│   ├── test/                     # Vitest tests
│   └── types.ts                  # Shared TypeScript types
├── src-tauri/                    # Rust/Tauri backend
│   ├── src/
│   │   ├── db/                   # Database models + schema (Diesel)
│   │   │   ├── models.rs         # Rust structs
│   │   │   └── schema.rs         # Diesel schema
│   │   ├── commands/             # Tauri command handlers
│   │   └── main.rs
│   └── migrations/               # SQLite migrations (native SQL)
├── public/                       # Static assets
├── docs/                         # Project documentation
│   ├── typescript/               # TypeScript/React docs
│   ├── rust/                     # Rust/Tauri docs
│   └── sql/                      # SQL/migration docs
└── plan/                         # Implementation plans
```

---

## Code Style & Standards

### TypeScript / React
Same as POS Full — see `../pos-full/AGENTS.md`.

### Rust / Tauri
- Direct SQLite access via Diesel ORM (no Python intermediary)
- Tauri `invoke` calls go directly to Rust command handlers
- Migrations are plain SQL files (not Diesel migrations) in `src-tauri/migrations/`

---

## No Python Sidecar

POS Mini does **not** include a Python sidecar. All data operations go through
Tauri invoke → Rust → Diesel → SQLite. This means:

- **No `sidecar/` directory**
- **No Django ORM models**
- **No Fusion fragments**
- **No `fusion-decoder.ts` or `fusion-store.ts`**
- **Simpler deployment** — single binary, no Python runtime needed

---

## Testing

```bash
# Frontend unit tests (Vitest)
npm run test

# E2E tests (Playwright — from pos-e2e project)
cd ../pos-e2e && npx playwright test --project=pos-mini

# TypeScript typecheck
npx tsc --noEmit

# Build
npm run build
```

---

## Documentation References

| Topic | File |
|-------|------|
| POS architecture | `../docs/POS_ARCHITECTURE.md` |
| Rust integration | `../docs/RUST_INTEGRATION.md` |
| Getting started | `../docs/GETTING_STARTED.md` |
| Theme system | `../docs/THEME_SYSTEM.md` |
| Implementation plan | `./plan/` |
| Prompt variations | `./PROMPTS.md` |
