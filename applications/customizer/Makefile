# ============================================================
# Customizer Makefile – Build, collectstatic & deploy targets
# ============================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

PYTHON     ?= python
MANAGE     := $(PYTHON) manage.py
ASSETS_DIR := assets
BUNDLES_DIR := $(ASSETS_DIR)/bundles/customizer
LOG_DIR    ?= logs

# -----------------------------------------------------------------
# Help
# -----------------------------------------------------------------
.PHONY: help

help:
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║   Structa Customizer – Makefile                         ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Frontend (webpack):"
	@echo "  make build             Production webpack build (Bootstrap + SCSS + JS)"
	@echo "  make build-dev         Development webpack build (faster, source maps)"
	@echo "  make watch             Webpack watch mode (rebuilds on file change)"
	@echo "  make dev               Webpack dev server with HMR (port 5093)"
	@echo "  make clean             Remove generated bundles"
	@echo ""
	@echo "Static files:"
	@echo "  make collectstatic     Django collectstatic → STATIC_ROOT (staticfiles/)"
	@echo "  make build-collect     Build + collectstatic (single command)"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy            Full deploy: build → collectstatic → migrate"
	@echo "  make install-assets    Install npm dependencies (npm ci)"
	@echo ""
	@echo "Django management:"
	@echo "  make check             Django system checks"
	@echo "  make migrate           Apply Django migrations"
	@echo "  make runserver         Dev server on 127.0.0.1:5073"
	@echo "  make shell             Django shell"
	@echo ""


# ============================================================
# FRONTEND (Webpack)
# ============================================================
# These mirror the project's workspace.mjs pattern:
#   workspace.mjs:  webpack(site, 'production')
#   workspace.mjs:  webpack(site, 'development')
#   workspace.mjs:  webpack(site, 'development', ['watch'])
#   workspace.mjs:  webpack(site, 'development', ['serve'])
#   workspace.mjs:  clean(site)  → removes bundles
#
# The customizer has its own assets/package.json, so we run
# webpack locally via npm --prefix assets.

.PHONY: build build-dev watch dev clean install-assets

build:
	@echo "🟢 Building production bundles…"
	@npm --prefix $(ASSETS_DIR) run build
	@echo "✅ Production build done → $(BUNDLES_DIR)/"

build-dev:
	@echo "🟡 Building development bundles…"
	@npm --prefix $(ASSETS_DIR) run build:dev
	@echo "✅ Development build done → $(BUNDLES_DIR)/"

watch:
	@echo "🔄 Watching for file changes…"
	@npm --prefix $(ASSETS_DIR) run watch

dev:
	@echo "🌐 Starting webpack dev server on http://localhost:5093 …"
	@npm --prefix $(ASSETS_DIR) run dev

clean:
	@echo "🧹 Removing generated bundles…"
	@rm -rf $(ASSETS_DIR)/bundles/customizer
	@echo "✅ Bundles cleaned: $(BUNDLES_DIR)/"

install-assets:
	@echo "📦 Installing npm dependencies…"
	@npm --prefix $(ASSETS_DIR) ci --include=dev --legacy-peer-deps
	@echo "✅ npm dependencies installed"


# ============================================================
# STATIC FILES
# ============================================================
# Mirrors workspace.mjs: manage(site, ['collectstatic', '--noinput'])
# and applications/Makefile: collectstatic-site target.

.PHONY: collectstatic build-collect

collectstatic:
	@mkdir -p $(LOG_DIR)
	@echo "📂 Collecting static files into STATIC_ROOT…"
	@echo "    STATIC_ROOT: $$($(MANAGE) diffsettings 2>/dev/null | grep ^STATIC_ROOT || echo 'staticfiles/')"
	@$(MANAGE) collectstatic --noinput --clear 2>&1 | tee $(LOG_DIR)/collectstatic.log
	@echo "✅ Collectstatic complete (logged to $(LOG_DIR)/collectstatic.log)"

build-collect:
	@mkdir -p $(LOG_DIR)
	@echo "🔨 Building assets + collecting static…"
	@$(MAKE) build 2>&1 | tee $(LOG_DIR)/build.log
	@$(MAKE) collectstatic 2>&1 | tee $(LOG_DIR)/collectstatic.log
	@echo "✅ Build + collectstatic complete"


# ============================================================
# DEPLOYMENT
# ============================================================
# Full deployment pipeline: build → collectstatic → migrate.
# Mirrors the project's full-site-check pattern.

.PHONY: deploy

deploy:
	@mkdir -p $(LOG_DIR)
	@echo "🚀 Deploying customizer…"
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


# ============================================================
# DJANGO MANAGEMENT
# ============================================================

.PHONY: check migrate runserver shell

check:
	$(MANAGE) check

migrate:
	$(MANAGE) migrate

runserver:
	$(MANAGE) runserver 127.0.0.1:5073

shell:
	$(MANAGE) shell
