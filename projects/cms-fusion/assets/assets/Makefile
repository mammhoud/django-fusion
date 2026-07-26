# v1/assets/Makefile – Frontend build and CSS tools
.PHONY: help install build production watch start purge analyze clean clean-site build-all build-ctc build-structa build-vresume collectstatic-site build-collect-site

.DEFAULT_GOAL := help

GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
CYAN   := \033[0;36m
NC     := \033[0m

NPM := npm
NPX := npm exec --no --
PYTHON ?= ../.venv/bin/python
PROJECT_PATH ?= ctc-research
DJANGO_SITE ?= $(PROJECT_PATH)

help: ## Show frontend commands help
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(CYAN)      FRONTEND / ASSETS COMMANDS         $(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-25s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Install npm dependencies
	@if [ -f "package-lock.json" ]; then \
		$(NPM) ci --include=dev --legacy-peer-deps --no-audit --no-fund; \
	else \
		$(NPM) install --legacy-peer-deps; \
	fi
	@echo -e "$(GREEN)✅ Installed$(NC)"

build: install ## Build frontend for PROJECT_PATH (default: ctc-research)
	@echo -e "$(BLUE)Building frontend for PROJECT_PATH=$(PROJECT_PATH)...$(NC)"
	PROJECT_PATH=$(PROJECT_PATH) $(NPM) run build
	@echo -e "$(GREEN)✅ Built$(NC)"

production: install ## Build production frontend for PROJECT_PATH
	@echo -e "$(BLUE)Building frontend for PROJECT_PATH=$(PROJECT_PATH) (production)...$(NC)"
	PROJECT_PATH=$(PROJECT_PATH) NODE_ENV=production $(NPM) run build
	@echo -e "$(GREEN)✅ Production build done$(NC)"

watch: install ## Watch and rebuild PROJECT_PATH on changes
	@echo -e "$(BLUE)Watching frontend for PROJECT_PATH=$(PROJECT_PATH)...$(NC)"
	PROJECT_PATH=$(PROJECT_PATH) NODE_ENV=development $(NPM) run watch

start: watch ## Alias for watch

purge: ## Run PurgeCSS manually
	@echo -e "$(BLUE)Purging CSS...$(NC)"
	NODE_ENV=production $(NPX) purgecss --config ./purgecss.config.js
	@echo -e "$(GREEN)✅ CSS purged$(NC)"

analyze: ## Analyze CSS bundle size
	@echo -e "$(BLUE)Analyzing CSS...$(NC)"
	@$(NPX) cssnano --no-map ../static/css/master.css | $(NPX) cssstats
	@echo -e "$(GREEN)✅ Analysis done$(NC)"

build-ctc: ## Build ctc-research assets
	@PROJECT_PATH=ctc-research $(NPM) run build:ctc

build-structa: ## Build lms/structa assets
	@PROJECT_PATH=lms $(NPM) run build:structa

build-vresume: ## Build VResume assets
	@PROJECT_PATH=vresume $(NPM) run build:vresume

build-all: install ## Build all project asset bundles
	@$(NPM) run build:all

collectstatic-site: ## Collect static for PROJECT_PATH/DJANGO_SITE
	@cd .. && $(PYTHON) manage.py --site=$(DJANGO_SITE) collectstatic --noinput

build-collect-site: build collectstatic-site clean-bundles-site ## Build assets, collect static, and clean bundles for PROJECT_PATH

clean-bundles-site: ## Remove frontend bundles after collectstatic to save space
	@echo "Cleaning bundles after collectstatic..."
	@rm -rf bundles/*.js bundles/*.css 2>/dev/null || true
	@echo "✅ Bundles cleaned"

clean-site: ## Remove only the selected PROJECT_PATH bundle artifacts
	@$(NPM) run clean:$(if $(filter $(PROJECT_PATH),ctc ctc-research ctc-research.com),ctc,$(if $(filter $(PROJECT_PATH),structa lms structa.cloud),structa,$(if $(filter $(PROJECT_PATH),vresume VResume resume),vresume,$(PROJECT_PATH)))) 2>/dev/null || rm -rf bundles/$(PROJECT_PATH) ../$(PROJECT_PATH)/assets/bundles

clean-bundles-site: ## Remove frontend bundles after collectstatic to save space
	@echo "Cleaning bundles after collectstatic..."
	@rm -rf bundles/*.js bundles/*.css 2>/dev/null || true
	@echo "✅ Bundles cleaned"

clean: ## Remove frontend build artifacts
	@echo -e "$(BLUE)Cleaning frontend...$(NC)"
	@rm -rf node_modules package-lock.json 2>/dev/null || true
	@if [ -d "node_modules" ]; then \
		echo -e "$(YELLOW)Removing old node_modules...$(NC)"; \
		rm -rf node_modules package-lock.json; \
	fi
	@$(NPM) cache clean --force 2>/dev/null || true

	@if [ -f "package.json" ]; then \
		$(NPM) run clean 2>/dev/null || rm -rf ./bundles 2>/dev/null; \
		echo -e "$(GREEN)✅ Frontend cleaned$(NC)"; \
	else \
		echo -e "$(YELLOW)No frontend config$(NC)"; \
	fi
