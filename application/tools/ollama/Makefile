SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
ENV_FILE     ?= ../../../.env

.PHONY: help up down deploy build restart logs status ps pull pull-model

help: ## Show this help menu
	@echo 'Ollama commands: make up | down | deploy | restart | logs | status | pull'
	@echo '  up        - Start Ollama + Open WebUI (tools.structa.cloud/ai/)'
	@echo '  deploy    - Build + start Ollama + Open WebUI'
	@echo '  build     - Build Ollama images'
	@echo '  down      - Stop Ollama'
	@echo '  restart   - Restart Ollama'
	@echo '  logs      - Tail Ollama logs'
	@echo '  status    - Show Ollama status (alias: ps)'
	@echo '  pull      - Pull a model: make pull MODEL=llama3.2:3b'

# ollama-net is external; create it if missing so a standalone `make up` works.
up:
	@docker network inspect ollama-net >/dev/null 2>&1 || docker network create ollama-net
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

# `make pull MODEL=llama3.2:3b`
pull:
	@docker exec -it ollama ollama pull $(MODEL)
