# precis-ctc — project-level orchestration
# Usage: make up | make down | make build | make logs | make check | make test

PROJECT := precis-ctc

# ── Config cascade (YAML defaults + .env) ──────────────────────────
# Merges shared Env YAML (projects/precis/configs/Env) → configs/*.yml →
# Env/_site.yml → .env → environment variables (highest). See configs/README.md.
UV_BIN := $(shell which uv 2>/dev/null || (test -x $(HOME)/.local/bin/uv && echo $(HOME)/.local/bin/uv) || echo /root/.local/bin/uv)
UV := $(UV_BIN) --project ../..
UV_RUN := $(UV) run

# Root .env carries POSTGRES_PASSWORD, REDIS_PASSWORD, and per-site DB names.
# Docker Compose auto-loads a .env from the CWD (this directory), but the
# shared secrets live three levels up. Pass it explicitly so interpolation of
# ${VAR:?...} required-variable syntax in docker-compose.yml doesn't abort.
ROOT_ENV := ../../../.env
DC := docker compose --env-file $(ROOT_ENV)
# Worker + scheduler live in docker-compose.tools.yml (standalone stack); the
# main compose includes backend + frontend. Merge both for full-stack ops.
DC_ALL := $(DC) -f docker-compose.yml -f docker-compose.tools.yml

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
NC := \033[0m

.PHONY: help check test run-dev migrate collectstatic shell \
        frontend-dev frontend-build frontend-check config-show config-check \
        build up down logs restart front-logs back-logs worker-logs status \
        clean-docker rebuild-backend rebuild-frontend clean \
        install-assets build-assets build-assets-dev assets-full skeleton-manifest redeploy

help:
	@echo "$(PROJECT) — Django/Wagtail + Astro medical research center"
	@echo "  Checks:  make check | test"
	@echo "  Config:  make config-show | config-check   (config cascade + static-files plan)"
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

# ── Config cascade (merged YAML + .env + env) ───────────────────────
config-show: ## Print the merged config + resolved front/back views + static plan
	@$(UV_RUN) python -c "from pathlib import Path; from django_fusion.config.project import load_config, staticfiles_plan; root = Path('.').resolve(); c = load_config(root); print('PROJECT CONFIG —', c.get('SITE.name', 'precis-ctc'), '| env:', c.env); [print(f'  {k}: {v}') for k in ('DEBUG', 'ALLOWED_HOSTS', 'PORT', 'FRONTEND_PORT', 'FUSION_RENDER_FIRST', 'SITE_DOMAIN', 'DOMAIN_NAME') if (v := c.get(k)) is not None]; print('  SITE:', c.section('SITE') or {}); print('  ADMIN:', c.section('ADMIN') or {}); print('  CSS_PANEL:', c.section('CSS_PANEL') or {}); print('  resolved back (https://ctc-research.com):'); [print(f'    {k}: {v}') for k, v in c.resolve('https://ctc-research.com', 'back').get('SITE', {}).items()]; print(); print(staticfiles_plan(root, overrides=c.section('STATIC')).render())"

config-check: ## Validate required identity keys resolve from the config
	@$(UV_RUN) python -c "from django_fusion.config.project import load_config; c = load_config('.'); req = {'SITE.name': 'precis-ctc', 'SITE.primary_domain': 'ctc-research.com', 'SITE.domains': 'ctc-research.com', 'ADMIN.panel_path': '/admin/'}; missing = [k for k, _ in req.items() if not c.get(k)]; print('CONFIG CHECK — OK ✅' if not missing else f'CONFIG CHECK — MISSING: {missing}'); raise SystemExit(1 if missing else 0)"

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
	$(DC_ALL) build backend worker scheduler frontend
	$(DC_ALL) up -d --force-recreate backend worker scheduler frontend
	@echo "$(GREEN)✅ Redeploy complete — stack status:$(NC)"
	$(DC_ALL) ps

# ── Clean Docker resources ─────────────────────────────────────────────
clean:
	rm -rf assets/bundles node_modules

clean-docker:
	@echo "$(CYAN)🧹 Cleaning Docker resources for $(PROJECT)...$(NC)"
	-$(DC) down -v --remove-orphans 2>/dev/null || true
	@echo "$(GREEN)✅ Clean complete$(NC)"
