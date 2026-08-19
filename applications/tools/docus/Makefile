SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
ENV_FILE     ?= ../../.env

.PHONY: help up down restart logs status ps

help: ## Show this help menu
	@echo 'Docus commands: make up | down | restart | logs | status'
	@echo '  up        - Build + start Docus docs (tools.structa.cloud/docs/)'
	@echo '  down      - Stop Docus'
	@echo '  restart   - Restart Docus'
	@echo '  logs      - Tail Docus logs'
	@echo '  status    - Show Docus status (alias: ps)'

up:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build

down:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down

restart:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) restart

logs:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f

status:
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) ps

ps: status
