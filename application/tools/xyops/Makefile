SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
ENV_FILE     ?= $(if $(wildcard .env),.env,$(if $(wildcard ../.env),../.env,../../../.env))

.PHONY: help up down deploy build restart logs status ps setup clean clean-unused

help: ## Show this help menu
	@echo 'xyOps commands: make up | down | deploy | build | restart | logs | status | setup'
	@echo '  setup     - Create .env from .env.example if missing'
	@echo '  up        - Start xyOps (ops.structa.cloud)'
	@echo '  deploy    - Build + start xyOps'
	@echo '  build     - Pull the xyOps image'
	@echo '  down      - Stop xyOps'
	@echo '  restart   - Restart xyOps'
	@echo '  logs      - Tail xyOps logs'
	@echo '  status    - Show xyOps status (alias: ps)'
	@echo ''
	@echo 'Default sign-in: admin / admin — change immediately after first login.'

setup: ## Create .env from .env.example if missing
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env from ../.env.example"; \
		cp ../.env.example .env; \
	else \
		echo "✅ .env already exists — leaving it untouched"; \
	fi

up:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d

deploy: build up

build:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) pull

down:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down

restart:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) restart

logs:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f

status:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) ps

ps: status

clean: ## Stop xyOps and prune its images/build cache (volumes kept)
	@echo "🧹 Cleaning xyOps (volumes kept)..."
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down --remove-orphans 2>/dev/null || true
	@docker image prune -f 2>/dev/null || true
	@echo "✅ xyOps clean complete"

clean-unused: clean ## clean + prune stopped containers and build cache (volumes preserved)
	@docker container prune -f 2>/dev/null || true
	@docker builder prune -f 2>/dev/null || true
	@echo "✅ clean-unused complete (volumes preserved)"