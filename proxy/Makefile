# ============================================================
# Proxy/Reverse Proxy Makefile
# ============================================================
SHELL := /bin/bash
LIVE_DIR := /data/coolify/proxy
SOURCE_DIR := $(shell pwd)
BACKUP_DIR := $(SOURCE_DIR)/backups
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)

# Networks required by the proxy stack
PROXY_NETWORKS := common traefik-net

.PHONY: help create-networks deploy validate backup restore restart logs logs-tail status
.PHONY: up down build clean clean-deprecated
.PHONY: cert cert-generate cert-backup cert-restore cert-validate cert-check
.PHONY: media-nginx media-traefik media-caddy media-all watch-configs

help:
	@echo "📋 Proxy/Reverse Proxy Makefile"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Available commands:"
	@echo "  make create-networks   - Create required Docker networks"
	@echo "  make deploy            - Validate, backup, sync config, and restart proxy"
	@echo "  make validate          - Validate YAML syntax of all config files"
	@echo "  make backup            - Backup current live configuration"
	@echo "  make restore           - Restore latest backup to live directory"
	@echo "  make restart           - Restart proxy container"
	@echo ""
	@echo "  make up                - Start proxy in detached mode"
	@echo "  make down              - Stop proxy"
	@echo "  make build             - Build/rebuild proxy image"
	@echo "  make clean             - Remove containers, volumes, and images"
	@echo "  make clean-deprecated  - Remove deprecated files from old location"
	@echo ""
	@echo "  make logs              - Tail proxy logs (default 200 lines)"
	@echo "  make logs-tail N=50    - Tail last N lines (e.g., make logs-tail N=50)"
	@echo "  make status            - Show container status, certificate expiry, routers"
	@echo ""
	@echo "  make cert:generate     - Generate self-signed certificates"
	@echo "  make cert:backup       - Backup certificates"
	@echo "  make cert:restore      - Restore certificates from backup"
	@echo "  make cert:validate     - Validate certificate/key pairs"
	@echo "  make cert:check        - Check certificate expiry status"
	@echo ""
	@echo "  make media-nginx       - Deploy Nginx media service"
	@echo "  make media-traefik     - Deploy Traefik proxy (primary)"
	@echo "  make media-caddy       - Deploy Caddy proxy"
	@echo "  make media-all         - Deploy all proxy services via custom compose"
	@echo ""
	@echo "  make watch-configs     - Watch for config changes (manual, requires inotifywait)"

# -----------------------------------------------------------------
# Network creation – idempotent
# -----------------------------------------------------------------
create-networks:
	@echo "🌐 Creating Docker networks for proxy..."
	@for net in $(PROXY_NETWORKS); do \
		if ! docker network inspect $$net >/dev/null 2>&1; then \
			echo "  ✅ Creating network: $$net"; \
			docker network create $$net; \
		else \
			echo "  ⏭️  Network $$net already exists"; \
		fi; \
	done
	@echo "✅ Networks ready"

# -----------------------------------------------------------------
# Deployment targets – create networks first
# -----------------------------------------------------------------
deploy: create-networks validate backup
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
	@docker compose -f docker-compose.yml up -d --remove-orphans || { echo "❌ Failed to start proxy (main)"; exit 1; }
	@docker restart default-proxy 2>/dev/null || true
	@echo "✅ Deployment complete"
	@sleep 2
	@echo "📊 Checking status..."
	@$(MAKE) status

validate:
	@echo "🔍 Validating YAML syntax..."
	@docker compose -f docker-compose.yml config -q || exit 1
	@echo "✅ All YAML files are valid"

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
			docker restart default-proxy; \
		else \
			echo "Cancelled."; \
		fi \
	else \
		echo "❌ File not found: $(BACKUP_DIR)/$$FILE"; \
	fi

restart:
	@echo "🔄 Restarting proxy..."
	@docker restart default-proxy
	@sleep 2
	@echo "✅ Proxy restarted"
	@$(MAKE) status

# -----------------------------------------------------------------
# Service Control (Docker Compose)
# -----------------------------------------------------------------
up: create-networks
	@echo "🟢 Starting proxy (Traefik)..."
	@docker compose -f docker-compose.yml up -d default-proxy
	@echo "✅ Proxy is up"

down:
	@echo "🔴 Stopping proxy..."
	@docker compose -f docker-compose.yml down
	@echo "✅ Proxy stopped"

build:
	@echo "🔨 Building proxy image (using official Traefik)..."
	@docker compose -f docker-compose.yml build --pull

clean:
	@echo "🧹 Removing proxy containers, volumes, and images..."
	@docker compose -f docker-compose.yml down -v --rmi all
	@echo "✅ Clean complete"

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

# -----------------------------------------------------------------
# Logs & Status
# -----------------------------------------------------------------
logs:
	@echo "📝 Proxy logs (tail 200)..."
	@docker logs default-proxy --tail 200 -f

logs-tail:
	@echo "📝 Proxy logs (last $(N) lines)..."
	@docker logs default-proxy --tail $(N)

status:
	@echo "📊 Proxy Status"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Container Status:"
	@docker ps --filter name=default-proxy --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "🔐 Certificate Expiry (from live acme.json):"
	@docker exec default-proxy cat /etc/traefik/acme/acme.json 2>/dev/null | \
		jq -r '.letsencrypt.Certificates[] | "\(.domain.main) expires: \(.certificate.notAfter)"' \
		2>/dev/null || echo "  (jq not available or no certificates yet)"
	@echo ""
	@echo "🌐 Routers Loaded:"
	@docker exec default-proxy traefik healthcheck --ping 2>/dev/null || \
		echo "  (dashboard access needed for router list)"
	@echo ""
	@echo "🔗 Endpoints:"
	@echo "  - Main sites: https://ctc-research.com, https://structa.cloud, https://vresume.structa.cloud"
	@echo "  - Media: https://media.structa.cloud, https://media.ctc-research.com"
	@echo "  - Traefik Dashboard: https://traefik.structa.cloud (requires basic auth)"

# -----------------------------------------------------------------
# Certificate Management (delegates to scripts/)
# -----------------------------------------------------------------
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

# -----------------------------------------------------------------
# Optional Media Servers
# -----------------------------------------------------------------
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
	@docker compose -f docker-compose.yml up -d --remove-orphans

# -----------------------------------------------------------------
# Development – watch for config changes (requires inotifywait)
# -----------------------------------------------------------------
watch-configs:
	@echo "🔍 Watching config files for changes..."
	@echo "⚠️  Use a separate terminal with 'inotifywait' for file watching"
	@echo "   Example: inotifywait -m -e modify --format '%w%f' dynamic/*.yml"