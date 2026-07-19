# ============================================================================
# POS — Root Makefile (v1.4)
# ============================================================================
# Orchestrates 3 POS editions + Cloud CRM server + Django Portals:
#   - pos-minimal : Core POS app + Portal (node only)
#   - pos-solo    : Core + sidecar + Portal (node + server + cloud sync)
#   - pos-full    : Core + sidecar + Portal (server + cloud CRM master)
#   - cloud       : Django-based cloud CRM server (pos-full/portal/cloud/)
#
# Quick start:
#   make              — print this menu
#   make clean        — delete all editions (regenerate with make editions)
#   make editions     — generate all editions from pos-full source
#   make setup-XXXX   — install dependencies for a specific edition
#   make build-XXXX   — build a specific edition
#   make portal-XXXX  — manage Django portals
#   make cloud-XXXX   — manage cloud CRM server

.PHONY: help
.PHONY: clean editions
.PHONY: setup-minimal setup-solo setup-full
.PHONY: build-minimal build-solo build-full
.PHONY: dev-minimal dev-solo dev-full
.PHONY: check-minimal check-solo check-full
.PHONY: portal-setup portal-migrate portal-dev portal-seed portal-node
.PHONY: cloud-setup cloud-dev cloud-check cloud-clean
.PHONY: screenshots publish

EDITION ?= full

# ── Default ────────────────────────────────────────────────────────────────

help:                 ## Show this help menu
	@echo ''
	@echo '╔══════════════════════════════════════════════════════════╗'
	@echo '║  POS v1.4 — 3 Edition System + Cloud CRM + Portals     ║'
	@echo '╚══════════════════════════════════════════════════════════╝'
	@echo ''
	@echo '── Editions ────────────────────────────────────────────────'
	@echo '  make editions          Generate all editions from source'
	@echo '  make clean             Delete all editions + build artifacts'
	@echo ''
	@echo '── Minimal Edition (no sidecar) ────────────────────────────'
	@echo '  make setup-minimal     Install dependencies'
	@echo '  make dev-minimal       Start Vite dev server'
	@echo '  make build-minimal     Build desktop app'
	@echo '  make check-minimal     TypeScript + Rust check'
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
	@echo '── Django Portals (EDITION=solo|minimal|full) ──────────────'
	@echo '  make portal-setup      Install portal deps + migrate'
	@echo '  make portal-dev        Start portal dev server'
	@echo '  make portal-seed       Seed sample menu data'
	@echo '  make portal-node       Run node agent (solo/minimal)'
	@echo '  Examples:'
	@echo '    make portal-dev EDITION=solo     # Solo portal on :8080'
	@echo '    make portal-dev EDITION=minimal  # Minimal portal on :8081'
	@echo '    make portal-dev EDITION=full     # Full portal on :8082'
	@echo ''
	@echo '── POS Client (Tauri + Vue 3) ──────────────────────────────'
	@echo '  make client-setup      Install pos-client dependencies'
	@echo '  make client-dev        Start pos-client dev server'
	@echo '  make client-build      Build pos-client desktop app'
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
	@echo '  → pos-minimal  (from pos-solo, removing sidecar)'
	@rm -rf pos-minimal
	@cp -a pos-solo pos-minimal
	@rm -rf pos-minimal/sidecar/
	@rm -f pos-minimal/src/api/sidecar.ts pos-minimal/src/api/chat.ts \
		pos-minimal/src/api/data.ts pos-minimal/src/api/tickets.ts
	@rm -f pos-minimal/src/components/ChatSupport.tsx
	@rm -f pos-minimal/src/pages/InvoicePage.tsx pos-minimal/src/pages/SupportChat.tsx
	@rm -f pos-minimal/src/utils/invoicePdf.ts
	@rm -f pos-minimal/src-tauri/src/operations/sidecar.rs
	@rm -f pos-minimal/src-tauri/templates/invoice.html
	@rm -rf pos-minimal/docs/server/ pos-minimal/docs/back-env/
	@rm -f pos-minimal/scripts/dev/build-sidecar.cjs
	@echo ''
	@echo '✓ 3 editions generated:'
	@du -sh pos-minimal pos-solo pos-full
	@echo ''

clean:                ## Delete all editions + build artifacts
	@echo '── Cleaning editions ──'
	rm -rf pos-minimal/ pos-solo/ pos-full/
	rm -rf node_modules/ dist/ src-tauri/target/ src-tauri/gen/
	@echo '✓ Clean. Run `make editions` to regenerate.'

# ── Minimal Edition ───────────────────────────────────────────────────────

setup-minimal:        ## Install minimal edition dependencies
	cd pos-minimal && pnpm install && cd src-tauri && cargo fetch

dev-minimal:          ## Start minimal Vite dev server
	cd pos-minimal && pnpm dev

build-minimal:        ## Build minimal desktop app
	cd pos-minimal && pnpm build:desktop

check-minimal:        ## TypeScript + Rust check (minimal)
	cd pos-minimal && pnpm tsc --noEmit && cd src-tauri && cargo check

# ── Solo Edition ──────────────────────────────────────────────────────────

setup-solo:           ## Install solo edition dependencies
	cd pos-solo && pnpm install && cd src-tauri && cargo fetch && \
	cd ../sidecar && pip install -r requirements.txt

dev-solo:             ## Start solo dev (Vite + sidecar + sync)
	cd pos-solo && python3 sidecar/server.py & pnpm dev

build-solo:           ## Build solo desktop app + sidecar
	cd pos-solo && pnpm build:desktop && pnpm build:sidecar

check-solo:           ## Full check (solo)
	cd pos-solo && pnpm tsc --noEmit && cd src-tauri && cargo check && \
	cd ../sidecar && python3 -c 'import server; print("sidecar OK")' && \
	python3 -c 'import sync_routes; print("sync OK")'

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

# ── Django Portals (now inside sidecar/) ──────────────────────────────────

portal-setup:         ## Install portal dependencies + run migrations
	@echo '── Setting up $(EDITION) portal ──'
	cd pos-$(EDITION)/sidecar && pip install -r requirements.txt && python3 manage.py migrate
	@echo '✓ $(EDITION) portal ready'

portal-dev:           ## Start portal dev server (default port per edition)
	@echo '── Starting $(EDITION) portal ──'
	@PORT=8080; \
	if [ "$(EDITION)" = "minimal" ]; then PORT=8081; fi; \
	if [ "$(EDITION)" = "full" ]; then PORT=8082; fi; \
	cd pos-$(EDITION)/sidecar && python3 manage.py runserver 0.0.0.0:$$PORT

portal-seed:          ## Seed sample menu data
	@echo '── Seeding $(EDITION) portal ──'
	cd pos-$(EDITION)/sidecar && python3 manage.py seed_menu

portal-node:          ## Run node agent (solo/minimal only)
	@echo '── Starting node agent for $(EDITION) portal ──'
	cd pos-$(EDITION)/sidecar && python3 manage.py run_node --master http://localhost:8080 --interval 60

# ── Cloud CRM Server (pos-full/sidecar/cloud/) ───────────────────────────

cloud-setup:          ## Install cloud CRM server dependencies
	cd pos-full/sidecar && pip install -r requirements.txt
	@echo '✓ Cloud server dependencies installed'

cloud-dev:            ## Start cloud CRM server (port 8082)
	@echo '── Starting Cloud CRM Server on port 8082 ──'
	cd pos-full/sidecar && python3 manage.py runserver 0.0.0.0:8082

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
	@cd pos-full/sidecar && python3 manage.py runserver 0.0.0.0:8082 &
	@sleep 1
	@cd pos-full/sidecar && python3 server.py --port 8765 --db ../restaurant.db &
	@sleep 1
	cd pos-full && pnpm dev
	@echo 'All services started. Press Ctrl+C to stop.'

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
