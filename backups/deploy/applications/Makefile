# ============================================================
# Application Services Makefile
# Manages Django websites, task workers, and utilities
# ============================================================

SHELL := /bin/bash
.PHONY: help

BASE_FILE ?= docker-compose.yml
COMPOSE ?= docker compose

.PHONY: help up down config build logs prune-containers prune-data media tasks docs

help:
	@echo "📋 Application Services Makefile"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Available commands:"
	@echo "  make up              - Start all application services"
	@echo "  make down            - Stop all application services"
	@echo "  make config          - Validate and display Compose configuration"
	@echo "  make build           - Build all application images"
	@echo "  make build:base      - Build base services only (proxy, db, redis)"
	@echo "  make build:app       - Build application services only"
	@echo "  make logs            - Show logs from all services"
	@echo "  make logs:tail=N     - Show last N lines of logs"
	@echo "  make media           - Start shared media server"
	@echo "  make tasks           - Start task workers and schedulers"
	@echo "  make docs            - Start documentation service"
	@echo "  make prune:containers - Remove stopped containers"
	@echo "  make prune:volumes   - Remove unused volumes"
	@echo ""
	@echo "Site-specific commands:"
	@echo "  make start:ctc       - Start only ctc-research website"
	@echo "  make start:lms       - Start only lms-demo website"
	@echo "  make start:vresume   - Start only vresume website"
	@echo "  make stop:ctc        - Stop only ctc-research website"
	@echo "  make stop:lms        - Stop only lms-demo website"
	@echo "  make stop:vresume    - Stop only vresume website"

# ──────────────────────────────────────────────────────────────
# Core Docker Compose targets
# ──────────────────────────────────────────────────────────────

_docker_check:
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker CLI is not installed"; exit 1; }

config: _docker_check
	@echo "🔍 Validating Compose configuration..."
	@$(COMPOSE) -f $(BASE_FILE) config > /dev/null && echo "✅ Configuration is valid" || echo "❌ Configuration error"
	@$(COMPOSE) -f $(BASE_FILE) config

build: _docker_check
	@echo "🔨 Building all application images..."
	@$(COMPOSE) -f $(BASE_FILE) build --no-cache
	@echo "✅ Build complete"

# Build only the shared/base services (proxy, db, redis, docs, adminer, blinko)
.PHONY: build-base
build-base: _docker_check
	@echo "🔨 Building base services..."
	@$(COMPOSE) -f $(BASE_FILE) build traefik postgres redis docs adminer blinko || echo "  (Some services may not exist)"
	@echo "✅ Base services built"

# Build only application services
.PHONY: build:app
build:app: _docker_check
	@echo "🔨 Building application services..."
	@$(COMPOSE) -f $(BASE_FILE) build ctc-research-website lms-demo-website vresume-website || echo "  (Some services may not exist)"
	@echo "✅ Application services built"

up: _docker_check
	@echo "🚀 Starting application services..."
	@$(COMPOSE) -f $(BASE_FILE) up -d --build --remove-orphans
	@echo "✅ Services started"
	@echo "📊 Status:"
	@$(COMPOSE) -f $(BASE_FILE) ps

down: _docker_check
	@echo "🛑 Stopping application services..."
	@$(COMPOSE) -f $(BASE_FILE) down --remove-orphans
	@echo "✅ Services stopped"

logs: _docker_check
	@echo "📝 Showing logs (tail 200)..."
	@$(COMPOSE) -f $(BASE_FILE) logs --tail=200 -f

logs:tail?=_docker_check
logs:tail:
	@echo "📝 Showing last $(tail) lines of logs..."
	@$(COMPOSE) -f $(BASE_FILE) logs --tail=$(tail) -f

# ──────────────────────────────────────────────────────────────
# Site-specific targets
# ──────────────────────────────────────────────────────────────

start:ctc: _docker_check
	@echo "🚀 Starting ctc-research website..."
	@$(COMPOSE) -f $(BASE_FILE) up -d ctc-research-website
	@echo "✅ ctc-research website started"

start:lms: _docker_check
	@echo "🚀 Starting lms-demo website..."
	@$(COMPOSE) -f $(BASE_FILE) up -d lms-demo-website
	@echo "✅ lms-demo website started"

start:vresume: _docker_check
	@echo "🚀 Starting vresume website..."
	@$(COMPOSE) -f $(BASE_FILE) up -d vresume-website
	@echo "✅ vresume website started"

stop:ctc: _docker_check
	@echo "🛑 Stopping ctc-research website..."
	@$(COMPOSE) -f $(BASE_FILE) stop ctc-research-website
	@echo "✅ ctc-research website stopped"

stop:lms: _docker_check
	@echo "🛑 Stopping lms-demo website..."
	@$(COMPOSE) -f $(BASE_FILE) stop lms-demo-website
	@echo "✅ lms-demo website stopped"

stop:vresume: _docker_check
	@echo "🛑 Stopping vresume website..."
	@$(COMPOSE) -f $(BASE_FILE) stop vresume-website
	@echo "✅ vresume website stopped"

# ──────────────────────────────────────────────────────────────
# Additional services
# ──────────────────────────────────────────────────────────────

media: _docker_check
	@echo "🚀 Starting shared media server..."
	@$(COMPOSE) -f docker-compose.media.yml up -d --build
	@echo "✅ Media server started"

tasks: _docker_check
	@echo "🚀 Starting task workers and schedulers..."
	@$(COMPOSE) -f docker-compose.tasks.yml up -d
	@echo "✅ Task workers started"

docs: _docker_check
	@echo "🚀 Starting documentation service..."
	@$(COMPOSE) -f docker-compose.docs.yml up -d
	@echo "✅ Documentation service started"

# ──────────────────────────────────────────────────────────────
# Pruning
# ──────────────────────────────────────────────────────────────

prune:containers: _docker_check
	@echo "🗑️  Removing stopped containers..."
	@$(COMPOSE) -f $(BASE_FILE) down --remove-orphans && docker container prune -f
	@echo "✅ Containers pruned"

prune:volumes: _docker_check
	@echo "🗑️  Removing unused volumes..."
	@$(COMPOSE) -f $(BASE_FILE) down --volumes --remove-orphans || true
	@echo "✅ Volumes pruned"
