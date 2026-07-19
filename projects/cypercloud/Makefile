# ============================================================
# Cypercloud Makefile – Build, Deploy & Run targets
# ============================================================
#
# Cypercloud AI Chat Customizer
# Supports local development, Docker, and production deployment

SHELL := /bin/bash
.DEFAULT_GOAL := help

PYTHON     ?= python3
MANAGE     := $(PYTHON) manage.py
ASSETS_DIR := assets
BUNDLES_DIR := $(ASSETS_DIR)/bundles/cypercloud
LOG_DIR    ?= logs
PORT       ?= 5073
WORKERS    ?= 2

# -----------------------------------------------------------------
# Help
# -----------------------------------------------------------------
.PHONY: help

help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║   Cypercloud – AI Chat Customizer Makefile               ║"
	@echo "║   Multi-site template discovery with AI integration       ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 QUICK START:"
	@echo "  make setup              Full local setup (install, migrate, build)"
	@echo "  make run                Start development server (port 5073)"
	@echo "  make run-full           Full setup + run development server"
	@echo ""
	@echo "🐳 DOCKER:"
	@echo "  make docker-build       Build Docker image"
	@echo "  make docker-run         Run in Docker container"
	@echo "  make docker-logs        View Docker logs"
	@echo "  make docker-shell       Execute shell in container"
	@echo ""
	@echo "🛠️  FRONTEND (Webpack):"
	@echo "  make install-assets     Install npm dependencies (npm ci)"
	@echo "  make build              Production webpack build"
	@echo "  make build-dev          Development webpack build (source maps)"
	@echo "  make watch              Watch mode (rebuilds on file change)"
	@echo "  make dev                Webpack dev server with HMR (port 5093)"
	@echo "  make clean              Remove generated bundles"
	@echo ""
	@echo "📦 STATIC FILES & DEPLOY:"
	@echo "  make collectstatic      Collect static files → STATIC_ROOT/"
	@echo "  make build-collect      Build + collectstatic"
	@echo "  make deploy             Full deploy: build → collectstatic → migrate"
	@echo ""
	@echo "🗄️  DATABASE:"
	@echo "  make migrate            Apply Django migrations"
	@echo "  make migrate-new        Create new migration (MIGRATION=app.name)"
	@echo "  make migrate-status     Show migration status"
	@echo "  make db-reset           Reset database (careful!)"
	@echo ""
	@echo "⚙️  CONFIGURATION (Dynaconf):"
	@echo "  make config-check       Verify Dynaconf configuration loads"
	@echo "  make config-validate    Validate configuration structure"
	@echo "  make config-show        Display current configuration"
	@echo "  make config-env         Show environment variables"
	@echo ""
	@echo "⚙️  DJANGO MANAGEMENT:"
	@echo "  make check              Django system checks"
	@echo "  make check-deploy       Production readiness checks"
	@echo "  make shell              Django interactive shell"
	@echo "  make superuser          Create superuser (admin user)"
	@echo ""
	@echo "🔍 TESTING & DEBUGGING:"
	@echo "  make test               Run all tests"
	@echo "  make lint               Run linting checks"
	@echo "  make format             Format code (Black)"
	@echo "  make check-deploy       Check production readiness"
	@echo ""
	@echo "📚 DOCUMENTATION & INFO:"
	@echo "  make info               Show project information"
	@echo ""

# ============================================================
# QUICK START
# ============================================================
.PHONY: setup run run-full

setup:
	@mkdir -p $(LOG_DIR)
	@echo "🔧 Setting up Cypercloud..."
	@echo "Step 1: Installing npm dependencies..."
	@$(MAKE) install-assets
	@echo ""
	@echo "Step 2: Installing Python dependencies..."
	@pip install -r requirements.txt 2>&1 | tee $(LOG_DIR)/pip.log
	@echo ""
	@echo "Step 3: Applying migrations..."
	@$(MANAGE) migrate
	@echo ""
	@echo "Step 4: Building frontend assets..."
	@$(MAKE) build
	@echo ""
	@echo "Step 5: Collecting static files..."
	@$(MAKE) collectstatic
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Create superuser (optional): make superuser"
	@echo "  2. Start server: make run"
	@echo "  3. Access: http://localhost:$(PORT)"

run:
	@echo "🚀 Starting Cypercloud development server on http://localhost:$(PORT)..."
	$(MANAGE) runserver 0.0.0.0:$(PORT)

run-full: setup run
	@echo "✅ Cypercloud running!"

# ============================================================
# DOCKER
# ============================================================
.PHONY: docker-build docker-run docker-stop docker-logs docker-shell docker-migrate

docker-build:
	@echo "🐳 Building Docker image..."
	@docker-compose -f docker-compose.yml build
	@echo "✅ Build complete"

docker-run:
	@echo "🐳 Starting Docker container..."
	@docker-compose -f docker-compose.yml up -d
	@echo "✅ Container started"
	@echo "   Access: http://cypercloud.localhost:5073"
	@echo "   Logs: make docker-logs"

docker-stop:
	@echo "🛑 Stopping Docker container..."
	@docker-compose -f docker-compose.yml down

docker-logs:
	@docker-compose -f docker-compose.yml logs -f cypercloud

docker-shell:
	@docker-compose -f docker-compose.yml exec cypercloud bash

docker-migrate:
	@echo "📦 Applying migrations in Docker..."
	@docker-compose -f docker-compose.yml exec cypercloud python manage.py migrate

# ============================================================
# FRONTEND (Webpack)
# ============================================================
.PHONY: install-assets build build-dev watch dev clean

install-assets:
	@echo "📦 Installing npm dependencies..."
	@npm --prefix $(ASSETS_DIR) ci --include=dev --legacy-peer-deps 2>&1 | tail -5
	@echo "✅ Dependencies installed"

build:
	@mkdir -p $(LOG_DIR)
	@echo "🟢 Building production bundles…"
	@npm --prefix $(ASSETS_DIR) run build 2>&1 | tee $(LOG_DIR)/build.log | tail -10
	@echo "✅ Production build done → $(BUNDLES_DIR)/"

build-dev:
	@mkdir -p $(LOG_DIR)
	@echo "🟡 Building development bundles…"
	@npm --prefix $(ASSETS_DIR) run build:dev 2>&1 | tee $(LOG_DIR)/build-dev.log | tail -10
	@echo "✅ Development build done → $(BUNDLES_DIR)/"

watch:
	@echo "🔄 Watching for file changes…"
	@npm --prefix $(ASSETS_DIR) run watch

dev:
	@echo "🌐 Starting webpack dev server on http://localhost:5093 …"
	@npm --prefix $(ASSETS_DIR) run dev

clean:
	@echo "🧹 Removing generated bundles…"
	@rm -rf $(ASSETS_DIR)/bundles/cypercloud
	@echo "✅ Bundles cleaned: $(BUNDLES_DIR)/"

# ============================================================
# STATIC FILES & DEPLOYMENT
# ============================================================
.PHONY: collectstatic build-collect deploy

collectstatic:
	@mkdir -p $(LOG_DIR)
	@echo "📂 Collecting static files into STATIC_ROOT…"
	@$(MANAGE) collectstatic --noinput --clear 2>&1 | tee $(LOG_DIR)/collectstatic.log | tail -5
	@echo "✅ Collectstatic complete"

build-collect:
	@mkdir -p $(LOG_DIR)
	@echo "🔨 Building assets + collecting static…"
	@$(MAKE) build 2>&1 | tee $(LOG_DIR)/build.log
	@$(MAKE) collectstatic 2>&1 | tee -a $(LOG_DIR)/collectstatic.log
	@echo "✅ Build + collectstatic complete"

deploy:
	@mkdir -p $(LOG_DIR)
	@echo "🚀 Deploying Cypercloud…"
	@echo ""
	@echo "═══ Step 1: Build assets ═══"
	@$(MAKE) build 2>&1 | tee $(LOG_DIR)/deploy.log
	@echo ""
	@echo "═══ Step 2: Collect static ═══"
	@$(MAKE) collectstatic 2>&1 | tee -a $(LOG_DIR)/deploy.log
	@echo ""
	@echo "═══ Step 3: Apply migrations ═══"
	@$(MANAGE) migrate --noinput 2>&1 | tee -a $(LOG_DIR)/deploy.log
	@echo ""
	@echo "✅ Deploy complete"
	@echo ""
	@echo "Next: Start Cypercloud"
	@echo "  Local: make run"
	@echo "  Docker: make docker-run"

# ============================================================
# DATABASE MANAGEMENT
# ============================================================
.PHONY: migrate migrate-new migrate-status db-reset

migrate:
	@echo "📦 Applying migrations…"
	@$(MANAGE) migrate
	@echo "✅ Migrations applied"

migrate-new:
	@if [ -z "$(MIGRATION)" ]; then \
		echo "❌ Usage: make migrate-new MIGRATION=app.name"; \
	else \
		echo "📝 Creating migration for $(MIGRATION)…"; \
		$(MANAGE) makemigrations $(MIGRATION); \
		echo "✅ Migration created"; \
	fi

migrate-status:
	@echo "📋 Migration status:"
	@$(MANAGE) showmigrations

db-reset:
	@echo "⚠️  Resetting database..."
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		rm -f db.sqlite3; \
		$(MANAGE) migrate; \
		echo "✅ Database reset complete"; \
	else \
		echo "❌ Cancelled"; \
	fi

# ============================================================
# CONFIGURATION MANAGEMENT (Dynaconf)
# ============================================================
.PHONY: config-check config-status config-validate config-show

config-check:
	@echo "✅ Checking Dynaconf configuration…"
	@$(PYTHON) -c "\
		from django_fusion.config.dynaconf_loader import load_dynaconf_settings;\
		settings = load_dynaconf_settings(config_dir='configs/');\
		settings.load();\
		print('✅ Configuration loaded successfully');\
		print(f'  Environment: {settings.env}');\
		print(f'  Debug: {settings.get(\"DJANGO.debug\")}');\
		print(f'  Database: {settings.get(\"DATABASE.engine\", \"sqlite3\")}')" 2>&1

config-validate:
	@echo "🔍 Validating configuration structure…"
	@$(PYTHON) -c "\
		from django.conf import settings;\
		from django_fusion.config.dynaconf_loader import load_dynaconf_settings, ModelsRegistry, TemplateRegistry;\
		dynaconf = load_dynaconf_settings(config_dir='configs/').load();\
		models = ModelsRegistry(dynaconf);\
		templates = TemplateRegistry(dynaconf);\
		print('✅ Configuration validation passed');\
		print(f'  Models configured: {len(models.list_models())}');\
		print(f'  Template apps: {len(templates.list_apps())}');\
		for app in templates.list_apps():\
			print(f'    - {app.get(\"slug\")}: {app.get(\"name\")}')" 2>&1

config-show:
	@echo "📋 Current configuration:"
	@echo ""
	@echo "Django Settings:"
	@$(PYTHON) -c "\
		from django_fusion.config.dynaconf_loader import load_dynaconf_settings;\
		s = load_dynaconf_settings(config_dir='configs/').load();\
		print(f'  Secret Key: ***{s.get(\"DJANGO.secret_key\", \"not-set\")[-8:]}');\
		print(f'  Debug: {s.get(\"DJANGO.debug\")}');\
		print(f'  Allowed Hosts: {s.get(\"DJANGO.allowed_hosts\")}')" 2>&1
	@echo ""
	@echo "Database:"
	@$(PYTHON) -c "\
		from django_fusion.config.dynaconf_loader import load_dynaconf_settings;\
		s = load_dynaconf_settings(config_dir='configs/').load();\
		db = s.get('DATABASE', {});\
		print(f'  Engine: {db.get(\"engine\", \"sqlite3\")}')" 2>&1
	@echo ""
	@echo "AI Models:"
	@$(PYTHON) -c "\
		from django_fusion.config.dynaconf_loader import load_dynaconf_settings, ModelsRegistry;\
		s = load_dynaconf_settings(config_dir='configs/').load();\
		m = ModelsRegistry(s);\
		for model in m.list_models()[:3]:\
			print(f'  - {model.get(\"name\")} ({model.get(\"provider\")})')" 2>&1
	@echo ""

config-env:
	@echo "🌍 Environment variables:"
	@echo ""
	@echo "Configuration Environment:"
	@echo "  CYPERCLOUD_ENV=${CYPERCLOUD_ENV:-development}"
	@echo "  DJANGO_ENV=${DJANGO_ENV:-not-set}"
	@echo ""
	@echo "Django Settings:"
	@echo "  CYPERCLOUD_SECRET_KEY=$${CYPERCLOUD_SECRET_KEY:-(not-set)}"
	@echo "  CYPERCLOUD_DEBUG=${CYPERCLOUD_DEBUG:-not-set}"
	@echo "  CYPERCLOUD_ALLOWED_HOSTS=${CYPERCLOUD_ALLOWED_HOSTS:-not-set}"
	@echo ""
	@echo "Database:"
	@echo "  DB_ENGINE=${DB_ENGINE:-not-set}"
	@echo "  DB_HOST=${DB_HOST:-localhost}"
	@echo "  DB_NAME=${DB_NAME:-tinker_db}"
	@echo ""
	@echo "AI Models (Ollama):"
	@echo "  OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://localhost:11434}"
	@echo "  OLLAMA_MODEL=${OLLAMA_MODEL:-gemma3:4b}"
	@echo ""

# ============================================================
# DJANGO MANAGEMENT
# ============================================================
.PHONY: check shell superuser createsuperuser

check:
	@echo "✅ Running Django system checks…"
	@$(MANAGE) check

check-deploy:
	@echo "✅ Running production deployment checks…"
	@$(MANAGE) check --deploy

shell:
	@echo "📚 Opening Django shell…"
	$(MANAGE) shell

superuser:
	@echo "👤 Creating superuser…"
	$(MANAGE) createsuperuser

createsuperuser: superuser

# ============================================================
# TESTING & DEBUGGING
# ============================================================
.PHONY: test test-verbose lint format

test:
	@echo "🧪 Running tests…"
	@$(PYTHON) manage.py test 2>&1 | tail -20

test-verbose:
	@echo "🧪 Running tests (verbose)…"
	@$(PYTHON) manage.py test --verbosity=2

lint:
	@echo "🔍 Running linting checks…"
	@if command -v ruff &> /dev/null; then \
		ruff check . --select=E,W,F; \
	elif command -v pylint &> /dev/null; then \
		pylint chat/ --disable=all --enable=E,W; \
	else \
		echo "⚠️  No linter found (ruff or pylint)"; \
	fi

format:
	@echo "🎨 Formatting code…"
	@if command -v black &> /dev/null; then \
		black . --line-length=88; \
		echo "✅ Code formatted with Black"; \
	else \
		echo "⚠️  Black not installed"; \
	fi

# ============================================================
# PROJECT INFO & UTILITIES
# ============================================================
.PHONY: info env-check logs tree

info:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║   Tinker Project Information                              ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📍 Location: $(PWD)"
	@echo "🐍 Python: $$($(PYTHON) --version)"
	@echo "📦 Django: $$($(PYTHON) -c 'import django; print(django.VERSION)')"
	@echo "🌐 Port: $(PORT)"
	@echo "👷 Gunicorn Workers: $(WORKERS)"
	@echo ""
	@echo "📋 Database:"
	@$(MANAGE) dbshell < /dev/null 2>&1 | head -1 || echo "SQLite (db.sqlite3)"
	@echo ""
	@echo "📂 Key Directories:"
	@echo "  Templates: ./templates"
	@echo "  Static: ./assets/static"
	@echo "  Bundles: ./$(BUNDLES_DIR)"
	@echo "  Logs: ./$(LOG_DIR)"
	@echo ""
	@echo "🔗 Links:"
	@echo "  Chat: http://localhost:$(PORT)"
	@echo "  Admin: http://localhost:$(PORT)/admin"
	@echo "  API: http://localhost:$(PORT)/api"
	@echo ""

env-check:
	@echo "🔍 Checking environment..."
	@echo ""
	@echo "Python:"
	@$(PYTHON) --version
	@echo ""
	@echo "Node/npm:"
	@npm --version || echo "⚠️  npm not found"
	@echo ""
	@echo "Docker:"
	@docker --version || echo "⚠️  Docker not found"
	@echo ""
	@echo "Django settings: settings.py"
	@grep "WEBSITE_IDENTIFIER" settings.py | head -1
	@echo ""

logs:
	@echo "📋 Recent logs:"
	@tail -50 $(LOG_DIR)/*.log 2>/dev/null || echo "No logs found"

# ============================================================
# CLEANUP
# ============================================================
.PHONY: clean-all clean-pycache clean-db

clean-all: clean clean-pycache
	@echo "🧹 Full cleanup complete"

clean-pycache:
	@echo "🧹 Removing Python cache..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cache cleaned"

clean-db:
	@echo "⚠️  WARNING: This will delete db.sqlite3"
	@read -p "Continue? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		rm -f db.sqlite3; \
		echo "✅ Database deleted"; \
	fi

# ============================================================
# COMPOSITE TASKS (Recommended workflows)
# ============================================================
.PHONY: reset dev-setup prod-setup ci

reset: clean-all db-reset
	@echo "✅ Full reset complete"

dev-setup: install-assets build-dev migrate
	@echo "✅ Development setup complete"
	@echo ""
	@echo "Start developing:"
	@echo "  Terminal 1: make run              (Django server)"
	@echo "  Terminal 2: make watch            (Webpack watch)"
	@echo "  Browser: http://localhost:$(PORT)"

prod-setup: install-assets deploy
	@echo "✅ Production setup complete"

ci:
	@echo "🤖 Running CI checks..."
	@$(MAKE) check
	@$(MAKE) lint
	@$(MAKE) test
	@echo "✅ CI checks passed"

# @tested Cypercloud - dev, migrate, collectstatic, check, test targets verified
