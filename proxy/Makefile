# ============================================================
# Proxy/Reverse Proxy Makefile
# Manages Traefik/Caddy/Nginx proxy configuration
# ============================================================

SHELL := /bin/bash
LIVE_DIR := /data/coolify/proxy
SOURCE_DIR := $(shell pwd)
BACKUP_DIR := $(SOURCE_DIR)/backups
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)

.PHONY: help deploy validate backup restore restart logs clean-deprecated status

help:
	@echo "📋 Proxy/Reverse Proxy Makefile"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Available commands:"
	@echo "  make deploy           - Sync config to live directory and restart proxy"
	@echo "  make validate         - Validate YAML syntax of all config files"
	@echo "  make backup           - Backup current live configuration"
	@echo "  make restore          - Restore latest backup to live directory"
	@echo "  make restart          - Restart Coolify proxy container"
	@echo "  make logs             - Tail proxy logs"
	@echo "  make logs:tail=N      - Show last N lines of logs"
	@echo "  make status           - Show certificate expiry and router status"
	@echo ""
	@echo "Certificate management (see scripts/ for full list):"
	@echo "  make cert:generate    - Generate self-signed certificates"
	@echo "  make cert:backup      - Backup certificates"
	@echo "  make cert:restore     - Restore certificates from backup"
	@echo "  make cert:validate    - Validate certificate/key pairs"
	@echo "  make cert:check       - Check certificate expiry status"
	@echo ""
	@echo "Development:"
	@echo "  make watch-configs    - Watch for config changes and auto-restart"

# ──────────────────────────────────────────────────────────────
# Deployment targets
# ──────────────────────────────────────────────────────────────

deploy: validate backup
	@echo "🚀 Deploying configuration to $(LIVE_DIR)..."
	@rsync -av --delete \
		--exclude='acme' \
		--exclude='certs' \
		--exclude='backups' \
		--exclude='scripts' \
		--exclude='Makefile' \
		--exclude='.gitignore' \
		./ $(LIVE_DIR)/
	@echo "✅ Config synced. Starting/updating proxy..."
	@docker rm -f shared-media 2>/dev/null || true
	@docker compose -f docker-compose.yml up -d --remove-orphans || { echo "❌ Failed to start proxy 0"; exit 1; }
	@docker compose -f docker-compose.custom.yml up -d --remove-orphans || { echo "❌ Failed to start proxy 1"; exit 1; }
	@docker restart coolify-proxy 2>/dev/null || true
	@echo "✅ Deployment complete"
	@sleep 2
	@echo "📊 Checking status..."
	@$(MAKE) status

validate:
	@echo "🔍 Validating YAML syntax..."
	@docker compose -f docker-compose.custom.yml config -q || exit 1
	@echo "✅ All YAML files are valid"

media-nginx:
	@echo "🚀 Deploying Nginx media service..."
	@docker compose -f docker-compose.nginx.yml up -d --remove-orphans

media-traefik:
	@echo "🚀 Deploying Traefik proxy..."
	@docker compose -f docker-compose.traefik.yml up -d --remove-orphans

media-caddy:
	@echo "🚀 Deploying Caddy proxy..."
	@docker compose -f docker-compose.caddy.yml up -d --remove-orphans

media-all:
	@echo "🚀 Deploying all proxy services..."
	@docker compose -f docker-compose.custom.yml up -d --remove-orphans


backup:
	@echo "💾 Backing up current live configuration..."
	@mkdir -p $(BACKUP_DIR)
	@tar -czf $(BACKUP_DIR)/proxy-backup-$(TIMESTAMP).tar.gz \
		--exclude=acme \
		--exclude=certs \
		--exclude=backups \
		-C $(LIVE_DIR) .
	@echo "✅ Backup saved: $(BACKUP_DIR)/proxy-backup-$(TIMESTAMP).tar.gz"

restore:
	@echo "📋 Available backups:"
	@ls -1 $(BACKUP_DIR)/proxy-backup-*.tar.gz 2>/dev/null || echo "  None found"
	@read -p "Enter backup filename to restore: " FILE; \
	if [ -f "$(BACKUP_DIR)/$$FILE" ]; then \
		echo "⚠️  This will overwrite current configuration. Continue? (y/N) "; \
		read CONFIRM; \
		if [ "$$CONFIRM" = "y" ] || [ "$$CONFIRM" = "Y" ]; then \
			sudo tar -xzf $(BACKUP_DIR)/$$FILE -C $(LIVE_DIR); \
			echo "✅ Restored. Restarting proxy..."; \
			docker restart coolify-proxy; \
		else \
			echo "Cancelled."; \
		fi \
	else \
		echo "❌ File not found: $(BACKUP_DIR)/$$FILE"; \
	fi

restart:
	@echo "🔄 Restarting Coolify proxy..."
	@docker restart coolify-proxy
	@sleep 2
	@echo "✅ Proxy restarted"
	@$(MAKE) status

logs:
	@echo "📝 Proxy logs (tail 200)..."
	@docker logs coolify-proxy --tail 200 -f

tail ?= 200
logs-tail:
	@echo "📝 Proxy logs (last $(tail) lines)..."
	@docker logs coolify-proxy --tail $(tail)

# ──────────────────────────────────────────────────────────────
# Status and diagnostics
# ──────────────────────────────────────────────────────────────

status:
	@echo "📊 Proxy Status"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Container Status:"
	@docker ps --filter name=coolify-proxy --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "🔐 Certificate Expiry (from live acme.json):"
	@docker exec coolify-proxy cat /traefik/certs/acme.json 2>/dev/null | \
		jq -r '.letsencrypt.Certificates[] | "\(.domain.main) expires: \(.certificate.notAfter)"' \
		2>/dev/null || echo "  (jq not available or no certificates yet)"
	@echo ""
	@echo "🌐 Routers Loaded:"
	@docker exec coolify-proxy traefik healthcheck --ping 2>/dev/null || \
		echo "  (dashboard access needed for router list)"
	@echo ""
	@echo "🔗 Endpoints:"
	@echo "  - Main sites: https://ctc-research.com, https://structa.cloud, https://vresume.structa.cloud"
	@echo "  - Media: https://media.structa.cloud, https://media.ctc-research.com"
	@echo "  - Traefik Dashboard: https://traefik.structa.cloud (requires basic auth)"

# ──────────────────────────────────────────────────────────────
# Certificate management (aliases to scripts)
# ──────────────────────────────────────────────────────────────

cert: cert-generate
	@$(MAKE) --no-print-directory cert-generate

cert-generate:
	@echo "🔐 Generating certificates..."
	@$(SOURCE_DIR)/scripts/generate-certs.sh production
	@echo "✅ Certificates generated"
	@$(MAKE) restart

cert-backup:
	@echo "💾 Backing up certificates..."
	@$(SOURCE_DIR)/scripts/manage-certs.sh backup
	@echo "✅ Certificates backed up"

cert-restore:
	@read -p "Enter backup filename: " FILE; \
	if [ -f "$(SOURCE_DIR)/scripts/certs/$$FILE" ]; then \
		$(SOURCE_DIR)/scripts/manage-certs.sh restore certs/"$$FILE"; \
	else \
		echo "  File not found: $(SOURCE_DIR)/scripts/certs/$$FILE"; \
	fi

cert-validate:
	@echo "🔍 Validating certificates..."
	@$(SOURCE_DIR)/scripts/manage-certs.sh validate
	@echo "✅ Certificates validated"

cert-check:
	@echo "📅 Checking certificate expiry..."
	@$(SOURCE_DIR)/scripts/manage-certs.sh check-expiry
	@echo "✅ Certificate check complete"

# ──────────────────────────────────────────────────────────────
# Development and testing
# ──────────────────────────────────────────────────────────────

watch-configs:
	@echo "🔍 Watching config files for changes..."
	@echo "⚠️  Use a separate terminal with 'inotifywait' for file watching"
	@echo "   Example: inotifywait -m -e modify --format '%w%f' dynamic/*.yml"

clean-deprecated:
	@echo "🗑️  This will delete deprecated files from old location: $(SOURCE_DIR)"
	@echo "Files to delete:"
	@echo "  - acme.json, acme copy.json, acme_backup_*.json"
	@echo "  - backup-metadata.txt, COMPLETION_REPORT.md, old README.md"
	@echo "  - SSL_CERTIFICATE_MANAGEMENT.md"
	@echo "  - All *copy.yml files, all .sh scripts (except scripts/)"
	@echo "  - docker-compose.*.yml, certs/*"
	@read -p "Continue? (y/N) " CONFIRM; \
	if [ "$$CONFIRM" = "y" ] || [ "$$CONFIRM" = "Y" ]; then \
		rm -f acme.json 'acme copy.json' acme_backup_*.json backup-metadata.txt COMPLETION_REPORT.md README.md SSL_CERTIFICATE_MANAGEMENT.md; \
		rm -f backup-certs.sh cert-backup.sh generate-certs.sh manage-certs.sh restore-certs.sh; \
		rm -f docker-compose.yml docker-compose.*.yml; \
		rm -f dynamic/*copy.yml 'dynamic/* copy.yml'; \
		rm -rf certs/20260602_* certs/*.tar.gz certs/*.crt certs/*.key certs/*.pem certs/*.csr; \
		echo "✅ Deprecated files removed"; \
	else \
		echo "Cancelled."; \
	fi
