# ============================================================================
# Formint Cloud — Root Makefile (Django full setup + frontend)
# ============================================================================
# Orchestrates the Cloud Master edition:
#   - backend/  : Django (Formint Cloud SaaS) — precis-style apps/ package
#                 (apps/core models+viewsets, apps/domain sync services,
#                 apps/handlers consumers/dashboard/fragments) + Unfold admin
#                 + django-fusion contract + django-bolt analytics. The API
#                 surface formerly served by the Robyn server now runs on
#                 Django directly (two dev servers share the same codebase:
#                 :8082 admin/bolt, :8767 server-compatible API contract).
#   - frontend/ : formintA Community UI (Astro + React) wired to :8767
#
# Quick start:
#   make install          — backend .venv + frontend deps
#   make migrate          — apply Django migrations
#   make dev-backend      — runserver :8082 (admin + bolt analytics)
#   make dev-api          — runserver :8767 (server-compatible API surface)
#   make dev-frontend     — astro dev :4323 (foreground)
#   make test             — backend Django test suite
#   make check            — django check + astro check
#   make stop             — kill running dev processes
#
# Env overrides: BACKEND_PORT (8082), API_PORT (8767), FRONTEND_PORT (4323)

NODE_BIN := $(shell dirname $$(command -v node 2>/dev/null) 2>/dev/null)
ifeq ($(strip $(NODE_BIN)),)
NODE_BIN := $(shell ls -d $$HOME/.nvm/versions/node/*/bin 2>/dev/null | tail -1)
endif
export PATH := $(NODE_BIN):$(PATH)

BACKEND_DIR   := backend
FRONTEND_DIR  := frontend
BACKEND_PORT  := 8082
API_PORT      := 8767
FRONTEND_PORT := 4323

# Shared TypeScript client consumed by the frontend via a `file:` dependency
# ("@formints/client": "file:../../packages/formints-client"). It ships only
# `dist/` (package.json `files: ["dist"]`), so it must be built BEFORE the
# frontend installs/checks — otherwise the file: dependency resolves to an
# empty package and `astro check` fails with "Cannot find module @formints/client".
CLIENT_PKG_DIR := ../packages/formints-client

.PHONY: help install migrate seed check test verify-stack dev-backend dev-api \
        dev-frontend stop clean styles config-show config-check client-build \
        backend-help backend-check backend-migrate \
        backend-test frontend-install frontend-dev frontend-build frontend-check

help: ## Show all commands
	@echo 'Formint Cloud — Hosted SaaS Master edition'
	@echo '  make config-show      merged cascade + static-files plan (configs/*.yml)'
	@echo '  make config-check     validate required identity keys resolve'
	@echo '  make install          backend venv + shared client build + frontend deps'
	@echo '  make client-build     build shared @formints/client package (dist/)'
	@echo '  make migrate          apply Django migrations'
	@echo '  make dev-backend      Django :$(BACKEND_PORT) (Unfold admin + bolt)'
	@echo '  make dev-api          Django :$(API_PORT) (server-compatible API)'
	@echo '  make dev-frontend     Astro :$(FRONTEND_PORT)'
	@echo '  make verify-stack     boot :$(API_PORT)+:$(BACKEND_PORT), sweep full surface'
	@echo '  make styles           compile tactical SCSS token layer → static CSS'
	@echo '  make check            django check + astro check'
	@echo '  make test             backend Django test suite'
	@echo '  make stop             kill dev processes'

install: client-build ## Install all layers
	cd $(BACKEND_DIR) && uv sync
	cd $(FRONTEND_DIR) && pnpm install

client-build: ## Build shared @formints/client (dist/) before frontend install/check
	cd $(CLIENT_PKG_DIR) && pnpm install --frozen-lockfile
	cd $(CLIENT_PKG_DIR) && pnpm run build

migrate: ## Apply Django migrations (shared formint_cloud.db)
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py migrate --noinput

seed: migrate ## Alias — migrate (DB is shared across dev servers)

dev-backend: ## Django dev server (Unfold admin + fusion road)
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py runserver 127.0.0.1:$(BACKEND_PORT)

dev-api: ## Django API surface on :8767 (daphne — serves REST + WebSocket sync-events)
	cd $(BACKEND_DIR) && ./.venv/bin/daphne -b 127.0.0.1 -p $(API_PORT) configs.asgi:application

dev-server: dev-api ## Legacy alias — the Robyn server was replaced by Django

dev-frontend: ## Astro dev server (proxies API :8767 + admin :8082)
	cd $(FRONTEND_DIR) && pnpm dev

verify-stack: ## Live end-to-end: boot :8767 + :8082, sweep the full surface
	node scripts/dev/verify-stack.mjs

styles: ## Compile the tactical SCSS token layer → committed static CSS
	cd $(BACKEND_DIR) && npx --yes sass \
		apps/core/static/tactical/scss/tactical.scss \
		apps/core/static/tactical/css/tactical.css \
		--style=compressed --no-source-map

# ── Config cascade (YAML defaults, django-fusion config.project) ──────────
# Merges configs/*.yml → Env/_site.yml → .env → env vars (highest). Backend
# settings stay env-driven; these targets show/validate the documented defaults.
config-show: ## Print the merged config cascade + static-files plan
	cd $(BACKEND_DIR) && ./.venv/bin/python -c "from pathlib import Path; from django_fusion.config.project import load_config, staticfiles_plan; root = Path('..').resolve(); c = load_config(root); print('PROJECT CONFIG —', c.get('SITE.name', 'formint-cloud'), '| env:', c.env); [print(f'  {k}: {v}') for k in ('DEBUG', 'ALLOWED_HOSTS', 'PORT', 'API_PORT', 'FRONTEND_PORT') if (v := c.get(k)) is not None]; print('  SITE:', c.section('SITE') or {}); print('  ADMIN:', c.section('ADMIN') or {}); print('  CSS_PANEL:', c.section('CSS_PANEL') or {}); print(); print(staticfiles_plan(root, overrides=c.section('STATIC')).render())"

config-check: ## Validate required identity keys resolve from the config
	cd $(BACKEND_DIR) && ./.venv/bin/python -c "from django_fusion.config.project import load_config; c = load_config('..'); req = {'SITE.name': 'formint-cloud', 'SITE.primary_domain': 'cloud.formint.app', 'ADMIN.panel_path': '/admin/'}; missing = [k for k, _ in req.items() if not c.get(k)]; print('CONFIG CHECK — OK ✅' if not missing else f'CONFIG CHECK — MISSING: {missing}'); raise SystemExit(1 if missing else 0)"

check: client-build ## Django system checks + Astro typecheck
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py check
	cd $(FRONTEND_DIR) && ./node_modules/.bin/astro check

test: ## Backend Django test suite
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py test apps --verbosity=1

stop: ## Kill dev processes
	@lsof -ti :$(BACKEND_PORT) | xargs kill -9 2>/dev/null || true
	@lsof -ti :$(API_PORT) | xargs kill -9 2>/dev/null || true
	@lsof -ti :$(FRONTEND_PORT) | xargs kill -9 2>/dev/null || true
	@echo 'stopped'

clean: ## Remove Cloud database and bytecode cache
	rm -f $(BACKEND_DIR)/pos_cloud.db
	find $(BACKEND_DIR) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(FRONTEND_DIR)/dist 2>/dev/null || true
	@echo '✓ Cloud cleaned'

# ── Backend delegation ────────────────────────────────────────────────────
backend-help:
	@echo 'Backend: make backend-check | backend-migrate | backend-test'

backend-check:
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py check

backend-migrate:
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py migrate --noinput

backend-test:
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py test apps --verbosity=1

# ── Frontend delegation ───────────────────────────────────────────────────
frontend-install: client-build
	cd $(FRONTEND_DIR) && pnpm install

frontend-dev:
	cd $(FRONTEND_DIR) && pnpm dev

frontend-build:
	cd $(FRONTEND_DIR) && pnpm build

frontend-check: client-build
	cd $(FRONTEND_DIR) && ./node_modules/.bin/astro check
