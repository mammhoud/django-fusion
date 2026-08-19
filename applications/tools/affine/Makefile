SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
ENV_FILE     ?= ../../.env

.PHONY: help up down restart logs status ps

help: ## Show this help menu
	@echo 'AFFiNE commands: make up | down | restart | logs | status'
	@echo '  up        - Start AFFiNE workspace (tools.structa.cloud/space/)'
	@echo '  down      - Stop AFFiNE'
	@echo '  restart   - Restart AFFiNE'
	@echo '  logs      - Tail AFFiNE logs'
	@echo '  status    - Show AFFiNE status (alias: ps)'

up:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d

down:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down

restart:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) restart

logs:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f

status:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) ps

ps: status
