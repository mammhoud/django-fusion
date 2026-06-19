# ============================================================
# Unified Workspace & Coolify Deployment Makefile
# Centralised command delegation for all deployment components
# ============================================================

SHELL := /bin/bash

# -----------------------------------------------------------------
# Directory layout – adjust these if your structure differs
# -----------------------------------------------------------------
WORKSPACE_ROOT   := .
DEPLOY_DIR       := deploy
APPLICATIONS_DIR := $(DEPLOY_DIR)/applications
PROXY_DIR        := $(DEPLOY_DIR)/proxy
SERVICES_DIR     := $(DEPLOY_DIR)/services
DATABASES_DIR    := $(DEPLOY_DIR)/databases
SOURCE_DIR       := source                # Coolify source (docker-compose.yml)

# -----------------------------------------------------------------
# Include sub‑Makefiles (ignore if missing)
# -----------------------------------------------------------------
-include $(APPLICATIONS_DIR)/Makefile
-include $(PROXY_DIR)/Makefile
-include $(SERVICES_DIR)/Makefile
-include $(DATABASES_DIR)/Makefile
-include $(SOURCE_DIR)/Makefile

# -----------------------------------------------------------------
# PHONY targets – always run
# -----------------------------------------------------------------
.PHONY: help deploy deploy-all deploy-proxy deploy-app deploy-media deploy-tasks deploy-docs
.PHONY: deploy-databases deploy-coolify restart-coolify build-coolify list-coolify
.PHONY: status logs logs-coolify stop restart
.PHONY: prune prune-containers prune-volumes prune-images
.PHONY: cert cert-generate cert-backup cert-restore cert-validate cert-check
.PHONY: build build-app build-media build-docs
.PHONY: validate help-all compose-up compose-down compose-merged-up compose-merged-down
.PHONY: ctc-research structa vresume proxy services databases

# -----------------------------------------------------------------
# Help – comprehensive overview
# -----------------------------------------------------------------
help:
	@echo "🚀 Structa Cloud Deployment System"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Available commands:"
	@echo "  make deploy            - Deploy all components (proxy, apps, media, databases, Coolify)"
	@echo "  make deploy:app        - Build and start application services"
	@echo "  make deploy:proxy      - Deploy and restart reverse proxy"
	@echo "  make deploy:media      - Build and start media server"
	@echo "  make deploy:tasks      - Start background task workers"
	@echo "  make deploy:docs       - Start documentation service"
	@echo "  make deploy:db         - Deploy databases (Postgres, Redis)"
	@echo "  make deploy:all        - Deploy all services (alias for deploy)"
	@echo ""
	@echo "Coolify management:"
	@echo "  make deploy-coolify    - Deploy Coolify using its docker compose"
	@echo "  make restart-coolify   - Restart Coolify service"
	@echo "  make build-coolify     - Rebuild Coolify containers"
	@echo "  make list-coolify      - List running Coolify containers"
	@echo ""
	@echo "Compose orchestration:"
	@echo "  make compose-up        - Start combined docker-compose.yml (+ custom if exists)"
	@echo "  make compose-down      - Stop combined stack"
	@echo "  make compose-merged-up - Start all compose files found recursively"
	@echo "  make compose-merged-down - Stop all compose files found recursively"
	@echo ""
	@echo "Management commands:"
	@echo "  make status            - Show deployment status"
	@echo "  make logs              - Show logs from all services"
	@echo "  make stop              - Stop all services"
	@echo "  make restart           - Restart all services"
	@echo ""
	@echo "Maintenance commands:"
	@echo "  make prune:containers  - Remove stopped containers"
	@echo "  make prune:volumes     - Remove unused volumes"
	@echo "  make prune:images      - Remove unused images"
	@echo ""
	@echo "Certificate management (Proxy component):"
	@echo "  make cert:generate     - Generate self-signed certificates"
	@echo "  make cert:backup       - Backup current certificates"
	@echo "  make cert:restore      - Restore certificates from backup"
	@echo "  make cert:validate     - Validate certificate/key pairs"
	@echo "  make cert:check        - Check certificate expiry status"
	@echo ""
	@echo "Per‑app shortcuts (if each has its own Makefile):"
	@echo "  make ctc-research      - Run ctc-research's Makefile"
	@echo "  make structa           - Run structa's Makefile"
	@echo "  make vresume           - Run vresume's Makefile"
	@echo "  make proxy             - Run proxy's Makefile"
	@echo "  make services          - Run services' Makefile"
	@echo "  make databases         - Run databases' Makefile"
	@echo ""
	@echo "See individual component Makefiles for more details."

# -----------------------------------------------------------------
# Deployment targets
# -----------------------------------------------------------------
deploy: deploy-all

deploy-all:
	@echo "🚀 Deploying all services..."
	@$(MAKE) --no-print-directory deploy-proxy
	@$(MAKE) --no-print-directory deploy-app
	@$(MAKE) --no-print-directory deploy-media
	@$(MAKE) --no-print-directory deploy-tasks
	@$(MAKE) --no-print-directory deploy-docs
	@$(MAKE) --no-print-directory deploy-databases
	@$(MAKE) --no-print-directory deploy-coolify
	@echo "✅ All services deployed"

deploy-app:
	@cd $(APPLICATIONS_DIR) && $(MAKE) up

deploy-tasks:
	@cd $(APPLICATIONS_DIR) && docker compose -f docker-compose.tasks.yml up -d

deploy-media:
	@docker rm -f shared-media 2>/dev/null || true
	@docker volume prune -f >/dev/null 2>&1 || true
	@docker compose -f $(SERVICES_DIR)/docker-compose.media.yml up -d

deploy-docs:
	@cd $(APPLICATIONS_DIR) && docker compose -f docker-compose.docs.yml up -d

deploy-proxy:
	@cd $(PROXY_DIR) && $(MAKE) deploy

deploy-databases:
	@$(MAKE) -C $(DATABASES_DIR) deploy-db

# Coolify specific
deploy-common:
	@echo "🚀 Deploying Coolify..."
	@docker network rm coolify 2>/dev/null || true
	@docker compose -f $(SOURCE_DIR)/docker-compose.yml up -d --remove-orphans

restart-common:
	@echo "🔄 Restarting Coolify..."
	@docker compose -f $(SOURCE_DIR)/docker-compose.yml restart coolify

build-common:
	@echo "🔧 Building Coolify images..."
	@docker compose -f $(SOURCE_DIR)/docker-compose.yml build --no-cache
	@echo "✅ Build complete"

list-common:
	@echo "📦 Listing Coolify containers..."
	@docker ps --filter name=coolify --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# -----------------------------------------------------------------
# Management commands
# -----------------------------------------------------------------
status:
	@echo "📊 Deployment Status"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Proxy Status:"
	@cd $(PROXY_DIR) && $(MAKE) status || echo "  (Proxy not available)"
	@echo ""
	@echo "Application Services:"
	@cd $(APPLICATIONS_DIR) && $(MAKE) config || echo "  (Config not available)"
	@docker ps --filter "name=structa-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  (No containers running)"
	@echo ""
	@echo "Media Server:"
	@docker ps --filter "name=shared-media" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "  (Media server not running)"
	@echo ""
	@echo "Databases:"
	@docker ps --filter "name=postgres" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "  (Postgres not running)"
	@docker ps --filter "name=redis" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "  (Redis not running)"

logs:
	@echo "📝 Service Logs"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "Proxy Logs (tail 50):"
	@docker logs default-proxy --tail 50 2>/dev/null || echo "  (Proxy container not found)"
	@echo ""
	@echo "Application Logs:"
	@docker logs ctc-research-website --tail 20 2>/dev/null || echo "  (ctc-research-website not found)"
	@docker logs lms-demo-website --tail 20 2>/dev/null || echo "  (lms-demo-website not found)"
	@docker logs vresume-website --tail 20 2>/dev/null || echo "  (vresume-website not found)"
	@echo ""
	@echo "Media Server Logs:"
	@docker logs shared-media --tail 20 2>/dev/null || echo "  (shared-media not found)"
	@echo ""
	@echo "Coolify Logs (tail 200):"
	@docker logs coolify --tail 200 2>/dev/null || echo "  (Coolify not found)"

logs-common:
	@echo "📝 Coolify logs (tail 200)..."
	@docker logs coolify --tail 200 -f

stop:
	@echo "🛑 Stopping all services..."
	@cd $(PROXY_DIR) && $(MAKE) stop || true
	@cd $(APPLICATIONS_DIR) && $(MAKE) down || true
	@docker compose -f $(SERVICES_DIR)/docker-compose.media.yml down 2>/dev/null || true
	@docker compose -f $(DATABASES_DIR)/docker-compose.yml down 2>/dev/null || true
	@docker compose -f $(SOURCE_DIR)/docker-compose.yml down 2>/dev/null || true
	@echo "✅ All services stopped"

restart:
	@echo "🔄 Restarting all services..."
	@$(MAKE) stop
	@$(MAKE) deploy
	@echo "✅ All services restarted"

# -----------------------------------------------------------------
# Pruning
# -----------------------------------------------------------------
prune: prune-containers prune-volumes prune-images

prune-containers:
	@echo "🗑️  Removing stopped containers..."
	@docker container prune -f
	@echo "✅ Containers pruned"

prune-volumes:
	@echo "🗑️  Removing unused volumes..."
	@docker volume prune -f
	@echo "✅ Volumes pruned"

prune-images:
	@echo "🗑️  Removing unused images..."
	@docker image prune -f
	@echo "✅ Images pruned"

# -----------------------------------------------------------------
# Certificate management (Proxy)
# -----------------------------------------------------------------
cert: cert-generate

cert-generate:
	@cd $(PROXY_DIR)/scripts && ./generate-certs.sh production
	@cd $(PROXY_DIR) && $(MAKE) restart
	@echo "✅ Certificates generated and proxy restarted"

cert-backup:
	@cd $(PROXY_DIR)/scripts && ./manage-certs.sh backup
	@echo "✅ Certificates backed up"

cert-restore:
	@read -p "Enter backup filename to restore: " FILE; \
	if [ -f "$(PROXY_DIR)/scripts/certs/$$FILE" ]; then \
		cd $(PROXY_DIR)/scripts && ./manage-certs.sh restore certs/"$$FILE"; \
	else \
		echo "❌ File not found: certs/$$FILE"; \
		echo "Available backups:"; \
		ls -1 $(PROXY_DIR)/scripts/certs/certs-backup-*.tar.gz 2>/dev/null || echo "  None found"; \
	fi

cert-validate:
	@cd $(PROXY_DIR)/scripts && ./manage-certs.sh validate
	@echo "✅ Certificates validated"

cert-check:
	@cd $(PROXY_DIR)/scripts && ./manage-certs.sh check-expiry
	@echo "✅ Certificate check complete"

# -----------------------------------------------------------------
# Build targets
# -----------------------------------------------------------------
build: build-app build-media build-docs

build-app:
	@cd $(APPLICATIONS_DIR) && docker compose build

build-media:
	@cd $(SERVICES_DIR) && docker compose -f docker-compose.media.yml build

build-docs:
	@cd $(APPLICATIONS_DIR) && docker compose -f docker-compose.docs.yml build

# -----------------------------------------------------------------
# Validation
# -----------------------------------------------------------------
validate:
	@echo "🔍 Validating all configuration files..."
	@cd $(PROXY_DIR) && $(MAKE) validate || echo "  (Proxy validation skipped)"
	@echo "✅ Configuration validation complete"

# -----------------------------------------------------------------
# Extended help (component-specific)
# -----------------------------------------------------------------
help-all:
	@$(MAKE) --no-print-directory help
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "Individual Component Help:"
	@echo "  make -C $(APPLICATIONS_DIR) help    - Application service commands"
	@echo "  make -C $(PROXY_DIR) help           - Proxy management commands"
	@echo "  make -C $(SERVICES_DIR) help        - Service-specific commands"
	@echo "  make -C $(DATABASES_DIR) help       - Database commands"
	@echo "  make -C $(SOURCE_DIR) help          - Coolify source commands"
	@echo "═══════════════════════════════════════════════════════════════"

# -----------------------------------------------------------------
# Compose orchestration (from second Makefile)
# -----------------------------------------------------------------
compose-up:
	@cd $(WORKSPACE_ROOT) && \
	  if [ -f docker-compose.custom.yml ]; then \
	    docker compose -f docker-compose.yml -f docker-compose.custom.yml up -d; \
	  else \
	    docker compose -f docker-compose.yml up -d; \
	  fi

compose-down:
	@cd $(WORKSPACE_ROOT) && \
	  if [ -f docker-compose.custom.yml ]; then \
	    docker compose -f docker-compose.yml -f docker-compose.custom.yml down; \
	  else \
	    docker compose -f docker-compose.yml down; \
	  fi

compose-merged-up:
	@files=$$(find $(WORKSPACE_ROOT) -type f -name 'docker-compose*.yml' ! -path '*/node_modules/*'); \
	if [ -z "$$files" ]; then \
	  echo "No compose files found"; exit 1; \
	fi; \
	set -e; \
	args=""; for f in $$files; do args="$$args -f $$f"; done; \
	project=$(if $(ENV_PREFIX),$(ENV_PREFIX),coolify); \
	docker compose $$args -p $$project up -d

compose-merged-down:
	@files=$$(find $(WORKSPACE_ROOT) -type f -name 'docker-compose*.yml' ! -path '*/node_modules/*'); \
	if [ -z "$$files" ]; then \
	  echo "No compose files found"; exit 1; \
	fi; \
	set -e; \
	args=""; for f in $$files; do args="$$args -f $$f"; done; \
	project=$(if $(ENV_PREFIX),$(ENV_PREFIX),coolify); \
	docker compose $$args -p $$project down

# -----------------------------------------------------------------
# Per‑app shortcuts (forward to individual Makefiles)
# -----------------------------------------------------------------
ctc-research:
	@$(MAKE) -C $(APPLICATIONS_DIR)/ctc-research

structa:
	@$(MAKE) -C $(APPLICATIONS_DIR)/structa

vresume:
	@$(MAKE) -C $(APPLICATIONS_DIR)/vresume

proxy:
	@$(MAKE) -C $(PROXY_DIR)

services:
	@$(MAKE) -C $(SERVICES_DIR)

databases:
	@$(MAKE) -C $(DATABASES_DIR)

# -----------------------------------------------------------------
# Generic forwarder – any unknown target goes to applications/Makefile
# -----------------------------------------------------------------
%:
	@$(MAKE) -C $(APPLICATIONS_DIR) $*