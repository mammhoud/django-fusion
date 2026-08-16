# Formint — CLI Commands Reference

> **Stack:** Tauri 2 + React 19 + Rust (Diesel ORM) + SQLite  
> **No server** — all data operations through Tauri invoke/ Rust backend directly

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
| `make build-server` | Build Python server binary (not included in forge-pos) |

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
| `make screenshots` | Capture 6 polished JPG screenshots → Landing-Fusion `related/formints/` |
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
| `cargo test -- --test-threads=1` | Run tests serially |
| `cargo clippy` | Run Clippy lints |
| `cargo fmt` | Format Rust code |
| `cargo run --bin seed` | Run seed binary manually |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SUPERUSER_EMAIL` | — | Superuser email (auth) |
| `SUPERUSER_PASSWORD` | — | Superuser password |
| `DATABASE_URL` | `restaurant.db` | SQLite database path |
| `SERVER_HOST` | `127.0.0.1` | Server bind address (optional) |
| `SERVER_PORT` | `8765` | Server port |
| `SMTP_*` | — | SMTP email configuration |

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
