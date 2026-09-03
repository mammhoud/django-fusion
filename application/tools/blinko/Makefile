SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
# The tool-local env wins so Blinko can be deployed independently. Fall back
# to the shared tools env, then the repo-root env for existing deployments.
ENV_FILE     ?= $(if $(wildcard .env),.env,$(if $(wildcard ../.env),../.env,../../../.env))

.PHONY: help up down deploy build restart logs status ps setup clean clean-unused

help: ## Show this help menu
	@echo 'Blinko commands: make up | down | deploy | build | restart | logs | status | setup'
	@echo '  setup     - Create .env from .env.example if missing'
	@echo '  up        - Start Blinko (tools.structa.cloud/notes/)'
	@echo '  deploy    - Build + start Blinko'
	@echo '  build     - Build the Blinko image'
	@echo '  down      - Stop Blinko'
	@echo '  restart   - Restart Blinko'
	@echo '  logs      - Tail Blinko logs'
	@echo '  status    - Show Blinko status (alias: ps)'

setup: ## Create .env from .env.example if missing
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env from .env.example (generated random defaults)"; \
		cp .env.example .env; \
	else \
		echo "✅ .env already exists — leaving it untouched"; \
	fi

up:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d

deploy: build up

build:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) build

down:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down

restart:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) restart

logs:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f

status:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) ps

ps: status

clean: ## Stop Blinko and prune its images/build cache (volumes kept)
	@echo "🧹 Cleaning Blinko (volumes kept)..."
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down --remove-orphans 2>/dev/null || true
	@docker image prune -f 2>/dev/null || true
	@echo "✅ Blinko clean complete"

clean-unused: clean ## clean + prune stopped containers and all unused build cache (volumes preserved)
	@docker container prune -f 2>/dev/null || true
	@docker image prune -af 2>/dev/null || true
	@docker builder prune -af 2>/dev/null || true
	@echo "✅ clean-unused complete (volumes preserved)"
