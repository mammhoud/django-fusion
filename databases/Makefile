SHELL := /bin/bash
COMPOSE_FILE := docker-compose.yml

.PHONY: up down build logs status restart clean deploy-db deploy-db-force

up:
	@echo "🟢 Starting databases..."
	@docker compose -f $(COMPOSE_FILE) up -d postgres # redis
	@echo "✅ Databases are up"

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