# ============================================================================
# Formint POS — Root Makefile (frontend + server + full commands)
# ============================================================================
# Orchestrates the merged package:
#   - server/   : Django + Ninja + django-fusion + Unfold admin
#                  (single merged Django project; optional legacy Robyn compatibility runner)
#   - frontend/  : Astro + Alpine.js + HTMX shell (proxies /api, /htmx, /fusion)
#   - src-tauri/ : Tauri v2 desktop shell
#
# Design: delegates to per-layer Makefiles via $(MAKE) -C, mirroring
# precis-landing's root Makefile (frontend targets here, server via
# `backend-*` → server/Makefile). The parent `projects/formints/Makefile`
# delegates its `pro-*` targets here too.
#
# Quick start:
#   make install          — server .venv + deps, frontend npm install, migrate
#   make seed             — migrate + idempotent superuser (admin@formint.local)
#   make env              — run BOTH servers in tmux (server :8767 + frontend :4321)
#   make dev-backend      — runserver :8767 (foreground)
#   make dev-frontend     — astro dev :4321 (foreground)
#   make test             — server tests + frontend contract tests
#   make check            — django check + astro check
#   make stop             — kill the tmux env sessions
#   make build            — production frontend build + server collectstatic
#
# Env overrides: BACKEND_PORT (8767), FRONTEND_PORT (4321), NODE_BIN

# Resolve node from PATH first (avoids hard-coding an .nvm version glob).
NODE_BIN := $(shell dirname $$(command -v node 2>/dev/null) 2>/dev/null)
export PATH := $(NODE_BIN):$(PATH)

BACKEND_DIR  := server
FRONTEND_DIR := frontend
BACKEND_PORT := 8767
FRONTEND_PORT := 4321

.PHONY: help install seed migrate check test env dev-backend dev-frontend stop \
        build preview clean screenshots \
        backend-help backend-dev backend-server backend-check backend-migrate backend-test backend-seed backend-clean backend-server-binary backend-server-install-bin \
        frontend-install frontend-dev frontend-build frontend-preview frontend-check frontend-test frontend-clean \
        desktop desktop-dev desktop-backend tauri tauri-dev tauri-build \
        desktop-build bundle server-build server-install-bin release server-binary

help: ## Show all commands
	@echo ''
	@echo '╔══════════════════════════════════════════════════════════╗'
	@echo '║  Formint POS — Professional (merged pos-full + pos-solo) ║'
	@echo '╚══════════════════════════════════════════════════════════╝'
	@echo ''
	@echo '── Setup ───────────────────────────────────────────────────'
	@echo '  make install          Backend .venv + deps + frontend npm install + migrate'
	@echo '  make seed             Migrate + superuser + demo data (admin@formint.local / admin123)'
	@echo '  make backend-seed-force  Wipe + re-seed all demo data'
	@echo ''
	@echo '── Running environments ────────────────────────────────────'
	@echo '  make env              Run backend (:8767) + frontend (:4321) in tmux'
	@echo '  make dev-backend      Run backend runserver :8767 (foreground)'
	@echo '  make dev-frontend     Run astro dev :4321 (foreground)'
	@echo '  make stop             Kill tmux env sessions (formint-be / formint-fe)'
	@echo '  make status           Show tmux sessions + endpoint health'
	@echo ''
	@echo '── Validation ──────────────────────────────────────────────'
	@echo '  make check            Django check + astro check'
	@echo '  make test             Backend suite + frontend contract tests'
	@echo ''
	@echo '── Build ───────────────────────────────────────────────────'
	@echo '  make build            Frontend production build + backend collectstatic'
	@echo '  make preview          Astro preview (:4321)'
	@echo '  make clean            Remove build artifacts + db + node_modules'
	@echo ''
	@echo '── Backend (delegates to server/Makefile) ─────────────────'
	@echo '  make backend-help backend-dev backend-server backend-check backend-migrate'
	@echo '  make backend-test backend-seed backend-seed-force backend-clean'
	@echo '  make backend-server-binary backend-server-install-bin'
	@echo ''
	@echo '── Frontend ────────────────────────────────────────────────'
	@echo '  make frontend-install frontend-dev frontend-build frontend-preview'
	@echo '  make frontend-check frontend-test frontend-clean'
	@echo ''
	@echo '── Desktop (Tauri) ─────────────────────────────────────────'
	@echo '  make desktop          Full desktop dev: backend tmux + Tauri window (:1420)'
	@echo '  make desktop-dev      Alias for make desktop'
	@echo '  make tauri-dev        Raw Tauri dev window (backend must already run)'
	@echo '  make tauri            Tauri CLI (config ../src-tauri/tauri.conf.json)'
	@echo ''
	@echo '── Full build / release ────────────────────────────────────'
	@echo '  make desktop-build    Full production desktop build (frontend + collectstatic + Tauri bundle)'
	@echo '  make bundle           Alias for make desktop-build'
	@echo '  make tauri-build      Raw Tauri production bundle (assumes frontend built)'
	@echo '  make server-build    PyInstaller server binary → dist/formint-backend'
	@echo '  make server-install-bin  Copy the server binary into src-tauri/binaries/ (Tauri externalBin)'
	@echo '  make server-binary   Build PyInstaller formint-backend → server/dist'
	@echo '  make release          check + test + web build + desktop bundle'
	@echo ''
	@echo '── Screenshots ─────────────────────────────────────────────'
	@echo '  make screenshots      Capture frontend + admin screenshots → Precis Landing related/formints/'
	@echo ''


# ── Setup ─────────────────────────────────────────────────────────────────

install: ## Full install: backend venv + deps + migrate, frontend npm install
	@echo '── Installing backend ──'
	$(MAKE) -C $(BACKEND_DIR) install
	@echo '── Installing frontend ──'
	$(MAKE) -C $(FRONTEND_DIR) install
	@echo '✅ Formint POS installed. Run: make env'

seed: ## Migrate + ensure superuser + seed demo data (admin@formint.local / admin123)
	$(MAKE) -C $(BACKEND_DIR) seed

seed-force: ## Wipe + re-seed all demo data
	$(MAKE) -C $(BACKEND_DIR) seed-force

migrate: ## Apply backend migrations
	$(MAKE) -C $(BACKEND_DIR) migrate

# ── Running environments ──────────────────────────────────────────────────

env: ## Run server (:8767) + frontend (:4321) in tmux sessions
	@echo '── Starting Formint POS environment ──'
	@echo '  Backend  → http://127.0.0.1:$(BACKEND_PORT)/api/v1/docs'
	@echo '  Admin    → http://127.0.0.1:$(BACKEND_PORT)/admin/'
	@echo '  Frontend → http://127.0.0.1:$(FRONTEND_PORT)/'
	@tmux kill-session -t formint-be 2>/dev/null || true
	@tmux kill-session -t formint-fe 2>/dev/null || true
	@tmux new-session -d -s formint-be 'cd $(CURDIR)/$(BACKEND_DIR) && ./.venv/bin/python3 manage.py runserver 127.0.0.1:$(BACKEND_PORT)'
	@tmux new-session -d -s formint-fe 'export PATH=$(NODE_BIN):$$PATH && cd $(CURDIR)/$(FRONTEND_DIR) && npm run dev -- --port $(FRONTEND_PORT) --host 0.0.0.0'
	@sleep 6
	@echo '── Health ──'
	@curl -s -o /dev/null -w '  backend  → %{http_code}\n' --max-time 3 http://127.0.0.1:$(BACKEND_PORT)/health/ || echo '  backend  → DOWN'
	@curl -s -o /dev/null -w '  frontend → %{http_code}\n' --max-time 3 http://127.0.0.1:$(FRONTEND_PORT)/ || echo '  frontend → DOWN'
	@curl -s http://127.0.0.1:$(FRONTEND_PORT)/fusion/render-mode/ 2>/dev/null || echo '  (render-mode proxy not ready yet)'
	@echo ''
	@echo 'Attach: tmux attach -t formint-be | tmux attach -t formint-fe — Stop: make stop'

dev-backend: ## Run backend runserver :8767 (foreground)
	$(MAKE) -C $(BACKEND_DIR) dev

dev-frontend: ## Run astro dev :4321 (foreground)
	export PATH=$(NODE_BIN):$$PATH; cd $(FRONTEND_DIR) && npm run dev -- --port $(FRONTEND_PORT) --host 0.0.0.0

stop: ## Kill tmux env sessions
	@tmux kill-session -t formint-be 2>/dev/null || echo '  (no formint-be session)'
	@tmux kill-session -t formint-fe 2>/dev/null || echo '  (no formint-fe session)'
	@echo '✅ Formint POS environment stopped'

status: ## Show tmux sessions + endpoint health
	@echo '── tmux sessions ──'
	@tmux ls 2>/dev/null | grep -E 'formint-(be|fe)' || echo '  (no formint sessions — run: make env)'
	@echo '── health ──'
	@curl -s -o /dev/null -w '  backend  → %{http_code}\n' --max-time 3 http://127.0.0.1:$(BACKEND_PORT)/health/ || echo '  backend  → DOWN'
	@curl -s -o /dev/null -w '  frontend → %{http_code}\n' --max-time 3 http://127.0.0.1:$(FRONTEND_PORT)/ || echo '  frontend → DOWN'

# ── Validation ─────────────────────────────────────────────────────────────

check: ## Django check + astro check
	$(MAKE) -C $(BACKEND_DIR) check
	$(MAKE) -C $(FRONTEND_DIR) check

test: ## Backend suite (35) + frontend contract tests
	$(MAKE) -C $(BACKEND_DIR) test
	$(MAKE) -C $(FRONTEND_DIR) test

# ── Build ─────────────────────────────────────────────────────────────────

build: ## Frontend production build + backend collectstatic
	$(MAKE) -C $(FRONTEND_DIR) build
	$(MAKE) -C $(BACKEND_DIR) collectstatic

preview: ## Astro preview (:4321)
	export PATH=$(NODE_BIN):$$PATH; cd $(FRONTEND_DIR) && npm run preview -- --port $(FRONTEND_PORT) --host 0.0.0.0

clean: ## Remove build artifacts + db + node_modules
	$(MAKE) -C $(BACKEND_DIR) clean
	$(MAKE) -C $(FRONTEND_DIR) clean
	@echo '✅ Formint POS cleaned'

screenshots: ## Capture frontend + admin screenshots → Precis Landing related/formints/
	@echo 'ℹ️  Re-capturing screenshots (requires: make env + make seed, chromium, selenium, imagemagick)'
	bash ../scripts/dev/capture-formint-screenshots.sh
	@echo '✅ Screenshots updated in Precis Landing related/formints/'

# ── Backend delegation ────────────────────────────────────────────────────

backend-help backend-dev backend-server backend-check backend-migrate backend-test backend-seed backend-seed-force backend-clean backend-server-binary backend-server-install-bin:
	$(MAKE) -C $(BACKEND_DIR) $(@:backend-%=%)

# ── Frontend delegation ───────────────────────────────────────────────────

frontend-install frontend-dev frontend-build frontend-preview frontend-check frontend-test frontend-clean:
	$(MAKE) -C $(FRONTEND_DIR) $(@:frontend-%=%)

# ── Desktop (Tauri) ────────────────────────────────────────────────────────

desktop: ## Run the desktop app in dev mode (backend tmux + Tauri window)
	@echo '── Starting Formint POS desktop (dev) ──'
	@$(MAKE) -s desktop-backend
	@echo '  Tauri window loads the Astro dev shell at http://127.0.0.1:1420'
	@echo '  (tauri.conf.json beforeDevCommand; proxies /api, /htmx, /fusion → :$(BACKEND_PORT))'
	@echo '  Quit the desktop app to return. Stop backend later with: make stop'
	cd $(FRONTEND_DIR) && npm run dev:desktop

desktop-dev: desktop ## Alias for make desktop

desktop-backend: ## Start the backend tmux session (formint-be) for desktop dev
	@tmux kill-session -t formint-be 2>/dev/null || true
	@tmux new-session -d -s formint-be 'cd $(CURDIR)/$(BACKEND_DIR) && ./.venv/bin/python3 manage.py runserver 127.0.0.1:$(BACKEND_PORT)'
	@sleep 4
	@curl -s -o /dev/null -w '  backend  → %{http_code}\n' --max-time 3 http://127.0.0.1:$(BACKEND_PORT)/health/ || echo '  backend  → DOWN (tmux attach -t formint-be to debug)'

tauri: ## Run the Tauri CLI (config ../src-tauri/tauri.conf.json)
	cd $(FRONTEND_DIR) && npm run tauri

tauri-dev: ## Raw Tauri dev window (hot-reload; assume backend is already running)
	cd $(FRONTEND_DIR) && npm run dev:desktop

tauri-build: ## Raw Tauri production bundle (assume frontend already built)
	cd $(FRONTEND_DIR) && npm run build:desktop

# ── Full build / release ───────────────────────────────────────────────────

desktop-build: ## Full production desktop build (collectstatic + frontend + Tauri bundle)
	@echo '── Desktop production build ──'
	$(MAKE) -C $(BACKEND_DIR) collectstatic
	$(MAKE) -C $(FRONTEND_DIR) build
	cd $(FRONTEND_DIR) && npm run build:desktop

bundle: desktop-build ## Alias for make desktop-build

server-binary: ## PyInstaller formint-backend → src-tauri/binaries/<target-triple>
	$(MAKE) -C $(BACKEND_DIR) server-binary

server-build: ## Build the optional legacy compatibility binary → server/dist/formint-backend
	$(MAKE) -C $(BACKEND_DIR) server-binary

server-install-bin: ## Copy the server binary into src-tauri/binaries/ (Tauri externalBin)
	$(MAKE) -C $(BACKEND_DIR) server-install-bin

release: ## Full release pipeline: check + test + web build + desktop bundle
	@echo '── Release pipeline ──'
	$(MAKE) check
	$(MAKE) test
	$(MAKE) build
	$(MAKE) desktop-build
	@echo '✅ Release complete'
