# ============================================================
# Services Makefile
# Manages Ollama, Media, and other service containers
# ============================================================

SHELL := /bin/bash
.PHONY: help

BASE_FILE ?= docker-compose.yml
MEDIA_FILE ?= docker-compose.media.yml
OLLAMA_FILE ?= ollama/docker-compose.yml
OLLAMA_FULL_FILE ?= ollama/docker-compose.full.yml
COMPOSE ?= docker compose

.PHONY: help up down config build media ollama ollama-full prune

help:
	@echo "📋 Services Makefile"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Available commands:"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make config          - Validate Compose configuration"
	@echo "  make build           - Build service images"
	@echo "  make build:media     - Build media server"
	@echo "  make build:ollama    - Build Ollama services"
	@echo "  make media           - Start shared media server"
	@echo "  make ollama          - Start Ollama (minimal)"
	@echo "  make ollama:full     - Start Ollama + Open-WebUI"
	@echo "  make logs            - Show logs from all services"
	@echo "  make prune:containers - Remove stopped containers"
	@echo "  make prune:volumes   - Remove unused volumes"
	@echo ""
	@echo "Media-specific:"
	@echo "  make media:status    - Check media server status"
	@echo "  make media:restart   - Restart media server"

# ──────────────────────────────────────────────────────────────
# Core Docker Compose targets
# ──────────────────────────────────────────────────────────────

_docker_check:
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker CLI is not installed"; exit 1; }

config: _docker_check
	@echo "🔍 Validating Compose configuration..."
	@$(COMPOSE) -f $(BASE_FILE) config > /dev/null && echo "✅ Base config is valid" || echo "❌ Base config error"
	@$(COMPOSE) -f $(BASE_FILE) config
	@$(COMPOSE) -f $(MEDIA_FILE) config > /dev/null && echo "✅ Media config is valid" || echo "❌ Media config error"

build: _docker_check
	@echo "🔨 Building all service images..."
	@$(COMPOSE) -f $(BASE_FILE) build
	@echo "✅ Build complete"

build:media: _docker_check
	@echo "🔨 Building media server..."
	@$(COMPOSE) -f $(MEDIA_FILE) build
	@echo "✅ Media server built"

build:ollama: _docker_check
	@echo "🔨 Building Ollama services..."
	@$(COMPOSE) -f $(OLLAMA_FULL_FILE) build
	@echo "✅ Ollama services built"

up: _docker_check
	@echo "🚀 Starting all services..."
	@$(COMPOSE) -f $(BASE_FILE) up -d
	@echo "✅ Services started"
	@$(COMPOSE) -f $(MEDIA_FILE) up -d
	@echo "✅ Media server started"
	@$(COMPOSE) -f $(OLLAMA_FILE) up -d
	@echo "✅ Ollama started"
	@echo "📊 Status:"
	@$(COMPOSE) -f $(BASE_FILE) ps
	@$(COMPOSE) -f $(MEDIA_FILE) ps

down: _docker_check
	@echo "🛑 Stopping all services..."
	@$(COMPOSE) -f $(OLLAMA_FILE) down
	@$(COMPOSE) -f $(MEDIA_FILE) down
	@$(COMPOSE) -f $(BASE_FILE) down
	@echo "✅ Services stopped"

logs: _docker_check
	@echo "📝 Showing logs (tail 200)..."
	@$(COMPOSE) -f $(BASE_FILE) logs --tail=200 -f
	@$(COMPOSE) -f $(MEDIA_FILE) logs --tail=200 -f
	@$(COMPOSE) -f $(OLLAMA_FILE) logs --tail=200 -f

# ──────────────────────────────────────────────────────────────
# Service-specific targets
# ──────────────────────────────────────────────────────────────

media: _docker_check
	@echo "🚀 Starting shared media server..."
	@$(COMPOSE) -f $(MEDIA_FILE) up -d --build
	@echo "✅ Media server started"

media:restart: _docker_check
	@echo "🔄 Restarting media server..."
	@$(COMPOSE) -f $(MEDIA_FILE) restart
	@echo "✅ Media server restarted"

media:status: _docker_check
	@echo "📊 Media Server Status:"
	@docker ps --filter name=shared-media --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@docker inspect shared-media --format '{{.State.Health.Status}}' 2>/dev/null || echo "  (Health check not configured)"

ollama: _docker_check
	@echo "🚀 Starting Ollama (minimal)..."
	@$(COMPOSE) -f $(OLLAMA_FILE) up -d
	@echo "✅ Ollama started"
	@echo "🌐 Access: http://localhost:11434"

ollama:full: _docker_check
	@echo "🚀 Starting Ollama + Open-WebUI..."
	@$(COMPOSE) -f $(OLLAMA_FULL_FILE) up -d
	@echo "✅ Ollama services started"
	@echo "🌐 Access:"
	@echo "  - Ollama API: http://localhost:11434"
	@echo "  - Open-WebUI: http://localhost:3000"

ollama:restart: _docker_check
	@echo "🔄 Restarting Ollama..."
	@$(COMPOSE) -f $(OLLAMA_FILE) restart
	@echo "✅ Ollama restarted"

# ──────────────────────────────────────────────────────────────
# Pruning
# ──────────────────────────────────────────────────────────────

prune:containers: _docker_check
	@echo "🗑️  Removing stopped containers..."
	@$(COMPOSE) -f $(BASE_FILE) down --remove-orphans
	@$(COMPOSE) -f $(MEDIA_FILE) down --remove-orphans
	@docker container prune -f
	@echo "✅ Containers pruned"

prune:volumes: _docker_check
	@echo "🗑️  Removing unused volumes..."
	@$(COMPOSE) -f $(BASE_FILE) down --volumes --remove-orphans
	@$(COMPOSE) -f $(MEDIA_FILE) down --volumes --remove-orphans
	@docker volume prune -f
	@echo "✅ Volumes pruned"
