# Makefile – Top‑level orchestrator for the Coolify repo
# ----------------------------------------------------------
# Place this file at /data/Makefile. It aggregates the sub‑Makefiles
# (proxy, applications, services, databases) and provides convenient
# high‑level targets such as `make deploy`.

SHELL := /bin/bash

# -----------------------------------------------------------------
# Helper variables – paths to the main components
# -----------------------------------------------------------------
COOLIFY_ROOT := coolify
PROXY_DIR    := $(COOLIFY_ROOT)/proxy
APP_DIR      := $(COOLIFY_ROOT)/applications
SERVICES_DIR := $(COOLIFY_ROOT)/services
DB_DIR       := $(COOLIFY_ROOT)/databases

# -----------------------------------------------------------------
# PHONY targets – make sure they always run
# -----------------------------------------------------------------
.PHONY: help deploy deploy-proxy deploy-app deploy-media deploy-databases  compose-up compose-down deploy-coolify #deploy-tasks

help:
	@echo "Coolify top‑level Makefile"
	@echo "Available targets:"
	@echo "  make deploy          – Deploy all components"
	@echo "  make deploy-proxy    – Deploy the proxy (Traefik + optional Caddy)"
	@echo "  make deploy-app      – Deploy application services (uses applications/Makefile)"
	@echo "  make deploy-media    – Deploy shared media service"
	@echo "  make deploy-databases – Deploy warehouse services (postgres, redis)"
# 	@echo "  make deploy-tasks    – Deploy background task workers"
	@echo "  make compose-up      – Run combined docker‑compose (docker-compose.yml + docker-compose.custom.yml)"
	@echo "  make compose-down    – Tear down the combined stack"

# ---------------------------------------------------------------
# Top‑level deployment – runs each component's own Makefile
# ---------------------------------------------------------------
deploy: deploy-proxy deploy-app deploy-media deploy-databases  deploy-coolify #deploy-tasks

# ---------------------------------------------------------------
# Delegated shortcuts – invoke sub‑Makefiles directly
# ---------------------------------------------------------------
# Applications (each site has its own Makefile)
ctc-research:
	@$(MAKE) -C $(APP_DIR)/ctc-research

structa:
	@$(MAKE) -C $(APP_DIR)/structa

vresume:
	@$(MAKE) -C $(APP_DIR)/vresume

# Proxy
proxy:
	@$(MAKE) -C $(PROXY_DIR)

# Services (e.g., shared media)
services:
	@$(MAKE) -C $(SERVICES_DIR)

# Databases
databases:
	@$(MAKE) -C $(DB_DIR)

# Generic delegation – forward any unknown target to the applications Makefile
%:
	@$(MAKE) -C $(APP_DIR) $*


deploy-proxy:
	@$(MAKE) -C $(PROXY_DIR) deploy

# The applications Makefile expects an "up" target; we provide an alias.
# It will start the selected website (default website variable can be overridden).
deploy-app:
	@$(MAKE) -C $(APP_DIR) up

# Media service lives under services (shared media nginx container)
deploy-media:
	@docker rm -f shared-media 2>/dev/null || true
	@docker volume prune -f >/dev/null 2>&1 || true
	@docker compose -f $(SERVICES_DIR)/media/docker-compose.yml up -d

# Shortcut to run the shared media nginx service directly
media-nginx:
	@docker compose -f $(SERVICES_DIR)/media/docker-compose.yml up -d

# Databases (postgres, redis) – each repo defines its own targets
deploy-databases:
	@$(MAKE) -C $(DB_DIR) deploy-db

# Deploy the entire Coolify stack (proxy, apps, media, databases, tasks)
# Alias for the top‑level `deploy` target.
deploy-coolify:
	@echo "🚀 Deploying Coolify source stack..."
	@docker network rm -f coolify || true
	@docker compose -f $(COOLIFY_ROOT)/source/docker-compose.yml up -d --remove-orphans

# Task workers – uses the applications Makefile's docker‑compose.tasks.yml
# deploy-tasks:
# 	@$(MAKE) -C $(APP_DIR) docker-up COMPOSE_FILE="docker-compose.tasks.yml"

# -----------------------------------------------------------------
# Convenience wrappers for combined docker‑compose files.
# If a docker‑compose.custom.yml exists, it will be merged.
# -----------------------------------------------------------------
compose-up:
	@cd $(COOLIFY_ROOT) && \
	  if [ -f docker-compose.custom.yml ]; then \
	    docker compose -f docker-compose.yml -f docker-compose.custom.yml up -d; \
	  else \
	    docker compose -f docker-compose.yml up -d; \
	  fi

compose-down:
	@cd $(COOLIFY_ROOT) && \
	  if [ -f docker-compose.custom.yml ]; then \
	    docker compose -f docker-compose.yml -f docker-compose.custom.yml down; \
	  else \
	    docker compose -f docker-compose.yml down; \
	  fi

# ---------------------------------------------------------------
# Merged compose – combines every docker‑compose*.yml under the repo.
# Optional ENV_PREFIX can be set to prepend a project name/prefix.
# ---------------------------------------------------------------
compose-merged-up:
	@files=$$(find $(COOLIFY_ROOT) -type f -name 'docker-compose*.yml' ! -path '*/node_modules/*'); \
	if [ -z "$$files" ]; then \
	  echo "No compose files found"; exit 1; \
	fi; \
	set -e; \
	# Build -f arguments
	args=""; for f in $$files; do args="$$args -f $$f"; done; \
	project=$(if $(ENV_PREFIX),$(ENV_PREFIX),coolify); \
	docker compose $$args -p $$project up -d

compose-merged-down:
	@files=$$(find $(COOLIFY_ROOT) -type f -name 'docker-compose*.yml' ! -path '*/node_modules/*'); \
	if [ -z "$$files" ]; then \
	  echo "No compose files found"; exit 1; \
	fi; \
	set -e; \
	args=""; for f in $$files; do args="$$args -f $$f"; done; \
	project=$(if $(ENV_PREFIX),$(ENV_PREFIX),coolify); \
	docker compose $$args -p $$project down

	@cd $(COOLIFY_ROOT) && \
	  if [ -f docker-compose.custom.yml ]; then \
	    docker compose -f docker-compose.yml -f docker-compose.custom.yml down; \
	  else \
	    docker compose -f docker-compose.yml down; \
	  fi
