SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
# Tools env (application/tools/.env) wins when present; repo-root .env is the
# fallback so existing deployments keep working untouched.
ENV_FILE     ?= $(if $(wildcard ../.env),../.env,../../../.env)

.PHONY: help up down deploy build restart logs status ps setup

help: ## Show this help menu
	@echo 'Adminer commands: make up | down | deploy | restart | logs | status | setup'
	@echo '  setup     - Create ../.env from ../.env.example (random defaults) if missing'
	@echo '  up        - Start Adminer (tools.structa.cloud/adminer/)'
	@echo '  deploy    - Build + start Adminer'
	@echo '  build     - Build the Adminer image'
	@echo '  down      - Stop Adminer'
	@echo '  restart   - Restart Adminer'
	@echo '  logs      - Tail Adminer logs'
	@echo '  status    - Show Adminer status (alias: ps)'

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
