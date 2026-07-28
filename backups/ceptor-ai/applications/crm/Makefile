# ============================================================
# CRM Makefile – Django, frontend, Docker, and test targets
# ============================================================
.PHONY: help check migrate collectstatic shell build-assets main-assets assets \
        scripts workspace-script test workspace-test \
        runserver docker-build docker-up docker-down docker-logs docker-rebuild \
        docker-shell

SHELL := /bin/bash
SITE_NAME := crm
COMPOSE_FILE := docker-compose.yml

.DEFAULT_GOAL := help

help:
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║   CRM – Makefile                                         ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Django:"
	@echo "  make check             Run Django system checks"
	@echo "  make migrate           Apply Django migrations"
	@echo "  make collectstatic     Collect static files"
	@echo "  make shell             Open Django shell"
	@echo "  make runserver         Run dev server on port 5074"
	@echo ""
	@echo "Frontend:"
	@echo "  make build-assets      Build production webpack bundle"
	@echo "  make assets            Delegate to assets/Makefile"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      Build CRM Docker image"
	@echo "  make docker-up         Start CRM containers"
	@echo "  make docker-down       Stop CRM containers"
	@echo "  make docker-logs       Follow container logs"
	@echo "  make docker-rebuild    Rebuild without cache"
	@echo "  make docker-shell      Shell into the running container"
	@echo ""
	@echo "Testing:"
	@echo "  make test              Run workspace crm tests"
	@echo "  make scripts           Delegate to workspace test scripts"
	@echo ""
	@echo "Delegation:"
	@echo "  make dev               Start development server (delegates to parent)"
	@echo "  make static            Alias for collectstatic"

check:
	@cd .. && ./.venv/bin/python manage.py --site=crm check

migrate:
	@cd .. && ./.venv/bin/python manage.py --site=crm migrate

collectstatic static:
	@cd .. && ./.venv/bin/python manage.py --site=crm collectstatic --noinput

build-assets main-assets:
	@cd .. && $(MAKE) -C assets PROJECT_PATH=crm build

assets:
	@$(MAKE) -C assets $(filter-out $@,$(MAKECMDGOALS))

scripts workspace-script:
	@cd .. && $(MAKE) scripts $(filter-out $@,$(MAKECMDGOALS))

test workspace-test:
	@cd .. && $(MAKE) -C tests crm

shell:
	@cd .. && ./.venv/bin/python manage.py --site=crm shell

runserver dev:
	@cd .. && ./.venv/bin/python manage.py --site=crm runserver 0.0.0.0:5074

# ── Docker targets ────────────────────────────────────────────

docker-build:
	@echo "🔨 Building CRM Docker image..."
	@docker compose -f $(COMPOSE_FILE) build crm-website
	@echo "✅ CRM image built"

docker-up:
	@echo "🚀 Starting CRM containers..."
	@docker compose -f $(COMPOSE_FILE) up -d --build --remove-orphans
	@echo "✅ CRM containers started"
	@docker compose -f $(COMPOSE_FILE) ps

docker-down:
	@echo "🛑 Stopping CRM containers..."
	@docker compose -f $(COMPOSE_FILE) down --remove-orphans
	@echo "✅ CRM containers stopped"

docker-logs:
	@docker compose -f $(COMPOSE_FILE) logs -f --tail=100

docker-rebuild:
	@echo "🔨 Rebuilding CRM Docker image (no cache)..."
	@docker compose -f $(COMPOSE_FILE) build --no-cache crm-website
	@echo "✅ CRM image rebuilt"

docker-shell:
	@docker compose -f $(COMPOSE_FILE) exec crm-website /bin/bash

# Delegated subtargets
.PHONY: list health containers production production-simple domains
list health containers production production-simple domains:
	@:
