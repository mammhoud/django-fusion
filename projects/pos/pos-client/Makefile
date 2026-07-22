# ============================================================================
# POS Client — Makefile
# ============================================================================
# Commands for development, building, testing, and maintenance.
# Uses pnpm for frontend and cargo for backend (Rust/Tauri).
# Based on Vue 3 + Vite + Tauri 2.
#
# Quick start:
#   make              — print this menu
#   make dev          — start Vite frontend dev server  (http://localhost:1420)
#   make build        — build for production (vue-tsc + vite build)
#   make lint         — run oxlint linter
#   make format       — format with prettier

.PHONY: help
.PHONY: dev build preview
.PHONY: lint lint-fix format
.PHONY: install clean info

# ── Default ────────────────────────────────────────────────────────────────

help:                 ## Show this help menu
	@echo ''
	@echo '╔══════════════════════════════════════════════════════════╗'
	@echo '║  POS Client — Commands                              ║'
	@echo '╚══════════════════════════════════════════════════════════╝'
	@echo ''
	@echo '── Development ──────────────────────────────────────────────'
	@echo '  make dev              Start Vite dev server (localhost:1420, browser only)'
	@echo '  make build            Build frontend for production (dist/)'
	@echo '  make preview          Preview production build locally'
	@echo ''
	@echo '── Linting & Formatting ─────────────────────────────────────'
	@echo '  make lint             Run oxlint linter'
	@echo '  make lint-fix         Run oxlint with auto-fix'
	@echo '  make format           Format code with prettier'
	@echo ''
	@echo '── Maintenance ───────────────────────────────────────────────'
	@echo '  make install          Install all dependencies (pnpm + cargo)'
	@echo '  make clean            Remove all build artifacts'
	@echo '  make info             Show tool versions'

# ── Development ────────────────────────────────────────────────────────────

dev:                  ## Start Vite frontend dev server (http://localhost:1420)
	pnpm dev

build:                ## Build frontend for production (vue-tsc + vite build → dist/)
	pnpm build

preview:              ## Preview the production frontend build
	pnpm preview

# ── Linting & Formatting ───────────────────────────────────────────────────

lint:                 ## Run oxlint linter
	pnpm lint

lint-fix:             ## Run oxlint with auto-fix
	pnpm lint:fix

format:               ## Format code with prettier
	pnpm format

# ── Maintenance ────────────────────────────────────────────────────────────

install:              ## Install all dependencies (pnpm + cargo)
	@echo '── Installing frontend dependencies ──'
	pnpm install
	@echo '── Installing Rust dependencies (if src-tauri present) ──'
	@if [ -f src-tauri/Cargo.toml ]; then cd src-tauri && cargo fetch; fi

clean:                ## Remove all build artifacts
	@echo '── Cleaning ──'
	rm -rf dist/
	rm -rf node_modules/
	@if [ -d src-tauri/target ]; then rm -rf src-tauri/target/; fi
	@if [ -d src-tauri/gen ]; then rm -rf src-tauri/gen/; fi
	@echo 'Done. Run `make install` to reinstall dependencies.'

info:                 ## Show installed tool versions
	@echo '── Tool Versions ──'
	@echo "pnpm:   $$(pnpm --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "node:   $$(node --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "rustc:  $$(rustc --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "cargo:  $$(cargo --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "tauri:  $$(pnpm tauri --version 2>/dev/null || echo 'NOT INSTALLED')"
