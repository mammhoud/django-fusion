.PHONY: help up down config build logs prune-containers prune-data media
COMPOSE ?= docker compose
BASE_FILE ?= ../docker-compose.yml

help:
	@echo "compose targets: up down config build logs media prune-containers prune-data"

_docker_check:
	@command -v docker >/dev/null 2>&1 || { echo "Docker CLI is not installed in this environment"; exit 0; }

config: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) config || true

build: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) build || true

# Build only the shared/base services (proxy, db, redis, docs, adminer, blinko)
.PHONY: build-base
build-base: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) build traefik postgres redis docs adminer blinko || true

up: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) up -d --build --remove-orphans || true

down: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) down --remove-orphans || true

logs: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) logs --tail=200 || true

media: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) up -d --build shared-media || true

prune-containers: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) down --remove-orphans && docker container prune -f || true

prune-data: _docker_check
	@command -v docker >/dev/null 2>&1 && $(COMPOSE) -f $(BASE_FILE) down --volumes --remove-orphans || true
<<<<<<< HEAD
	@rm -rf postgres/backups/* ../compose/data/*
	@mkdir -p postgres/backups ../compose/data
=======
	@rm -rf postgres/backups/* ../compose/data/* ../.docker-image-data/*
	@mkdir -p postgres/backups ../compose/data ../.docker-image-data
	@touch ../.docker-image-data/.keep
>>>>>>> generic
