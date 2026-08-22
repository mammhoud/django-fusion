# loop-crm backend — Django + django-fusion (unified sales + marketing)
# Mirrors the precis-landing backend Makefile verb set so `make -C backend`
# behaves identically across the workspace.
.PHONY: help dev server worker scheduler install migrate static collectstatic superuser seed seed-demo seed-pages seed-builder shell check test format lint fix i18n makemessages compilemessages

.DEFAULT_GOAL := help
SHELL := /bin/bash

DEFAULT_PORT := 8000
PYTHONPATH := $(CURDIR):$(CURDIR)/apps
export PYTHONPATH
UV_BIN := $(shell which uv 2>/dev/null || (test -x $(HOME)/.local/bin/uv && echo $(HOME)/.local/bin/uv) || echo /root/.local/bin/uv)
UV := $(UV_BIN) --project ../..
UV_RUN := $(UV) run
MANAGE := $(UV_RUN) python manage.py

help: ## Show backend commands
	@echo "=== Loop-CRM Backend (Django + django-fusion) ==="
	@echo "Site: loop-crm"
	@echo "  Nx: nx-* aliases delegate to the workspace Nx graph; run `make help` at projects/loop-crm"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  %-16s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

dev: ## Run Django dev server
	$(MANAGE) runserver 0.0.0.0:$${PORT:-$(DEFAULT_PORT)}

server: ## Production server (gunicorn, WSGI)
	$(UV_RUN) gunicorn wsgi:application --bind 0.0.0.0:$${PORT:-$(DEFAULT_PORT)} --workers $${WORKERS:-4} --timeout $${TIMEOUT:-120} --log-level $${LOG_LEVEL:-info}

worker: ## Dramatiq background worker
	$(MANAGE) rundramatiq --processes 2 --threads 4

scheduler: ## APScheduler cron runner for @task(schedule=...) jobs
	$(UV_RUN) python -m django_fusion.tasks.scheduler

install: ## Install Python deps (workspace venv)
	@cd ../.. && $(UV) sync

migrate: ## Make + apply migrations
	@$(MANAGE) makemigrations --noinput
	@$(MANAGE) migrate --noinput

static: collectstatic ## Alias for collectstatic
collectstatic: ## Collect static files
	@$(MANAGE) collectstatic --noinput

superuser: ## Create superuser (interactive)
	@$(MANAGE) createsuperuser

seed: seed-demo ## Alias for seed-demo

seed-demo: ## Seed the demo workspace + demo accounts (idempotent, superuser)
	@$(MANAGE) seed_demo --superuser

seed-pages: ## Seed the Wagtail landing pages (Home/Pricing/FAQ/Privacy/Terms)
	@$(MANAGE) seed_pages

seed-builder: ## Seed the landing-builder demo pages (theme + dynamic fields)
	@$(MANAGE) seed_builder

shell: ## Django shell
	@$(MANAGE) shell

check: ## Django system checks
	@$(MANAGE) check

test: ## Run Django tests
	@$(MANAGE) test apps --verbosity=2

format: ## Format with ruff
	@$(UV_RUN) ruff format .

lint: ## Lint with ruff
	@$(UV_RUN) ruff check .

fix: ## Auto-fix lint issues
	@$(UV_RUN) ruff check --fix .

makemessages: ## Extract translatable strings into locale/ .po files
	@$(MANAGE) makemessages -l en -l ar --no-wrap

compilemessages: ## Compile .po files into .mo catalogs
	@$(MANAGE) compilemessages -l en -l ar

i18n: makemessages compilemessages ## Extract + compile translations
