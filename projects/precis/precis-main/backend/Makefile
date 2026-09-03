# precis-landing backend — Django + Wagtail (landing-only)
# Mirrors projects/cms-fusion/backend conventions, trimmed to the landing slice.
# ============================================================
.PHONY: help dev server scheduler install migrate static collectstatic superuser shell check test format lint fix erd erd-all

.DEFAULT_GOAL := help
SHELL := /bin/bash

# Colors
CYAN   := \033[0;36m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
RED    := \033[0;31m
NC     := \033[0m

DEFAULT_PORT := 8074
PYTHONPATH := $(CURDIR):$(CURDIR)/apps
export PYTHONPATH
UV_BIN := $(shell which uv 2>/dev/null || (test -x $(HOME)/.local/bin/uv && echo $(HOME)/.local/bin/uv) || echo /root/.local/bin/uv)
UV := $(UV_BIN) --project ../../..
UV_RUN := $(UV) run
MANAGE := $(UV_RUN) python manage.py

help: ## Show backend commands
	@echo -e "$(CYAN)=== Precis Landing Backend (Django + Wagtail) ===$(NC)"
	@echo -e "$(BLUE)Site: precis-landing$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-18s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

dev: ## Run Django dev server
	$(MANAGE) runserver 0.0.0.0:$${PORT:-$(DEFAULT_PORT)}

server: ## Production server (gunicorn, WSGI)
	$(UV_RUN) gunicorn wsgi:application --bind 0.0.0.0:$${PORT:-$(DEFAULT_PORT)} --workers $${WORKERS:-4} --timeout $${TIMEOUT:-120} --log-level $${LOG_LEVEL:-info}

scheduler: ## APScheduler cron runner for @task(schedule=...) jobs
	$(UV_RUN) python -m django_fusion.tasks.scheduler

install: ## Install Python deps (workspace venv)
	@echo -e "$(BLUE)Syncing workspace deps...$(NC)"
	@cd ../.. && $(UV) sync
	@echo -e "$(GREEN)✅ Installed$(NC)"

migrate: ## Make + apply migrations
	@echo -e "$(BLUE)Making migrations...$(NC)"
	@$(MANAGE) makemigrations --noinput
	@echo -e "$(BLUE)Applying migrations...$(NC)"
	@$(MANAGE) migrate --noinput
	@echo -e "$(GREEN)✅ Migrations done$(NC)"

static: collectstatic ## Alias for collectstatic
collectstatic: ## Collect static files
	@$(MANAGE) collectstatic --noinput

superuser: ## Create superuser — interactive, or non-interactive with DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD set
	@if [ -n "$${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "$${DJANGO_SUPERUSER_PASSWORD:-}" ]; then \
		echo -e "$(BLUE)Creating superuser non-interactively (DJANGO_SUPERUSER_EMAIL/PASSWORD)...$(NC)"; \
		$(MANAGE) createsuperuser --noinput --username "$${DJANGO_SUPERUSER_USERNAME:-admin}"; \
	else \
		$(MANAGE) createsuperuser; \
	fi

shell: ## Django shell
	@$(MANAGE) shell

check: ## Django system checks
	@$(MANAGE) check

seed: ## Create the Wagtail page tree + default landing content
	@$(MANAGE) seed_pages

skeleton-manifest: ## Generate skeleton manifest for Astro build (runs after webpack)
	@echo -e "$(BLUE)Generating skeleton manifest...$(NC)"
	@$(MANAGE) generate_skeleton_manifest \
		--output assets/static/skeleton-manifest.json \
		--page pages/home.html \
		--page pages/pricing.html \
		--page pages/about.html \
		--page pages/contact.html \
		--page pages/features.html \
		--page pages/services.html \
		--page pages/products.html \
		--page pages/blog.html
	@echo -e "$(GREEN)✅ Skeleton manifest generated → assets/static/skeleton-manifest.json$(NC)"

test: ## Run Django tests
	@$(MANAGE) test apps.pages --verbosity=2

format: ## Format with ruff
	@$(UV_RUN) ruff format .

lint: ## Fast lint (unused imports)
	@$(UV_RUN) ruff check --select F401,F841,I001 --fix --no-cache .

fix: ## Fix all ruff issues
	@$(UV_RUN) ruff check --fix .

# ── ERD — database schema diagrams ─────────────────────────────────────────
# Uses django-extensions graph_models → pydot (DOT format) → graphviz dot (PNG).
# Two-step approach avoids memory issues with very large graphs.
# Requires: graphviz system package + pydot + django-extensions in INSTALLED_APPS.
ERD_OUT := ../docs/erd
ERD_APPS ?= content pages handlers landing_auth learning tasks components shared

erd: ## Generate ERD PNG for all apps → docs/erd/
	@echo -e "$(BLUE)Generating ERD (DOT intermediate)...$(NC)"
	@mkdir -p $(ERD_OUT)
	@$(MANAGE) graph_models \
		--pydot -g --color-code-deletions \
		--output $(ERD_OUT)/precis_main_erd.dot \
		$(ERD_APPS) 2>/dev/null
	@echo -e "$(BLUE)Rendering PNG...$(NC)"
	@dot -Tpng -Gsize="24,16\!" -Gdpi=96 \
		$(ERD_OUT)/precis_main_erd.dot \
		-o $(ERD_OUT)/precis_main_erd.png
	@echo -e "$(GREEN)✅ ERD saved → $(ERD_OUT)/precis_main_erd.png$(NC)"

erd-all: ## Generate per-app ERD PNGs → docs/erd/
	@echo -e "$(BLUE)Generating per-app ERDs...$(NC)"
	@mkdir -p $(ERD_OUT)
	@for app in content pages handlers landing_auth learning tasks components shared; do \
		echo -e "  $(CYAN)→ $$app$(NC)"; \
		$(MANAGE) graph_models --pydot -g --color-code-deletions \
			--output $(ERD_OUT)/$$app.dot $$app 2>/dev/null && \
		dot -Tpng -Gsize="16,12\!" -Gdpi=96 \
			$(ERD_OUT)/$$app.dot -o $(ERD_OUT)/$$app.png 2>/dev/null || \
			echo -e "  $(YELLOW)⚠️  $$app skipped$(NC)"; \
	done
	@echo -e "$(GREEN)✅ Per-app ERDs saved → $(ERD_OUT)/$(NC)"
