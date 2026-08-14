# Formint — AI Agent Instructions

> **Project:** `projects/formints/formintA/` (site slug `formint-pos`)  
> **Type:** Tauri desktop app (no server)  
> **Stack:** React 19 + TypeScript + Vite + Tailwind CSS + Rust (Tauri 2) + Diesel ORM + SQLite (direct)

---

## Project Overview

Formint is the lightweight edition (formerly pos-mini / forge-pos), marketed as
**Formints** on the landing site (`/products/formint-pos/`). It uses Tauri with a React frontend and
a Rust backend that talks directly to SQLite via Diesel ORM — **no Python
server**. This makes it the simplest and fastest to deploy.

---

## Key Differences

| Feature | POS Full | POS Solo | Formint |
|---------|:--------:|:--------:|:---------:|
| Python server | ✅ | ✅ | ❌ |
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
formintA/  (site slug formint-pos)
├── src/                          # React 19 frontend
│   ├── components/               # 16 reusable UI components
│   ├── pages/                    # 22 route-level pages
│   ├── hooks/                    # Custom React hooks
│   ├── contexts/                 # React contexts (Theme, Auth, Language)
│   ├── api/                      # Tauri invoke wrappers
│   ├── utils/                    # Utilities (invoice PDF, export)
│   ├── i18n/                     # Internationalization (en, fr, ar)
│   ├── test/                     # Vitest tests
│   └── types.ts                  # Shared TypeScript types
├── src-tauri/                    # Rust/Tauri backend
│   ├── src/
│   │   ├── lib.rs               # 80+ Tauri command registrations
│   │   ├── operations/           # 27 CRUD operation modules
│   │   ├── db/                   # Diesel models + schema + connection
│   │   ├── email.rs              # SMTP email
│   │   └── bin/seed.rs           # Seed binary (4 presets)
│   └── migrations/               # Diesel SQLite migrations
├── docs/                         # Comprehensive documentation
│   ├── commands.md               # CLI commands reference
│   ├── project-tree.md           # Full directory structure
│   ├── rust-code.md              # Rust backend architecture
│   ├── customization.md          # Customization guide
│   ├── calculations.md           # All formulas & calculations
│   └── roles-permissions.md      # Role-based access control
├── scripts/                      # Build & dev scripts
└── Makefile                      # Build, dev, test commands
```

---

## Code Style & Standards

### TypeScript / React
Same as the merged package — see `../formint-pos/README.md` and the archived React UI at `../formint-pos/legacy-react/` (formerly pos-full/pos-solo).

### Rust / Tauri
- Direct SQLite access via Diesel ORM (no Python intermediary)
- Tauri `invoke` calls go directly to Rust command handlers
- Migrations are plain SQL files (not Diesel migrations) in `src-tauri/migrations/`

---

## No Python Server

Formint does **not** include a Python server. All data operations go through
Tauri invoke → Rust → Diesel → SQLite. This means:

- **No `server/` directory**
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
| POS architecture | `../../docs/POS_ARCHITECTURE.md` |
| Role system | `../../docs/ROLE_SYSTEM.md` |
| Commands | `docs/commands.md` |
| Project structure | `docs/project-tree.md` |
| Rust backend | `docs/rust-code.md` |
| Calculations | `docs/calculations.md` |
| Roles & Permissions | `docs/roles-permissions.md` |
| Customization | `docs/customization.md` |
