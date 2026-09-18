# Django backend, tests, linting, server, and frontend delegation
# ============================================================
.PHONY: help dev server scheduler install install-internal setup migrate static collectstatic \
        superuser test test-quick test-url populate-data populate-data-test-only \
        populate-data-pages-only populate-data-clear test-reports clean-test-reports check format \
        lint fix fix-unused shell debug db-shell reset-db clean-migrations \
        reset-migrations clean-python clean env-show \
        frontend-install frontend-build frontend-watch frontend-production build-assets main-assets assets \
        workspace-assets workspace-test scripts workspace-script css-purge css-analyze frontend-clean assets-setup webpack-validate \
        erd erd-all

.DEFAULT_GOAL := help
SHELL := /bin/bash

# Colors
RED    := \033[0;31m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
CYAN   := \033[0;36m
NC     := \033[0m

SITE_NAME := $(notdir $(abspath ..))
DEFAULT_PORT := 5070
# PYTHONPATH includes site root, workspace root, www subdirectory, and libs
PYTHONPATH := $(CURDIR):$(CURDIR)/www:$(abspath ..):$(abspath ../../../..):$(abspath ../../../../libs/django-fusion/src)
export PYTHONPATH
UV_BIN := $(shell which uv 2>/dev/null || (test -x $(HOME)/.local/bin/uv && echo $(HOME)/.local/bin/uv) || echo /root/.local/bin/uv)
UV := $(UV_BIN) --project ../../..
UV_RUN := $(UV) run --frozen
MANAGE := $(UV_RUN) python manage.py
VENV_DIR := ../.venv
ASSETS_MAKE := assets/Makefile

# Helper function to validate and clean broken venv
define clean_broken_venv
	@if [ -d "$(VENV_DIR)" ]; then \
		if [ ! -f "$(VENV_DIR)/bin/python" ] || ! $(VENV_DIR)/bin/python --version >/dev/null 2>&1; then \
			echo -e "$(YELLOW)⚠️  Broken venv detected, removing...$(NC)"; \
			rm -rf "$(VENV_DIR)"; \
		fi; \
	fi
endef

help: ## Show Django + frontend commands help
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(CYAN)      DJANGO & FRONTEND COMMANDS         $(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BLUE)Site: $(SITE_NAME)$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-25s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

env-show: ## Show active Django website environment wiring
	@echo -e "$(CYAN)Environment wiring$(NC)"
	@echo "  SITE_NAME=$(SITE_NAME)"
	@echo "  PYTHONPATH=$(PYTHONPATH)"
	@$(MANAGE) shell -c "from django.conf import settings; print('  DJANGO_SETTINGS_MODULE=' + __import__('os').environ.get('DJANGO_SETTINGS_MODULE', 'settings')); print('  BASE_DIR=' + str(settings.BASE_DIR)); print('  SITE_DOMAIN=' + str(getattr(settings, 'SITE_DOMAIN', ''))); print('  WAGTAIL_SITE_NAME=' + str(getattr(settings, 'WAGTAIL_SITE_NAME', '')))"

dev: ## Run Django dev server
	$(call clean_broken_venv)
	$(MANAGE) runserver 0.0.0.0:$${PORT:-$(DEFAULT_PORT)}

scheduler: ## APScheduler cron runner for @task(schedule=...) jobs
	$(UV_RUN) python -m django_fusion.tasks.scheduler

server: ## Production server (auto-select WSGI/ASGI based on SERVER_TYPE env var)
	$(call clean_broken_venv)
	@echo -e "$(CYAN)Starting production server for $(SITE_NAME)$(NC)"
	@$(MAKE) webpack-validate
	@echo -e "$(BLUE)Populating initial data before server start...$(NC)"; \
	$(MAKE) populate-data || true
	@DB_NAME=$${DB_NAME_CTC:-db_precis_ctc}; \ 
	HOST=$${HOST:-0.0.0.0}; \
	PORT=$${PORT:-$(DEFAULT_PORT)}; \
	WORKERS=$${WORKERS:-4}; \
	TIMEOUT=$${TIMEOUT:-120}; \
	LOG_LEVEL=$${LOG_LEVEL:-info}; \
	SERVER_TYPE=$${SERVER_TYPE:-wsgi}; \
	# IMPORTANT: default to the per-site `server:application` (defined in
	# projects/<site>/server.py) rather than the Django default www.{asgi,wsgi}:
	# application. The bare `www.asgi/wsgi` modules skip the env-var bootstrap
	# (`DJANGO_SITE`, `DJANGO_SETTINGS_MODULE`, etc.) that Dynaconf needs to
	# load the postgres DATABASE settings — and silently fall back to the
	# SQLite default database, which has no migrations applied.
	if [ "$$SERVER_TYPE" = "asgi" ]; then \
		APP_MODULE=$${APP_MODULE:-server:application}; \
		echo "ASGI mode detected – using Uvicorn worker"; \
		$(UV_RUN) gunicorn $$APP_MODULE --bind $$HOST:$$PORT --workers $$WORKERS --timeout $$TIMEOUT --log-level $$LOG_LEVEL -k uvicorn.workers.UvicornWorker; \
	else \
		APP_MODULE=$${APP_MODULE:-server:application}; \
		echo "WSGI mode detected – using sync workers"; \
		$(UV_RUN) gunicorn $$APP_MODULE --bind $$HOST:$$PORT --workers $$WORKERS --timeout $$TIMEOUT --log-level $$LOG_LEVEL; \
	fi


assets: ## Delegate to this project's assets/Makefile (pass target after assets)
	@$(MAKE) -C assets $(filter-out $@,$(MAKECMDGOALS))

build-assets main-assets: frontend-production ## Build this project's main frontend assets

workspace-assets: ## Delegate to workspace assets Makefile for this project
	@PROJECT_PATH=$(SITE_NAME) $(MAKE) -C ../assets $(filter-out $@,$(MAKECMDGOALS))

workspace-test: ## Run workspace pytest for this project
	@cd ../.. && $(MAKE) tests-website WEBSITE=precis-ctc

scripts workspace-script: ## Delegate to workspace test utility scripts
	@cd ../.. && $(MAKE) scripts $(filter-out $@,$(MAKECMDGOALS))

frontend-install: ## Install npm dependencies
	@$(MAKE) -C assets install

frontend-build: ## Build frontend (development)
	@$(MAKE) -C assets build

frontend-watch: ## Watch frontend for changes
	@$(MAKE) -C assets watch

frontend-production: ## Build frontend (production)
	@$(MAKE) -C assets production

css-purge: ## Purge unused CSS
	@$(MAKE) -C assets purge

css-analyze: ## Analyze CSS bundle size
	@$(MAKE) -C assets analyze

frontend-clean: ## Clean frontend build artifacts
	@$(MAKE) -C assets clean

assets-setup: frontend-install frontend-build ## Full frontend setup (install + build)

webpack-validate: ## Validate/rebuild webpack bundles if missing or invalid
	@echo -e "$(BLUE)Validating webpack bundles...$(NC)"
	@BUNDLES_JSON=$$(pwd)/assets/bundles/$(SITE_NAME)/bundles.json; \
	if [ ! -f "$$BUNDLES_JSON" ]; then \
		echo -e "$(YELLOW)⚠️  bundles.json not found. Rebuilding frontend...$(NC)"; \
		$(MAKE) assets-setup; \
	elif ! python3 -c "import json; json.load(open('$$BUNDLES_JSON'))" 2>/dev/null; then \
		echo -e "$(YELLOW)⚠️  bundles.json is invalid. Rebuilding frontend...$(NC)"; \
		$(MAKE) assets-setup; \
	else \
		echo -e "$(GREEN)✅ Webpack bundles valid$(NC)"; \
	fi

install: ## Install Python dependencies
	$(call clean_broken_venv)
	@echo -e "$(BLUE)Installing Python deps...$(NC)"
	@$(UV) sync
	@echo -e "$(GREEN)✅ Installed$(NC)"
	# Install local django_fusion library in editable mode
	@echo -e "$(BLUE)Installing local django_fusion library...$(NC)"
	@cd $(abspath ../../../../libs/django-fusion) && $(UV) pip install -e .
	@echo -e "$(GREEN)✅ Local library installed$(NC)"

install-internal: ## Refresh mammhoud GitHub packages (django-fusion)
	$(call clean_broken_venv)
	@echo -e "$(BLUE)Installing mammhoud GitHub packages...$(NC)"
	@$(UV) sync --upgrade-package django-fusion
	@echo -e "$(GREEN)✅ Internal packages refreshed from GitHub$(NC)"

setup: ## Full setup (frontend, migrations, static, checks, superuser, data)
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(CYAN)        FULL SETUP                       $(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@$(MAKE) install
	@echo ""
	@echo -e "$(BLUE)Building frontend (webpack)...$(NC)"
	@$(MAKE) assets-setup
	@echo -e "$(GREEN)✅ Frontend built$(NC)"
	@echo ""
	@echo -e "$(BLUE)Running migrations...$(NC)"
	@$(MANAGE) makemigrations --noinput
	@$(MANAGE) migrate --noinput
	@echo -e "$(GREEN)✅ Migrations done$(NC)"
	@echo ""
	@echo -e "$(BLUE)Collecting static (includes webpack bundles)...$(NC)"
	@$(MANAGE) collectstatic --noinput
	@echo -e "$(GREEN)✅ Static collected$(NC)"
	@echo ""
	@echo -e "$(BLUE)Django checks...$(NC)"
	@$(MANAGE) check || echo -e "$(YELLOW)⚠️  Warnings$(NC)"
	@echo -e "$(GREEN)✅ Checks done$(NC)"
	@echo ""
	@if [ -n "$$DJANGO_SUPERUSER_PASSWORD" ]; then \
		$(MANAGE) createsuperuser --noinput || true; \
		echo -e "$(GREEN)✅ Superuser created$(NC)"; \
	else \
		echo -e "$(YELLOW)Set DJANGO_SUPERUSER_PASSWORD to auto-create superuser$(NC)"; \
	fi
	@echo ""
	@echo -e "$(BLUE)Populating data...$(NC)"
	@$(UV_RUN) python -m tests.data_populator --verbose || true
	@echo -e "$(GREEN)✅ Setup complete$(NC)"

migrate: ## Run migrations
	@echo -e "$(BLUE)Running migrations...$(NC)"
	@$(MANAGE) makemigrations --noinput
	@$(MANAGE) migrate --noinput
	@echo -e "$(GREEN)✅ Migrations done$(NC)"

static: collectstatic ## Alias for collectstatic

collectstatic: ## Collect static
	@echo -e "$(BLUE)Collecting static...$(NC)"
	@$(MANAGE) collectstatic --noinput
	@echo -e "$(GREEN)✅ Static collected$(NC)"

superuser: ## Create superuser (interactive)
	@$(MANAGE) createsuperuser

test: ## Run comprehensive tests
	@echo -e "$(BLUE)Running tests with isolated SQLite test settings...$(NC)"
	@DJANGO_SETTINGS_MODULE=tests.test_settings $(UV_RUN) pytest tests -q
	@echo -e "$(GREEN)✅ Tests done$(NC)"

test-quick: ## Run tests (less output)
	@DJANGO_SETTINGS_MODULE=tests.test_settings $(UV_RUN) pytest tests -q

test-url: ## Test custom URL (make test-url URL=http://...)
	@BASE_URL=$(URL) $(UV_RUN) pytest tests -q

populate-data: ## Populate test data + pages
	@$(UV_RUN) python -m tests.data_populator --verbose

populate-data-test-only: ## Populate test data only
	@$(UV_RUN) python -m tests.data_populator --test-data --verbose

populate-data-pages-only: ## Populate pages only
	@$(UV_RUN) python -m tests.data_populator --pages --verbose

populate-data-clear: ## Clear test data
	@$(UV_RUN) python -m tests.data_populator --clear

test-reports: ## Show latest test reports
	@find test_reports -maxdepth 1 -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -5 || echo "No reports"

clean-test-reports: ## Clean test reports
	@rm -rf test_reports/

check: ## Django system checks
	@$(MANAGE) check

format: ## Format code with ruff
	@$(UV_RUN) ruff format .

lint: ## Fast lint (unused imports)
	@$(UV_RUN) ruff check --select F401,F841,I001 --fix --no-cache .

fix: ## Fix all ruff issues
	@$(UV_RUN) ruff check --fix .

fix-unused: ## Remove unused imports
	@$(UV_RUN) ruff check --select F401,F841 --fix .

shell: ## Django shell (shell_plus if available)
	@$(MANAGE) shell_plus --ipython 2>/dev/null || $(MANAGE) shell

debug: ## Debug shell with ipdb
	@$(UV_RUN) python -m ipdb manage.py shell

db-shell: ## PostgreSQL shell (if Docker)
	@docker compose exec db psql -U postgres 2>/dev/null || echo "DB not running"

reset-db: ## Danger: delete all data and migrations, then recreate
	@echo -e "$(RED)⚠️  This deletes all data!$(NC)"
	@read -p "Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		rm -f db.sqlite3 ../dev_db.sqlite3 2>/dev/null || true; \
		find . -path "*/migrations/*.py" ! -path "*/.venv/*" ! -name "__init__.py" -delete; \
		find . -path "*/migrations/*.pyc" -delete; \
		$(MAKE) migrate; \
		echo -e "$(GREEN)✅ Reset done$(NC)"; \
	else \
		echo "Cancelled"; \
	fi

clean-migrations: ## Delete all migration files
	@echo -e "$(RED)Danger: deleting migration files!$(NC)"
	@find . -path "*/migrations/*.py" ! -path "*/.venv/*" ! -name "__init__.py" -delete
	@find . -path "*/migrations/*.pyc" -delete
	@echo -e "$(GREEN)✅ Migration files removed$(NC)"

reset-migrations: clean-migrations ## Delete migrations and recreate
	@$(MANAGE) makemigrations --noinput
	@$(MANAGE) migrate --noinput
	@echo -e "$(GREEN)✅ Migrations reset$(NC)"

clean-python: ## Clean Python cache artifacts (SAFE — never deletes source .py/.tsx/.rs files)
	@echo -e "$(BLUE)Cleaning Python cache...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -not -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -not -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null || true
	@echo -e "$(GREEN)✅ Python cache cleaned$(NC)"

clean: clean-python clean-test-reports frontend-clean ## Django + frontend clean
	@echo -e "$(GREEN)✅ Django cleaned$(NC)"

skeleton-manifest: ## Generate skeleton manifest for Astro build (runs after webpack)
	@echo -e "$(BLUE)Generating skeleton manifest...$(NC)"
	@$(MANAGE) generate_skeleton_manifest \
		--output assets/static/skeleton-manifest.json \
		--page blog/blog_index.html \
		--page blog/blog_detail.html \
		--page blog/blog_list.html \
		--page courses/catalog.html \
		--page courses/detail.html
	@echo -e "$(GREEN)✅ Skeleton manifest generated → assets/static/skeleton-manifest.json$(NC)"

# Delegated subtargets are consumed by nested Makefiles.
.PHONY: list health containers production production-simple domains vresume-pages
list health containers production production-simple domains vresume-pages:
	@:

# ── ERD — database schema diagrams ─────────────────────────────────────────
# Uses django-extensions graph_models → pydot (DOT format) → graphviz dot (PNG).
# -X Note,AbstractNote,AbstractSharedNote excludes abstract fusion models that
# have no concrete counterpart in this project's app registry.
# Two-step approach avoids memory issues with very large graphs.
# Requires: graphviz system package + pydot + django-extensions in INSTALLED_APPS.
ERD_OUT := ../docs/erd
ERD_APPS ?= apps_core pages handlers accounts lms blog products profile precis_auth tasks
ERD_EXCLUDE ?= Note,AbstractNote,AbstractSharedNote

erd: ## Generate ERD PNG for all apps → docs/erd/
	@echo -e "$(BLUE)Generating ERD (DOT intermediate)...$(NC)"
	@mkdir -p $(ERD_OUT)
	@$(MANAGE) graph_models \
		--pydot -g --color-code-deletions \
		-X $(ERD_EXCLUDE) \
		--output $(ERD_OUT)/precis_ctc_erd.dot \
		$(ERD_APPS) 2>/dev/null
	@echo -e "$(BLUE)Rendering PNG...$(NC)"
	@dot -Tpng -Gsize="24,16\!" -Gdpi=96 \
		$(ERD_OUT)/precis_ctc_erd.dot \
		-o $(ERD_OUT)/precis_ctc_erd.png
	@echo -e "$(GREEN)✅ ERD saved → $(ERD_OUT)/precis_ctc_erd.png$(NC)"

erd-all: ## Generate per-app ERD PNGs → docs/erd/
	@echo -e "$(BLUE)Generating per-app ERDs...$(NC)"
	@mkdir -p $(ERD_OUT)
	@for app in apps_core pages handlers accounts lms blog products profile precis_auth tasks; do \
		echo -e "  $(CYAN)→ $$app$(NC)"; \
		$(MANAGE) graph_models --pydot -g --color-code-deletions \
			-X $(ERD_EXCLUDE) \
			--output $(ERD_OUT)/$$app.dot $$app 2>/dev/null && \
		dot -Tpng -Gsize="16,12\!" -Gdpi=96 \
			$(ERD_OUT)/$$app.dot -o $(ERD_OUT)/$$app.png 2>/dev/null || \
			echo -e "  $(YELLOW)⚠️  $$app skipped$(NC)"; \
	done
	@echo -e "$(GREEN)✅ Per-app ERDs saved → $(ERD_OUT)/$(NC)"
