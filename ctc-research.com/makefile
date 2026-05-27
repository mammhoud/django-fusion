# Makefile for Django + Frontend Development with Python Sync
# ============================================================

# Configuration
.PHONY: help menu dev up down sync clean setup test shell migrate static superuser check format lint fix-unused frontend docs
.DEFAULT_GOAL := help

# Color codes for output
RED    := \033[0;31m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
CYAN   := \033[0;36m
PURPLE := \033[0;35m
BOLD   := \033[1m
NC     := \033[0m

# Project variables
PROJECT_NAME := ctc-research
PYTHONPATH := $(shell pwd)
export PYTHONPATH
PYTHON_DIRS := . core apps config theme
PYTHON := python
UV := uv
MANAGE := $(UV) --no-cache run ./com
DOCKER_COMPOSE := $(shell command -v docker-compose 2>/dev/null || echo "docker compose")
SYNC_PY := $(UV) run configs sync

# Frontend configuration
NPM := npm
NPX := npx
NODE_ENV := development
WEBPACK_CONFIG := webpack/main.config.js
BUNDLES_DIR := $(if $(wildcard assets/bundles),assets/bundles,static/bundles)
POSTCSS_CONFIG := postcss.config.js

# Variant configurations
# Use cases:
# - basic: Lightweight version for general projects (No LMS, No Blog).
# - blogger: Content-focused site (Includes Blog, No LMS).
# - lms: Full Learning Management System (Default).
VARIANT_PY := $(UV) run -m configs variant

##@ Main Menu & Help

help: ## 📚 Display this help message
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)🚀 Django Development Environment$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@echo -e "$(GREEN)Available commands:$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { \
		if ($$1 == "menu") next; \
		if ($$1 == "help") next; \
		printf "  $(CYAN)%-25s$(NC) %s\n", $$1, $$2 \
	}' $(MAKEFILE_LIST)
	@echo ""
	@echo -e "$(YELLOW)Quick start:$(NC)"
	@echo "  make setup    # First-time setup"
	@echo "  make dev      # Start development server"
	@echo "  make menu     # Interactive menu"
	@echo "  make docs     # Generate documentation"
	@echo ""

menu: ## 🎛️ Interactive development menu
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)🔧 Development Menu$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@echo "What would you like to do?"
	@echo ""
	@echo "1. 🚀 Start Django server with Uvicorn (auto-reload)"
	@echo "2. 📦 Install/Update Python dependencies"
	@echo "3. 🔄 Run sync (Python-based)"
	@echo "4. 🗃️  Run database migrations"
	@echo "5. 🧹 Collect static files"
	@echo "6. 👑 Create superuser"
	@echo "7. 🔍 Run Django checks"
	@echo "8. 🧪 Run tests"
	@echo "9. 🐚 Open Django shell"
	@echo "10. 🎨 Build frontend (production)"
	@echo "11. 👁️  Watch frontend (development)"
	@echo "12. 🧹 Clean unused CSS (PurgeCSS)"
	@echo "13. 📖 Generate documentation"
	@echo "14. ⚡ Full setup (all of the above)"
	@echo "0. 🚪 Exit"
	@echo ""
	@read -p "Choose an option (0-14): " choice; \
	echo ""; \
	case $$choice in \
		1) make dev;; \
		2) make install;; \
		3) make sync-interactive;; \
		4) make migrate;; \
		5) make static;; \
		6) make superuser;; \
		7) make check;; \
		8) make test;; \
		9) make shell;; \
		10) make frontend-production;; \
		11) make frontend-watch;; \
		12) make css-purge;; \
		13) make docs;; \
		14) make setup;; \
		0) echo -e "$(GREEN)Goodbye! 👋$(NC)"; exit 0;; \
		*) echo -e "$(RED)Invalid option$(NC)";; \
	esac

docs: ## 📖 Generate commands documentation
	@echo -e "$(BLUE)Generating commands documentation...$(NC)"
	@make help | sed 's/\x1b\[[0-9;]*m//g' > commands.md
	@echo -e "$(GREEN)✅ Documentation generated: commands.md$(NC)"

##@ Development Server

dev: ## 🚀 Start Django development server (Uvicorn)
	$(UV) run ./com runserver

run: dev ## 🏃‍♂️ Alias for dev
server: dev ## 🌐 Alias for dev

##@ Frontend Build System

frontend-install: ## 📦 Install frontend dependencies
	@echo -e "$(BLUE)Installing frontend dependencies...$(NC)"
	$(NPM) install
	@echo -e "$(GREEN)✅ Frontend dependencies installed$(NC)"

frontend-build: frontend-install ## 🔨 Build frontend (development)
	@echo -e "$(BLUE)Building frontend (development)...$(NC)"
	NODE_ENV=development $(NPM) run build
	@echo -e "$(GREEN)✅ Frontend built (development)$(NC)"

frontend-production: frontend-install ## 🏭 Build frontend (production with PurgeCSS)
	@echo -e "$(BLUE)Building frontend (production with PurgeCSS)...$(NC)"
	NODE_ENV=production $(NPM) run build
	@echo -e "$(GREEN)✅ Frontend built (production)$(NC)"

frontend-watch: frontend-install ## 👁️ Watch frontend (development)
	@echo -e "$(BLUE)Watching frontend for changes...$(NC)"
	NODE_ENV=development $(NPM) run dev

frontend-start: frontend-watch ## 📦 Alias for frontend-watch

css-purge: ## 🧹 Run PurgeCSS manually
	@echo -e "$(BLUE)Running PurgeCSS...$(NC)"
	NODE_ENV=production $(NPX) purgecss --config ./purgecss.config.js
	@echo -e "$(GREEN)✅ CSS purged$(NC)"

css-analyze: ## 📊 Analyze CSS bundle size
	@echo -e "$(BLUE)Analyzing CSS bundle...$(NC)"
	$(NPX) cssnano --no-map assets/static/css/master.css | $(NPX) cssstats
	@echo -e "$(GREEN)✅ CSS analysis complete$(NC)"

##@ Setup & Sync

setup: ## ⚡ Full project setup (first time)
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)⚡ Full Project Setup$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@echo -e "$(BLUE)1. 📦 Installing Python dependencies...$(NC)"
	@$(UV) sync
	@echo -e "$(GREEN)   ✅ Dependencies installed$(NC)"
	@echo ""
	@echo -e "$(BLUE)2. 🗃️  Running database migrations...$(NC)"
	@$(MANAGE) makemigrations --noinput
	@$(MANAGE) migrate --noinput
	@echo -e "$(GREEN)   ✅ Database migrations completed$(NC)"
	@echo ""
	@echo -e "$(BLUE)3. 🧹 Collecting static files...$(NC)"
	@$(MANAGE) collectstatic --noinput
	@echo -e "$(GREEN)   ✅ Static files collected$(NC)"
	@echo ""
	@echo -e "$(BLUE)4. 🔍 Running Django system checks...$(NC)"
	@$(MANAGE) check || echo -e "$(YELLOW)   ⚠️  Some checks may have warnings$(NC)"
	@echo -e "$(GREEN)   ✅ System checks completed$(NC)"
	@echo ""
	@echo -e "$(BLUE)5. 🎨 Setting up frontend...$(NC)"
	@if [ -f "package.json" ]; then \
		$(MAKE) frontend-install; \
		$(MAKE) frontend-build; \
		echo -e "$(GREEN)   ✅ Frontend setup completed$(NC)"; \
	else \
		echo -e "$(YELLOW)   ⚠️  No frontend configuration found$(NC)"; \
	fi
	@echo ""
	@echo -e "$(BLUE)6. 👑 Creating superuser...$(NC)"
	@if [ -z "$$DJANGO_SUPERUSER_PASSWORD" ]; then \
		echo -e "$(YELLOW)   ℹ️  Set DJANGO_SUPERUSER_PASSWORD env var for auto-creation$(NC)"; \
		echo -e "$(YELLOW)   ℹ️  Or run: make superuser$(NC)"; \
	else \
		$(MANAGE) createsuperuser --noinput || echo -e "$(YELLOW)   ⚠️  Superuser might already exist$(NC)"; \
		echo -e "$(GREEN)   ✅ Superuser created$(NC)"; \
	fi
	@echo ""
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)🎉 Setup completed!$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@echo -e "Next steps:"
	@echo "  make dev      # Start development server"
	@echo "  make test     # Run tests"
	@echo "  make shell    # Open Django shell"
	@echo ""

install: ## 📥 Install/update Python dependencies
	@echo -e "$(BLUE)Installing dependencies...$(NC)"
	@$(UV) sync
	@echo -e "$(GREEN)✅ Dependencies installed$(NC)"

##@ Database

migrate: ## 🗃️ Run database migrations
	@echo -e "$(BLUE)Running migrations...$(NC)"
	@$(MANAGE) makemigrations --noinput
	@$(MANAGE) migrate --noinput
	@echo -e "$(GREEN)✅ Migrations completed$(NC)"

migrations: migrate ## 📝 Alias for migrate

db-shell: ## 🐚 Open database shell (PostgreSQL)
	@if [ -f "docker-compose.yml" ]; then \
		$(DOCKER_COMPOSE) exec db psql -U postgres 2>/dev/null || \
		echo -e "$(YELLOW)Could not connect to database$(NC)"; \
	else \
		echo -e "$(YELLOW)Docker Compose not configured$(NC)"; \
	fi

reset-db: ## 💣 Reset database (DANGER: deletes all data!)
	@echo -e "$(RED)=========================================$(NC)"
	@echo -e "$(RED)⚠️  DANGER: This will delete ALL database data!$(NC)"
	@echo -e "$(RED)=========================================$(NC)"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo -e "$(YELLOW)Resetting database...$(NC)"; \
		rm -f db.sqlite3 2>/dev/null || true; \
		find . -path "*/migrations/*.py" ! -path "./core/utils/migrations/*" ! -name "__init__.py" -delete 2>/dev/null || true \
		find . -path "*/migrations/*.pyc" ! -path "./core/utils/migrations/*" -delete 2>/dev/null || true \
		make migrate; \
		echo -e "$(GREEN)✅ Database reset complete$(NC)"; \
	else \
		echo -e "$(YELLOW)Cancelled$(NC)"; \
	fi

clean-migrations: clean ## 💣 Reset database (DANGER: deletes all data!)
	@echo -e "$(RED)=========================================$(NC)"
	@echo -e "$(RED)⚠️  DANGER: This will delete ALL database migrations data!$(NC)"
	@echo -e "$(RED)=========================================$(NC)"
	@find . -path "*/migrations/*.py" ! -path "./core/contrib/migrations/*" ! -name "__init__.py" -delete 2>/dev/null || true
	@find . -path "*/migrations/*.pyc" ! -path "./core/contrib/migrations/*" -delete 2>/dev/null || true
	@echo -e "$(GREEN)✅ migrations reset complete$(NC)"; \

reset-migrations-all: clean-migrations ## 💣 Reset database (DANGER: deletes all data!)
	@echo -e "$(RED)=========================================$(NC)"
	@echo -e "$(RED)⚠️  DANGER: This will delete ALL database migrations data!$(NC)"
	@echo -e "$(RED)=========================================$(NC)"
	@find . -path "*/migrations/*.py" ! -path "./core/contrib/migrations/*" ! -name "__init__.py" -delete 2>/dev/null || true
	@find . -path "*/migrations/*.pyc" ! -path "./core/contrib/migrations/*" -delete 2>/dev/null || true
	@make migrate
	@echo -e "$(GREEN)✅ migrations reset complete$(NC)"; \

reset-migrations: ## 💣 Reset database (DANGER: deletes all data!)
	@echo -e "$(RED)=========================================$(NC)"
	@echo -e "$(RED)⚠️  DANGER: This will delete ALL database migrations (py) files!$(NC)"
	@echo -e "$(RED)=========================================$(NC)"
	@find . -path "*/migrations/*.py" ! -path "./core/contrib/migrations/*" ! -path "*/.venv/*" ! -name "__init__.py" -delete 2>/dev/null || true
	@find . -path "*/migrations/*.pyc" ! -path "./core/contrib/migrations/*" ! -path "*/.venv/*" -delete 2>/dev/null || true
	@make migrate
	@echo -e "$(GREEN)✅ migrations reset complete$(NC)"; \

##@ Static Files

static: ## 🧹 Collect static files
	@echo -e "$(BLUE)Collecting static files...$(NC)"
	@$(MANAGE) collectstatic --noinput
	@echo -e "$(GREEN)✅ Static files collected$(NC)"

collectstatic: static ## 📁 Alias for static

##@ User Management

superuser: ## 👑 Create Django superuser (interactive)
	@echo -e "$(BLUE)Creating superuser...$(NC)"
	@$(MANAGE) createsuperuser
	@echo -e "$(GREEN)✅ Superuser created$(NC)"

superuser-auto: ## 🤖 Create superuser automatically using .env credentials
	@echo -e "$(BLUE)Creating superuser from .env...$(NC)"
	@$(MANAGE) superuser_auto || $(UV) run python -m django_grep.scripts.superuser
	@echo -e "$(GREEN)✅ Superuser auto-creation process complete$(NC)"

createsuperuser: superuser ## 👤 Alias for superuser

##@ Testing & Quality

test: ## 🧪 Run Django tests
	@echo -e "$(BLUE)Running tests...$(NC)"
	@$(MANAGE) test --noinput
	@echo -e "$(GREEN)✅ Tests completed$(NC)"

test-production: ## 🚀 Run comprehensive production tests
	@echo -e "$(BLUE)Running production tests...$(NC)"
	@python scripts/test_production.py
	@echo -e "$(GREEN)✅ Production tests completed$(NC)"

test-docker: ## 🐳 Run Docker environment tests
	@echo -e "$(BLUE)Running Docker environment tests...$(NC)"
	@python scripts/test_docker_environments.py
	@echo -e "$(GREEN)✅ Docker tests completed$(NC)"

test-all-environments: ## 🌍 Run tests in all environments
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)🧪 Comprehensive Testing Suite$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@echo -e "$(BLUE)1. Running development tests...$(NC)"
	@$(MAKE) test
	@echo ""
	@echo -e "$(BLUE)2. Running production tests...$(NC)"
	@$(MAKE) test-production
	@echo ""
	@echo -e "$(BLUE)3. Running Docker environment tests...$(NC)"
	@$(MAKE) test-docker
	@echo ""
	@echo -e "$(GREEN)🎉 All environment tests completed!$(NC)"

test-database: ## 🗄️ Test database functionality
	@echo -e "$(BLUE)Testing database functionality...$(NC)"
	@$(MANAGE) shell -c "from django.db import connection; print('Database:', connection.settings_dict['NAME']); connection.cursor().execute('SELECT 1'); print('✅ Database connection successful')"
	@echo -e "$(GREEN)✅ Database tests completed$(NC)"

test-migrations: ## 📊 Test migration status
	@echo -e "$(BLUE)Checking migration status...$(NC)"
	@$(MANAGE) showmigrations
	@echo -e "$(GREEN)✅ Migration check completed$(NC)"

test-coverage: ## 📊 Run tests with coverage
	@echo -e "$(BLUE)Running tests with coverage...$(NC)"
	@$(UV) run pytest --cov=. --cov-report=html
	@echo -e "$(GREEN)✅ Coverage report generated in htmlcov/$(NC)"

test-performance: ## ⚡ Run performance tests
	@echo -e "$(BLUE)Running performance tests...$(NC)"
	@$(MANAGE) shell -c "import time; start=time.time(); from django.contrib.auth.models import User; User.objects.count(); print(f'Query time: {time.time()-start:.3f}s')"
	@echo -e "$(GREEN)✅ Performance tests completed$(NC)"

check: ## 🔍 Run Django system checks
	@echo -e "$(BLUE)Running system checks...$(NC)"
	@$(MANAGE) check
	@echo -e "$(GREEN)✅ System checks passed$(NC)"

check-deploy: ## 🚀 Run deployment checks
	@echo -e "$(BLUE)Running deployment checks...$(NC)"
	@$(MANAGE) check --deploy
	@echo -e "$(GREEN)✅ Deployment checks passed$(NC)"

##@ Python Sync System

sync-interactive: ## 🔄 Interactive sync (choose environment/direction)
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)🔄 Python Sync Pipeline$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@$(SYNC_PY)

sync: sync-interactive ## 📡 Alias for sync-interactive

sync-demo: ## 🎯 Sync demo environment
	@$(SYNC_PY) sync env=demo direction=push workflow=standard

sync-main: ## 🚀 Sync main environment
	@$(SYNC_PY) sync env=main direction=push workflow=standard

sync-xellent: ## 🔄 Sync files from ctc-research to xellent-site
	@$(MANAGE) sync_xellent

sync-push: ## 📤 Push to current environment
	@$(SYNC_PY) sync direction=push workflow=standard

sync-pull: ## 📥 Pull from current environment
	@$(SYNC_PY) sync direction=pull workflow=standard

sync-full: ## ⚡ Full sync with all steps
	@$(SYNC_PY) sync direction=sync workflow=full

sync-quick: ## ⚡ Quick sync (minimal steps)
	@$(SYNC_PY) sync direction=push workflow=quick

sync-config: ## ⚙️ Save current sync configuration
	@$(SYNC_PY) token action=save

sync-test: ## 🧪 Test sync without changes
	@$(SYNC_PY) sync direction=push workflow=quick no_interactive=True

sync-clean: ## 🧹 Clean sync artifacts
	@echo -e "$(BLUE)Cleaning sync artifacts...$(NC)"
	@rm -f .sync-config.json 2>/dev/null || true
	@rm -rf .sync-config 2>/dev/null || true
	@echo -e "$(GREEN)✅ Sync artifacts cleaned$(NC)"

##@ Variant Management
setup-core: ## 🧱 Setup Core variant (No LMS, No Blog)
	@$(VARIANT_PY) setup core

setup-blog: ## ✍️ Setup Blog variant (No LMS)
	@$(VARIANT_PY) setup blog

setup-lms: ## 🎓 Setup LMS variant (No Blog)
	@$(VARIANT_PY) setup lms

setup-all: ## 🌟 Setup Full variant (LMS + Blog)
	@$(VARIANT_PY) setup all

publish-core: ## 🧱 Publish Core variant to dedicated repo
	@$(VARIANT_PY) publish core

publish-blog: ## ✍️ Publish Blog variant to dedicated repo
	@$(VARIANT_PY) publish blog

publish-lms: ## 🎓 Publish LMS variant to dedicated repo
	@$(VARIANT_PY) publish lms

publish-all: ## 🚀 Publish ALL variants to their repos
	@$(VARIANT_PY) publish_all

##@ Token Management (Python Sync)

token-list: ## 🔐 List available tokens from all sources
	@$(SYNC_PY) token action=list

token-save: ## 💾 Save current token to secure storage
	@$(SYNC_PY) token action=save

token-test: ## 🧪 Test current token validity
	@$(SYNC_PY) token action=test

token-from-env: ## 📁 Load token from .env file
	@if [ -f .env ]; then \
		export $$(grep -v '^#' .env | xargs) && \
		echo -e "$(GREEN)✅ Loaded tokens from .env$(NC)"; \
	else \
		echo -e "$(YELLOW)⚠️  No .env file found$(NC)"; \
	fi

token-config: ## ⚙️ Configure token sources
	@echo -e "$(CYAN)Token Configuration$(NC)"
	@echo "1. Set token in environment:"
	@echo "   export GIT_TOKEN=ghp_xxxx"
	@echo ""
	@echo "2. Add to .env file:"
	@echo "   echo 'GIT_TOKEN=ghp_xxxx' >> .env"
	@echo ""
	@echo "3. Use Python sync to save:"
	@echo "   make token-save"
	@echo ""
	@echo "4. List available tokens:"
	@echo "   make token-list"

##@ Code Quality & Formatting

format: ## 🎨 Format code with ruff
	@echo -e "$(BLUE)Formatting code...$(NC)"
	@ruff format .
	@echo -e "$(GREEN)✅ Code formatted$(NC)"

lint: ## 🔍 Fast linting (imports only)
	@echo -e "$(BLUE)Fast linting (imports only)...$(NC)"
	@ruff check --select F401,F841,I001 --fix --no-cache .
	@echo -e "$(GREEN)✅ Fast linting completed$(NC)"

fix: ## 🔧 Fix all fixable issues with ruff
	@echo -e "$(BLUE)Fixing code issues...$(NC)"
	@ruff check --fix .
	@echo -e "$(GREEN)✅ Issues fixed$(NC)"

fix-unused: ## 🧹 Remove unused imports and variables
	@echo -e "$(BLUE)Cleaning unused imports...$(NC)"
	@ruff check --select F401,F841 --fix .
	@echo -e "$(GREEN)✅ Unused imports cleaned$(NC)"

clean-imports: fix-unused ## 📦 Alias for fix-unused

##@ Shell & Debugging

shell: ## 🐚 Open Django shell
	@echo -e "$(BLUE)Opening Django shell...$(NC)"
	@$(MANAGE) shell_plus --ipython 2>/dev/null || $(MANAGE) shell

shell-plus: shell ## 🐍 Alias for shell

debug: ## 🐛 Start debug shell (ipdb)
	@echo -e "$(BLUE)Starting debug shell...$(NC)"
	@$(UV) run python -m ipdb com shell

##@ Docker Management

up: ## 🐳 Start Docker containers
	@if [ -f "docker-compose.yml" ]; then \
		echo -e "$(BLUE)Starting Docker containers...$(NC)"; \
		$(DOCKER_COMPOSE) up -d; \
		echo -e "$(GREEN)✅ Docker containers started$(NC)"; \
	else \
		echo -e "$(YELLOW)No docker-compose.yml found$(NC)"; \
	fi

down: ## ⏹️ Stop Docker containers
	@if [ -f "docker-compose.yml" ]; then \
		echo -e "$(BLUE)Stopping Docker containers...$(NC)"; \
		$(DOCKER_COMPOSE) down; \
		echo -e "$(GREEN)✅ Docker containers stopped$(NC)"; \
	fi

docker-logs: ## 📋 Show Docker container logs
	@if [ -f "docker-compose.yml" ]; then \
		$(DOCKER_COMPOSE) logs -f; \
	else \
		echo -e "$(YELLOW)No docker-compose.yml found$(NC)"; \
	fi

docker-restart: ## 🔄 Restart Docker containers
	@if [ -f "docker-compose.yml" ]; then \
		echo -e "$(BLUE)Restarting Docker containers...$(NC)"; \
		$(DOCKER_COMPOSE) restart; \
		echo -e "$(GREEN)✅ Docker containers restarted$(NC)"; \
	fi

##@ Cleanup

clean: clean-python clean-frontend clean-sync ## 🧹 Clean Python, frontend, and sync cache
	@rm -f uv.lock
	@echo -e "$(GREEN)✅ Cleanup completed$(NC)"

clean-python: ## 🐍 Clean Python cache and build files
	@echo -e "$(BLUE)Cleaning Python cache...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	# @find . -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo -e "$(GREEN)✅ Python cache cleaned$(NC)"

clean-frontend: ## 🎨 Clean frontend build artifacts
	@echo -e "$(BLUE)Cleaning frontend...$(NC)"
	@rm -rf node_modules 2>/dev/null || true
	@if [ -f "package.json" ]; then \
		$(NPM) run clean 2>/dev/null || \
		(if [ -d "$(BUNDLES_DIR)" ]; then rm -rf $(BUNDLES_DIR); fi); \
		echo -e "$(GREEN)✅ Frontend cleaned$(NC)"; \
	else \
		echo -e "$(YELLOW)⚠️  No frontend configuration found$(NC)"; \
	fi

clean-sync: sync-clean ## 🔄 Clean sync artifacts
	@echo -e "$(GREEN)✅ Sync artifacts cleaned$(NC)"

clean-docker: ## 🐳 Clean Docker resources
	@echo -e "$(BLUE)Cleaning Docker resources...$(NC)"
	@-docker container prune -f 2>/dev/null || true
	@-docker image prune -f 2>/dev/null || true
	@-docker network prune -f 2>/dev/null || true
	@-docker volume prune -f 2>/dev/null || true
	@echo -e "$(GREEN)✅ Docker cleanup completed$(NC)"

clean-all: clean clean-docker ## 💥 Complete cleanup (everything)
	@echo -e "$(GREEN)✅ Complete cleanup finished$(NC)"

##@ Utility & Info

status: ## 📊 Show project status
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)📊 Project Status$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@echo -e "$(GREEN)🐍 Python:$(NC) $(shell python --version 2>/dev/null || echo 'Not found')"
	@echo -e "$(GREEN)📦 uv:$(NC) $(shell uv --version 2>/dev/null || echo 'Not installed')"
	@echo -e "$(GREEN)🟢 Node:$(NC) $(shell node --version 2>/dev/null || echo 'Not installed')"
	@echo -e "$(GREEN)📁 Working dir:$(NC) $(shell pwd)"
	@echo ""
	@echo -e "$(GREEN)📈 Cache sizes:$(NC)"
	@du -sh .ruff_cache 2>/dev/null | while read size dir; do echo "  $$dir: $$size"; done || true
	@du -sh node_modules 2>/dev/null | while read size dir; do echo "  $$dir: $$size"; done || true
	@du -sh __pycache__ 2>/dev/null | while read size dir; do echo "  $$dir: $$size"; done || true
	@echo ""
	@echo -e "$(GREEN)📂 Key files:$(NC)"
	@ls -la com package.json pyproject.toml docker-compose.yml 2>/dev/null | tail -n +2
	@echo ""
	@if [ -f "docker-compose.yml" ]; then \
		echo -e "$(GREEN)🐳 Docker status:$(NC)"; \
		$(DOCKER_COMPOSE) ps 2>/dev/null || echo "  Not running"; \
	fi
remove-ctc: ## 🐳 Remove Docker containers with names starting with "ctc"
	@echo -e "$(BLUE)Removing Docker containers with prefix 'ctc'...$(NC)"
	@docker ps -a --format '{{.Names}}' | grep '^ctc' | xargs -r docker stop
	@docker ps -a --format '{{.Names}}' | grep '^ctc' | xargs -r docker rm
	@echo -e "$(GREEN)✅ ctc containers removed$(NC)"

env-check: ## 🌍 Check environment configuration
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)🌍 Environment Check$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@echo -e "$(GREEN)Environment variables:$(NC)"
	@if [ -n "$$DJANGO_SETTINGS_MODULE" ]; then \
		echo -e "  DJANGO_SETTINGS_MODULE: $$DJANGO_SETTINGS_MODULE"; \
	else \
		echo -e "  $(YELLOW)DJANGO_SETTINGS_MODULE: Not set$(NC)"; \
	fi
	@if [ -n "$$DATABASE_URL" ]; then \
		echo -e "  DATABASE_URL: Set"; \
	else \
		echo -e "  $(YELLOW)DATABASE_URL: Not set$(NC)"; \
	fi
	@if [ -n "$$GIT_TOKEN" ]; then \
		echo -e "  GIT_TOKEN: Set"; \
	else \
		echo -e "  $(YELLOW)GIT_TOKEN: Not set$(NC)"; \
	fi
	@echo ""
	@echo -e "$(GREEN)Python path:$(NC)"
	@echo "$$PYTHONPATH" | tr ':' '\n' | while read path; do echo "  $$path"; done
	@echo ""

version: ## 🏷️ Show project versions
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)🏷️ Project Versions$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@if [ -f "pyproject.toml" ]; then \
		grep -E '^version|^name' pyproject.toml | while read line; do \
			echo -e "$(GREEN)$$line$(NC)"; \
		done; \
	fi
	@echo ""
	@echo -e "$(GREEN)Django version:$(NC)"
	@$(MANAGE) --version 2>/dev/null || echo "  Could not determine"
	@if [ -f "package.json" ]; then \
		echo ""; \
		echo -e "$(GREEN)Node version:$(NC)"; \
		$(NPM) --version 2>/dev/null || echo "  Not installed"; \
	fi

##@ Pipeline Shortcuts

push-demo: sync-demo ## 📤 Push to demo
push-main: sync-main ## 📤 Push to main
pull-demo: ## 📥 Pull from demo
	@$(SYNC_PY) sync env=demo direction=pull workflow=standard
pull-main: ## 📥 Pull from main
	@$(SYNC_PY) sync env=main direction=pull workflow=standard

deploy: sync-full ## 🚀 Full deployment pipeline
	@echo -e "$(GREEN)✅ Deployment completed$(NC)"

rollback: ## ↩️ Rollback last deployment
	@echo -e "$(YELLOW)Rolling back last deployment...$(NC)"
	@git reset --hard HEAD~1
	@$(SYNC_PY) sync direction=push workflow=quick no_interactive=True
	@echo -e "$(GREEN)✅ Rollback completed$(NC)"

verify: ## 🔍 Run full deployment verification suite
	@echo -e "$(BLUE)Running deployment verification...$(NC)"
	@$(UV) run python -m core.CI.verify_deployment
	@echo -e "$(GREEN)✅ Verification complete$(NC)"

##@ Shortcuts (for quick typing)

# Development shortcuts
s: setup
d: dev
r: run
t: test
c: check
m: migrate
f: format
l: lint
x: fix

# Frontend shortcuts
fb: frontend-build
fp: frontend-production
fw: frontend-watch
fi: frontend-install

# Cleanup shortcuts
cl: clean-python clean-frontend clean-sync
cla: clean-all
cd: clean-docker
# Docker shortcuts
du: up
dd: down
dl: docker-logs
dr: docker-restart

# Shell shortcuts
sh: shell
sp: shell-plus

# Static files
st: static
cs: collectstatic

# User management
su: superuser
csu: createsuperuser

# Quick fixes
fu: fix-unused
ci: clean-imports
rm: reset-migrations
cm: clean-migrations

# Sync shortcuts
sync-i: sync-interactive
sync-d: sync-demo
sync-m: sync-main

# Build pipeline
build: fb st m dr cd
	@echo -e "$(GREEN)✅ build completed$(NC)"

reset: cla rm fb st dr cd ## 🔨 Build everything (frontend + static)
	@echo -e "$(GREEN)✅ Full build completed$(NC)"

instance: rm fb st
	@echo -e "$(GREEN)✅ build completed$(NC)"

build-assets: ## 🧱 Build frontend assets via webpack
	@npm run build
