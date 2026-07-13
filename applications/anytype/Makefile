# ============================================================
# Anytype Application Makefile
# ============================================================

SHELL := /bin/bash

# -----------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------
COMPOSE_CMD := docker compose -f docker-compose.yml

# -----------------------------------------------------------------
# PHONY targets – always run
# -----------------------------------------------------------------
.PHONY: help deploy up down status logs rebuild clean

# -----------------------------------------------------------------
# Help – overview
# -----------------------------------------------------------------
help:
	@echo "🚀 Anytype Application"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Available commands:"
	@echo "  make deploy  - Build and start Anytype"
	@echo "  make up      - Start Anytype services"
	@echo "  make down    - Stop Anytype services"
	@echo "  make status  - Show Anytype status"
	@echo "  make logs    - Show Anytype logs (tail 100)"
	@echo "  make rebuild - Rebuild and restart Anytype"
	@echo "  make clean   - Stop and remove containers and volumes"
	@echo ""

# -----------------------------------------------------------------
# Deployment targets
# -----------------------------------------------------------------
deploy: up

up:
	@echo "🚀 Starting Anytype..."
	@$(COMPOSE_CMD) up -d
	@echo "✅ Anytype started"
	@$(MAKE) status

down:
	@echo "🛑 Stopping Anytype..."
	@$(COMPOSE_CMD) down
	@echo "✅ Anytype stopped"

status:
	@echo "📊 Anytype Status"
	@echo "═══════════════════════════════════════════════════════════════"
	@docker ps --filter name=anytype --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  (Anytype container not running)"
	@echo ""
	@echo "Volume:"
	@docker volume inspect anytype_anytype-data --format '{{.Mountpoint}}' 2>/dev/null || echo "  (Volume not found)"

logs:
	@echo "📝 Anytype Logs (tail 100)..."
	@docker logs anytype --tail 100

rebuild:
	@echo "🔨 Rebuilding Anytype..."
	@$(COMPOSE_CMD) build --no-cache
	@$(MAKE) up

clean:
	@echo "🧹 Removing Anytype containers and volumes..."
	@$(COMPOSE_CMD) down -v --remove-orphans
	@echo "✅ Anytype cleaned"
