# v1/Makefile – Django backend, tests, linting, server, and frontend delegation
# ============================================================
.PHONY: help dev server install setup migrate static collectstatic \
        superuser test test-quick test-url populate-data populate-data-test-only \
        populate-data-pages-only populate-data-clear test-reports clean-test-reports check format \
        lint fix fix-unused shell debug db-shell reset-db clean-migrations \
        reset-migrations clean-python clean \
        frontend-install frontend-build frontend-watch frontend-production \
        css-purge css-analyze frontend-clean assets-setup webpack-validate

.DEFAULT_GOAL := help

# Colors
RED    := \033[0;31m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
CYAN   := \033[0;36m
NC     := \033[0m

PYTHONPATH := $(shell pwd)
export PYTHONPATH
UV := $(shell which uv 2>/dev/null || echo /root/.local/bin/uv)
MANAGE := $(UV) --no-cache run python manage.py
VENV_DIR := .venv

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
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-25s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

dev: ## Run Django dev server (Uvicorn)
	$(call clean_broken_venv)
	$(MANAGE) runserver

# Unified production server – automatically chooses WSGI or ASGI
server: ## Production server (auto-select WSGI/ASGI based on SERVER_TYPE env var)
	$(call clean_broken_venv)
	@echo -e "$(CYAN)Starting production server$(NC)"
	@$(MAKE) webpack-validate
	@echo -e "$(BLUE)Populating initial data before server start...$(NC)"; \
	$(MAKE) populate-data || true; \
	# Set defaults
	@HOST=$${HOST:-0.0.0.0}; \
	PORT=$${PORT:-5072}; \
	WORKERS=$${WORKERS:-4}; \
	TIMEOUT=$${TIMEOUT:-120}; \
	LOG_LEVEL=$${LOG_LEVEL:-info}; \
	APP_MODULE=$${APP_MODULE:-core.server:application}; \
	SERVER_TYPE=$${SERVER_TYPE:-wsgi}; \
	if [ "$$SERVER_TYPE" = "asgi" ]; then \
		echo "ASGI mode detected – using Uvicorn worker"; \
		$(UV) run gunicorn $$APP_MODULE \
			--bind $$HOST:$$PORT \
			--workers $$WORKERS \
			--timeout $$TIMEOUT \
			--log-level $$LOG_LEVEL \
			-k uvicorn.workers.UvicornWorker; \
	else \
		echo "WSGI mode detected – using sync workers"; \
		$(UV) run gunicorn $$APP_MODULE \
			--bind $$HOST:$$PORT \
			--workers $$WORKERS \
			--timeout $$TIMEOUT \
			--log-level $$LOG_LEVEL; \
	fi

# Frontend delegation targets (call assets/Makefile)
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

# asset-setup: full frontend setup (install + build)
assets-setup: frontend-install frontend-build ## Full frontend setup (install + build)

webpack-validate: ## Validate/rebuild webpack bundles if missing or invalid
	@echo -e "$(BLUE)Validating webpack bundles...$(NC)"
	@BUNDLES_JSON=$$(pwd)/assets/bundles/bundles.json; \
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
	@$(UV) run python -m tests.data_populator --verbose || true
	@echo -e "$(GREEN)✅ Setup complete$(NC)"

migrate: ## Run migrations
	@echo -e "$(BLUE)Running migrations...$(NC)"
	@$(MANAGE) makemigrations --noinput
	@$(MANAGE) migrate --noinput
	@echo -e "$(GREEN)✅ Migrations done$(NC)"

static: ## Collect static
	@echo -e "$(BLUE)Collecting static...$(NC)"
	@$(MANAGE) collectstatic --noinput
	@echo -e "$(GREEN)✅ Static collected$(NC)"

superuser: ## Create superuser (interactive)
	@$(MANAGE) createsuperuser

test: ## Run comprehensive tests
	@echo -e "$(BLUE)Running tests...$(NC)"
	@$(UV) run python -m tests.runner --verbose
	@echo -e "$(GREEN)✅ Tests done$(NC)"

test-quick: ## Run tests (less output)
	@$(UV) run python -m tests.runner

test-url: ## Test custom URL (make test-url URL=http://...)
	@$(UV) run python -m tests.runner --base-url $(URL) --verbose

populate-data: ## Populate test data + pages
	@$(UV) run python -m tests.data_populator --verbose

populate-data-test-only: ## Populate test data only
	@$(UV) run python -m tests.data_populator --test-data --verbose

populate-data-pages-only: ## Populate pages only
	@$(UV) run python -m tests.data_populator --pages --verbose

populate-data-clear: ## Clear test data
	@$(UV) run python -m tests.data_populator --clear

test-reports: ## Show latest test reports
	@ls -lht test_reports/ 2>/dev/null | head -5 || echo "No reports"

clean-test-reports: ## Clean test reports
	@rm -rf test_reports/

check: ## Django system checks
	@$(MANAGE) check

format: ## Format code with ruff
	@ruff format .

lint: ## Fast lint (unused imports)
	@ruff check --select F401,F841,I001 --fix --no-cache .

fix: ## Fix all ruff issues
	@ruff check --fix .

fix-unused: ## Remove unused imports
	@ruff check --select F401,F841 --fix .

shell: ## Django shell (shell_plus if available)
	@$(MANAGE) shell_plus --ipython 2>/dev/null || $(MANAGE) shell

debug: ## Debug shell with ipdb
	@$(UV) run python -m ipdb manage.py shell

db-shell: ## PostgreSQL shell (if Docker)
	@docker compose exec db psql -U postgres 2>/dev/null || echo "DB not running"

reset-db: ## Danger: delete all data and migrations, then recreate
	@echo -e "$(RED)⚠️  This deletes all data!$(NC)"
	@read -p "Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		rm -f db.sqlite3 2>/dev/null || true; \
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

clean-python: ## Clean Python cache artifacts
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
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo -e "$(GREEN)✅ Python cache cleaned$(NC)"

clean: clean-python clean-test-reports frontend-clean ## Django + frontend clean
	@echo -e "$(GREEN)✅ Django cleaned$(NC)"
