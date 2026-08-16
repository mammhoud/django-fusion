# precis-lms — project-level orchestration
# Usage: make up | make down | make build | make logs

PROJECT := precis-lms

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
NC := \033[0m

.PHONY: help check test run-dev migrate collectstatic shell \
        frontend-dev frontend-build frontend-check \
        build up down logs restart front-logs back-logs worker-logs status \
        clean-docker rebuild-backend rebuild-frontend clean \
        install-assets build-assets build-assets-dev skeleton-manifest

help:
	@echo "precis — Django/Wagtail + Astro LMS (main)"
	@echo "  Checks:  make check | test"
	@echo "  Dev:     make run-dev | frontend-dev"
	@echo "  Docker:  make build | up | down | logs | restart | status"
	@echo "  Assets:  make install-assets | build-assets | build-assets-dev"
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

# ── Webpack Asset Build (Django-side SCSS/JS) ──────────────────────
# Extends projects/webpack/base.config.js — see webpack/precis.config.js
install-assets:
	npm install

build-assets: skeleton-manifest
	npx webpack --config webpack/precis.config.js --mode=production

build-assets-dev:
	npx webpack --config webpack/precis.config.js --mode=development

# ── Skeleton Manifest ──────────────────────────────────────────────
# Runs the Django management command to produce a static JSON manifest
# consumed by the Astro frontend (SkeletonBridge.astro). Depends on
# webpack having been run first so the manifest can resolve CSS/JS deps.
skeleton-manifest:
	$(MAKE) -C backend skeleton-manifest

# ── Docker targets ──────────────────────────────────────────────────
build: install-assets build-assets
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

front-logs:
	docker compose logs -f frontend

back-logs:
	docker compose logs -f backend

worker-logs:
	docker compose logs -f worker

status:
	docker compose ps

# ── Rebuild targets ─────────────────────────────────────────────────────────
rebuild-backend:
	docker compose build --no-cache backend worker

rebuild-frontend:
	docker compose build --no-cache frontend

# ── Clean Docker resources ──────────────────────────────────────────────────
clean:
	rm -rf assets/bundles node_modules

clean-docker:
	@echo "$(CYAN)🧹 Cleaning Docker resources for $(PROJECT)...$(NC)"
	-docker compose down -v --remove-orphans 2>/dev/null || true
	-docker system prune -f --volumes 2>/dev/null || true
	@echo "$(GREEN)✅ Clean complete$(NC)"
