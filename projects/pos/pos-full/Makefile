# ============================================================================
# POS — Makefile
# ============================================================================
# Commands for development, building, testing, and maintenance.
# Uses pnpm for frontend and cargo for backend (Rust/Tauri).
#
# Quick start:
#   make              — print this menu
#   make dev          — start Vite frontend dev server  (http://localhost:1420)
#   make dev-desktop  — start full Tauri desktop app (hot-reload, includes Rust backend)
#   make tauri-dev    — alias for dev-desktop
#   make check        — typecheck both frontend & backend
#   make build        — build full desktop app (release)

.PHONY: help
.PHONY: dev dev-desktop tauri-dev preview
.PHONY: build build-frontend build-desktop build-android build-ios build-all clean-build
.PHONY: screenshots
.PHONY: check typecheck cargo-check cargo-test cargo-clippy
.PHONY: lint format clean install install-tauri-cli info seed db-seed
.PHONY: test test-watch i18n-audit i18n-check i18n-fix i18n-fix-check port-kill
.PHONY: admin-bootstrap admin-ensure-superuser

# ── Default ────────────────────────────────────────────────────────────────

help:                 ## Show this help menu
	@echo ''
	@echo '╔══════════════════════════════════════════════════════════╗'
	@echo '║  POS — Commands                                     ║'
	@echo '╚══════════════════════════════════════════════════════════╝'
	@echo ''
	@echo '── Admin ────────────────────────────────────────────────────'
	@echo '  make admin-bootstrap        Migrate + create superuser + start runserver :8000'
	@echo '  make admin-ensure-superuser Create superuser from env vars (idempotent)'
	@echo ''
	@echo '── Development ──────────────────────────────────────────────'
	@echo '  make dev              Start Vite dev server (localhost:1420, browser only)'
	@echo '  make dev-desktop      Start full Tauri desktop app (hot-reload, with Rust backend)'
	@echo '  make tauri-dev        Alias for dev-desktop'
	@echo '  make preview          Preview production build locally'
	@echo ''
	@echo '── Building ─────────────────────────────────────────────────'
	@echo '  make build            Build Tauri desktop app (production)'
	@echo '  make build-frontend   Build frontend only  (into dist/)'
	@echo '  make build-android    Build Android APK   (SDK required)'
	@echo '  make build-ios        Build iOS app       (Xcode required)'
	@echo ''
	@echo '── Checking & Testing ───────────────────────────────────────'
	@echo '  make check            TypeScript + Rust compilation check'
	@echo '  make typecheck        TypeScript type-check only'
	@echo '  make cargo-check      Rust cargo check only'
	@echo '  make cargo-test       Run Rust unit/integration tests'
	@echo '  make cargo-clippy     Run Rust Clippy linter'
	@echo '  make test             Run Vitest unit tests'
	@echo '  make test-watch       Run Vitest in watch mode'
	@echo '  make i18n-audit       Regenerate docs/i18n-gaps.md'
	@echo '  make i18n-check       CI-friendly i18n audit (exits non-zero on gaps)'
	@echo '  make i18n-fix         Apply scripts/dev/i18n-merge-ar.cjs + regenerate docs/i18n-gaps.md (idempotent)'
	@echo '  make i18n-fix-check   `make i18n-fix` + `make i18n-check` (full pipeline)'
	@echo '                         (MSA register rules live in docs/i18n-conventions.md)'
	@echo ''
	@echo '── Maintenance ───────────────────────────────────────────────'
	@echo '  make install          Install all dependencies'
	@echo '  make lint             Run all linters'
	@echo '  make format           Format code (rustfmt only)'
	@echo '  make clean            Remove all build artifacts'
	@echo '  make clean-build      Clean everything, reinstall, rebuild the app from scratch'
	@echo '  make screenshots      Capture 6 polished screenshots into docs/screenshots/'
	@echo '  make seed             Reset DB + apply preset; PRESET=all (default)'
	@echo '  make seed PRESET=foo  Reset DB + apply one preset: all|base|gaming|coffee'
	@echo '  make db-seed          [DEPRECATED] → forwards to `make seed`'
	@echo '  make info             Show tool versions'
	@echo ''

# ── Development ────────────────────────────────────────────────────────────

dev: port-kill        ## Start Vite frontend dev server (http://localhost:1420, browser only — no Rust backend)
	pnpm dev

dev-desktop: port-kill  ## Start full Tauri desktop app (hot-reload, includes Rust backend for invoke support)
	pnpm dev:desktop

tauri-dev:            ## Alias for dev-desktop (start Tauri desktop app with hot-reload)
	pnpm dev:desktop

preview:              ## Preview the production frontend build
	pnpm preview

# ── Building ───────────────────────────────────────────────────────────────

build: build-desktop  ## Build everything (default = desktop app)

build-frontend:       ## Build only the frontend (outputs to dist/)
	pnpm build

build-desktop:        ## Build desktop app (.dmg / .msi / .AppImage)
	pnpm build:desktop

build-android:        ## Build Android APK (requires Android SDK + NDK)
	pnpm build:android

build-ios:            ## Build iOS app (requires macOS + Xcode)
	pnpm build:ios

build-all:            ## Build all platforms sequentially
	pnpm build:all

# ── Sidecar ───────────────────────────────────────────────────────────────

build-sidecar:        ## Build the Python/Sanic sidecar binary for the current platform
	node scripts/dev/build-sidecar.cjs

build-sidecar-%:      ## Build the sidecar for a specific target triple (e.g. build-sidecar-x86_64-unknown-linux-gnu)
	node scripts/dev/build-sidecar.cjs --target $*


# ── Admin ───────────────────────────────────────────────────────────────────

admin-bootstrap:      ## Bootstrap admin: migrate + create superuser + start runserver
	@echo '── Admin Bootstrap ──'
	@echo '  → Running migrations...'
	@cd sidecar && python3 manage.py migrate
	@echo '  → Creating superuser from env vars (or defaults)...'
	@cd sidecar && python3 manage.py --ensure-superuser
	@echo '  → Starting admin panel at http://localhost:8000/admin/'
	@cd sidecar && python3 manage.py runserver 0.0.0.0:8000

admin-ensure-superuser: ## Create/update superuser from env vars (idempotent)
	@cd sidecar && python3 manage.py --ensure-superuser

# ── Screenshots ─────────────────────────────────────────────────────────────

# The capture pipeline lives in scripts/dev/capture-screenshots.sh so that
# multi-line shell logic (booting vite, looping over routes, converting PNGs)
# does not have to survive Make's `define` expansion — reformatting the file
# or moving the block between recipes cannot silently break it.
#
# The script requires in PATH: chromium-browser (or chromium), ImageMagick
# `convert`, and pnpm. Each is checked at script entry with a hint to install.
#
# Outputs land at docs/screenshots/{01_pos_overview,02_dashboard,
# 03_point_of_sale,04_inventory,05_reports,06_settings}.jpg — the canonical
# filenames referenced by docs/PUBLISH.md#visual-preview.
screenshots: port-kill  ## Capture 6 polished JPG screenshots into docs/screenshots/
	@bash scripts/dev/capture-screenshots.sh

# ── Clean Build ────────────────────────────────────────────────────────────

clean-build:          ## Clean all build artifacts, reinstall, rebuild from scratch
	@echo '── Clean ──'
	@$(MAKE) clean
	@echo '── Reinstall ──'
	@$(MAKE) install
	@echo '── Rebuild ──'
	@$(MAKE) build
	@echo '── ✓ Clean build complete ──'

# ── Checking & Testing ─────────────────────────────────────────────────────

check: typecheck cargo-check  ## TypeScript + Rust compilation check

typecheck:            ## TypeScript type-check without emitting files
	@echo '── TypeScript type-check ──'
	pnpm tsc --noEmit

cargo-check:          ## Rust cargo check (fast compilation check)
	@echo '── Rust cargo check ──'
	cd src-tauri && cargo check

cargo-test:           ## Run Rust tests
	@echo '── Rust tests ──'
	cd src-tauri && cargo test

cargo-clippy:         ## Run Rust Clippy linter (warnings-as-errors)
	@echo '── Rust Clippy ──'
	cd src-tauri && cargo clippy

test:                 ## Run Vitest unit tests (frontend)
	@echo '── Vitest ──'
	pnpm vitest run

test-watch:           ## Run Vitest in watch mode
	pnpm vitest

i18n-audit:           ## Regenerate docs/i18n-gaps.md from src/i18n/*.json
	@echo '── i18n audit ──'
	node scripts/dev/check-i18n.cjs

i18n-check:           ## CI-friendly i18n audit (exits 1 if any locale has missing keys)
	node scripts/dev/check-i18n.cjs --check

i18n-fix:             ## Apply scripts/i18n-merge-ar.cjs (idempotent) + regenerate docs/i18n-gaps.md
	@echo '── i18n fix ──'
	node scripts/dev/i18n-merge-ar.cjs
	@$(MAKE) i18n-audit

i18n-fix-check:       ## `make i18n-fix` + `make i18n-check` (full pipeline; exits non-zero on remaining gaps)
	@$(MAKE) i18n-fix
	@$(MAKE) i18n-check

# ── Maintenance ────────────────────────────────────────────────────────────

port-kill:            ## Kill any process on port 1420 (prevent port conflict)
	@node scripts/dev/kill-port.cjs

install:              ## Install all dependencies (pnpm + cargo)
	@echo '── Installing frontend dependencies ──'
	pnpm install
	@echo '── Installing Rust dependencies ──'
	cd src-tauri && cargo fetch

install-tauri-cli:    ## Install/update Tauri CLI
	pnpm add -D @tauri-apps/cli

lint: typecheck cargo-clippy  ## Run all available linters

format:               ## Format Rust code (cargo fmt)
	@echo '── Formatting Rust code ──'
	cd src-tauri && cargo fmt

clean:                ## Remove all build artifacts
	@echo '── Cleaning ──'
	rm -rf dist/
	rm -rf src-tauri/target/
	rm -rf node_modules/
	rm -rf src-tauri/gen/
	@echo 'Done. Run `make install` to reinstall dependencies.'

# ── Database ───────────────────────────────────────────────────────────────

seed:                                                ## Reset DB + apply preset (PRESET=all|base|gaming|coffee; default: all)
	@DB=$$(grep -E '^DATABASE_URL=' .env 2>/dev/null | cut -d= -f2- | sed -E 's/\r$$//;s/^[ \t]+//;s/[ \t]+$$//'); \
	if [ -z "$$DB" ]; then DB=restaurant.db; fi; \
	echo "── Reset + seed — preset=$(or $(PRESET),all) → $$DB ──"; \
	rm -f "$$DB"; \
	export DATABASE_URL="$$DB" && \
	PRESET='$(PRESET)' cargo run --manifest-path src-tauri/Cargo.toml --bin seed

db-seed:                                             ## DEPRECATED: alias of `make seed` (PRESET=all)
	@echo '⚠️  `make db-seed` is deprecated — use `make seed [PRESET=...]` instead.' >&2
	@PRESET='$(PRESET)' $(MAKE) seed

# ── Info ───────────────────────────────────────────────────────────────────

info:                 ## Show installed tool versions
	@echo '── Tool Versions ──'
	@echo "pnpm:   $$(pnpm --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "node:   $$(node --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "rustc:  $$(rustc --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "cargo:  $$(cargo --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "tauri:  $$(pnpm tauri --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "sqlite: $$(sqlite3 --version 2>/dev/null || echo 'NOT INSTALLED')"
