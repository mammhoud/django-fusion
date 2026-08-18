SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
ENV_FILE     ?= ../../.env

.PHONY: up down restart logs status ps pull pull-model

# ollama-net is external; create it if missing so a standalone `make up` works.
up:
	@docker network inspect ollama-net >/dev/null 2>&1 || docker network create ollama-net
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

# `make pull MODEL=llama3.2:3b`
pull:
	@docker exec -it ollama ollama pull $(MODEL)
