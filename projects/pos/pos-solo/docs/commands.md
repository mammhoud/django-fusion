# POS — CLI Commands Reference

> **All commands run from:** `projects/pos/pos-full/`

---

## Development

| Command | Description |
|---------|-------------|
| `make dev` | Start Vite dev server at `localhost:1420` (browser only, no Rust backend) |
| `make dev-desktop` | Start full Tauri desktop app with hot-reload (Rust backend included) |
| `make tauri-dev` | Alias for `dev-desktop` |
| `make preview` | Preview production frontend build locally |

## Building

| Command | Description |
|---------|-------------|
| `make build` | Build Tauri desktop app (production) — `.dmg` / `.msi` / `.AppImage` |
| `make build-frontend` | Build frontend only → `dist/` |
| `make build-android` | Build Android APK (requires Android SDK + NDK) |
| `make build-ios` | Build iOS app (requires macOS + Xcode) |
| `make build-all` | Build all platforms sequentially |
| `make build-sidecar` | Build Python/Sanic sidecar binary for current platform |
| `make build-sidecar-<triple>` | Build sidecar for specific target (e.g., `x86_64-unknown-linux-gnu`) |

## Checking & Testing

| Command | Description |
|---------|-------------|
| `make check` | TypeScript + Rust compilation check (fast) |
| `make typecheck` | TypeScript `tsc --noEmit` |
| `make cargo-check` | Rust `cargo check` |
| `make cargo-test` | Run Rust unit/integration tests |
| `make cargo-clippy` | Run Rust Clippy linter |
| `make test` | Run Vitest unit tests (frontend) |
| `make test-watch` | Run Vitest in watch mode |

## i18n (Internationalization)

| Command | Description |
|---------|-------------|
| `make i18n-audit` | Regenerate `docs/i18n-gaps.md` from `src/i18n/*.json` |
| `make i18n-check` | CI-friendly audit — exits non-zero on gaps |
| `make i18n-fix` | Apply `i18n-merge-ar.cjs` + regenerate gap report (idempotent) |
| `make i18n-fix-check` | `i18n-fix` + `i18n-check` together |

## Database & Seeding

| Command | Description |
|---------|-------------|
| `make seed` | Reset DB + apply `PRESET=all` (default: all 100+ items) |
| `make seed PRESET=base` | Reset + seed basic restaurant (30 items) |
| `make seed PRESET=gaming` | Reset + seed POS-KO Gaming Center |
| `make seed PRESET=coffee` | Reset + seed coffee shop |
| `make db-seed` | **[Deprecated]** — use `make seed` instead |

## Maintenance

| Command | Description |
|---------|-------------|
| `make install` | Install all deps (`pnpm install` + `cargo fetch`) |
| `make install-tauri-cli` | Install/update Tauri CLI |
| `make lint` | Run all linters (typecheck + clippy) |
| `make format` | Format Rust code (`cargo fmt`) |
| `make clean` | Remove all build artifacts (`dist/`, `target/`, `node_modules/`) |
| `make clean-build` | Clean everything + reinstall + rebuild |
| `make screenshots` | Capture 6 polished JPG screenshots → `docs/screenshots/` |
| `make info` | Show installed tool versions |
| `make port-kill` | Kill any process on port 1420 |

---

## pnpm Scripts (from `package.json`)

| Script | Description |
|--------|-------------|
| `pnpm dev` | Vite dev server |
| `pnpm dev:desktop` | Tauri desktop with hot-reload |
| `pnpm build` | Vite production build |
| `pnpm build:desktop` | Tauri production build |
| `pnpm build:android` | Tauri Android build |
| `pnpm build:ios` | Tauri iOS build |
| `pnpm build:all` | Build all platforms |
| `pnpm preview` | Preview production build |

---

## cargo Commands (from `src-tauri/`)

| Command | Description |
|---------|-------------|
| `cargo check` | Fast compilation check |
| `cargo build` | Debug build |
| `cargo build --release` | Release build |
| `cargo test` | Run Rust tests |
| `cargo test -- --test-threads=1` | Run tests serially (needed for env var tests) |
| `cargo clippy` | Run Clippy lints |
| `cargo fmt` | Format Rust code |
| `cargo run --bin seed` | Run seed binary manually |

---

## Environment Variables

All env vars are loaded from `.env` via `dotenvy`:

```bash
# ── Required ──
SUPERUSER_EMAIL=admin@pos.local          # Superuser email
SUPERUSER_PASSWORD=changeme              # Superuser password
SUPERUSER_NAME=Admin                     # Superuser display name

# ── Optional ──
DATABASE_URL=restaurant.db               # SQLite path (default: restaurant.db)
SIDECAR_HOST=127.0.0.1                   # Sidecar host
SIDECAR_PORT=8765                        # Sidecar port

# ── SMTP (optional, for email) ──
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## Quick Reference

```bash
# Fastest workflow
make dev                  # Start browser dev
make check                # Verify everything compiles
make test                 # Run frontend tests
make cargo-test           # Run backend tests
make seed                 # Reset & seed database

# Before committing
make lint                 # Check everything
make i18n-check           # Verify translations
```
