# docs/Makefile – Documentation build, serve, deploy, clean
.PHONY: help build serve deploy clean check

.DEFAULT_GOAL := help

GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
CYAN   := \033[0;36m
RED    := \033[0;31m
NC     := \033[0m

help: ## Show docs commands help
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(CYAN)      DOCUMENTATION COMMANDS             $(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-25s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

build: ## Build docs with MkDocs
	@echo -e "$(BLUE)Building documentation...$(NC)"
	@if command -v mkdocs >/dev/null 2>&1; then \
		mkdocs build; \
		echo -e "$(GREEN)✅ Built into site/$(NC)"; \
	else \
		echo -e "$(RED)mkdocs not installed$(NC)"; \
	fi

serve: ## Serve docs locally
	@echo -e "$(BLUE)Serving docs at http://localhost:8000...$(NC)"
	@if command -v mkdocs >/dev/null 2>&1; then \
		mkdocs serve; \
	else \
		echo -e "$(RED)mkdocs not installed$(NC)"; \
	fi

deploy: ## Deploy to GitHub Pages
	@echo -e "$(BLUE)Deploying docs...$(NC)"
	@if command -v mkdocs >/dev/null 2>&1; then \
		mkdocs gh-deploy; \
		echo -e "$(GREEN)✅ Deployed$(NC)"; \
	else \
		echo -e "$(RED)mkdocs not installed$(NC)"; \
	fi

clean: ## Remove built docs
	@echo -e "$(BLUE)Cleaning docs...$(NC)"
	@rm -rf site/
	@echo -e "$(GREEN)✅ Cleaned$(NC)"

check: ## Check docs structure
	@echo -e "$(BLUE)Checking docs...$(NC)"
	@if [ -f "mkdocs.yml" ]; then \
		echo -e "$(GREEN)✅ mkdocs.yml found$(NC)"; \
		echo "Sections:"; \
		grep "^  - " mkdocs.yml | sed 's/^/  /'; \
	else \
		echo -e "$(RED)❌ mkdocs.yml missing$(NC)"; \
	fi
	@echo ""
	@if [ -d "docs" ]; then \
		echo "Doc directories:"; \
		ls -d docs/*/ 2>/dev/null | sed 's|docs/||; s|/||; s|^|  |'; \
	fi