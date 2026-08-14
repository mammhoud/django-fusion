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

.PHONY: help install migrate seed check test verify-stack dev-backend dev-api \
        dev-frontend stop clean styles backend-help backend-check backend-migrate \
        backend-test frontend-install frontend-dev frontend-build frontend-check

help: ## Show all commands
	@echo 'Formint Cloud — Hosted SaaS Master edition'
	@echo '  make install          backend venv + frontend deps'
	@echo '  make migrate          apply Django migrations'
	@echo '  make dev-backend      Django :$(BACKEND_PORT) (Unfold admin + bolt)'
	@echo '  make dev-api          Django :$(API_PORT) (server-compatible API)'
	@echo '  make dev-frontend     Astro :$(FRONTEND_PORT)'
	@echo '  make verify-stack     boot :$(API_PORT)+:$(BACKEND_PORT), sweep full surface'
	@echo '  make styles           compile tactical SCSS token layer → static CSS'
	@echo '  make check            django check + astro check'
	@echo '  make test             backend Django test suite'
	@echo '  make stop             kill dev processes'

install: ## Install all layers
	cd $(BACKEND_DIR) && uv sync
	cd $(FRONTEND_DIR) && pnpm install

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

check: ## Django system checks + Astro typecheck
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
frontend-install:
	cd $(FRONTEND_DIR) && pnpm install

frontend-dev:
	cd $(FRONTEND_DIR) && pnpm dev

frontend-build:
	cd $(FRONTEND_DIR) && pnpm build

frontend-check:
	cd $(FRONTEND_DIR) && ./node_modules/.bin/astro check
