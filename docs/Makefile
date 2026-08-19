# docs/Makefile — Docus documentation build, serve, validate, and deploy
# The Docus app lives at the root of docs/ (flattened from docs/docus/).
SHELL := /bin/bash

COMPOSE_FILE := docker-compose.yml
ENV_FILE     ?= ../.env

.PHONY: help install build build-static serve preview check clean deploy \
        up down restart logs status ps

.DEFAULT_GOAL := help

DocusDir := .

help: ## Show documentation commands
	@printf '%s\n' \
		'Docus documentation commands:' \
		'  make install       Install Docus dependencies' \
		'  make build         Build the Docus Nuxt server' \
		'  make build-static  Generate an optional static export' \
		'  make serve         Run the Docus development server' \
		'  make preview       Preview the generated server output' \
		'  make check         Validate Docus configuration and locale sources' \
		'  make clean         Remove generated Docus output' \
		'  make deploy        Build the Docus image (docs/Dockerfile)' \
		'  make up            Build + start the Docus container (docs.structa.cloud)' \
		'  make down          Stop the Docus container' \
		'  make restart       Restart the Docus container' \
		'  make logs          Tail Docus container logs' \
		'  make status        Show Docus container status (alias: ps)'

install: ## Install Docus dependencies
	cd $(DocusDir) && npm install

build: ## Build the Docus Nuxt server
	cd $(DocusDir) && npm run build

build-static: ## Generate an optional static Docus export
	cd $(DocusDir) && npm run build:static

serve: ## Serve Docus locally at the /docs/ base path
	cd $(DocusDir) && npm run dev

preview: ## Preview the generated Docus server output
	cd $(DocusDir) && npm run preview

check: ## Validate Docus configuration, generated graph metadata, and locale sources
	@test -f $(DocusDir)/nuxt.config.ts
	@test -f $(DocusDir)/app.config.ts
	@test -f $(DocusDir)/ar-content/index.md
	@test -f $(DocusDir)/ar-content/guides/quickstart.md
	@test -f $(DocusDir)/ar-content/guides/deployment.md
	@node --check $(DocusDir)/scripts/prepare-content.mjs
	@node --check $(DocusDir)/scripts/validate-content.mjs
	@cd $(DocusDir) && npm run prepare-content >/dev/null
	@cd $(DocusDir) && npm run validate-content
	@grep -q "@nuxtjs/i18n" $(DocusDir)/package.json
	@grep -q "code: 'ar'" $(DocusDir)/nuxt.config.ts
	@echo 'Docus configuration and English/Arabic source checks passed.'

deploy: ## Build the Docus image (docs/Dockerfile)
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) build

up: ## Build + start the Docus container (docs.structa.cloud)
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build

down: ## Stop the Docus container
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down

restart: ## Restart the Docus container
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) restart

logs: ## Tail Docus container logs
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f

status: ## Show Docus container status
	@docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) ps

ps: status

clean: ## Remove generated Docus output and content
	rm -rf $(DocusDir)/content $(DocusDir)/.nuxt $(DocusDir)/.output $(DocusDir)/dist
