SHELL := /bin/bash
COMPOSE_FILE := docker-compose.assets.yml
COMPOSE_NGINX_FILE := docker-compose.nginx.yml
COMPOSE_TOOLS_FILE := docker-compose.yml

# Isolated project names so each proxy can be deployed independently without
# Docker Compose detecting the other as an orphan from the aggregate compose.
PROJECT_MEDIA := structa-media
PROJECT_TOOLS := structa-tools
PROJECT_ALL := structa-toolbelt

.PHONY: help deploy-media up-media down-media logs-media status-media build-media restart-media \
        deploy-tools up-tools down-tools logs-tools status-tools build-tools restart-tools

help: ## Show this help menu
	@echo 'Tools commands:'
	@echo '  deploy-media     - Build + start assets-proxy (static/media server, independent of tools-proxy)'
	@echo '  up-media         - Start assets-proxy only'
	@echo '  down-media       - Stop assets-proxy'
	@echo '  logs-media       - Tail assets-proxy logs'
	@echo '  status-media     - Show assets-proxy container status'
	@echo '  build-media      - Rebuild assets-proxy image'
	@echo '  restart-media    - Restart assets-proxy'
	@echo ''
	@echo '  deploy-tools     - Build + start tools-proxy (tools/docs hosts)'
	@echo '  up-tools         - Start tools-proxy only'
	@echo '  down-tools       - Stop tools-proxy'
	@echo '  logs-tools       - Tail tools-proxy logs'
	@echo '  status-tools     - Show tools-proxy container status'
	@echo '  build-tools      - Rebuild tools-proxy image'
	@echo '  restart-tools    - Restart tools-proxy'
	@echo ''
	@echo '  deploy-all       - Build + start both proxies (full tools stack)'

# ── Assets-proxy (independent static/media server) ────────────────────────────

deploy-media: build-media up-media
	@echo "📦 Assets-proxy deployed — media.* static+bundles serving"

up-media:
	@echo "🟢 Starting assets-proxy..."
	@docker compose -p $(PROJECT_MEDIA) -f $(COMPOSE_FILE) up -d
	@echo "✅ Assets-proxy is up"

down-media:
	@echo "🔴 Stopping assets-proxy..."
	@docker compose -p $(PROJECT_MEDIA) -f $(COMPOSE_FILE) down
	@echo "✅ Assets-proxy stopped"

logs-media:
	@docker compose -p $(PROJECT_MEDIA) -f $(COMPOSE_FILE) logs -f

status-media:
	@docker compose -p $(PROJECT_MEDIA) -f $(COMPOSE_FILE) ps

build-media:
	@echo "🔨 Building assets-proxy image..."
	@docker compose -p $(PROJECT_MEDIA) -f $(COMPOSE_FILE) build --pull

restart-media: down-media up-media
	@echo "🔄 Assets-proxy restarted"

# ── Tools-proxy (tools/docs hosts) ────────────────────────────────────────────

deploy-tools: build-tools up-tools
	@echo "📦 Tools-proxy deployed — tools.structa.cloud + docs.structa.cloud serving"

up-tools:
	@echo "🟢 Starting tools-proxy..."
	@docker compose -p $(PROJECT_TOOLS) -f $(COMPOSE_NGINX_FILE) up -d
	@echo "✅ Tools-proxy is up"

down-tools:
	@echo "🔴 Stopping tools-proxy..."
	@docker compose -p $(PROJECT_TOOLS) -f $(COMPOSE_NGINX_FILE) down
	@echo "✅ Tools-proxy stopped"

logs-tools:
	@docker compose -p $(PROJECT_TOOLS) -f $(COMPOSE_NGINX_FILE) logs -f

status-tools:
	@docker compose -p $(PROJECT_TOOLS) -f $(COMPOSE_NGINX_FILE) ps

build-tools:
	@echo "🔨 Building tools-proxy image..."
	@docker compose -p $(PROJECT_TOOLS) -f $(COMPOSE_NGINX_FILE) build --pull

restart-tools: down-tools up-tools
	@echo "🔄 Tools-proxy restarted"

# ── Full tools stack (both proxies) ───────────────────────────────────────────

deploy-all:
	@echo "🚀 Deploying full tools stack (tools-proxy + assets-proxy)..."
	@docker compose -p $(PROJECT_ALL) -f $(COMPOSE_TOOLS_FILE) up -d --build
	@echo "✅ Tools stack deployed"