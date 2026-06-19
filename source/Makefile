# ============================================================
# Source Deployment Makefile
# Manages Coolify source deployment and upgrades
# ============================================================
# Note: All paths are relative to /data/deploy/source
# ============================================================

SHELL := /bin/bash
SOURCE_DIR := $(shell pwd)
BASE_DIR := $(shell dirname $(SOURCE_DIR))
DATA_DIR ?= /data/coolify
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)

# Compose files with relative paths
BASE_COMPOSE := docker-compose.yml
PROD_COMPOSE := docker-compose.prod.yml
CUSTOM_COMPOSE := docker-compose.custom.yml

.PHONY: help deploy upgrade upgrade:postgres restart stop status

help:
	@echo "📋 Source Deployment Makefile"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Available commands:"
	@echo "  make deploy           - Deploy Coolify from source"
	@echo "  make deploy:prod      - Deploy Coolify in production mode"
	@echo "  make upgrade          - Upgrade Coolify to latest version"
	@echo "  make upgrade:postgres - Upgrade PostgreSQL database"
	@echo "  make restart          - Restart Coolify services"
	@echo "  make stop             - Stop Coolify services"
	@echo "  make start            - Start Coolify services"
	@echo "  make status           - Show Coolify status"
	@echo "  make logs             - Show Coolify logs"
	@echo "  make validate         - Validate compose files"
	@echo ""
	@echo "Maintenance:"
	@echo "  make backup           - Backup Coolify data"
	@echo "  make backup:restore   - Restore from backup"
	@echo ""
	@echo "Environment:"
	@echo "  - DATA_DIR            - Data directory (default: /data/coolify)"
	@echo "  - APP_PORT            - Application port (default: 8000)"

_docker_check:
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker CLI is not installed"; exit 1; }

validate: _docker_check
	@echo "🔍 Validating compose files..."
	@for compose in $(BASE_COMPOSE) $(PROD_COMPOSE) $(CUSTOM_COMPOSE); do \
		echo "  Checking: $$compose"; \
		if [ -f "$$compose" ]; then \
			docker compose -f $$compose config --quiet && \
				echo "  ✅ Valid: $$compose" || \
				echo "  ❌ Invalid: $$compose"; \
		else \
			echo "  ⚠️  Not found: $$compose"; \
		fi; \
	done
	@echo "✅ Validation complete"

deploy: _docker_check
	@echo "🚀 Deploying Coolify from source..."
	@cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) up -d --remove-orphans
	@echo "✅ Coolify deployment started"
	@sleep 5
	@$(MAKE) status

deploy:prod: _docker_check
	@echo "🚀 Deploying Coolify in production mode..."
	@cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) -f $(PROD_COMPOSE) -f $(CUSTOM_COMPOSE) up -d --remove-orphans
	@echo "✅ Coolify production deployment started"
	@sleep 5
	@$(MAKE) status

upgrade: _docker_check
	@echo "🔄 Upgrading Coolify..."
	@$(MAKE) backup
	@echo "Pulling latest images..."
	@cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) -f $(PROD_COMPOSE) -f $(CUSTOM_COMPOSE) pull
	@echo "Recreating containers..."
	@cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) -f $(PROD_COMPOSE) -f $(CUSTOM_COMPOSE) up -d --force-recreate
	@echo "✅ Upgrade complete"
	@sleep 5
	@$(MAKE) status

upgrade:postgres: _docker_check
	@echo "🔄 Upgrading PostgreSQL..."
	@echo "Stopping services..."
	@cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) stop coolify
	@echo "Creating database backup..."
	@mkdir -p $(DATA_DIR)/backups
	@docker exec postgres pg_dump -U ${DB_USERNAME:-coolify} ${DB_DATABASE:-coolify} > $(DATA_DIR)/backups/coolify-db-$(TIMESTAMP).sql 2>/dev/null || \
		docker exec postgres pg_dumpall -U ${DB_USERNAME:-coolify} > $(DATA_DIR)/backups/coolify-all-$(TIMESTAMP).sql
	@echo "Starting database upgrade..."
	@cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) up -d postgres
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 10
	@echo "Starting Coolify..."
	@cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) -f $(PROD_COMPOSE) -f $(CUSTOM_COMPOSE) up -d coolify
	@echo "✅ PostgreSQL upgrade complete"

restart: _docker_check
	@echo "🔄 Restarting Coolify services..."
	@cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) -f $(PROD_COMPOSE) -f $(CUSTOM_COMPOSE) restart
	@echo "✅ Services restarted"
	@sleep 3
	@$(MAKE) status

stop: _docker_check
	@echo "🛑 Stopping Coolify services..."
	@cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) -f $(PROD_COMPOSE) -f $(CUSTOM_COMPOSE) down
	@echo "✅ Services stopped"

start: _docker_check
	@echo "🚀 Starting Coolify services..."
	@cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) -f $(PROD_COMPOSE) -f $(CUSTOM_COMPOSE) up -d
	@echo "✅ Services started"
	@sleep 5
	@$(MAKE) status

status: _docker_check
	@echo "📊 Coolify Status"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Container Status:"
	@docker ps --filter name=coolify --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@docker ps --filter name=coolify-db --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@docker ps --filter name=coolify-redis --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@docker ps --filter name=coolify-realtime --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "Health Check:"
	@docker inspect coolify --format '{{.State.Health.Status}}' 2>/dev/null || \
		(docker exec coolify curl -s http://127.0.0.1:8080/api/health || echo "  (Health endpoint not available)")
	@echo ""
	@echo "Web Interface:"
	@echo "  - http://localhost:8000 (default port)"
	@echo "  - Check .env for APP_PORT configuration"

logs: _docker_check
	@echo "📝 Coolify logs (tail 200)..."
	@docker logs coolify --tail 200 -f

logs:all: _docker_check
	@echo "📝 All Coolify logs (tail 200)..."
	@docker logs coolify --tail 200 -f
	@docker logs postgres --tail 200 -f
	@docker logs redis --tail 200 -f
	@docker logs coolify-realtime --tail 200 -f

backup: _docker_check
	@echo "💾 Backing up Coolify data..."
	@mkdir -p $(DATA_DIR)/backups/$(TIMESTAMP)
	@echo "Backing up SSH keys..."
	@cp -r $(DATA_DIR)/ssh $(DATA_DIR)/backups/$(TIMESTAMP)/ 2>/dev/null || true
	@echo "Backing up applications..."
	@cp -r $(DATA_DIR)/applications $(DATA_DIR)/backups/$(TIMESTAMP)/ 2>/dev/null || true
	@echo "Backing up databases..."
	@cp -r $(DATA_DIR)/databases $(DATA_DIR)/backups/$(TIMESTAMP)/ 2>/dev/null || true
	@echo "Backing up services..."
	@cp -r $(DATA_DIR)/services $(DATA_DIR)/backups/$(TIMESTAMP)/ 2>/dev/null || true
	@echo "Backing up SSL certificates..."
	@cp -r $(DATA_DIR)/ssl $(DATA_DIR)/backups/$(TIMESTAMP)/ 2>/dev/null || true
	@echo "Backing up database data..."
	@docker exec postgres pg_dumpall -U ${DB_USERNAME:-coolify} > $(DATA_DIR)/backups/$(TIMESTAMP)/database.sql 2>/dev/null || true
	@echo "✅ Backup complete: $(DATA_DIR)/backups/$(TIMESTAMP)"

backup:restore:
	@read -p "Enter backup timestamp to restore (e.g., 20260613_225231): " BACKUP; \
	if [ -d "$(DATA_DIR)/backups/$$BACKUP" ]; then \
		echo "⚠️  This will overwrite current data. Continue? (y/N) "; \
		read CONFIRM; \
		if [ "$$CONFIRM" = "y" ] || [ "$$CONFIRM" = "Y" ]; then \
			echo "Stopping services..."; \
			cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) -f $(PROD_COMPOSE) -f $(CUSTOM_COMPOSE) down; \
			echo "Restoring SSH keys..."; \
			cp -r $(DATA_DIR)/backups/$$BACKUP/ssh/* $(DATA_DIR)/ssh/ 2>/dev/null || true; \
			echo "Restoring applications..."; \
			cp -r $(DATA_DIR)/backups/$$BACKUP/applications/* $(DATA_DIR)/applications/ 2>/dev/null || true; \
			echo "Restoring services..."; \
			cp -r $(DATA_DIR)/backups/$$BACKUP/services/* $(DATA_DIR)/services/ 2>/dev/null || true; \
			echo "Restoring database..."; \
			docker exec -i postgres psql -U ${DB_USERNAME:-coolify} -d ${DB_DATABASE:-coolify} < $(DATA_DIR)/backups/$$BACKUP/database.sql 2>/dev/null || true; \
			echo "Starting services..."; \
			cd $(SOURCE_DIR) && docker compose -f $(BASE_COMPOSE) -f $(PROD_COMPOSE) -f $(CUSTOM_COMPOSE) up -d; \
			echo "✅ Restore complete"; \
		else \
			echo "Cancelled."; \
		fi \
	else \
		echo "❌ Backup not found: $(DATA_DIR)/backups/$$BACKUP"; \
		echo "Available backups:"; \
		ls -1 $(DATA_DIR)/backups 2>/dev/null || echo "  None found"; \
	fi
