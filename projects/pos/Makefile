# ============================================================================
# POS — Root Makefile (v2.1)
# ============================================================================
# Orchestrates 4 POS editions + Cloud CRM server + Django Portals:
#   - pos-mini    : Minimal Tauri + Rust/Diesel — local CRUD, no sidecar
#   - pos-solo    : Core + sidecar + Portal (node + server + cloud sync)
#   - pos-full    : Core + sidecar + Portal (server + cloud CRM master)
#   - pos-client  : Vue 3 + Tauri desktop app (separate client)
#   - cloud       : Django-based cloud CRM server (pos-full/portal/cloud/)
#
# Design: Delegates to per-edition Makefiles via $(MAKE) -C.
# This ensures each edition owns its own targets and the root Makefile
# stays a thin dispatcher with aggregated convenience targets.
#
# Quick start:
#   make editions              — generate all editions from pos-full source
#   make setup-{mini,solo,full,client}  — install dependencies for an edition
#   make dev-{mini,solo,full}          — start Vite dev server for an edition
#   make build-{mini,solo,full}        — build desktop app for an edition

.PHONY: help
.PHONY: clean editions
.PHONY: setup-mini setup-solo setup-full setup-client
.PHONY: dev-mini dev-solo dev-full dev-all
.PHONY: build-mini build-solo build-full build-client
.PHONY: check-mini check-solo check-full
.PHONY: server-install server-run server-dev server-check server-test server-clean
.PHONY: server-full-install server-full-run server-full-dev server-full-check server-full-test server-full-clean
.PHONY: screenshots publish

# ── Edition directories ────────────────────────────────────────────────────
# Used for delegation targets below.
POS_MINI  := pos-mini
POS_SOLO  := pos-solo
POS_FULL  := pos-full
POS_CLIENT := pos-client

# ── Default ────────────────────────────────────────────────────────────────

help:                 ## Show this help menu
	@echo ''
	@echo '╔══════════════════════════════════════════════════════════╗'
	@echo '║  POS v2.1 — Mini + Solo + Full + Client Editions    ║'
	@echo '╚══════════════════════════════════════════════════════════╝'
	@echo ''
	@echo '── Editions ────────────────────────────────────────────────'
	@echo '  make editions          Generate all editions from source'
	@echo '  make clean             Delete all editions + build artifacts'
	@echo ''
	@echo '── POS Mini (Minimal Tauri + Rust/Diesel) ──────────────────'
	@echo '  make setup-mini        Install dependencies (pnpm + cargo)'
	@echo '  make dev-mini          Start Vite dev server (port 1420)'
	@echo '  make build-mini        Build desktop app (production)'
	@echo '  make check-mini        TypeScript + Rust compilation check'
	@echo ''
	@echo '── POS Solo (Branch device + sidecar + cloud sync) ─────────'
	@echo '  make setup-solo        Install dependencies'
	@echo '  make dev-solo          Start Vite + sidecar dev'
	@echo '  make build-solo        Build desktop app + sidecar'
	@echo '  make check-solo        Full type check'
	@echo ''
	@echo '── POS Full (Master manager + sidecar + Django admin) ──────'
	@echo '  make setup-full        Install dependencies'
	@echo '  make dev-full          Start full stack'
	@echo '  make build-full        Build everything'
	@echo '  make check-full        Full validation'
	@echo ''
	@echo '── POS Client (Vue 3 + Tauri desktop) ───────────────────────'
	@echo '  make setup-client      Install dependencies (pnpm + cargo)'
	@echo '  make dev-client        Start Vite dev server'
	@echo '  make build-client      Build frontend for production'
	@echo ''
	@echo '── All Editions ─────────────────────────────────────────────'
	@echo '  make dev-all           Start all dev servers concurrently'
	@echo ''
	@echo '── POS Server (Consolidated Robyn + Django ORM) ────────────'
	@echo '  make server-install    Install dependencies'
	@echo '  make server-run        Start server (port 8765)'
	@echo '  make server-dev        Dev mode with hot reload'
	@echo '  make server-check      Validate imports'
	@echo '  make server-test       Run 155-test suite'
	@echo '  make server-clean      Remove database'
	@echo ''
	@echo '── POS Full Server (Cloud Master) ───────────────────────────'
	@echo '  make server-full-install    Install dependencies'
	@echo '  make server-full-run        Start server (port 8766)'
	@echo '  make server-full-dev        Dev mode'
	@echo '  make server-full-check      Validate imports'
	@echo '  make server-full-test       Run 45-test suite'
	@echo '  make server-full-clean      Remove database'
	@echo ''
	@echo '── Publishing ──────────────────────────────────────────────'
	@echo '  make screenshots       Capture marketplace screenshots'
	@echo '  make publish           Prepare publish bundle'
	@echo ''
	@echo '── Direct edition access ───────────────────────────────────'
	@echo '  Delegated: make -C pos-mini <target>  (or pos-solo, pos-full, pos-client)'
	@echo '  See per-edition Makefile for full target list.'
	@echo ''

# ── Editions generation ───────────────────────────────────────────────────

editions:             ## Generate all editions (canonical source: pos-full/)
	@echo '── Generating editions ──'
	@if [ ! -d pos-full ]; then echo 'ERROR: pos-full/ not found — editions ship in the repo.'; exit 1; fi
	@echo '  → pos-solo (from pos-full, removing Django models, preserving sync files)'
	@if [ -d pos-solo ]; then \
		echo '  └─ Preserving pos-solo (canonical source — sync files not overwritten)'; \
	else \
		cp -a pos-full pos-solo; \
		rm -rf pos-solo/sidecar/posapp/; \
		echo '  └─ pos-solo created from pos-full (no sync files — cp from pos-solo-backup if available)'; \
	fi
	@echo ''
	@echo '✓ 2 editions generated:'
	@du -sh pos-solo pos-full
	@echo ''

clean:                ## Delete all editions + build artifacts
	@echo '── Cleaning editions ──'
	rm -rf pos-solo/ pos-full/
	rm -rf node_modules/ dist/ src-tauri/target/ src-tauri/gen/
	@echo '✓ Clean. Run `make editions` to regenerate.'

# ── POS Mini Edition ───────────────────────────────────────────────────
# Delegates to pos-mini/Makefile for all targets.

setup-mini:           ## Install mini edition dependencies
	$(MAKE) -C $(POS_MINI) install

dev-mini:             ## Start mini Vite dev server (port 1420)
	$(MAKE) -C $(POS_MINI) dev

build-mini:           ## Build mini desktop app
	$(MAKE) -C $(POS_MINI) build

check-mini:           ## Full check (mini)
	$(MAKE) -C $(POS_MINI) check

# ── Solo Edition ──────────────────────────────────────────────────────────
# Delegates to pos-solo/Makefile for frontend/Rust targets.
# Sidecar/server targets are handled directly for edition-specific paths.

setup-solo:           ## Install solo edition dependencies
	$(MAKE) -C $(POS_SOLO) install
	@cd $(POS_SOLO)/sidecar && pip install -r requirements.txt

dev-solo:             ## Start solo dev (Vite + sidecar)
	cd $(POS_SOLO) && python3 sidecar/server.py & $(MAKE) -C $(POS_SOLO) dev

build-solo:           ## Build solo desktop app + sidecar
	$(MAKE) -C $(POS_SOLO) build
	$(MAKE) -C $(POS_SOLO) build-sidecar

check-solo:           ## Full check (solo)
	$(MAKE) -C $(POS_SOLO) check
	@cd $(POS_SOLO)/sidecar && python3 -c 'from server import app; print("✓ POS server")' && \
	python3 -c 'from unified_models import Node; print("✓ models OK")'

# ── Full Edition ──────────────────────────────────────────────────────────
# Delegates to pos-full/Makefile for frontend/Rust targets.
# Admin and server targets handled directly.

setup-full:           ## Install full edition dependencies
	$(MAKE) -C $(POS_FULL) install
	cd $(POS_FULL)/sidecar && pip install -r requirements.txt && \
	python3 -c 'import django; print("Django OK")'

dev-full:             ## Start full stack (Vite + sidecar)
	cd $(POS_FULL) && python3 sidecar/server.py & $(MAKE) -C $(POS_FULL) dev

build-full:           ## Build full edition (everything)
	$(MAKE) -C $(POS_FULL) build
	$(MAKE) -C $(POS_FULL) build-sidecar

check-full:           ## Full validation
	$(MAKE) -C $(POS_FULL) check
	@cd $(POS_FULL)/sidecar && python3 -c 'import server; print("sidecar OK")' && \
	python3 -c 'import django; import os; os.environ.setdefault("DJANGO_SETTINGS_MODULE","posapp.apps"); print("Django OK")'

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
	@echo '  Starting sidecar on :8765, Vite dev servers on :1420'
	@echo '  Press Ctrl+C to stop.'
	@sleep 1
	@echo '  Starting POS Full sidecar...'
	@cd $(POS_FULL)/sidecar && python3 server.py --port 8765 &
	@sleep 1
	@echo '  Starting POS Full Vite dev server...'
	@cd $(POS_FULL) && pnpm dev
	@echo '  Start other editions individually: make dev-{mini|solo|client}'

# ── POS Server (Robyn + Django ORM) ────────────────────────────────
# Consolidated server in pos-solo/sidecar/server.py.
# These are edition-specific and stay as direct commands.

server-install:               ## Install POS server dependencies
	cd $(POS_SOLO)/sidecar && pip install -r requirements.txt && pip install robyn httpx asgiref
	@echo '✓ POS server dependencies installed'

server-run:                   ## Start POS server (port 8765)
	cd $(POS_SOLO)/sidecar && python3 server.py --port 8765

server-dev:                   ## Start POS server with hot reload
	cd $(POS_SOLO)/sidecar && python3 server.py --port 8765 --dev --verbose

server-check:                 ## Validate POS server imports
	cd $(POS_SOLO)/sidecar && python3 -c 'from unified_models import *; print("✓ unified_models OK"); from server import app; print("✓ server OK")'

server-test:                  ## Run unified test suite (155 tests)
	DJANGO_SETTINGS_MODULE='' python3 -m pytest $(POS_SOLO)/sidecar/tests/test_unified_api.py -v --tb=short --import-mode=importlib

server-clean:                 ## Clean POS server data
	rm -f $(POS_SOLO)/restaurant.db
	@echo '✓ Database cleaned'

server-full-install:              ## Install POS Full server dependencies
	cd $(POS_FULL)/sidecar && pip install -r requirements.txt && pip install robyn httpx asgiref
	@echo '✓ POS Full server dependencies installed'

server-full-run:                  ## Start POS Full server (port 8766)
	cd $(POS_FULL)/sidecar && python3 server.py --port 8766

server-full-dev:                  ## Start POS Full server with verbose output
	cd $(POS_FULL)/sidecar && python3 server.py --port 8766 --verbose

server-full-check:                ## Validate POS Full server imports
	cd $(POS_FULL)/sidecar && DJANGO_SETTINGS_MODULE='' python3 -c 'from server import app; print("✓ POS Full server OK")'

server-full-test:                 ## Run POS Full test suite (45 tests)
	DJANGO_SETTINGS_MODULE='' python3 -m pytest $(POS_FULL)/sidecar/tests/test_server.py -v --tb=short --import-mode=importlib

server-full-clean:                ## Clean POS Full server data
	rm -f $(POS_FULL)/sidecar/full_portal.db
	@echo '✓ Database cleaned'

# ── Publishing ────────────────────────────────────────────────────────────

screenshots:          ## Capture 6 marketplace screenshots
	@if [ ! -d pos-full ]; then echo 'ERROR: pos-full/ not found.'; exit 1; fi
	$(MAKE) -C $(POS_FULL) screenshots

publish:              ## Prepare publish bundle from full edition
	@echo '── Preparing publish bundle ──'
	@mkdir -p publish-bundle
	@rsync -a --exclude='node_modules' --exclude='.git' --exclude='src-tauri/target' \
		--exclude='src-tauri/gen' --exclude='dist' pos-full/ publish-bundle/
	@cp PUBLISH.md publish-bundle/
	@echo '✓ Bundle ready at publish-bundle/'
	@du -sh publish-bundle/
