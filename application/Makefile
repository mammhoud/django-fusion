SHELL := /bin/bash
COMPOSE_FILE := docker-compose.yml
.PHONY: help up deploy down build status logs restart ps \
        up-coder down-coder logs-coder status-coder deploy-coder env-coder \
        clean clean-unused

help: ## Show this help menu
	@echo 'Applications (Coder platform) commands:'
	@echo '  make up           - Start the Coder container'
	@echo '  make deploy       - Build + start Coder (used by root make deploy-coder)'
	@echo '  make down         - Stop and remove the Coder container'
	@echo '  make build        - Build the Coder image'
	@echo '  make status       - Show Coder container status (alias: ps)'
	@echo '  make logs         - Follow Coder logs'
	@echo '  make restart      - Restart the Coder container'
	@echo '  make env-coder    - Print the Coder container env vars'
	@echo '  (back-compat: up-coder / down-coder / logs-coder / status-coder / deploy-coder)'

up: up-coder ## Start the Coder container

deploy: build up ## Build + start Coder

build:
	@docker compose -f $(COMPOSE_FILE) build coder

down: down-coder ## Stop and remove the Coder container

status: status-coder ## Show Coder status

logs: logs-coder ## Follow Coder logs

restart: down-coder up-coder ## Restart the Coder container

ps: status-coder

up-coder:
	@echo "🟢 Starting Coder..."
	@docker compose -f $(COMPOSE_FILE) up -d coder
	@echo "✅ Coder is up"

down-coder:
	@echo "🔴 Stopping Coder..."
	@docker compose -f $(COMPOSE_FILE) stop coder
	@docker compose -f $(COMPOSE_FILE) rm -f coder
	@echo "✅ Coder stopped"

logs-coder:
	@docker compose -f $(COMPOSE_FILE) logs -f coder

status-coder:
	@docker ps --filter "name=coder" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

deploy-coder: deploy ## Deploy Coder (back-compat alias)

env-coder:
	@echo "📋 Exported env vars for the Coder container:"
	@docker compose -f $(COMPOSE_FILE) config 2>/dev/null | awk '/^  coder:/{flag=1} flag && /^  [a-z]/{flag=0} flag' | sed -n '/    environment:/,/^[a-zA-Z]/p' | grep -E '^      CODER_[A-Z_]+' || true

clean: ## Stop Coder and prune its images/build cache (volumes kept)
	@echo "🧹 Cleaning Coder (volumes kept)..."
	@docker compose -f $(COMPOSE_FILE) down --remove-orphans 2>/dev/null || true
	@docker image prune -f 2>/dev/null || true
	@echo "✅ Coder clean complete"

clean-unused: clean ## clean + prune stopped containers and build cache (volumes preserved)
	@docker container prune -f 2>/dev/null || true
	@docker builder prune -f 2>/dev/null || true
	@echo "✅ clean-unused complete (volumes preserved)"
