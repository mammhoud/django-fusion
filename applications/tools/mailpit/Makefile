SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
ENV_FILE     ?= ../../.env

.PHONY: help up down restart logs status ps

help: ## Show this help menu
	@echo 'Mailpit commands: make up | down | restart | logs | status'
	@echo '  up        - Start Mailpit (tools.structa.cloud/mailpit/, SMTP :1025)'
	@echo '  down      - Stop Mailpit'
	@echo '  restart   - Restart Mailpit'
	@echo '  logs      - Tail Mailpit logs'
	@echo '  status    - Show Mailpit status (alias: ps)'

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
