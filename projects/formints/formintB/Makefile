# ============================================================================
# POS Cloud (formintB) — Root Makefile (backend + sidecar + frontend)
# ============================================================================
# Orchestrates the Cloud Master edition:
#   - backend/  : Django (pos-cloud SaaS) — precis-style apps/ package
#                 (apps/core models+viewsets, apps/domain sync services,
#                 apps/handlers consumers/dashboard/fragments) + Unfold admin
#   - sidecar/  : Robyn + Django ORM sidecar (REST + WebSocket APIs on :8767)
#   - frontend/ : formintA Community UI (Astro + React) wired to the sidecar
#
# Quick start:
#   make install          — backend .venv + sidecar .venv + frontend deps
#   make migrate          — apply Django migrations
#   make dev-backend      — runserver :8082 (foreground)
#   make dev-sidecar      — Robyn sidecar :8767 (foreground)
#   make dev-frontend     — astro dev :4323 (foreground)
#   make test             — sidecar tests + backend tests
#   make check            — django check + astro check
#   make stop             — kill running dev processes
#
# Env overrides: BACKEND_PORT (8082), SIDECAR_PORT (8767), FRONTEND_PORT (4323)

NODE_BIN := $(shell dirname $$(command -v node 2>/dev/null) 2>/dev/null)
export PATH := $(NODE_BIN):$(PATH)

BACKEND_DIR   := backend
SIDECAR_DIR   := sidecar
FRONTEND_DIR  := frontend
BACKEND_PORT  := 8082
SIDECAR_PORT  := 8767
FRONTEND_PORT := 4323

.PHONY: help install migrate seed check test dev-backend dev-sidecar dev-frontend stop \
        backend-help backend-check backend-migrate backend-test \
        sidecar-help sidecar-test \
        frontend-install frontend-dev frontend-build frontend-check

help: ## Show all commands
	@echo 'POS Cloud (formintB) — Cloud Master edition'
	@echo '  make install          backend + sidecar venvs + frontend deps'
	@echo '  make migrate          apply Django migrations'
	@echo '  make dev-backend      Django :$(BACKEND_PORT) (Unfold admin)'
	@echo '  make dev-sidecar      Robyn sidecar :$(SIDECAR_PORT)'
	@echo '  make dev-frontend     Astro :$(FRONTEND_PORT)'
	@echo '  make check            django check + astro check'
	@echo '  make test             backend + sidecar tests'
	@echo '  make stop             kill dev processes'

install: ## Install all layers
	cd $(BACKEND_DIR) && uv sync
	cd $(SIDECAR_DIR) && uv sync
	cd $(FRONTEND_DIR) && pnpm install

migrate: ## Apply Django migrations (shared pos_cloud.db)
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py migrate --noinput

seed: migrate ## Alias — migrate (DB is shared with the sidecar)

dev-backend: ## Django dev server (Unfold admin + fusion road)
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py runserver 127.0.0.1:$(BACKEND_PORT)

dev-sidecar: ## Robyn sidecar (REST APIs)
	cd $(SIDECAR_DIR) && ./.venv/bin/python server.py --port $(SIDECAR_PORT)

dev-frontend: ## Astro dev server (proxies sidecar + backend)
	cd $(FRONTEND_DIR) && pnpm dev

check: ## Django system checks + Astro typecheck
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py check
	cd $(FRONTEND_DIR) && ./node_modules/.bin/astro check

test: ## Backend + sidecar tests
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py test apps --verbosity=1
	cd $(SIDECAR_DIR) && ./.venv/bin/python -m pytest tests/ -q

stop: ## Kill dev processes
	@lsof -ti :$(BACKEND_PORT) | xargs kill -9 2>/dev/null || true
	@lsof -ti :$(SIDECAR_PORT) | xargs kill -9 2>/dev/null || true
	@lsof -ti :$(FRONTEND_PORT) | xargs kill -9 2>/dev/null || true
	@echo 'stopped'

# ── Backend delegation ────────────────────────────────────────────────────
backend-help:
	@echo 'Backend: make backend-check | backend-migrate | backend-test'

backend-check:
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py check

backend-migrate:
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py migrate --noinput

backend-test:
	cd $(BACKEND_DIR) && ./.venv/bin/python manage.py test apps --verbosity=1

# ── Sidecar delegation ────────────────────────────────────────────────────
sidecar-help:
	@echo 'Sidecar: make sidecar-test'

sidecar-test:
	cd $(SIDECAR_DIR) && ./.venv/bin/python -m pytest tests/ -q

# ── Frontend delegation ───────────────────────────────────────────────────
frontend-install:
	cd $(FRONTEND_DIR) && pnpm install

frontend-dev:
	cd $(FRONTEND_DIR) && pnpm dev

frontend-build:
	cd $(FRONTEND_DIR) && pnpm build

frontend-check:
	cd $(FRONTEND_DIR) && ./node_modules/.bin/astro check
