# ============================================================================
# Formint Client (POS) — Makefile
# ============================================================================
# Commands for development, building, testing, and maintenance across the
# full stack:
#   · Vue 3 POS app      (root)          → http://localhost:1420
#   · Astro storefront   (frontend/)     → http://localhost:4322
#   · Django backend     (backend/)      → http://localhost:8075
#   · Tauri desktop shell (src-tauri/)
#
# Quick start:
#   make              — print this menu
#   make dev          — start Vite frontend dev server  (http://localhost:1420)
#   make stack        — start Vue + Astro + Django dev servers together
#   make tauri-dev    — start the desktop app in dev mode
#   make check        — run all typechecks and system checks
#   make test         — run all test suites

SHELL := /bin/bash

.PHONY: help
.PHONY: dev web backend stack tauri-dev
.PHONY: build web-build build-all tauri-build preview
.PHONY: lint lint-fix format fix
.PHONY: typecheck astro-check backend-check check
.PHONY: test e2e
.PHONY: install install-all clean info
.PHONY: migrate seed superuser shell

# ── Default ────────────────────────────────────────────────────────────────

help:                 ## Show this help menu
	@echo ''
	@echo '╔══════════════════════════════════════════════════════════════════╗'
	@echo '║  Formint Client — Commands                                        ║'
	@echo '╚══════════════════════════════════════════════════════════════════╝'
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-22s %s\n", $$1, $$2}'

# ── Development ────────────────────────────────────────────────────────────

dev:                  ## Start Vue POS dev server (http://localhost:1420)
	pnpm dev

web:                  ## Start Astro storefront dev server (http://localhost:4322)
	cd frontend && pnpm dev

backend:              ## Start Django backend dev server (http://localhost:8075)
	$(MAKE) -C backend dev

stack:                ## Start Vue + Astro + Django dev servers together
	bash scripts/dev-stack.sh

tauri-dev:            ## Start the Tauri desktop app in dev mode
	pnpm tauri dev

# ── Build ──────────────────────────────────────────────────────────────────

build:                ## Build the Vue POS app for production (dist/)
	pnpm build

web-build:            ## Build the Astro storefront (frontend/dist/)
	cd frontend && pnpm build

build-all:            ## Build Vue + Astro frontends
	$(MAKE) build
	$(MAKE) web-build

tauri-build:          ## Build the desktop app (bundles)
	pnpm tauri build

preview:              ## Preview the Vue production build
	pnpm preview

# ── Linting & Formatting ───────────────────────────────────────────────────

lint:                 ## Run oxlint linter
	pnpm lint

lint-fix:             ## Run oxlint with auto-fix
	pnpm lint:fix

format:               ## Format code with prettier
	pnpm format

fix:                  ## Auto-fix lint issues and format
	pnpm lint:fix
	pnpm format

# ── Checks ─────────────────────────────────────────────────────────────────

typecheck:            ## Typecheck the Vue app (vue-tsc)
	pnpm exec vue-tsc --noEmit

astro-check:          ## Check the Astro storefront (astro check)
	cd frontend && pnpm check

backend-check:        ## Django system checks
	$(MAKE) -C backend check

check:                ## Run all typechecks + system checks
	$(MAKE) typecheck
	$(MAKE) astro-check
	$(MAKE) backend-check

# ── Tests ──────────────────────────────────────────────────────────────────

test:                 ## Run all checks + backend tests
	@echo '── Lint (oxlint) ──'
	pnpm lint
	@echo '── Typecheck (vue-tsc) ──'
	pnpm exec vue-tsc --noEmit
	@echo '── Astro check ──'
	cd frontend && pnpm check
	@echo '── Backend tests ──'
	$(MAKE) -C backend test

e2e:                  ## Full-stack end-to-end tests (boots backend + Astro)
	bash scripts/e2e.sh

# ── Maintenance ────────────────────────────────────────────────────────────

install:              ## Install frontend deps (pnpm) + fetch Rust crates
	@echo '── Installing Vue dependencies ──'
	pnpm install
	@echo '── Installing Astro storefront dependencies ──'
	cd frontend && pnpm install
	@echo '── Fetching Rust dependencies (if src-tauri present) ──'
	@if [ -f src-tauri/Cargo.toml ]; then cd src-tauri && cargo fetch; fi

install-all:          ## Install ALL dependencies (pnpm + cargo + backend uv)
	$(MAKE) install
	@echo '── Syncing backend Python deps ──'
	$(MAKE) -C backend install

clean:                ## Remove all build artifacts
	@echo '── Cleaning ──'
	rm -rf dist/
	rm -rf frontend/dist/
	rm -rf node_modules/
	rm -rf frontend/node_modules/
	@if [ -d src-tauri/target ]; then rm -rf src-tauri/target/; fi
	@if [ -d src-tauri/gen ]; then rm -rf src-tauri/gen/; fi
	@echo 'Done. Run `make install` to reinstall dependencies.'

info:                 ## Show installed tool versions
	@echo '── Tool Versions ──'
	@echo "node:   $$(node --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "pnpm:   $$(pnpm --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "rustc:  $$(rustc --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "cargo:  $$(cargo --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "tauri:  $$(pnpm tauri --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "uv:     $$(uv --version 2>/dev/null || echo 'NOT INSTALLED')"

# ── Backend shortcuts (delegate to backend/Makefile) ───────────────────────

migrate:              ## Make + apply Django migrations
	$(MAKE) -C backend migrate

seed:                 ## Migrate + seed the demo catalog + users
	$(MAKE) -C backend seed

superuser:            ## Create a Django admin superuser
	$(MAKE) -C backend superuser

shell:                ## Open a Django shell
	$(MAKE) -C backend shell
