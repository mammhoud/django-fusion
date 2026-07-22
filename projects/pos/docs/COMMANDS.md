# POS — Commands Reference

> **All editions:** [mini](#pos-mini-edition) · [solo](#pos-solo-edition) · [full](#pos-full-edition) · [client](#pos-client-edition)  
> **Topics:** [Dev Workflows](#development) · [Building](#building) · [Testing](#testing--checking) · [Server](#pos-server) · [Admin (Full)](#admin-pos-full) · [i18n](#i18n) · [Publishing](#publishing)  
> **Last updated:** July 22, 2026

---

## Quick Reference

| Action | Mini | Solo | Full | Client |
|--------|:----:|:----:|:----:|:------:|
| **Run `make` from repo root** | `make pos-mini ...` | `make pos-solo ...` | `make pos-full ...` | `make pos-client ...` |
| **Run `make` from POS root** | `make setup-mini` | `make setup-solo` | `make setup-full` | `make setup-client` |
| **Run `make` from edition dir** | `cd pos-mini && make ...` | `cd pos-solo && make ...` | `cd pos-full && make ...` | `cd pos-client && make ...` |
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

The POS command system uses a **layered delegation** pattern:

```
     Root Makefile                          projects/pos/
  ┌────────────────┐                    ┌──────────────────────┐
  │ make pos-mini  │ ── pos-mini ──►    │ make setup-mini     │ ──► pos-mini/Makefile
  │ make pos-solo  │ ── pos-solo ──►    │ make dev-solo       │ ──► pos-solo/Makefile
  │ make pos-full  │ ── pos-full ──►    │ make build-full     │ ──► pos-full/Makefile
  │ make pos-client│ ── pos-client ──►  │ make setup-client   │ ──► pos-client/Makefile
  └────────────────┘                    └──────────────────────┘
```

**From repo root:**
```bash
# Access any edition's Makefile directly
make pos-mini help      # Show pos-mini commands
make pos-solo dev       # Start solo Vite dev server
make pos-full build     # Build full desktop app
make pos-client lint    # Lint pos-client code
```

**From POS root (`projects/pos/`):**
```bash
cd projects/pos

# Aggregated convenience targets (delegate to per-edition Makefiles)
make setup-mini         # Install mini deps
make dev-solo           # Start solo Vite + sidecar
make build-full         # Build full desktop + sidecar
make check-mini         # TypeScript + Rust check for mini

# Direct per-edition access
make -C pos-mini dev-desktop
make -C pos-solo test
make -C pos-full admin-bootstrap
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
| `make screenshots` | Capture 6 polished screenshots into `docs/screenshots/` |
| `make info` | Show installed tool versions (pnpm, node, rustc, cargo, tauri, sqlite) |
| `make port-kill` | Kill any process on port 1420 (prevents port conflict) |

---

## POS Solo Edition

**Directory:** `projects/pos/pos-solo/`  
**Stack:** React 19 + Tauri 2 + Rust/Diesel + Python/Sanic sidecar + cloud sync  
**Sidecar port:** `:8765`  
**Cloud sync:** pushes data to pos-full master

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
| `make build` | Build production desktop app |
| `make build-frontend` | Build frontend only |
| `make build-desktop` | Build desktop app |
| `make build-android` | Build Android APK |
| `make build-ios` | Build iOS app |
| `make build-all` | Build all platforms sequentially |
| `make build-sidecar` | Build the Python/Sanic sidecar binary for current platform |
| `make build-sidecar-x86_64-unknown-linux-gnu` | Build sidecar for specific target triple |

### Testing & Checking

| Command | Description |
|---------|-------------|
| `make check` | `typecheck` + `cargo-check` |
| `make typecheck` | TypeScript type-check |
| `make cargo-check` | Rust compilation check |
| `make cargo-test` | Run Rust tests |
| `make cargo-clippy` | Run Rust Clippy linter |
| `make test` | Run Vitest unit tests |
| `make test-watch` | Run Vitest in watch mode |

### Database

| Command | Description |
|---------|-------------|
| `make seed` | Reset DB + apply preset |
| `make db-seed` | **DEPRECATED** — forwards to `make seed` |

### i18n

| Command | Description |
|---------|-------------|
| `make i18n-audit` | Regenerate i18n gaps report |
| `make i18n-check` | CI-friendly audit |
| `make i18n-fix` | Apply i18n fix + regenerate audit |
| `make i18n-fix-check` | Full i18n pipeline |

### Maintenance

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies (pnpm + cargo fetch) |
| `make install-tauri-cli` | Install/update Tauri CLI |
| `make lint` | `typecheck` + `cargo-clippy` |
| `make format` | `cargo fmt` |
| `make clean` | Remove all build artifacts |
| `make clean-build` | Clean, reinstall, rebuild |
| `make screenshots` | Capture 6 screenshots |
| `make info` | Show tool versions |
| `make port-kill` | Kill process on port 1420 |

---

## POS Full Edition

**Directory:** `projects/pos/pos-full/`  
**Stack:** React 19 + Tauri 2 + Rust/Diesel + Python/Sanic sidecar + Django admin + WebSocket  
**Sidecar port:** `:8766`  
**Admin panel:** `http://localhost:8000/admin/`  
**Extra features:** Django ORM, WebSocket chat, Cloud CRM master, JSON seed fixtures

POS Full has all the same commands as [POS Solo](#pos-solo-edition) plus additional admin targets.

### Admin (Full Only)

| Command | Description |
|---------|-------------|
| `make admin-bootstrap` | Migrate DB → create superuser → start runserver on `:8000` |
| `make admin-ensure-superuser` | Create/update superuser from env vars (idempotent) |
| `make admin-screenshots` | Capture 6 admin dashboard screenshots (requires running `:8000`) |

### Development

Same as Solo edition. All commands delegate to the shared pattern:
`dev`, `dev-desktop`, `tauri-dev`, `preview`

### Building

Same as Solo edition: `build`, `build-frontend`, `build-desktop`, `build-android`, `build-ios`, `build-all`, `build-sidecar`, `build-sidecar-%`

### Testing & Checking

Same as Solo edition: `check`, `typecheck`, `cargo-check`, `cargo-test`, `cargo-clippy`, `test`, `test-watch`

### Database & i18n

Same as Solo edition: `seed`, `db-seed`, `i18n-audit`, `i18n-check`, `i18n-fix`, `i18n-fix-check`

### Maintenance

Same as Solo edition: `install`, `install-tauri-cli`, `lint`, `format`, `clean`, `clean-build`, `screenshots`, `info`, `port-kill`

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

The POS server is a consolidated **Robyn + Django ORM** server located in `pos-solo/sidecar/`.

Commands are available from the POS root Makefile (`projects/pos/Makefile`).

### Solo Server (port 8765)

| Command | Description |
|---------|-------------|
| `make server-install` | Install server dependencies (`pip install -r requirements.txt`) |
| `make server-run` | Start server on port 8765 |
| `make server-dev` | Start server with hot reload and verbose output (`--dev --verbose`) |
| `make server-check` | Validate imports (unified_models + server) |
| `make server-test` | Run 155-test unified test suite |
| `make server-clean` | Remove `restaurant.db` |

### Full Server (port 8766)

| Command | Description |
|---------|-------------|
| `make server-full-install` | Install server dependencies |
| `make server-full-run` | Start server on port 8766 |
| `make server-full-dev` | Start server with verbose output |
| `make server-full-check` | Validate server imports |
| `make server-full-test` | Run 45-test server test suite |
| `make server-full-clean` | Remove `full_portal.db` |

---

## Edition Generation & Cleanup

| Command | Description |
|---------|-------------|
| `make editions` | Generate `pos-solo` and `pos-full` from canonical `pos-full/` source |
| `make clean` | Delete `pos-solo/`, `pos-full/`, and all build artifacts |

---

## Combined Dev (All Editions)

| Command | Description |
|---------|-------------|
| `make dev-all` | Start POS Full sidecar (`:8765`) + POS Full Vite dev server. Start other editions individually: `make dev-{mini\|solo\|client}` |

---

## Testing Scripts

Unit tests and integration tests for the POS sidecar servers live in:

| Test Suite | Location | Count | Run Command |
|-----------|----------|:-----:|-------------|
| Unified API (Solo) | `pos-solo/sidecar/tests/test_unified_api.py` | 155 | `make server-test` |
| Server (Full) | `pos-full/sidecar/tests/test_server.py` | 45 | `make server-full-test` |
| Rust unit tests | `pos-{mini,solo,full}/src-tauri/src/` | inline | `make cargo-test` |
| Vitest (Frontend) | `pos-{mini,solo,full}/src/test/` | inline | `make test` |

---

## Publishing

| Command | Description |
|---------|-------------|
| `make screenshots` | Capture 6 marketplace screenshots (requires pos-full) |
| `make publish` | Prepare publish bundle from `pos-full/` → `publish-bundle/` |

---

## Workflow Examples

### First-time setup (mini)
```bash
cd projects/pos
make setup-mini            # pnpm install + cargo fetch
make dev                   # Vite dev server on :1420
```

### First-time setup (solo with sidecar)
```bash
cd projects/pos
make setup-solo            # pnpm install + cargo fetch + pip install
make dev-solo              # Start sidecar on :8765 + Vite on :1420
```

### First-time setup (full with admin)
```bash
cd projects/pos
make setup-full            # Install everything
make dev-full              # Start sidecar + Vite
# In another terminal:
make -C pos-full admin-bootstrap  # Migrate + seed superuser + run admin on :8000
```

### Full validation before release
```bash
cd projects/pos
make check-full            # TypeScript + Rust + sidecar + Django check
make -C pos-full test      # Run Vitest frontend tests
make server-full-test      # Run server test suite (45 tests)
make -C pos-full cargo-test # Run Rust tests
make screenshots           # Capture marketplace screenshots
```

### Quick development loop
```bash
# From repo root — start coding immediately
make pos-mini dev          # Vite on :1420
# or
make pos-solo dev          # Solo Vite on :1420
# or
make pos-full dev          # Full Vite on :1420
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
