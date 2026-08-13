# ============================================================================
# POS — Root Makefile (v4.0)
# ============================================================================
# Uniform dispatcher over the POS editions in projects/formints/:
#
#   - formint-community/ Community — free, offline-first Tauri + React 19 +
#                                 Rust/Diesel desktop POS (no sidecar)
#   - formint-pro/    Professional — merged package: Django Ninja backend +
#                                 Robyn sidecar + Astro frontend + Tauri
#   - formint-cloud/ Cloud   — Django Formint Cloud SaaS master (Unfold admin)
#                                 + Community UI frontend
#   - formint-standard/ Standard — Astro 5 + React 19 + Tauri 2 desktop POS
#   - formint-client/  pos-client   — Vue 3 + Tauri desktop client
#   - packages/formints-client  — @formints/client TS SDK (editions consume it)
#
# Every edition exposes the same uniform verbs through <edition>-<verb>:
#   install | check | test | run (dev/env) | stop | clean
# e.g. make community-test · make cloud-check · make sdk-test
#
# Quick start:
#   make community-dev        — Vite dev server for the Community edition (:1420)
#   make community-desktop    — full Tauri desktop app (Community)
#   make pro-env              — merged backend :8767 + frontend :4321 (tmux)
#   make cloud-dev-backend    — Cloud Django admin/API on :8082
#   make test-all             — run every edition's test suite
#   make community-bundle     — refresh the standalone community publish bundle
#
# Direct edition access is always possible: make -C formint-community <target>

.PHONY: help clean
.PHONY: install-all check-all test-all clean-all stop-all
# ── Community (formint-community) ──
.PHONY: community-install community-dev community-desktop community-build \
        community-check community-test community-test-all community-cargo-test \
        community-seed community-clean
# ── Standard (formint-standard) / Pro (formint-pro) ──
.PHONY: standard-install standard-check standard-test standard-env standard-run \
        standard-stop standard-clean pro-install pro-check pro-test pro-env \
        pro-stop pro-clean
# ── Cloud (formint-cloud) ──
.PHONY: cloud-install cloud-check cloud-test cloud-dev-backend cloud-dev-api \
        cloud-dev-frontend cloud-stop cloud-clean
# ── pos-client (formint-client) ──
.PHONY: client-install client-dev client-build client-lint client-test client-clean
# ── SDK (packages/formints-client) ──
.PHONY: sdk-install sdk-build sdk-typecheck sdk-test
.PHONY: test check
# ── Legacy aliases ──
.PHONY: mini-install mini-dev mini-build mini-check \
        formint-install formint-env formint-run formint-stop formint-test \
        formint-check formint-clean server-install server-run server-dev \
        server-check server-test server-clean cloud-run cloud-dev cloud-clean \
        screenshots publish community-bundle

# ── Edition directories (canonical) ─────────────────────────────────────────
COMMUNITY  := formint-community
MERGED     := formint-pro    # Professional merged package (Standard tier shares it)
CLOUD      := formint-cloud
CLIENT     := formint-client
SDK        := packages/formints-client
COMMUNITY_BUNDLE := publish/community-bundle  # generated standalone public repo copy

# ── Default ────────────────────────────────────────────────────────────────

help:                 ## Show this help menu
	@echo ''
	@echo '╔══════════════════════════════════════════════════════════╗'
	@echo '║  POS v4.0 — Community · Standard · Pro · Cloud · Client ║'
	@echo '╚══════════════════════════════════════════════════════════╝'
	@echo '── Editions (uniform verbs: install | check | test | run | stop | clean) ──'
  @echo '  Community (formint-community) — make community-{install,check,test,dev,clean}'
  @echo '  Standard (formint-standard)   — make standard-{install,check,test,env,stop,clean}'
  @echo '  Pro (formint-pro)       — make pro-{install,check,test,env,stop,clean}'
  @echo '  Cloud (formint-cloud)   — make cloud-{install,check,test,dev-backend,stop,clean}'
  @echo '  pos-client (formint-client)  — make client-{install,dev,build,lint,test,clean}'
	@echo '  SDK (@formints/client) — make sdk-{install,build,typecheck,test}'
	@echo ''
	@echo '── Aggregates ──────────────────────────────────────────────'
	@echo '  make install-all       Install every edition (run first on a fresh clone)'
	@echo '  make check-all         Run checks for every edition'
	@echo '  make test-all          Run every edition test suite (needs install-all first)'
	@echo '  make stop-all          Stop all running dev processes'
	@echo '  make clean-all         Clean every edition (also removes formint-community/ — run make community-bundle to regenerate)'
	@echo ''
	@echo '── Community quick start ───────────────────────────────────'
	@echo '  make community-dev        Vite dev server (:1420, browser only)'
	@echo '  make community-desktop    Full Tauri desktop app (hot-reload)'
	@echo '  make community-cargo-test Rust cargo test'
	@echo '  make community-test       Vitest unit tests'
	@echo '  make community-test-all   Vitest + Playwright e2e'
	@echo '  make community-seed       Reset + seed restaurant.db'
	@echo ''
	@echo '── Merged (Standard/Pro) quick start ──────────────────────'
	@echo '  make standard-env         Backend :8767 + frontend :4321 (tmux)'
	@echo '  make standard-test        Backend + frontend contract tests'
	@echo '  make server-test          Merged Robyn sidecar pytest suite'
	@echo ''
	@echo '── Cloud quick start ───────────────────────────────────────'
	@echo '  make cloud-dev-backend    Django :8082 (Unfold admin + bolt)'
	@echo '  make cloud-dev-api        Django :8767 (sidecar-compatible API)'
	@echo '  make cloud-dev-frontend   Astro :4323 (Community UI)'
	@echo '  make cloud-test           Backend Django test suite'
	@echo '── Community bundle (standalone public repo) ───────────────'
  @echo '  make community-bundle     Refresh publish/community-bundle/ from formint-community'
  @echo '  make community-version    Alias for community-bundle'
	@echo ''
	@echo '── Publishing ──────────────────────────────────────────────'
	@echo '  make screenshots          Capture marketplace screenshots'
	@echo '  make publish              Prepare publish bundle'
	@echo ''
	@echo '── Legacy aliases (kept for back-compat) ──────────────────'
	@echo '  make mini-*       → community-* · make formint-* → standard/pro (formint)'
	@echo '@echo '  make cloud-*      → cloud (formint-cloud) · make server-* → sidecar tests''
	@echo ''

# ── Aggregates ─────────────────────────────────────────────────────────────

install-all:          ## Install every edition
	$(MAKE) community-install
	$(MAKE) standard-install
	$(MAKE) cloud-install
	$(MAKE) client-install
	$(MAKE) sdk-install

check-all:            ## Run checks for every edition
	$(MAKE) community-check
	$(MAKE) standard-check
	$(MAKE) cloud-check
	$(MAKE) client-lint
	$(MAKE) sdk-typecheck

test-all:             ## Run every edition test suite
	$(MAKE) community-test
	$(MAKE) standard-test
	$(MAKE) cloud-test
	$(MAKE) client-test
	$(MAKE) sdk-test

stop-all:             ## Stop all running dev processes
	$(MAKE) -C $(MERGED) stop
	$(MAKE) -C $(CLOUD) stop

clean-all:            ## Clean every edition
	$(MAKE) -C $(COMMUNITY) clean
	$(MAKE) -C $(MERGED) clean
	$(MAKE) -C $(CLOUD) clean
	$(MAKE) -C $(CLIENT) clean
	rm -rf $(COMMUNITY_BUNDLE)
	@echo '✓ All editions cleaned'

test: test-all         ## Alias — run every edition test suite

check: check-all       ## Alias — run checks for every edition

clean: clean-all      ## Alias — clean every edition

# ── Community — formint-community ───────────────────────────────────────────

community-install:    ## Install Community dependencies (pnpm + cargo)
	$(MAKE) -C $(COMMUNITY) install

community-dev:        ## Vite dev server (:1420, browser only)
	$(MAKE) -C $(COMMUNITY) dev

community-desktop:    ## Full Tauri desktop app (hot-reload)
	$(MAKE) -C $(COMMUNITY) dev-desktop

community-build:      ## Build Community desktop app
	$(MAKE) -C $(COMMUNITY) build

community-check:      ## TypeScript + Rust compilation check
	$(MAKE) -C $(COMMUNITY) check

community-test:       ## Vitest unit tests
	$(MAKE) -C $(COMMUNITY) test

community-test-all:   ## Vitest + Playwright e2e
	$(MAKE) -C $(COMMUNITY) test-all

community-cargo-test: ## Rust cargo test
	$(MAKE) -C $(COMMUNITY) cargo-test

community-seed:       ## Reset DB + apply preset (PRESET=all|base|gaming|coffee)
	$(MAKE) -C $(COMMUNITY) seed

community-clean:      ## Clean Community build artifacts
	$(MAKE) -C $(COMMUNITY) clean

# ── Standard — formint-standard (standalone Tauri + React edition) ────────────

standard-install: ## Install Standard edition (pnpm + cargo)
	$(MAKE) -C formint-standard install

standard-check:   ## TypeScript + Rust compilation check
	$(MAKE) -C formint-standard check

standard-test:    ## Vitest unit tests
	$(MAKE) -C formint-standard test

standard-dev:     ## Vite dev server (browser only)
	$(MAKE) -C formint-standard dev

standard-clean:   ## Clean Standard build artifacts
	$(MAKE) -C formint-standard clean

# ── Pro — formint-pro (merged package) ───────────────────────────────────────

pro-install:      ## Install merged package (backend + frontend + migrate)
	$(MAKE) -C $(MERGED) install

pro-check:        ## Django check + astro check
	$(MAKE) -C $(MERGED) check

pro-test:         ## Backend suite + frontend contract tests
	$(MAKE) -C $(MERGED) test

pro-env:          ## Backend :8767 + frontend :4321 (tmux)
	$(MAKE) -C $(MERGED) env

pro-run:          ## Backend runserver :8767 (foreground)
	$(MAKE) -C $(MERGED) dev-backend

pro-stop:         ## Stop merged tmux env
	$(MAKE) -C $(MERGED) stop

pro-clean:        ## Clean merged artifacts
	$(MAKE) -C $(MERGED) clean

# ── Cloud — formint-cloud ───────────────────────────────────────────────────────

cloud-install:        ## Install Cloud backend venv + frontend deps
	$(MAKE) -C $(CLOUD) install

cloud-check:          ## Django check + astro check
	$(MAKE) -C $(CLOUD) check

cloud-test:           ## Cloud backend Django test suite
	$(MAKE) -C $(CLOUD) test

cloud-dev-backend:    ## Django :8082 (Unfold admin + bolt)
	$(MAKE) -C $(CLOUD) dev-backend

cloud-dev-api:        ## Django :8767 (sidecar-compatible API)
	$(MAKE) -C $(CLOUD) dev-api

cloud-dev-frontend:   ## Astro :4323 (Community UI)
	$(MAKE) -C $(CLOUD) dev-frontend

cloud-stop:           ## Kill Cloud dev processes
	$(MAKE) -C $(CLOUD) stop

cloud-clean:          ## Remove Cloud db + bytecode cache
	$(MAKE) -C $(CLOUD) clean

# ── pos-client — formint-client ────────────────────────────────────────────

client-install:       ## Install pos-client dependencies
	$(MAKE) -C $(CLIENT) install

client-dev:           ## Start pos-client Vite dev server
	$(MAKE) -C $(CLIENT) dev

client-build:         ## Build pos-client for production
	$(MAKE) -C $(CLIENT) build

client-lint:          ## Lint pos-client (oxlint)
	$(MAKE) -C $(CLIENT) lint

client-test:          ## Test pos-client (lint + vue-tsc typecheck)
	$(MAKE) -C $(CLIENT) test

client-clean:         ## Clean pos-client artifacts
	$(MAKE) -C $(CLIENT) clean

# ── SDK — packages/formints-client ─────────────────────────────────────────

sdk-install:          ## Install @formints/client deps
	cd $(SDK) && pnpm install

sdk-build:            ## Build the SDK (tsc)
	cd $(SDK) && pnpm build

sdk-typecheck:        ## Typecheck the SDK
	cd $(SDK) && pnpm typecheck

sdk-test:             ## Run SDK vitest suite
	cd $(SDK) && pnpm test

# ── Community version (standalone public repo) ─────────────────────────────

community-bundle community-version: ## Refresh the standalone community bundle from formint-community
	node scripts/publish/community-bundle.cjs

# ── Sidecar server (merged formint/sidecar) ────────────────────────────────

server-install:       ## Install merged sidecar dependencies
	cd $(MERGED)/sidecar && pip install -r requirements.txt
	@echo '✓ Sidecar dependencies installed'

server-run:           ## Start sidecar (port 8765)
	cd $(MERGED)/sidecar && python3 server.py --port 8765

server-dev:           ## Start sidecar with hot reload
	cd $(MERGED)/sidecar && python3 server.py --port 8765 --dev --verbose

server-check:         ## Validate sidecar imports
	cd $(MERGED)/sidecar && DJANGO_SETTINGS_MODULE='' python3 -c 'from server import app; print("✓ sidecar OK")'

server-test:          ## Run merged sidecar test suite
	cd $(MERGED)/sidecar && DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/ -k 'not rust_db' --tb=short --no-header

server-clean:         ## Clean sidecar data
	rm -f $(MERGED)/sidecar/restaurant.db
	@echo '✓ Database cleaned'

# ── Legacy aliases (back-compat) ───────────────────────────────────────────

mini-install: community-install  ## Alias — Community install
mini-dev: community-dev          ## Alias — Community Vite dev
mini-build: community-build      ## Alias — Community build
mini-check: community-check      ## Alias — Community check

formint-install: pro-install      ## Alias — merged install (formint-pro)
formint-env: pro-env              ## Alias — merged env (formint-pro)
formint-run: pro-run              ## Alias — merged backend run (formint-pro)
formint-stop: pro-stop            ## Alias — merged stop (formint-pro)
formint-test: pro-test            ## Alias — merged test (formint-pro)
formint-check: pro-check          ## Alias — merged check (formint-pro)
formint-clean: pro-clean          ## Alias — merged clean (formint-pro)

cloud-run: cloud-dev-backend      ## Alias — Cloud Django :8082
cloud-dev: cloud-dev-backend      ## Alias — Cloud Django :8082

screenshots:          ## Capture marketplace screenshots (Community)
	$(MAKE) -C $(COMMUNITY) screenshots

publish:              ## Prepare publish bundle from the merged edition
	@echo '── Preparing publish bundle ──'
	@mkdir -p publish-bundle
	@rsync -a --exclude='node_modules' --exclude='.git' --exclude='src-tauri/target' \
		--exclude='src-tauri/gen' --exclude='dist' --exclude='legacy-react' \
		--exclude='sidecar/.venv' $(MERGED)/ publish-bundle/
	@cp PUBLISH.md publish-bundle/ 2>/dev/null || true
	@echo '✓ Bundle ready at publish-bundle/'
	@du -sh publish-bundle/
