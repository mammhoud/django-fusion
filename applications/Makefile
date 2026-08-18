SHELL := /bin/bash
COMPOSE_FILE := docker-compose.yml
.PHONY: up-coder down-coder logs-coder status-coder deploy-coder env-coder


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


deploy-coder:
	@echo "🚀 Deploying Coder platform..."
	@$(MAKE) --no-print-directory up-coder
	@echo "✅ Coder deployed (http(s)://$${CODER_HOSTNAME:-coder.localhost}:$${CODER_HTTP_PORT:-7080})"

env-coder:
	@echo "📋 Exported env vars for the Coder container:"	@docker compose -f $(COMPOSE_FILE) config 2>/dev/null | awk '/^  coder:/{flag=1} flag && /^  [a-z]/{flag=0} flag' | sed -n '/    environment:/,/^[a-zA-Z]/p' | grep -E '^      CODER_[A-Z_]+' || true
