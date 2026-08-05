# ============================================================================
# POS — Root Makefile (v3.0)
# ============================================================================
# Orchestrates POS editions + Cloud CRM server + Django Portals:
#   - forge-pos    : Forge POS — lightweight Tauri + Rust/Diesel edition
#   - formint-pos  : Formint POS — merged package (pos-full + pos-solo)
#                    Astro frontend + Django Ninja backend + Robyn sidecar
#                    + Unfold admin + legacy React UI archive
#   - pos-client   : Vue 3 + Tauri desktop app (separate client)
#   - cloud        : Django-based cloud CRM server (pos-cloud/)
#
# Design: Delegates to per-edition Makefiles via $(MAKE) -C.
# This ensures each edition owns its own targets and the root Makefile
# stays a thin dispatcher with aggregated convenience targets.
#
# Quick start:
#   make setup-mini              — install mini edition dependencies
#   make formint-install         — install merged package (backend + frontend)
#   make formint-env             — run full formint env (backend + frontend)
#   make dev-mini                — start Vite dev server for mini edition

.PHONY: help
.PHONY: clean
.PHONY: setup-mini setup-client
.PHONY: dev-mini dev-all
.PHONY: dev-desktop-mini
.PHONY: build-mini build-client
.PHONY: check-mini
.PHONY: server-install server-run server-dev server-check server-test server-clean
.PHONY: cloud-install cloud-run cloud-dev cloud-check cloud-test cloud-clean
.PHONY: formint-install formint-run formint-env formint-stop formint-test formint-check formint-clean formint-sidecar-test
.PHONY: screenshots publish

# ── Edition directories ────────────────────────────────────────────────────
# Used for delegation targets below.
FORGE_POS  := forge-pos
FORMINT_POS := formint-pos
POS_CLIENT := pos-client
POS_CLOUD  := pos-cloud

# ── Default ────────────────────────────────────────────────────────────────

help:                 ## Show this help menu
	@echo ''
	@echo '╔══════════════════════════════════════════════════════════╗'
	@echo '║  POS v3.0 — Mini + Formint (merged) + Client Editions ║'
	@echo '╚══════════════════════════════════════════════════════════╝'
	@echo ''
	@echo '── Editions ────────────────────────────────────────────────'
	@echo '  make clean             Delete build artifacts'
	@echo ''
	@echo '── POS Mini (Minimal Tauri + Rust/Diesel) ──────────────────'
	@echo '  make setup-mini        Install dependencies (pnpm + cargo)'
	@echo '  make dev-mini          Start Vite dev server (port 1420)'
	@echo '  make dev-desktop-mini  Start full Tauri desktop app (hot-reload, with Rust backend)'
	@echo '  make build-mini        Build desktop app (production)'
	@echo '  make check-mini        TypeScript + Rust compilation check'
	@echo ''
	@echo '── Formint POS (merged pos-full + pos-solo) ────────────────'
	@echo '  make formint-install   Install backend .venv + frontend npm + migrate'
	@echo '  make formint-run       Run backend (API + admin on :8767)'
	@echo '  make formint-env       Run full env (backend :8767 + frontend :4321 in tmux)'
	@echo '  make formint-stop      Stop the formint tmux env'
	@echo '  make formint-test      Run backend + JS contract tests'
	@echo '  make formint-check     Django check + astro check'
	@echo '  make formint-sidecar-test   Run merged Robyn sidecar suite'
	@echo '  make formint-clean     Remove db + staticfiles + node_modules'
	@echo ''
	@echo '── POS Client (Vue 3 + Tauri desktop) ───────────────────────'
	@echo '  make setup-client      Install dependencies (pnpm + cargo)'
	@echo '  make dev-client        Start Vite dev server'
	@echo '  make build-client      Build frontend for production'
	@echo ''
	@echo '── All Editions ─────────────────────────────────────────────'
	@echo '  make dev-all           Start all dev servers concurrently'
	@echo ''
	@echo '── POS Server (Merged Robyn sidecar — formint-pos/sidecar) ─'
	@echo '  make server-install    Install sidecar dependencies'
	@echo '  make server-run        Start sidecar (port 8765)'
	@echo '  make server-dev        Dev mode with hot reload'
	@echo '  make server-check      Validate imports'
	@echo '  make server-test       Run merged sidecar test suite'
	@echo '  make server-clean      Remove database'
	@echo ''
	@echo '── POS Cloud Server (Django ASGI + Unfold Admin + Bolt Dashboard) ──'
	@echo '  make cloud-install     Install cloud server dependencies'
	@echo '  make cloud-run         Start daphne ASGI server (port 8082)'
	@echo '  make cloud-dev         Start with auto-reload'
	@echo '  make cloud-check       Validate Django imports'
	@echo '  make cloud-test        Run cloud test suite'
	@echo '  make cloud-clean       Remove cloud database'
	@echo ''
	@echo '── Publishing ──────────────────────────────────────────────'
	@echo '  make screenshots       Capture marketplace screenshots'
	@echo '  make publish           Prepare publish bundle'
	@echo ''
	@echo '── Direct edition access ───────────────────────────────────'
	@echo '  Delegated: make -C forge-pos <target>  (or formint-pos, pos-client)'
	@echo '  See per-edition Makefile for full target list.'
	@echo ''

clean:                ## Delete build artifacts
	@echo '── Cleaning build artifacts ──'
	rm -rf node_modules/ dist/ src-tauri/target/ src-tauri/gen/
	@echo '✓ Clean. Editions are canonical in forge-pos/ and formint-pos/.'

# ── POS Mini Edition ───────────────────────────────────────────────────
# Delegates to forge-pos/Makefile for all targets.

setup-mini:           ## Install mini edition dependencies
	$(MAKE) -C $(FORGE_POS) install

dev-mini:             ## Start mini Vite dev server (port 1420)
	$(MAKE) -C $(FORGE_POS) dev

dev-desktop-mini:     ## Start mini Tauri desktop app (hot-reload)
	$(MAKE) -C $(FORGE_POS) dev-desktop

build-mini:           ## Build mini desktop app
	$(MAKE) -C $(FORGE_POS) build

check-mini:           ## Full check (mini)
	$(MAKE) -C $(FORGE_POS) check

# ── POS Client Edition ──────────────────────────────────────────────────
# Delegates to pos-client/Makefile.

setup-client:         ## Install pos-client dependencies
	$(MAKE) -C $(POS_CLIENT) install

dev-client:           ## Start pos-client dev server
	$(MAKE) -C $(POS_CLIENT) dev

build-client:         ## Build pos-client desktop app
	$(MAKE) -C $(POS_CLIENT) build

# ── All Editions ───────────────────────────────────────────────────────────

dev-all:              ## Start all services (development)
	@echo '── Starting all services ──'
	@echo '  Starting formint env (backend :8767 + frontend :4321)...'
	$(MAKE) -C $(FORMINT_POS) env
	@echo '  Start other editions individually: make dev-mini | dev-client'

# ── POS Server (Merged Robyn sidecar — formint-pos/sidecar) ──────────────

server-install:               ## Install sidecar dependencies
	cd $(FORMINT_POS)/sidecar && pip install -r requirements.txt
	@echo '✓ Sidecar dependencies installed'

server-run:                   ## Start sidecar (port 8765)
	cd $(FORMINT_POS)/sidecar && python3 server.py --port 8765

server-dev:                   ## Start sidecar with hot reload
	cd $(FORMINT_POS)/sidecar && python3 server.py --port 8765 --dev --verbose

server-check:                 ## Validate sidecar imports
	cd $(FORMINT_POS)/sidecar && DJANGO_SETTINGS_MODULE='' python3 -c 'from server import app; print("✓ sidecar OK")'

server-test:                  ## Run merged sidecar test suite
	cd $(FORMINT_POS)/sidecar && DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/ -k 'not rust_db' --tb=short --no-header

server-clean:                 ## Clean sidecar data
	rm -f $(FORMINT_POS)/sidecar/restaurant.db
	@echo '✓ Database cleaned'

# ── POS Cloud Server (Django ASGI + Unfold Admin + Bolt Dashboard) ─────

cloud-install:        ## Install cloud server dependencies
	pip install channels daphne django-unfold django-bolt django-fusion django-filter djangorestframework msgspec
	cd $(POS_CLOUD) && python3 manage.py migrate
	@echo '✓ POS Cloud server dependencies installed'

cloud-run:            ## Start daphne ASGI server (port 8082)
	cd $(POS_CLOUD) && daphne configs.asgi:application --port 8082 --bind 0.0.0.0

cloud-dev:            ## Start daphne with auto-reload
	cd $(POS_CLOUD) && daphne configs.asgi:application --port 8082 --bind 0.0.0.0 --reload

cloud-check:          ## Validate Django imports
	cd $(POS_CLOUD) && python3 -c 'import os; os.environ.setdefault("DJANGO_SETTINGS_MODULE","configs"); import django; django.setup(); from core.models import Organization, Branch, BranchProduct; from core.sync_api import sync_receive_products, _broadcast_sync_event; from core.consumers import SyncEventConsumer; print("✓ POS Cloud imports OK")'

cloud-test:           ## Run cloud test suite
	cd $(POS_CLOUD) && python3 -m pytest tests/ -v --tb=short || echo 'Tests not found or failed'

cloud-clean:          ## Remove cloud database and bytecode cache
	rm -f $(POS_CLOUD)/pos_cloud.db
	find $(POS_CLOUD) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find $(POS_CLOUD) -name '*.pyc' -delete 2>/dev/null || true
	@echo '✓ Cloud database and cache cleaned'

# ── Formint POS (merged package: pos-full + pos-solo) ────────────────────

formint-install:      ## Install formint-pos (backend .venv + frontend npm + migrate)
	$(MAKE) -C $(FORMINT_POS) install

formint-run:          ## Run formint-pos backend (API + admin on :8767)
	$(MAKE) -C $(FORMINT_POS) dev-backend

formint-env:          ## Run full formint env (backend :8767 + frontend :4321 in tmux)
	$(MAKE) -C $(FORMINT_POS) env

formint-stop:         ## Stop the formint tmux env
	$(MAKE) -C $(FORMINT_POS) stop

formint-test:         ## Run formint-pos tests (backend + js contract)
	$(MAKE) -C $(FORMINT_POS) test

formint-check:        ## Validate formint-pos (django check + astro check)
	$(MAKE) -C $(FORMINT_POS) check

formint-sidecar-test: ## Run merged Robyn sidecar suite (formint-pos/sidecar)
	cd $(FORMINT_POS)/sidecar && DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/ -k 'not rust_db' --tb=short --no-header

formint-clean:        ## Clean formint-pos artifacts (db + staticfiles + node_modules)
	$(MAKE) -C $(FORMINT_POS) clean


# ── Publishing ────────────────────────────────────────────────────────────

screenshots:          ## Capture 6 marketplace screenshots
	$(MAKE) -C $(FORMINT_POS) screenshots

publish:              ## Prepare publish bundle from formint-pos
	@echo '── Preparing publish bundle ──'
	@mkdir -p publish-bundle
	@rsync -a --exclude='node_modules' --exclude='.git' --exclude='src-tauri/target' \
		--exclude='src-tauri/gen' --exclude='dist' --exclude='legacy-react' \
		--exclude='sidecar/.venv' $(FORMINT_POS)/ publish-bundle/
	@cp PUBLISH.md publish-bundle/
	@echo '✓ Bundle ready at publish-bundle/'
	@du -sh publish-bundle/
