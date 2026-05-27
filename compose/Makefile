.PHONY: help up down config build logs
COMPOSE ?= docker compose
BASE_FILE ?= ../docker-compose.yml

help:
	@echo "compose targets: up down config build logs"

_docker_check:
	@command -v docker >/dev/null 2>&1 || { echo "Docker CLI is not installed in this environment"; exit 0; }

config: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) config || true

build: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) build || true

up: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) up -d --build --remove-orphans || true

down: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) down --remove-orphans || true

logs: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) logs --tail=200 || true
