SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
# Tools env (application/tools/.env) wins when present; repo-root .env is the
# fallback so existing deployments keep working untouched.
ENV_FILE     ?= $(if $(wildcard ../.env),../.env,../../../.env)

.PHONY: help up down deploy build restart logs status ps setup clean clean-unused

help: ## Show this help menu
	@echo 'Mailpit commands: make up | down | deploy | restart | logs | status | setup'
	@echo '  setup     - Create ../.env from ../.env.example (random defaults) if missing'
	@echo '  up        - Start Mailpit (tools.structa.cloud/mailpit/, SMTP :1025)'
	@echo '  deploy    - Build + start Mailpit'
	@echo '  build     - Build the Mailpit image'
	@echo '  down      - Stop Mailpit'
	@echo '  restart   - Restart Mailpit'
	@echo '  logs      - Tail Mailpit logs'
	@echo '  status    - Show Mailpit status (alias: ps)'

setup: ## Create ../.env from ../.env.example if missing
	@if [ ! -f ../.env ]; then \
		echo "📝 Creating ../.env from ../.env.example (generated random defaults — rotate before shared use)"; \
		cp ../.env.example ../.env; \
	else \
		echo "✅ ../.env already exists — leaving it untouched"; \
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

clean: ## Stop Mailpit and prune its images/build cache (volumes kept)
	@echo "🧹 Cleaning Mailpit (volumes kept)..."
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down --remove-orphans 2>/dev/null || true
	@docker image prune -f 2>/dev/null || true
	@echo "✅ Mailpit clean complete"

clean-unused: clean ## clean + prune stopped containers and build cache (volumes preserved)
	@docker container prune -f 2>/dev/null || true
	@docker builder prune -f 2>/dev/null || true
	@echo "✅ clean-unused complete (volumes preserved)"
