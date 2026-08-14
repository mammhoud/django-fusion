# POS System — Developer's Guide

> **Quick start guides for all POS editions**  
> **Last Updated:** 24 July 2026

---

## Which POS Edition Do I Need?

| If you want... | Use... | Backend | Database |
|---------------|--------|---------|----------|
| A standalone POS for one device | **pos-mini** | Rust/Diesel | SQLite |
| A branch POS that syncs to a master | **pos-solo** | Python/Robyn + Django ORM | SQLite |
| A multi-branch enterprise POS with cloud sync | **pos-full** | Python/Robyn + Django ORM | SQLite |
| A cloud SaaS dashboard for all branches | **pos-cloud** | Django + PostgreSQL | PostgreSQL |

---

## Quick Start: pos-mini

```bash
cd projects/pos/pos-mini

# Development Desktop
make dev-desktop

# Just the frontend (browser)
make dev
```

**Key commands:**
- `make dev-desktop` — Full Tauri desktop app
- `make dev` — Vite dev server only (http://localhost:1420)
- `make build` — Production build
- `make test` — Run Rust tests

---

## Quick Start: pos-solo

```bash
cd projects/pos/pos-solo

# Start frontend + server
make dev

# Just the server API server
make server

# Run server tests
cd server && uv run pytest
```

**Key commands:**
- `make dev` — Frontend + server (http://localhost:1420, API :8766)
- `make server` — Server only (http://localhost:8766)
- `make seed` — Seed the database
- `cd server && uv run pytest -v` — Run all tests

---

## Quick Start: pos-full

```bash
cd projects/pos/pos-full

# Start frontend + server
make dev

# Admin dashboard (Django Unfold)
make admin-bootstrap

# Run tests
cd server && uv run pytest
```

**Key commands:**
- `make dev` — Frontend + server (http://localhost:1420, API :8767)
- `make admin-bootstrap` — Bootstrap admin + dashboard
- `cd server && uv run pytest -v` — Run tests

---

## Project Structure

```
projects/pos/
├── pos-mini/          # Standalone POS (Rust + React + Tauri)
│   ├── src/           # React frontend
│   └── src-tauri/     # Rust backend (Diesel ORM)
├── pos-solo/          # Branch POS (Python + React + Tauri)
│   ├── src/           # React frontend
│   └── server/       # Python API server (Robyn + Django ORM)
├── pos-full/          # Enterprise POS (Python + React + Tauri)
│   ├── src/           # React frontend
│   └── server/       # Python API server + Django admin
├── pos-cloud/         # SaaS cloud server (Django)
├── pos-client/        # Vue.js thin client
├── shared/            # Shared Python modules
└── docs/              # Architecture and design docs
```

---

## Theme System Quick Reference

```typescript
// Use theme in any component
import { useTheme, THEME_VARIANTS } from '../contexts/ThemeContext';

function MyComponent() {
  const { mode, variant, toggleMode, setVariant, followSystem, setFollowSystem } = useTheme();
  
  return (
    <div>
      <p>Current mode: {mode} {followSystem ? '(auto)' : ''}</p>
      <p>Current variant: {variant}</p>
      
      {/* Light/Dark toggle */}
      <button onClick={toggleMode}>Toggle</button>
      
      {/* Theme variant selector */}
      {THEME_VARIANTS.map(v => (
        <button key={v.id} onClick={() => setVariant(v.id)}>
          {v.icon} {v.label}
        </button>
      ))}
      
      {/* System preference toggle */}
      <button onClick={() => setFollowSystem(!followSystem)}>
        Auto: {followSystem ? 'ON' : 'OFF'}
      </button>
    </div>
  );
}
```

**Theme variant system:** When a user selects a theme variant in Settings, Tailwind's built-in color tokens (`--color-teal-500`, `--color-slate-900`, etc.) are overridden per variant — this means **all existing components automatically adopt the new colors** without any code changes. See [THEME_SYSTEM.md](THEME_SYSTEM.md) for the full technical explanation.

---

## Adding a New Page

1. Create the page component in `src/pages/`
2. Add route to `App.tsx`
3. Add navigation entry to `SideNav.tsx`
4. Add API endpoint to `server/routes/` (if backend needed)
5. Register CRUD in `server.py` (if needed)

---

## Testing

```bash
# pos-mini: Rust tests
cd projects/pos/pos-mini
cargo test

# pos-solo: Server Python tests
cd projects/pos/pos-solo/server
uv run pytest -v

# pos-full: Server Python tests
cd projects/pos/pos-full/server
uv run pytest -v
```

---

## Common Tasks

### Add a new model field
1. Update the Django model in `server/models/`
2. Run `python3 manage.py makemigrations` (or use `--migrate` flag)
3. Update serialization in `handlers.py` `_ser_*()` function
4. Update TypeScript types in `src/types.ts`

### Add a new API endpoint
1. Add handler in `server/routes/` (or use `_register_crud()` for standard CRUD)
2. Register route in `server/routes/__init__.py` `register_all()`
3. Add RTK Query endpoint in `src/store/api/endpoints/`
4. Use hook in React component

### Add a new theme variant
See [THEME_SYSTEM.md](THEME_SYSTEM.md) section 7.

### Add a new role
See [ROLE_SYSTEM.md](ROLE_SYSTEM.md) section 5.
