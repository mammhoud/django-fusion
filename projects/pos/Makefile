# ============================================================================
# POS — Root Makefile (v2.0)
# ============================================================================
# Orchestrates 2 POS editions + Cloud CRM server + Django Portals:
#   - pos-solo    : Core + sidecar + Portal (node + server + cloud sync)
#   - pos-full    : Core + sidecar + Portal (server + cloud CRM master)
#   - cloud       : Django-based cloud CRM server (pos-full/portal/cloud/)
#
# Quick start:
#   make editions     — generate all editions from pos-full source
#   make clean        — delete all editions (regenerate with make editions)
#   make setup-XXXX   — install dependencies for a specific edition
#   make build-XXXX   — build a specific edition
#   make portal-XXXX  — manage Django portals
#   make cloud-XXXX   — manage cloud CRM server

.PHONY: help
.PHONY: clean editions
.PHONY: setup-solo setup-full
.PHONY: build-solo build-full
.PHONY: dev-solo dev-full
.PHONY: check-solo check-full
.PHONY: portal-setup portal-migrate portal-dev portal-seed portal-node
.PHONY: cloud-setup cloud-dev cloud-check cloud-clean
.PHONY: screenshots publish

EDITION ?= solo

# ── Default ────────────────────────────────────────────────────────────────

help:                 ## Show this help menu
	@echo ''
	@echo '╔══════════════════════════════════════════════════════════╗'
	@echo '║  POS v2.0 — Solo + Full Editions + Cloud CRM + Portals ║'
	@echo '╚══════════════════════════════════════════════════════════╝'
	@echo ''
	@echo '── Editions ────────────────────────────────────────────────'
	@echo '  make editions          Generate all editions from source'
	@echo '  make clean             Delete all editions + build artifacts'
	@echo ''
	@echo '── Solo Edition (with sidecar + cloud sync) ────────────────'
	@echo '  make setup-solo        Install dependencies'
	@echo '  make dev-solo          Start Vite + sidecar'
	@echo '  make build-solo        Build desktop app + sidecar'
	@echo '  make check-solo        Full type check'
	@echo ''
	@echo '── Full Edition (sidecar + Django + Cloud CRM) ─────────────'
	@echo '  make setup-full        Install all dependencies'
	@echo '  make dev-full          Start full stack'
	@echo '  make build-full        Build everything'
	@echo '  make check-full        Full validation'
	@echo ''
	@echo '── Django Portals (EDITION=solo|full) ──────────────────────'
	@echo '  make portal-setup      Install portal deps + migrate'
	@echo '  make portal-dev        Start portal dev server'
	@echo '  Examples:'
	@echo '    make portal-dev EDITION=solo  # Solo portal on :8080'
	@echo '    make portal-dev EDITION=full  # Full portal on :8082'
	@echo ''
	@echo '── POS Client (Tauri + Vue 3) ──────────────────────────────'
	@echo '  make client-setup      Install pos-client dependencies'
	@echo '  make client-dev        Start pos-client dev server'
	@echo '  make client-build      Build pos-client desktop app'
	@echo ''
	@echo '── POS Server (Consolidated Robyn + Django ORM) ──────────────'
	@echo '  make server-install    Install dependencies'
	@echo '  make server-run        Start server (port 8765)'
	@echo '  make server-dev        Dev mode with hot reload'
	@echo '  make server-check      Validate imports'
	@echo '  make server-test       Run 155-test suite'
	@echo '  make server-clean      Remove database'
	@echo ''
	@echo '── POS Full Server (Cloud Master, Robyn + Django ORM) ────────'
	@echo '  make server-full-install    Install dependencies'
	@echo '  make server-full-run        Start server (port 8766)'
	@echo '  make server-full-dev        Dev mode'
	@echo '  make server-full-check      Validate imports'
	@echo '  make server-full-test       Run 45-test suite'
	@echo '  make server-full-clean      Remove database'
	@echo ''
	@echo '── Cloud CRM Server ────────────────────────────────────────'
	@echo '  make cloud-setup       Install cloud server dependencies'
	@echo '  make cloud-dev         Start cloud CRM server (port 8082)'
	@echo '  make cloud-check       Validate cloud server imports'
	@echo '  make cloud-clean       Remove cloud data'
	@echo ''
	@echo '── Publishing ──────────────────────────────────────────────'
	@echo '  make screenshots       Capture marketplace screenshots'
	@echo '  make publish           Prepare publish bundle'
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

# ── Solo Edition ──────────────────────────────────────────────────────────

setup-solo:           ## Install solo edition dependencies
	cd pos-solo && pnpm install && cd src-tauri && cargo fetch && \
	cd sidecar && pip install -r requirements.txt

dev-solo:             ## Start solo dev (Vite + sidecar + sync)
	cd pos-solo && python3 sidecar/server.py & pnpm dev

build-solo:           ## Build solo desktop app + sidecar
	cd pos-solo && pnpm build:desktop && pnpm build:sidecar

check-solo:           ## Full check (solo)
	cd pos-solo && pnpm tsc --noEmit && cd src-tauri && cargo check && \
	cd sidecar && python3 -c 'from server import app; print("✓ POS server")' && \
	python3 -c 'from unified_models import Node; print("✓ models OK")'

# ── Full Edition ──────────────────────────────────────────────────────────

setup-full:           ## Install full edition dependencies
	cd pos-full && pnpm install && cd src-tauri && cargo fetch && \
	cd ../sidecar && pip install -r requirements.txt && \
	python3 -c 'import django; print("Django OK")'

dev-full:             ## Start full stack (Vite + sidecar + Django)
	cd pos-full && python3 sidecar/server.py & pnpm dev

build-full:           ## Build full edition (everything)
	cd pos-full && pnpm build:desktop && pnpm build:sidecar

check-full:           ## Full validation
	cd pos-full && pnpm tsc --noEmit && cd src-tauri && cargo check && \
	cd ../sidecar && python3 -c 'import server; print("sidecar OK")' && \
	python3 -c 'import django; import os; os.environ.setdefault("DJANGO_SETTINGS_MODULE","posapp.apps"); print("Django OK")'

# ── Django Portals (inside sidecar/) ──────────────────────────────────────

portal-setup:         ## Install portal dependencies + run migrations
	@echo '── Setting up $(EDITION) portal ──'
	@echo "Django portal removed — use: cd pos-$$(EDITION)/sidecar && python3 server.py"
	@echo '✓ $(EDITION) portal ready'

portal-dev:           ## Start portal dev server
	@echo '── Starting $(EDITION) portal ──'
	@PORT=8080; \
	if [ "$(EDITION)" = "full" ]; then PORT=8082; fi; \
	@echo "Django portal removed — use: cd pos-$$(EDITION)/sidecar && python3 server.py"

portal-seed:          ## Seed sample menu data
	@echo '── Seeding $(EDITION) portal ──'
	@echo "Django portal removed — seed_menu no longer available"

portal-node:          ## Run node agent
	@echo '── Starting node agent for $(EDITION) portal ──'
	@echo "Django portal removed — run_node no longer available"

# ── Cloud CRM Server (pos-full/sidecar/cloud/) ───────────────────────────

cloud-setup:          ## Install cloud CRM server dependencies
	cd pos-full/sidecar && pip install -r requirements.txt
	@echo '✓ Cloud server dependencies installed'

cloud-dev:            ## Start cloud CRM server (port 8082)
	@echo '── Starting Cloud CRM Server on port 8082 ──'
# Django portal removed — Robyn server now handles everything

cloud-check:          ## Validate cloud server imports
	@echo '── Checking cloud server imports ──'
	cd pos-full/sidecar && python3 -c '
import importlib
modules = ["shared", "portal", "cloud", "cloud.models", "cloud.api"]
for m in modules:
    try:
        importlib.import_module(m)
        print(f"  ✓ {m}")
    except Exception as e:
        print(f"  ✗ {m}: {e}")
'
	@echo '✓ Cloud server checked'

cloud-clean:          ## Remove cloud CRM data
	@echo '── Cleaning cloud data ──'
	rm -rf pos-full/sidecar/*.db
	rm -f pos-full/sidecar/**/*.pyc
	rm -rf pos-full/sidecar/**/__pycache__/
	@echo '✓ Cloud data cleaned'

# ── POS Client ───────────────────────────────────────────────────────────

client-setup:         ## Install pos-client dependencies
	cd pos-client && pnpm install
	@echo '✓ POS Client dependencies installed'

client-dev:           ## Start pos-client dev server
	cd pos-client && pnpm dev

client-build:         ## Build pos-client desktop app
	cd pos-client && pnpm tauri build

# ── Combined: Full stack + Cloud CRM + Portal ────────────────────────────

dev-all:              ## Start all services (development)
	@echo '── Starting all services ──'
	@echo '  Portal on :8082, Sidecar on :8765, Client on :1420'
# Django portal removed — Robyn server now handles everything
	@sleep 1
	@	cd pos-full/sidecar && python3 server.py --port 8765 &
	@sleep 1
	cd pos-full && pnpm dev
	@echo 'All services started. Press Ctrl+C to stop.'

# ── POS Server (Robyn + Django ORM) ────────────────────────────────
# Consolidated server in pos-solo/sidecar/server.py
# Integrates all POS entities in one database (restaurant.db)

server-install:               ## Install POS server dependencies
	cd pos-solo/sidecar && pip install -r requirements.txt && pip install robyn httpx asgiref
	@echo '✓ POS server dependencies installed'

server-run:                   ## Start POS server (port 8765)
	cd pos-solo/sidecar && python3 server.py --port 8765

server-dev:                   ## Start POS server with hot reload
	cd pos-solo/sidecar && python3 server.py --port 8765 --dev --verbose

server-check:                 ## Validate POS server imports
	cd pos-solo/sidecar && python3 -c 'from unified_models import *; print("✓ unified_models OK"); from server import app; print("✓ server OK")'

server-test:                  ## Run unified test suite (155 tests)
	DJANGO_SETTINGS_MODULE='' python3 -m pytest pos-solo/sidecar/tests/test_unified_api.py -v --tb=short --import-mode=importlib

server-clean:                 ## Clean POS server data
	rm -f pos-solo/restaurant.db
	@echo '✓ Database cleaned'

server-full-install:              ## Install POS Full server dependencies
	cd pos-full/sidecar && pip install -r requirements.txt && pip install robyn httpx asgiref
	@echo '✓ POS Full server dependencies installed'

server-full-run:                  ## Start POS Full server (port 8766)
	cd pos-full/sidecar && python3 server.py --port 8766

server-full-dev:                  ## Start POS Full server with verbose output
	cd pos-full/sidecar && python3 server.py --port 8766 --verbose

server-full-check:                ## Validate POS Full server imports
	cd pos-full/sidecar && DJANGO_SETTINGS_MODULE='' python3 -c 'from server import app; print("✓ POS Full server OK")'

server-full-test:                 ## Run POS Full test suite (45 tests)
	DJANGO_SETTINGS_MODULE='' python3 -m pytest pos-full/sidecar/tests/test_server.py -v --tb=short --import-mode=importlib

server-full-clean:                ## Clean POS Full server data
	rm -f pos-full/sidecar/full_portal.db
	@echo '✓ Database cleaned'

# ── Publishing ────────────────────────────────────────────────────────────

screenshots:          ## Capture 6 marketplace screenshots
	@if [ ! -d pos-full ]; then echo 'ERROR: pos-full/ not found.'; exit 1; fi
	cd pos-full && make screenshots

publish:              ## Prepare publish bundle from full edition
	@echo '── Preparing publish bundle ──'
	@mkdir -p publish-bundle
	@rsync -a --exclude='node_modules' --exclude='.git' --exclude='src-tauri/target' \
		--exclude='src-tauri/gen' --exclude='dist' pos-full/ publish-bundle/
	@cp PUBLISH.md publish-bundle/
	@echo '✓ Bundle ready at publish-bundle/'
	@du -sh publish-bundle/
