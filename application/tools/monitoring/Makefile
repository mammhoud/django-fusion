SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
ENV_FILE     ?= ../../../.env

.PHONY: help up down deploy build restart logs status ps

help: ## Show this help menu
	@echo 'Monitoring commands: make up | down | deploy | restart | logs | status'
	@echo '  up        - Start Prometheus + Grafana (tools.structa.cloud/grafana/)'
	@echo '  deploy    - Build + start monitoring stack'
	@echo '  build     - Build monitoring images'
	@echo '  down      - Stop monitoring stack'
	@echo '  restart   - Restart monitoring stack'
	@echo '  logs      - Tail monitoring logs'
	@echo '  status    - Show monitoring status (alias: ps)'

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
