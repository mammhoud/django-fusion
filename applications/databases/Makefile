SHELL := /bin/bash
COMPOSE_FILE := docker-compose.yml

.PHONY: up down build logs status restart clean deploy-db deploy-db-force
.PHONY: up-coder down-coder logs-coder status-coder deploy-coder env-coder

up:
	@echo "🟢 Starting databases..."
	@docker compose -f $(COMPOSE_FILE) up -d postgres # redis
	@echo "✅ Databases are up"

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

down:
	@echo "🔴 Stopping databases..."
	@docker compose -f $(COMPOSE_FILE) down
	@echo "✅ Databases stopped"

build:
	@echo "🔨 Building database images..."
	@docker compose -f $(COMPOSE_FILE) build --pull

logs:
	@docker compose -f $(COMPOSE_FILE) logs -f

status:
	@docker compose -f $(COMPOSE_FILE) ps

restart: down up

clean:
	@echo "🧹 Removing databases containers, volumes, and images..."
	@docker compose -f $(COMPOSE_FILE) down -v --rmi all
	@echo "✅ Clean complete"

deploy-db: build up
	@echo "🚀 Databases deployed successfully"

deploy-db-force:
	@echo "🚀 Deploying databases with forced re‑init..."
	@FORCE_REINIT=true docker compose -f $(COMPOSE_FILE) up -d --build postgres
	@echo "✅ Databases deployed (forced re‑init)"

deploy-coder:
	@echo "🚀 Deploying Coder platform..."
	@$(MAKE) --no-print-directory up-coder
	@echo "✅ Coder deployed (http(s)://$${CODER_HOSTNAME:-coder.localhost}:$${CODER_HTTP_PORT:-7080})"

env-coder:
	@echo "📋 Exported env vars for the Coder container:"
	@docker compose -f $(COMPOSE_FILE) config 2>/dev/null | awk '/^  coder:/{flag=1} flag && /^  [a-z]/{flag=0} flag' | sed -n '/    environment:/,/^[a-zA-Z]/p' | grep -E '^      CODER_[A-Z_]+' || true