# POS Shared Scripts

This directory contains scripts shared across all POS editions (mini, solo, full). Scripts are organized into three subdirectories based on their purpose.

> **Location:** `projects/pos/scripts/` — referenced from edition directories via `../scripts/...`

---

## Quick Reference

| Command | What it does |
|---------|-------------|
| `node ../scripts/dev/kill-port.cjs 1420` | Free port 1420 before starting dev server |
| `PROJECT_ROOT=. node ../scripts/dev/update-year.cjs` | Update copyright year in `tauri.conf.json` |
| `PROJECT_ROOT=. node ../scripts/dev/ensure-db.cjs` | Auto-seed database if missing |
| `node ../scripts/dev/check-i18n.cjs` | Audit i18n translation gaps |
| `PROJECT_ROOT=. node ../scripts/publish/generate-checksums.cjs` | Generate SHA256 checksums for build artifacts |
| `PROJECT_ROOT=. node ../scripts/publish/build-sidecar.cjs` | Build Python sidecar binary via PyInstaller |
| `bash ../scripts/dev/capture-screenshots.sh` | Capture 6 POS route screenshots |

Most scripts accept `PROJECT_ROOT` env var to locate the edition directory. When called from an edition's `package.json` or `Makefile`, pass `PROJECT_ROOT=.` (the CWD is the edition root).

---

## `scripts/dev/` — Development Scripts

| Script | Description | Usage | Env Required |
|--------|------------|-------|-------------|
| `kill-port.cjs` | Kills processes holding given port(s). Supports multiple ports, `PORT` env var, and cross-platform (macOS, Linux, Windows). | `node kill-port.cjs` (default 1420), `node kill-port.cjs 3000`, `node kill-port.cjs 1420 8766` | — |
| `ensure-db.cjs` | Pre-dev/pre-build hook. Checks if `restaurant.db` exists; auto-runs `pnpm db:seed` if missing. Reads `DATABASE_URL` from `.env`. | `PROJECT_ROOT=. node ensure-db.cjs` | `PROJECT_ROOT` |
| `update-year.cjs` | Updates `© {year}` in `src-tauri/tauri.conf.json` to the current year. Skips if already up-to-date to avoid Tauri file-watcher recompilation loops. | `PROJECT_ROOT=. node update-year.cjs` | `PROJECT_ROOT` |
| `check-i18n.cjs` | Audits `src/i18n/{en,fr,ar}.json` for missing translations vs English reference. Writes gap report to `docs/i18n-gaps.md`. Pass `--check` for CI mode (exits 1 if gaps found). | `PROJECT_ROOT=. node check-i18n.cjs`, `PROJECT_ROOT=. node check-i18n.cjs --check` | `PROJECT_ROOT` |
| `i18n-merge-ar.cjs` | Merges Modern Standard Arabic translations for enterprise-module UI keys into `src/i18n/ar.json`. Idempotent — never overwrites existing keys. | `node i18n-merge-ar.cjs` | — (CWD = edition root) |
| `fill-fr-translations.cjs` | One-shot French gap-fill for `src/i18n/fr.json`. Inserts missing keys from embedded map. Pass `--check` to exit 1 if keys still missing. | `PROJECT_ROOT=. node fill-fr-translations.cjs`, `PROJECT_ROOT=. node fill-fr-translations.cjs --check` | `PROJECT_ROOT` |
| `capture-screenshots.sh` | Boots Vite dev server, captures 6 POS routes via headless Chromium, converts PNG → JPG. Requires `chromium-browser` and ImageMagick `convert`. | `bash capture-screenshots.sh`, `bash capture-screenshots.sh --keep` | — (CWD = edition root) |

### Edition-specific dev scripts

These remain in each edition's local `scripts/` directory (not shared):

| Edition | Script | Purpose |
|---------|--------|---------|
| `formint-pos` | `dev/start-browser-dev.cjs` | Starts sidecar + frontend dev server together |
| `formint-pos` | `dev/test-sidecar-api.sh` | curl-based API smoke test against running sidecar |
| `formint-pos` | `dev/capture-admin-screenshots.sh` | Captures Unfold admin dashboard screenshots |

---

## `scripts/publish/` — Publishing Scripts

| Script | Description | Usage | Env Required |
|--------|------------|-------|-------------|
| `build-all.cjs` | Builds for all platforms (Linux x86_64/aarch64/armv7, Windows x86_64/aarch64/i686, macOS x86_64/aarch64, Android). Handles cross-compilation detection, Android SDK checks, and generates checksums. | `node build-all.cjs` | — (CWD = edition root) |
| `build-sidecar.cjs` | Builds the POS Python sidecar into a standalone binary via PyInstaller. Installs PyInstaller into a temporary venv if not already available. Supports `--target` for specific target triples. | `PROJECT_ROOT=. node build-sidecar.cjs`, `PROJECT_ROOT=. node build-sidecar.cjs --target x86_64-unknown-linux-gnu` | `PROJECT_ROOT` |
| `generate-checksums.cjs` | Scans `src-tauri/target/release/bundle/` for build artifacts and generates SHA256 `.sha256` files + a `CHECKSUMS.txt` manifest. | `PROJECT_ROOT=. node generate-checksums.cjs` | `PROJECT_ROOT` |
| `verify-checksum.cjs` | Verifies a file's integrity by comparing its SHA256 hash against a checksum file. Auto-discovers `.sha256` files. | `node verify-checksum.cjs <file>` | — |
| `generate-android-keystore.sh` | Interactive script to generate an Android release keystore for app signing. Prompts for passwords and certificate information. | `bash generate-android-keystore.sh` | — |

---

## `scripts/github/` — GitHub CI/CD Scripts

| Script | Description | Usage |
|--------|------------|-------|
| `diff-i18n.cjs` | Compares i18n translation gaps between PR base and head branches. Used in `.github/workflows/i18n.yml` workflow. | `node diff-i18n.cjs` |
| `encode-keystore-for-github.sh` | Base64-encodes an Android keystore file for storage as a GitHub secret. Used during release setup. | `bash encode-keystore-for-github.sh` |

---

## Path Convention

All shared scripts resolve edition-specific paths using the `PROJECT_ROOT` environment variable. From an edition directory:

```bash
# From projects/pos/forge-pos/ (or formint-pos/)
PROJECT_ROOT=. node ../scripts/dev/update-year.cjs
PROJECT_ROOT=. node ../scripts/dev/ensure-db.cjs
PROJECT_ROOT=. node ../scripts/publish/build-sidecar.cjs
```

Scripts that don't need `PROJECT_ROOT` (like `check-i18n.cjs`, `kill-port.cjs`, `build-all.cjs`) resolve their paths from `process.cwd()` and can be called directly from the edition root:

```bash
cd projects/pos/forge-pos && node ../scripts/dev/kill-port.cjs
```

---

## Makefile Integration

Each edition's `Makefile` references these shared scripts via relative paths. Key targets:

```makefile
port-kill:            @node ../scripts/dev/kill-port.cjs
i18n-audit:           node ../scripts/dev/check-i18n.cjs
i18n-fix:             node ../scripts/dev/i18n-merge-ar.cjs
screenshots:          @bash ../scripts/dev/capture-screenshots.sh
build-sidecar:        PROJECT_ROOT=. node ../scripts/publish/build-sidecar.cjs
```

The root `projects/pos/Makefile` also has convenience targets:
- `make dev-desktop-mini` — delegates to forge-pos `dev-desktop`
- `make check-mini` — runs forge-pos checks
- `make formint-*` — installs/runs/tests the merged package
- `make screenshots` — captures marketplace screenshots via `formint-pos`

---

## Adding a New Shared Script

1. Place the canonical version in the appropriate `projects/pos/scripts/<category>/` directory
2. For scripts that need edition-specific paths, use `process.env.PROJECT_ROOT || process.cwd()` as the fallback
3. Update each edition's `package.json` and/or `Makefile` to reference `../scripts/...` paths
4. Delete the duplicate script from individual edition `scripts/` directories
5. Update this README with the new script entry
