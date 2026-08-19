SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
ENV_FILE     ?= ../../../.env

.PHONY: help up down deploy build restart logs status ps

help: ## Show this help menu
	@echo 'Adminer commands: make up | down | deploy | restart | logs | status'
	@echo '  up        - Start Adminer (tools.structa.cloud/adminer/)'
	@echo '  deploy    - Build + start Adminer'
	@echo '  build     - Build the Adminer image'
	@echo '  down      - Stop Adminer'
	@echo '  restart   - Restart Adminer'
	@echo '  logs      - Tail Adminer logs'
	@echo '  status    - Show Adminer status (alias: ps)'

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
