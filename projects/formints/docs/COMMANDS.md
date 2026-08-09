# POS — Commands Reference> **All editions:** [mini](#pos-mini-edition) · [formint](#formint-pos-merged-package) · [client](#pos-client-edition)  
> **Topics:** [Dev Workflows](#development) · [Building](#building) · [Testing](#testing--checking) · [Server](#pos-server) · [Publishing](#publishing)  

  
> **Last updated:** July 22, 2026

---

## Quick Reference

| Action | Mini | Solo | Full | Client |
|--------|:----:|:----:|:----:|:------:|| **Run `make` from repo root** | `make pos-mini ...` | `make pos-formint ...` | `make pos-client ...` |


| **Run `make` from POS root** | `make setup-mini` | `make setup-solo` | `make setup-full` | `make setup-client` |
| **Run `make` from edition dir** | `cd forge-pos && make ...` | `cd formint-pos && make ...` | `cd pos-client && make ...` |
| Dev server | `make dev` | `make dev` | `make dev` | `make dev` |
| Desktop dev | `make dev-desktop` | `make dev-desktop` | `make dev-desktop` | — |
| Production build | `make build` | `make build` | `make build` | `make build` |
| TypeScript check | `make typecheck` | `make typecheck` | `make typecheck` | — |
| Rust check | `make cargo-check` | `make cargo-check` | `make cargo-check` | — |
| Tests | `make test` | `make test` | `make test` | — |
| Install deps | `make install` | `make install` | `make install` | `make install` |
| Clean artifacts | `make clean` | `make clean` | `make clean` | `make clean` |
| DB seed | `make seed` | `make seed` | `make seed` | — |
| Frontend port | `:1420` | `:1420` | `:1420` | `:1420` |
| Sidecar port | — | `:8765` | `:8766` | — |

---

## Delegation Chain

The POS command system uses a **layered delegation** pattern with two access paths:

```
Path 1: Direct edition access (from repo root)
  make pos-{mini|solo|full|client} <target>
     └──► projects/pos/pos-{edition}/Makefile

Path 2: Aggregated targets (from repo root via projects/pos/Makefile)
  make setup-{mini|solo|full}
  make dev-{mini|solo|full}
  make build-{mini|solo|full}
  make check-{mini|solo|full}
     └──► projects/pos/Makefile ──► projects/pos/pos-{edition}/Makefile

Path 3: Direct POS root access
  make -C projects/pos <target>
  make -C projects/pos/pos-{edition} <target>
```

**Tip:** `make pos` (from repo root) or `make -C projects/pos help` shows the aggregated POS help menu.

**From repo root:**
```bash
# Access any edition's Makefile directly
make pos-mini help         # Show pos-mini commands
make pos-formint env       # Start formint backend + frontend
make pos-client lint       # Lint pos-client code
```

**From POS root (`projects/pos/`):**
```bash
cd projects/pos

# Aggregated convenience targets (delegate to per-edition Makefiles)
make setup-mini            # Install mini deps
make formint-install       # Install merged package (backend + frontend)
make formint-env           # Run full formint env (backend :8767 + frontend :4321)
make formint-test          # Run merged package tests
make check-mini            # TypeScript + Rust check for mini
make server-test           # Run merged sidecar suite

# Direct per-edition access
make -C forge-pos dev-desktop
make -C formint-pos backend-test
make -C formint-pos seed
```

**From within an edition directory:**
```bash
cd projects/pos/pos-mini
make dev                # Start Vite dev server
make typecheck          # TypeScript type-check
make cargo-check        # Rust compilation check
```

---

## POS Mini Edition

**Directory:** `projects/pos/pos-mini/`  
**Stack:** React 19 + Tauri 2 + Rust/Diesel + SQLite  
**No sidecar** — pure desktop app

### Development

| Command | Description |
|---------|-------------|
| `make dev` | Start Vite frontend dev server at `http://localhost:1420` (browser only) |
| `make dev-desktop` | Start full Tauri desktop app with hot-reload (includes Rust backend) |
| `make tauri-dev` | Alias for `dev-desktop` |
| `make preview` | Preview production build locally |

### Building

| Command | Description |
|---------|-------------|
| `make build` | Build production desktop app (`.dmg` / `.msi` / `.AppImage`) |
| `make build-frontend` | Build frontend only (outputs to `dist/`) |
| `make build-desktop` | Same as `make build` |
| `make build-android` | Build Android APK (requires SDK + NDK) |
| `make build-ios` | Build iOS app (requires macOS + Xcode) |
| `make build-all` | Build all platforms sequentially |
| `make build-sidecar` | Build the Python/Sanic sidecar binary (not used in mini, but available) |
| `make build-sidecar-x86_64-unknown-linux-gnu` | Build sidecar for a specific target triple |

### Testing & Checking

| Command | Description |
|---------|-------------|
| `make check` | Run `typecheck` + `cargo-check` |
| `make typecheck` | TypeScript type-check (`pnpm tsc --noEmit`) |
| `make cargo-check` | Rust compilation check (`cargo check`) |
| `make cargo-test` | Run Rust unit/integration tests |
| `make cargo-clippy` | Run Rust Clippy linter (warnings-as-errors) |
| `make test` | Run Vitest unit tests (frontend) |
| `make test-watch` | Run Vitest in watch mode |

### Database

| Command | Description |
|---------|-------------|
| `make seed` | Reset DB + apply preset (`PRESET=all\|base\|gaming\|coffee`; default: `all`) |
| `make db-seed` | **DEPRECATED** — forwards to `make seed` |

### i18n

| Command | Description |
|---------|-------------|
| `make i18n-audit` | Regenerate `docs/i18n-gaps.md` from `src/i18n/*.json` |
| `make i18n-check` | CI-friendly audit (exits non-zero on gaps) |
| `make i18n-fix` | Apply i18n merge script + regenerate audit |
| `make i18n-fix-check` | `make i18n-fix` + `make i18n-check` (full pipeline) |

### Maintenance

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies (pnpm + cargo fetch) |
| `make install-tauri-cli` | Install/update Tauri CLI |
| `make lint` | Run all linters (`typecheck` + `cargo-clippy`) |
| `make format` | Format Rust code (`cargo fmt`) |
| `make clean` | Remove `dist/`, `src-tauri/target/`, `node_modules/`, `src-tauri/gen/` |
| `make clean-build` | Clean everything, reinstall, rebuild from scratch |
| `make screenshots` | Capture 6 polished screenshots into Landing-Fusion `related/formints/` |
| `make info` | Show installed tool versions (pnpm, node, rustc, cargo, tauri, sqlite) |
| `make port-kill` | Kill any process on port 1420 (prevents port conflict) |

---

## Formint POS (merged package)

**Directory:** `projects/pos/formint-pos/`  
**Stack:** Astro + Alpine.js + HTMX frontend, Django 5 + Ninja + django-fusion backend, Robyn sidecar, Unfold admin  
**Backend port:** `:8767` · **Frontend port:** `:4321` · **Sidecar port:** `:8765`  
**Admin panel:** `http://127.0.0.1:8767/admin/`  
**API docs:** `http://127.0.0.1:8767/api/v1/docs`

> Merges the former `pos-full` (Cloud Master) + `pos-solo` (Standalone)
> editions. Legacy React UIs archived under `formint-pos/legacy-react/`.

### Setup & Running

| Command | Description |
|---------|-------------|
| `make install` | Backend .venv + deps + migrate + frontend npm install |
| `make seed` | Migrate + idempotent superuser (admin@formint.local) |
| `make env` | Run backend + frontend in tmux (formint-be / formint-fe) |
| `make dev-backend` | Run backend runserver `:8767` (foreground) |
| `make dev-frontend` | Run astro dev `:4321` (foreground) |
| `make stop` | Kill tmux env sessions |
| `make status` | Show tmux sessions + endpoint health |

### Validation

| Command | Description |
|---------|-------------|
| `make check` | Django check + astro check |
| `make test` | Backend suite + frontend contract tests |
| `make backend-test` | Backend Django test suite |
| `make frontend-test` | Frontend vitest contract tests |

### Admin

| Command | Description |
|---------|-------------|
| `make backend-seed` | Create/update superuser from env (idempotent) |
| `make screenshots` | Capture Unfold admin dashboard screenshots → Landing-Fusion `related/formints/` |

### Build & Maintenance

| Command | Description |
|---------|-------------|
| `make build` | Frontend production build + backend collectstatic |
| `make preview` | Astro preview `:4321` |
| `make clean` | Remove db + staticfiles + node_modules |
| `make tauri` / `tauri-dev` / `tauri-build` | Tauri desktop shell commands |

---

## POS Client Edition

**Directory:** `projects/pos/pos-client/`  
**Stack:** Vue 3 + Vite + Tauri 2 + Pinia + Tailwind CSS 4  
**Note:** This is a separate Vue 3 desktop client (not the React-based POS itself)

### Development

| Command | Description |
|---------|-------------|
| `make dev` | Start Vite dev server at `http://localhost:1420` |
| `make build` | Build frontend for production (`vue-tsc --noEmit && vite build` → `dist/`) |
| `make preview` | Preview production build locally |

### Linting & Formatting

| Command | Description |
|---------|-------------|
| `make lint` | Run oxlint linter |
| `make lint-fix` | Run oxlint with auto-fix |
| `make format` | Format code with prettier |

### Maintenance

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies (pnpm + cargo fetch if `src-tauri/Cargo.toml` exists) |
| `make clean` | Remove `dist/`, `node_modules/`, `src-tauri/target/`, `src-tauri/gen/` |
| `make info` | Show installed tool versions |

---

## POS Server

The POS server is a consolidated **Robyn + Django ORM** server located in `formint-pos/sidecar/`.

Commands are available from the POS root Makefile (`projects/pos/Makefile`).

### Merged Sidecar (port 8765)

| Command | Description |
|---------|-------------|
| `make server-install` | Install server dependencies (`pip install -r requirements.txt`) |
| `make server-run` | Start server on port 8765 |
| `make server-dev` | Start server with hot reload and verbose output (`--dev --verbose`) |
| `make server-check` | Validate server imports |
| `make server-test` | Run merged sidecar test suite (171 passing + legacy known issues) |
| `make server-clean` | Remove `restaurant.db` |

---

## Combined Dev (All Editions)

| Command | Description |
|---------|-------------|
| `make dev-all` | Start the formint env (backend `:8767` + frontend `:4321`). Start other editions individually: `make dev-mini` / `dev-client` |

---

## Testing Scripts

Unit tests and integration tests for the POS sidecar servers live in:

| Test Suite | Location | Count | Run Command |
|-----------|----------|:-----:|-------------|
| Merged sidecar | `formint-pos/sidecar/tests/` | 171 passing (+85 legacy failures, 21 errors) | `make server-test` |
| Formint backend | `formint-pos/backend/` | 35 | `make formint-test` |
| Rust unit tests | `forge-pos/src-tauri/src/` | inline | `make check-mini` |
| Vitest (Frontend) | `formint-pos/frontend/src/` + `tests/js/` | inline | `make formint-test` |

---

## Publishing

| Command | Description |
|---------|-------------|
| `make screenshots` | Capture Unfold admin screenshots (via formint-pos) |
| `make publish` | Prepare publish bundle from `formint-pos/` → `publish-bundle/` |

---

## Workflow Examples

### First-time setup (mini)
```bash
cd projects/pos
make setup-mini            # pnpm install + cargo fetch
make dev                   # Vite dev server on :1420
```

### First-time setup (merged package)
```bash
cd projects/pos
make formint-install       # Backend .venv + deps + migrate + frontend npm install
make formint-env           # Start backend :8767 + frontend :4321 in tmux
# Admin panel at http://127.0.0.1:8767/admin/ (admin@formint.local / admin123)
```

### Full validation before release
```bash
cd projects/pos
make formint-check         # Django check + astro check
make formint-test          # Backend suite + frontend contract tests
make server-test           # Run merged sidecar test suite
make screenshots           # Capture admin screenshots
```

### Quick development loop
```bash
# From repo root — start coding immediately
make pos-mini dev          # forge-pos Vite on :1420
# or
make pos-formint env       # formint backend + frontend
```

### Clean rebuild
```bash
cd projects/pos/pos-mini
make clean-build           # Clean → install → build (one command)
```

---

## Troubleshooting

### Port 1420 already in use
```bash
make port-kill             # Kills any process on port 1420
```

### Sidecar won't start
```bash
# Check Python dependencies
make server-install

# Check import validity
make server-check

# Run with verbose output
make server-dev
```

### TypeScript errors
```bash
make typecheck             # Shows all TS errors without emitting files
```

### Rust compilation errors
```bash
make cargo-check           # Fast compilation check
make cargo-clippy          # Detailed linting with suggestions
```

---

> See the individual edition `Makefile` for the exact commands and
> `docs/POS_ARCHITECTURE.md` for the full architecture reference.
