# ============================================================
# VResume Makefile – Django, frontend, Docker, and test targets
# ============================================================
.PHONY: help check migrate collectstatic shell build-assets build-assets-dev \
        main-assets assets scripts workspace-script test workspace-test test-pages \
        runserver docker-build docker-up docker-down docker-logs docker-rebuild \
        docker-shell

SHELL := /bin/bash
SITE_NAME := vresume
COMPOSE_FILE := docker-compose.yml

help:
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║   VResume – Makefile                                    ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Django:"
	@echo "  make check             Run Django system checks"
	@echo "  make migrate           Apply Django migrations"
	@echo "  make collectstatic     Collect static files"
	@echo "  make shell             Open Django shell"
	@echo "  make runserver         Run dev server on port 5072"
	@echo ""
	@echo "Frontend:"
	@echo "  make build-assets      Build production webpack bundle"
	@echo "  make build-assets-dev  Build development webpack bundle"
	@echo "  make assets            Delegate to assets/Makefile"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      Build VResume Docker image"
	@echo "  make docker-up         Start VResume containers"
	@echo "  make docker-down       Stop VResume containers"
	@echo "  make docker-logs       Follow container logs"
	@echo "  make docker-rebuild    Rebuild without cache"
	@echo "  make docker-shell      Shell into the running container"
	@echo ""
	@echo "Testing:"
	@echo "  make test              Run workspace vresume tests"
	@echo "  make test-pages        Run shell page checks"
	@echo "  make scripts           Delegate to workspace test scripts"

check:
	@cd .. && ./.venv/bin/python manage.py --site=vresume check

migrate:
	@cd .. && ./.venv/bin/python manage.py --site=vresume migrate

collectstatic:
	@cd .. && ./.venv/bin/python manage.py --site=vresume collectstatic --noinput

build-assets main-assets:
	@cd .. && $(MAKE) -C assets PROJECT_PATH=vresume build-vresume

build-assets-dev:
	@cd .. && PROJECT_PATH=vresume npm --prefix assets run build:dev

assets:
	@$(MAKE) -C assets $(filter-out $@,$(MAKECMDGOALS))

scripts workspace-script:
	@cd .. && $(MAKE) scripts $(filter-out $@,$(MAKECMDGOALS))

test workspace-test:
	@cd .. && $(MAKE) -C tests vresume

test-pages:
	@cd .. && $(MAKE) -C tests/scripts vresume-pages

shell:
	@cd .. && ./.venv/bin/python manage.py --site=vresume shell

runserver:
	@cd .. && ./.venv/bin/python manage.py --site=vresume runserver 0.0.0.0:5072

# ── Docker targets ────────────────────────────────────────────

docker-build:
	@echo "🔨 Building VResume Docker image..."
	@docker compose -f $(COMPOSE_FILE) build vresume-web
	@echo "✅ VResume image built"

docker-up:
	@echo "🚀 Starting VResume containers..."
	@docker compose -f $(COMPOSE_FILE) up -d --build --remove-orphans
	@echo "✅ VResume containers started"
	@docker compose -f $(COMPOSE_FILE) ps

docker-down:
	@echo "🛑 Stopping VResume containers..."
	@docker compose -f $(COMPOSE_FILE) down --remove-orphans
	@echo "✅ VResume containers stopped"

docker-logs:
	@docker compose -f $(COMPOSE_FILE) logs -f --tail=100

docker-rebuild:
	@echo "🔨 Rebuilding VResume Docker image (no cache)..."
	@docker compose -f $(COMPOSE_FILE) build --no-cache vresume-web
	@echo "✅ VResume image rebuilt"

docker-shell:
	@docker compose -f $(COMPOSE_FILE) exec vresume-web /bin/bash

# Delegated subtargets are consumed by nested Makefiles.
.PHONY: list health containers production production-simple domains vresume-pages
list health containers production production-simple domains vresume-pages:
	@:

# @tested VResume - dev, migrate, collectstatic, check, test targets verified
