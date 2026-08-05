# ============================================================================
# Formint POS — Root Makefile (frontend + sidecar + full commands)
# ============================================================================
# Orchestrates the merged package:
#   - sidecar/   : Django + Ninja + django-fusion + Unfold admin + Robyn server
#                  (single merged Django project — pos_full + formint apps)
#   - frontend/  : Astro + Alpine.js + HTMX shell (proxies /api, /htmx, /fusion)
#   - src-tauri/ : Tauri v2 desktop shell
#
# Design: delegates to per-layer Makefiles via $(MAKE) -C, mirroring
# landing-fusion's root Makefile (frontend targets here, sidecar via
# `backend-*` → sidecar/Makefile). The parent `projects/pos/Makefile`
# delegates its `formint-*` targets here too.
#
# Quick start:
#   make install          — sidecar .venv + deps, frontend npm install, migrate
#   make seed             — migrate + idempotent superuser (admin@formint.local)
#   make env              — run BOTH servers in tmux (sidecar :8767 + frontend :4321)
#   make dev-backend      — runserver :8767 (foreground)
#   make dev-frontend     — astro dev :4321 (foreground)
#   make test             — sidecar tests + frontend contract tests
#   make check            — django check + astro check
#   make stop             — kill the tmux env sessions
#   make build            — production frontend build + sidecar collectstatic
#
# Env overrides: BACKEND_PORT (8767), FRONTEND_PORT (4321), NODE_BIN

# Resolve node from PATH first (avoids hard-coding an .nvm version glob).
NODE_BIN := $(shell dirname $$(command -v node 2>/dev/null) 2>/dev/null)
export PATH := $(NODE_BIN):$(PATH)

BACKEND_DIR  := sidecar
FRONTEND_DIR := frontend
BACKEND_PORT := 8767
FRONTEND_PORT := 4321

.PHONY: help install seed migrate check test env dev-backend dev-frontend stop \
        build preview clean screenshots \
        backend-help backend-dev backend-check backend-migrate backend-test backend-seed backend-clean \
        frontend-install frontend-dev frontend-build frontend-preview frontend-check frontend-test frontend-clean \
        tauri tauri-dev tauri-build

help: ## Show all commands
	@echo ''
	@echo '╔══════════════════════════════════════════════════════════╗'
	@echo '║  Formint POS — Professional (merged pos-full + pos-solo) ║'
	@echo '╚══════════════════════════════════════════════════════════╝'
	@echo ''
	@echo '── Setup ───────────────────────────────────────────────────'
	@echo '  make install          Backend .venv + deps + frontend npm install + migrate'
	@echo '  make seed             Migrate + idempotent superuser (admin@formint.local)'
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
	@echo '  make test             Backend suite (35) + frontend contract tests'
	@echo ''
	@echo '── Build ───────────────────────────────────────────────────'
	@echo '  make build            Frontend production build + backend collectstatic'
	@echo '  make preview          Astro preview (:4321)'
	@echo '  make clean            Remove build artifacts + db + node_modules'
	@echo ''
	@echo '── Backend (delegates to backend/Makefile) ────────────────'
	@echo '  make backend-help backend-dev backend-check backend-migrate'
	@echo '  make backend-test backend-seed backend-clean'
	@echo ''
	@echo '── Frontend ────────────────────────────────────────────────'
	@echo '  make frontend-install frontend-dev frontend-build frontend-preview'
	@echo '  make frontend-check frontend-test frontend-clean'
	@echo ''
	@echo '── Tauri desktop ───────────────────────────────────────────'
	@echo '  make tauri            Run Tauri CLI (config ../src-tauri/tauri.conf.json)'
	@echo '  make tauri-dev        Tauri dev (desktop hot-reload)'
	@echo '  make tauri-build      Tauri production build'
	@echo ''
	@echo '── Screenshots ─────────────────────────────────────────────'
	@echo '  make screenshots      Capture Unfold admin screenshots → docs/screenshots/admin/'
	@echo ''


# ── Setup ─────────────────────────────────────────────────────────────────

install: ## Full install: backend venv + deps + migrate, frontend npm install
	@echo '── Installing backend ──'
	$(MAKE) -C $(BACKEND_DIR) install
	@echo '── Installing frontend ──'
	$(MAKE) -C $(FRONTEND_DIR) install
	@echo '✅ Formint POS installed. Run: make env'

seed: ## Migrate + ensure superuser (admin@formint.local / admin123)
	$(MAKE) -C $(BACKEND_DIR) seed

migrate: ## Apply backend migrations
	$(MAKE) -C $(BACKEND_DIR) migrate

# ── Running environments ──────────────────────────────────────────────────

env: ## Run sidecar (:8767) + frontend (:4321) in tmux sessions
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

screenshots: ## Capture Unfold admin screenshots → docs/screenshots/admin/
	@mkdir -p docs/screenshots/admin
	@echo 'ℹ️  Admin screenshots live in docs/screenshots/admin/ (4 images, committed).'
	@echo '   To re-capture: start the backend (make env), log in at http://127.0.0.1:$(BACKEND_PORT)/admin/,'
	@echo '   then run the legacy capture tool: bash ../scripts/dev/capture-admin-screenshots.sh'
	@echo '   (that tool targets the legacy pos-full admin layout; for formint admin pages, capture'
	@echo '   /admin/ + the formint model changelists manually at 1440px via headless Chromium.)'

# ── Backend delegation ────────────────────────────────────────────────────

backend-help backend-dev backend-check backend-migrate backend-test backend-seed backend-clean:
	$(MAKE) -C $(BACKEND_DIR) $(@:backend-%=%)

# ── Frontend delegation ───────────────────────────────────────────────────

frontend-install frontend-dev frontend-build frontend-preview frontend-check frontend-test frontend-clean:
	$(MAKE) -C $(FRONTEND_DIR) $(@:frontend-%=%)

# ── Tauri desktop ─────────────────────────────────────────────────────────

tauri: ## Run Tauri CLI (config ../src-tauri/tauri.conf.json)
	cd $(FRONTEND_DIR) && npm run tauri

tauri-dev: ## Tauri dev (desktop hot-reload)
	cd $(FRONTEND_DIR) && npm run dev:desktop

tauri-build: ## Tauri production build
	cd $(FRONTEND_DIR) && npm run build:desktop
