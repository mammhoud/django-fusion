# Project Root Makefile – Delegation hub (no Docker logic)
# ============================================================
.PHONY: help menu dev up down clean setup test shell migrate static superuser check format lint docs \
        server frontend-build frontend-watch frontend-install css-purge clean-all \
        clean-docker clean-python clean-frontend clean-docs status env-check version \
        install test-quick populate-data frontend-production frontend-start \
        css-analyze test-url test-reports clean-test-reports fix fix-unused \
        debug db-shell reset-db clean-migrations reset-migrations

.DEFAULT_GOAL := help

# Colors
RED    := \033[0;31m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
CYAN   := \033[0;36m
NC     := \033[0m

help: ## Show this help (base commands + delegation)
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(CYAN)      PROJECT MAKE HELP (root)          $(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@echo -e "$(GREEN)Main commands (delegated to sub-makefiles):$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-25s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo -e "For Docker commands:   $(YELLOW)cd compose && make help$(NC)"
	@echo -e "For Django commands:   $(YELLOW)cd v1 && make help$(NC)"
	@echo -e "For frontend:          $(YELLOW)cd v1/assets && make help$(NC)"
	@echo -e "For docs:              $(YELLOW)cd docs && make help$(NC)"
	@echo ""

menu: ## Interactive menu (delegates to sub-targets)
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)🔧 Development Menu$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@echo "1. 🚀 Start Django dev server"
	@echo "2. 📦 Install Python deps"
	@echo "3. 🗃️  Run migrations"
	@echo "4. 🧹 Collect static"
	@echo "5. 👑 Create superuser"
	@echo "6. 🔍 Django checks"
	@echo "7. 🧪 Run tests"
	@echo "8. 🐚 Django shell"
	@echo "9. 🎨 Build frontend (production)"
	@echo "10. 👁️  Watch frontend"
	@echo "11. 📖 Build docs"
	@echo "12. 🐳 Start all Docker services"
	@echo "13. ⏹️  Stop all Docker services"
	@echo "0. 🚪 Exit"
	@echo ""
	@read -p "Choose: " choice; \
	case $$choice in \
		1) $(MAKE) dev;; \
		2) $(MAKE) install;; \
		3) $(MAKE) migrate;; \
		4) $(MAKE) static;; \
		5) $(MAKE) superuser;; \
		6) $(MAKE) check;; \
		7) $(MAKE) test;; \
		8) $(MAKE) shell;; \
		9) $(MAKE) frontend-production;; \
		10) $(MAKE) frontend-watch;; \
		11) $(MAKE) docs;; \
		12) $(MAKE) up;; \
		13) $(MAKE) down;; \
		0) echo -e "$(GREEN)Bye!$(NC)"; exit 0;; \
		*) echo -e "$(RED)Invalid$(NC)";; \
	esac

# ----------------------------------------------------------------------
# Delegation targets (Django, frontend, docs)
# ----------------------------------------------------------------------
dev: ## Start Django dev server (Uvicorn)
	@$(MAKE) -C v1 dev

server: ## Start production server (auto WSGI/ASGI)
	@$(MAKE) -C v1 server

install: ## Install Python dependencies
	@$(MAKE) -C v1 install

setup: ## Full project setup (calls v1 setup)
	@$(MAKE) -C v1 setup

migrate: ## Run DB migrations
	@$(MAKE) -C v1 migrate

static: ## Collect static files
	@$(MAKE) -C v1 static

superuser: ## Create superuser
	@$(MAKE) -C v1 superuser

test: ## Run tests
	@$(MAKE) -C v1 test

test-quick: ## Quick tests
	@$(MAKE) -C v1 test-quick

test-url: ## Test custom URL
	@$(MAKE) -C v1 test-url

populate-data: ## Populate data
	@$(MAKE) -C v1 populate-data

test-reports: ## Show test reports
	@$(MAKE) -C v1 test-reports

clean-test-reports: ## Clean test reports
	@$(MAKE) -C v1 clean-test-reports

check: ## Django system checks
	@$(MAKE) -C v1 check

format: ## Format code
	@$(MAKE) -C v1 format

lint: ## Fast lint
	@$(MAKE) -C v1 lint

fix: ## Fix code
	@$(MAKE) -C v1 fix

fix-unused: ## Remove unused imports
	@$(MAKE) -C v1 fix-unused

shell: ## Django shell
	@$(MAKE) -C v1 shell

debug: ## Debug shell
	@$(MAKE) -C v1 debug

db-shell: ## DB shell
	@$(MAKE) -C v1 db-shell

reset-db: ## Reset database
	@$(MAKE) -C v1 reset-db

clean-migrations: ## Clean migration files
	@$(MAKE) -C v1 clean-migrations

reset-migrations: ## Reset migrations
	@$(MAKE) -C v1 reset-migrations

# Frontend delegation
frontend-install: ## Install frontend deps
	@$(MAKE) -C v1/assets install

frontend-build: ## Build frontend (dev)
	@$(MAKE) -C v1/assets build

frontend-production: ## Build frontend (production)
	@$(MAKE) -C v1/assets production

frontend-watch: ## Watch frontend
	@$(MAKE) -C v1/assets watch

frontend-start: frontend-watch ## Alias

css-purge: ## Purge CSS
	@$(MAKE) -C v1/assets purge

css-analyze: ## Analyze CSS
	@$(MAKE) -C v1/assets analyze

# Docs delegation
docs: ## Build documentation
	@$(MAKE) -C docs build

docs-serve: ## Serve docs locally
	@$(MAKE) -C docs serve

docs-deploy: ## Deploy docs
	@$(MAKE) -C docs deploy

docs-clean: ## Clean docs artifacts
	@$(MAKE) -C docs clean

docs-check: ## Check docs structure
	@$(MAKE) -C docs check

# ----------------------------------------------------------------------
# Docker delegation (all forwarded to compose/Makefile)
# ----------------------------------------------------------------------
up: ## Start all Docker services
	@$(MAKE) -C compose up

down: ## Stop all Docker containers
	@$(MAKE) -C compose down

docker-full: ## All services + Traefik
	@$(MAKE) -C compose docker-full

docker-db: ## Start DB + Redis only
	@$(MAKE) -C compose docker-db

docker-app: ## Start app services
	@$(MAKE) -C compose docker-app

docker-proxy: ## Start Traefik only
	@$(MAKE) -C compose docker-proxy

docker-dev: docker-db ## Alias

docker-prod: up ## Alias

# ----------------------------------------------------------------------
# Cleanup (orchestrated – Docker cleanup delegated)
# ----------------------------------------------------------------------
clean-python: ## Clean Python cache (delegates)
	@$(MAKE) -C v1 clean-python

clean-frontend: ## Clean frontend artifacts (delegates)
	@$(MAKE) -C v1/assets clean

clean-docs: ## Clean docs artifacts
	@$(MAKE) -C docs clean

clean-docker: ## Fully clean Docker (delegates)
	@$(MAKE) -C compose clean-docker

clean: clean-python clean-frontend clean-docs ## Clean all project artifacts (no Docker)
	@rm -f uv.lock
	@echo -e "$(GREEN)✅ Project cleaned (no Docker)$(NC)"

clean-all: clean clean-docker ## 💥 Clean everything including Docker
	@echo -e "$(GREEN)✅ Complete cleanup finished$(NC)"

# ----------------------------------------------------------------------
# Utility & Status
# ----------------------------------------------------------------------
status: ## Show project status
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)📊 Project Status$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@echo -e "$(GREEN)🐍 Python:$(NC) $$(python --version 2>/dev/null || echo 'Not found')"
	@echo -e "$(GREEN)📦 uv:$(NC) $$(uv --version 2>/dev/null || echo 'Not installed')"
	@echo -e "$(GREEN)🟢 Node:$(NC) $$(node --version 2>/dev/null || echo 'Not installed')"
	@echo -e "$(GREEN)📁 Working dir:$(NC) $$(pwd)"
	@echo ""
	@echo -e "$(GREEN)📈 Cache sizes:$(NC)"
	@du -sh .ruff_cache v1/.ruff_cache 2>/dev/null | while read s d; do echo "  $$d: $$s"; done || true
	@du -sh node_modules v1/node_modules 2>/dev/null | while read s d; do echo "  $$d: $$s"; done || true
	@du -sh __pycache__ v1/__pycache__ 2>/dev/null | while read s d; do echo "  $$d: $$s"; done || true
	@echo ""
	@echo -e "$(GREEN)📂 Key files:$(NC)"
	@ls -la compose v1/package.json v1/pyproject.toml docker-compose.yml 2>/dev/null | tail -n +2
	@echo ""
	@if [ -f "docker-compose.yml" ]; then \
		echo -e "$(GREEN)🐳 Docker:$(NC)"; \
		docker compose ps 2>/dev/null || echo "  Not running"; \
	fi

env-check: ## Check environment vars
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)🌍 Environment Check$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@echo -e "$(GREEN)DJANGO_SETTINGS_MODULE:$(NC) $$DJANGO_SETTINGS_MODULE"
	@echo -e "$(GREEN)DATABASE_URL:$(NC) $$( [ -n "$$DATABASE_URL" ] && echo 'Set' || echo 'Not set' )"
	@echo ""
	@echo -e "$(GREEN)PYTHONPATH:$(NC)"
	@echo "$$PYTHONPATH" | tr ':' '\n' | sed 's/^/  /'

version: ## Show project versions
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(BOLD)🏷️ Versions$(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@if [ -f "pyproject.toml" ]; then grep -E '^version|^name' pyproject.toml; fi
	@echo -e "$(GREEN)Django version:$(NC) $$(cd v1 && uv run python -m django --version 2>/dev/null || echo 'unknown')"
	@if [ -f "package.json" ]; then echo -e "$(GREEN)Node version:$(NC) $$(cd v1 && npm --version 2>/dev/null || echo 'N/A')"; fi

# ----------------------------------------------------------------------
# Shortcuts
# ----------------------------------------------------------------------
s: setup
d: dev
r: run
t: test
tq: test-quick
c: check
m: migrate
f: format
l: lint
x: fix
pd: populate-data
pdc: populate-data-clear
fb: frontend-build
fp: frontend-production
fw: frontend-watch
fi: frontend-install
cl: clean
cla: clean-all
cd: clean-docker
du: up
dd: down
sh: shell
sp: shell-plus
st: static
cs: collectstatic
su: superuser
csu: createsuperuser
fu: fix-unused
ci: clean-imports
rm: reset-migrations
cm: clean-migrations
doc: docs
docs-s: docs-serve
docs-d: docs-deploy
docs-c: docs-clean