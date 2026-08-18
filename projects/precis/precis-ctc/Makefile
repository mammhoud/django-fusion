# precis-ctc — project-level orchestration
# Usage: make up | make down | make build | make logs | make check | make test

PROJECT := precis-ctc

# Root .env carries POSTGRES_PASSWORD, REDIS_PASSWORD, and per-site DB names.
# Docker Compose auto-loads a .env from the CWD (this directory), but the
# shared secrets live three levels up. Pass it explicitly so interpolation of
# ${VAR:?...} required-variable syntax in docker-compose.yml doesn't abort.
ROOT_ENV := ../../../.env
DC := docker compose --env-file $(ROOT_ENV)

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
NC := \033[0m

.PHONY: help check test run-dev migrate collectstatic shell \
        frontend-dev frontend-build frontend-check \
        build up down logs restart front-logs back-logs worker-logs status \
        clean-docker rebuild-backend rebuild-frontend clean \
        install-assets build-assets build-assets-dev assets-full skeleton-manifest redeploy

help:
	@echo "$(PROJECT) — Django/Wagtail + Astro medical research center"
	@echo "  Checks:  make check | test"
	@echo "  Dev:     make run-dev | frontend-dev"
	@echo "  Docker:  make build | up | down | logs | restart | status"
	@echo "  Redeploy: make redeploy   (front + back + worker + scheduler)"
	@echo "  Assets:  make install-assets | build-assets | build-assets-dev | assets-full"
	@echo "  Skeleton: make skeleton-manifest"
	@echo "  Clean:   make clean | clean-docker"

# ── Backend / frontend command delegation ──────────────────────────────
check:
	$(MAKE) -C backend check

test:
	$(MAKE) -C backend test

run-dev:
	$(MAKE) -C backend dev

migrate:
	$(MAKE) -C backend migrate

collectstatic:
	$(MAKE) -C backend collectstatic

shell:
	$(MAKE) -C backend shell

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

frontend-check:
	cd frontend && npm run check

# ── Webpack Asset Build (Django-side SCSS/JS) ─────────────────────────
# Extends projects/webpack/base.config.js — see webpack/precis.config.js
install-assets:
	npm install

build-assets: skeleton-manifest
	npx webpack --config webpack/precis.config.js --mode=production

build-assets-dev:
	npx webpack --config webpack/precis.config.js --mode=development

# ── One-step asset pipeline ─────────────────────────────────────────
# Install npm deps, rebuild the Django webpack bundles, then collect
# everything into the shared static tree in a single invocation.
assets-full: install-assets build-assets collectstatic
	@echo "$(GREEN)✅ Assets rebuilt and collected$(NC)"

# ── Skeleton Manifest ─────────────────────────────────────────────────
# Runs the Django management command to produce a static JSON manifest
# consumed by the Astro frontend (SkeletonBridge.astro).
skeleton-manifest:
	$(MAKE) -C backend skeleton-manifest

# ── Docker targets ────────────────────────────────────────────────────
build: install-assets build-assets
	$(DC) build

up:
	$(DC) up -d

down:
	$(DC) down

logs:
	$(DC) logs -f

restart:
	$(DC) restart

front-logs:
	$(DC) logs -f frontend

back-logs:
	$(DC) logs -f backend

worker-logs:
	$(DC) logs -f worker

status:
	$(DC) ps

# ── Rebuild targets ────────────────────────────────────────────────────
rebuild-backend:
	$(DC) build --no-cache backend worker

rebuild-frontend:
	$(DC) build --no-cache frontend

# ── Redeploy (front + back + attached containers) ──────────────────────
# Single command to pick up the latest changes: runs the same checks the
# dispatcher uses (make check / make frontend-check), rebuilds the images,
# then recreates the whole stack (backend, worker, scheduler, frontend).
# Invoke via the Precis dispatcher with:
#   cd projects && make website-ctc redeploy
#   cd projects && make redeploy-with-stack WEBSITE=precis-ctc  (alias below)
redeploy: check frontend-check
	@echo "$(CYAN)🔄 Redeploying $(PROJECT) — backend + worker + scheduler + frontend...$(NC)"
	$(DC) build backend worker scheduler frontend
	$(DC) up -d --force-recreate backend worker scheduler frontend
	@echo "$(GREEN)✅ Redeploy complete — stack status:$(NC)"
	$(DC) ps

# ── Clean Docker resources ─────────────────────────────────────────────
clean:
	rm -rf assets/bundles node_modules

clean-docker:
	@echo "$(CYAN)🧹 Cleaning Docker resources for $(PROJECT)...$(NC)"
	-$(DC) down -v --remove-orphans 2>/dev/null || true
	@echo "$(GREEN)✅ Clean complete$(NC)"
