# ============================================================
# Workspace Deploy Makefile
# Centralized command delegation for all deployment components
# ============================================================

SHELL := /bin/bash
.PHONY: help

# Include sub-makes for specific components
include deploy/applications/Makefile
include deploy/proxy/Makefile
include deploy/services/Makefile
include deploy/source/Makefile

help:
	@echo "🚀 Structa Cloud Deployment System"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Available commands:"
	@echo "  make deploy:app       - Build and start application services"
	@echo "  make deploy:proxy     - Deploy and restart reverse proxy"
	@echo "  make deploy:media     - Build and start media server"
	@echo "  make deploy:tasks     - Start background task workers"
	@echo "  make deploy:docs      - Start documentation service"
	@echo "  make deploy:all       - Deploy all services"
	@echo ""
	@echo "Management commands:"
	@echo "  make status           - Show deployment status"
	@echo "  make logs             - Show logs from all services"
	@echo "  make stop             - Stop all services"
	@echo "  make restart          - Restart all services"
	@echo ""
	@echo "Maintenance commands:"
	@echo "  make prune:containers - Remove stopped containers"
	@echo "  make prune:volumes    - Remove unused volumes"
	@echo "  make prune:images     - Remove unused images"
	@echo ""
	@echo "Certificate management (Proxy component):"
	@echo "  make cert:generate    - Generate self-signed certificates"
	@echo "  make cert:backup      - Backup current certificates"
	@echo "  make cert:restore     - Restore certificates from backup"
	@echo "  make cert:validate    - Validate certificate/key pairs"
	@echo "  make cert:check       - Check certificate expiry status"
	@echo ""
	@echo "See individual component Makefiles for more details."

# ──────────────────────────────────────────────────────────────
# Deployment targets
# ──────────────────────────────────────────────────────────────

deploy: deploy:all
	@$(MAKE) --no-print-directory deploy:all

deploy:all:
	@echo "🚀 Deploying all services..."
	@$(MAKE) --no-print-directory deploy:proxy
	@$(MAKE) --no-print-directory deploy:app
	@$(MAKE) --no-print-directory deploy:media
	@echo "✅ All services deployed"

deploy:app:
	@cd applications && $(MAKE) up

deploy:tasks:
	@cd applications && $(MAKE) -f docker-compose.tasks.yml up -d

deploy:media:
	@cd services && $(MAKE) -f docker-compose.media.yml up -d

deploy:docs:
	@cd applications && $(MAKE) -f docker-compose.docs.yml up -d

deploy:proxy:
	@cd proxy && $(MAKE) deploy

# ──────────────────────────────────────────────────────────────
# Management targets
# ──────────────────────────────────────────────────────────────

status:
	@echo "📊 Deployment Status"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Proxy Status:"
	@cd proxy && $(MAKE) status || echo "  (Proxy not available)"
	@echo ""
	@echo "Application Services:"
	@cd applications && $(MAKE) config || echo "  (Config not available)"
	@docker ps --filter "name=structa-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  (No containers running)"
	@echo ""
	@echo "Media Server:"
	@docker ps --filter "name=shared-media" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "  (Media server not running)"

logs:
	@echo "📝 Service Logs"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Proxy Logs (tail 50):"
	@docker logs coolify-proxy --tail 50 2>/dev/null || echo "  (Proxy container not found)"
	@echo ""
	@echo "Application Logs:"
	@docker logs ctc-research-website --tail 20 2>/dev/null || echo "  (ctc-research-website not found)"
	@docker logs lms-demo-website --tail 20 2>/dev/null || echo "  (lms-demo-website not found)"
	@docker logs vresume-website --tail 20 2>/dev/null || echo "  (vresume-website not found)"
	@echo ""
	@echo "Media Server Logs:"
	@docker logs shared-media --tail 20 2>/dev/null || echo "  (shared-media not found)"

stop:
	@echo "🛑 Stopping all services..."
	@cd proxy && $(MAKE) stop
	@cd applications && $(MAKE) down
	@echo "✅ All services stopped"

restart:
	@echo "🔄 Restarting all services..."
	@cd applications && $(MAKE) down
	@cd proxy && $(MAKE) restart
	@cd applications && $(MAKE) up
	@echo "✅ All services restarted"

# ──────────────────────────────────────────────────────────────
# Pruning targets
# ──────────────────────────────────────────────────────────────

prune: prune:all
	@$(MAKE) --no-print-directory prune:all

prune:all:
	@$(MAKE) --no-print-directory prune:containers
	@$(MAKE) --no-print-directory prune:volumes
	@$(MAKE) --no-print-directory prune:images

prune:containers:
	@echo "🗑️  Removing stopped containers..."
	@docker container prune -f
	@echo "✅ Containers pruned"

prune:volumes:
	@echo "🗑️  Removing unused volumes..."
	@docker volume prune -f
	@echo "✅ Volumes pruned"

prune:images:
	@echo "🗑️  Removing unused images..."
	@docker image prune -f
	@echo "✅ Images pruned"

# ──────────────────────────────────────────────────────────────
# Certificate management
# ──────────────────────────────────────────────────────────────

cert: cert:generate
	@$(MAKE) --no-print-directory cert:generate

cert:generate:
	@cd proxy/scripts && ./generate-certs.sh production
	@cd proxy && $(MAKE) restart
	@echo "✅ Certificates generated and proxy restarted"

cert:backup:
	@cd proxy/scripts && ./manage-certs.sh backup
	@echo "✅ Certificates backed up"

cert:restore:
	@read -p "Enter backup filename to restore: " FILE; \
	if [ -f "proxy/scripts/certs/$$FILE" ]; then \
		cd proxy/scripts && ./manage-certs.sh restore certs/"$$FILE"; \
	else \
		echo "❌ File not found: certs/$$FILE"; \
		echo "Available backups:"; \
		ls -1 proxy/scripts/certs/certs-backup-*.tar.gz 2>/dev/null || echo "  None found"; \
	fi

cert:validate:
	@cd proxy/scripts && ./manage-certs.sh validate
	@echo "✅ Certificates validated"

cert:check:
	@cd proxy/scripts && ./manage-certs.sh check-expiry
	@echo "✅ Certificate check complete"

# ──────────────────────────────────────────────────────────────
# Build and development
# ──────────────────────────────────────────────────────────────

build: build:all
	@$(MAKE) --no-print-directory build:all

build:all:
	@$(MAKE) --no-print-directory build:app
	@$(MAKE) --no-print-directory build:media
	@$(MAKE) --no-print-directory build:docs

build:app:
	@cd applications && $(MAKE) build

build:media:
	@cd services && $(MAKE) -f docker-compose.media.yml build

build:docs:
	@cd applications && $(MAKE) -f docker-compose.docs.yml build

# ──────────────────────────────────────────────────────────────
# Utility commands
# ──────────────────────────────────────────────────────────────

validate:
	@echo "🔍 Validating all configuration files..."
	@cd proxy && $(MAKE) validate || echo "  (Proxy validation skipped)"
	@echo "✅ Configuration validation complete"

help:all:
	@$(MAKE) --no-print-directory help
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "Individual Component Help:"
	@echo "  make -C applications help    - Application service commands"
	@echo "  make -C proxy help           - Proxy management commands"
	@echo "  make -C services help        - Service-specific commands"
	@echo "  make -C source help          - Source deployment commands"
	@echo "═══════════════════════════════════════════════════════════════"
