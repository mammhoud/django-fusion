SHELL := /bin/bash
COMPOSE_FILE := docker-compose.yml

.PHONY: up down build logs status restart clean

up:
	@echo "🟢 Starting databases..."
	@docker compose -f $(COMPOSE_FILE) up -d postgres redis
	@echo "✅ Databases are up"

down:
	@echo "🔴 Stopping databases..."
	@docker compose -f $(COMPOSE_FILE) down
	@echo "✅ Databases stopped"

build:
	@echo "🔨 Building database images (using official images)"
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