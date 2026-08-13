# FormintC purchase-app backend — Django (mirrors landing-fusion conventions)
# ============================================================
.PHONY: help dev server install migrate seed superuser shell check test

.DEFAULT_GOAL := help
SHELL := /bin/bash

DEFAULT_PORT := 8075
PYTHONPATH := $(CURDIR)
export PYTHONPATH
UV_BIN := $(shell which uv 2>/dev/null || echo /root/.local/bin/uv)
UV := $(UV_BIN) --project ../../..
UV_RUN := $(UV) run
MANAGE := $(UV_RUN) python manage.py

help: ## Show backend commands
	@echo "=== FormintC Purchase Backend (Django) ==="
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

dev: ## Run Django dev server (:8075)
	$(MANAGE) runserver 0.0.0.0:$${PORT:-$(DEFAULT_PORT)}

install: ## Install Python deps (workspace venv)
	@cd ../../.. && $(UV) sync

migrate: ## Make + apply migrations
	$(MANAGE) makemigrations shop employee --noinput
	$(MANAGE) migrate --noinput

seed: migrate ## Migrate + seed the catalog + demo users
	$(MANAGE) seed_shop

superuser: ## Create a Django admin superuser
	$(MANAGE) createsuperuser

shell: ## Django shell
	$(MANAGE) shell

check: ## Django system checks
	$(MANAGE) check

test: ## Run backend tests
	$(UV_RUN) pytest tests/
