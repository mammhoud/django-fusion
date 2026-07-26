# scripts/dev/ — Development & Build Utilities

Scripts that are part of the **development workflow** (not CI, not checksums, not translations).

## Contents

| Script | Purpose | Used by |
|--------|---------|---------|
| `kill-port.cjs` | Kill process on port 1420 before dev server starts | `make dev`, `make dev-desktop`, `pnpm predev` |
| `update-year.cjs` | Update copyright year in `tauri.conf.json` | `pnpm prebuild`, `pnpm predev` |
| `ensure-db.cjs` | Auto-seed the SQLite database if missing | `pnpm prebuild`, `pnpm predev` |
| `capture-screenshots.sh` | Headless Chromium screenshots for docs | `make screenshots` |
| `build-sidecar.cjs` | Build the Python/Sanic sidecar via PyInstaller | `make build-sidecar`, `pnpm build:sidecar` |
| `build-all.cjs` | Multi-platform build orchestrator | `pnpm build:all` |
| `generate-android-keystore.sh` | Generate an Android release signing keystore | manual (CI/release prep) |

## Enhancement Ideas

- **`watch.cjs`** — file-watcher that restarts the Vite dev server on config changes
- **`clean-artifacts.cjs`** — clean build artifacts while preserving node_modules (faster than `make clean`)
- **`bump-version.cjs`** — bump version in `package.json`, `tauri.conf.json`, and `Cargo.toml` in one step
- **`generate-icons.sh`** — generate all icon sizes from a single source image
- **`lint-staged.cjs`** — pre-commit hook runner for linting staged files only
