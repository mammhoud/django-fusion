.PHONY: all fb fb-ctc fb-xellent watch remove-ctc build-ctc

# Color codes
BLUE := \033[0;34m
GREEN := \033[0;32m
NC := \033[0m

all: fb

fb: fb-ctc fb-xellent

fb-ctc:
	@echo "📦 Compiling CTC-Research SCSS..."
	@mkdir -p ctc-research/assets/styles/css
	@sass ctc-research/assets/styles/scss/main.scss ctc-research/assets/styles/css/main.css --style=compressed --no-source-map
	@echo "✅ CTC-Research compiled"

fb-xellent:
	@echo "📦 Compiling Xellent SCSS..."
	@mkdir -p xellent-site/assets/styles/css
	@sass xellent-site/assets/styles/scss/main.scss xellent-site/assets/styles/css/main.css --style=compressed --no-source-map
	@echo "✅ Xellent compiled"
	@echo "📦 Setting up Preline CSS..."
	@PRELINE_SRC=$$(find xellent-site/node_modules/preline -name "preline.css" 2>/dev/null | head -1); \
	if [ -n "$$PRELINE_SRC" ] && [ -f "$$PRELINE_SRC" ]; then \
		cp "$$PRELINE_SRC" xellent-site/assets/styles/css/preline.css; \
		echo "✅ Preline CSS copied"; \
	else \
		touch xellent-site/assets/styles/css/preline.css; \
		echo "⚠️  Preline CSS not found -> Placeholder created."; \
	fi

watch:
	@echo "👀 Watching SCSS files..."
	@sass --watch ctc-research/assets/styles/scss:ctc-research/assets/styles/css xellent-site/assets/styles/scss:xellent-site/assets/styles/css

remove-ctc: ## 🐳 Remove Docker containers, networks, and named volumes for ctc-research
	@echo -e "$(BLUE)Removing Docker containers with prefix 'ctc'...$(NC)"
	@docker ps -a --format '{{.Names}}' | grep '^ctc' | xargs -r docker stop
	@docker ps -a --format '{{.Names}}' | grep '^ctc' | xargs -r docker rm
	@echo -e "$(BLUE)Removing ctc-research named volumes...$(NC)"
	@docker volume ls --format '{{.Name}}' | grep '^ctc-research_' | xargs -r docker volume rm || true
	@echo -e "$(GREEN)✅ ctc containers and volumes removed$(NC)"

build-ctc: ## 🐳 Rebuild and start the ctc-research service
	@echo -e "$(BLUE)Rebuilding ctc-research Docker image...$(NC)"
	@docker compose -f ctc-research/docker-compose.yml build --no-cache
	@echo -e "$(BLUE)Starting ctc-research containers...$(NC)"
	@docker compose -f ctc-research/docker-compose.yml up -d ctc-django-main ctc-nginx
	@echo -e "$(BLUE)Waiting for containers to be healthy...$(NC)"
	@sleep 10
	@docker logs ctc-django-main --tail 50
	@echo -e "$(GREEN)✅ ctc-research service started$(NC)"
