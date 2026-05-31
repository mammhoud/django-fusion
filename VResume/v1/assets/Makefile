# v1/assets/Makefile – Frontend build and CSS tools
.PHONY: help install build production watch start purge analyze clean

.DEFAULT_GOAL := help

GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
CYAN   := \033[0;36m
NC     := \033[0m

NPM := npm
NPX := npx

help: ## Show frontend commands help
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(CYAN)      FRONTEND / ASSETS COMMANDS         $(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-25s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Install npm dependencies
	@if [ -f "package-lock.json" ]; then \
		$(NPM) ci --legacy-peer-deps --no-audit --no-fund; \
	else \
		$(NPM) install --legacy-peer-deps; \
	fi
	@echo -e "$(GREEN)✅ Installed$(NC)"

build: install ## Build frontend (development)
	@echo -e "$(BLUE)Building frontend (dev)...$(NC)"
	$(NPM) run build
	@echo -e "$(GREEN)✅ Built$(NC)"

production: install ## Build frontend (production with PurgeCSS)
	@echo -e "$(BLUE)Building frontend (production)...$(NC)"
	$(NPM) run build
	@echo -e "$(GREEN)✅ Production build done$(NC)"

watch: install ## Watch and rebuild on changes
	@echo -e "$(BLUE)Watching frontend...$(NC)"
	NODE_ENV=development $(NPM) run dev

start: watch ## Alias for watch

purge: ## Run PurgeCSS manually
	@echo -e "$(BLUE)Purging CSS...$(NC)"
	NODE_ENV=production $(NPX) purgecss --config ./purgecss.config.js
	@echo -e "$(GREEN)✅ CSS purged$(NC)"

analyze: ## Analyze CSS bundle size
	@echo -e "$(BLUE)Analyzing CSS...$(NC)"
	@$(NPX) cssnano --no-map ../static/css/master.css | $(NPX) cssstats
	@echo -e "$(GREEN)✅ Analysis done$(NC)"

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