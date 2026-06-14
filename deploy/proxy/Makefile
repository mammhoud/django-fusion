# Makefile for Traefik proxy management (Coolify integration)
# Usage: make <command>

SHELL := /bin/bash
LIVE_DIR := /data/coolify/proxy
SOURCE_DIR := $(shell pwd)
BACKUP_DIR := $(SOURCE_DIR)/backups
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)

.PHONY: help deploy validate backup restore restart logs clean-deprecated

help:
	@echo "Available commands:"
	@echo "  make deploy           - Sync local config to live directory and restart proxy"
	@echo "  make validate         - Validate YAML syntax of all config files"
	@echo "  make backup           - Backup current live configuration"
	@echo "  make restore          - Restore latest backup to live directory (interactive)"
	@echo "  make restart          - Restart Coolify proxy container"
	@echo "  make logs             - Tail proxy logs"
	@echo "  make clean-deprecated - Remove deprecated files from old location (interactive)"
	@echo "  make status           - Show certificate expiry and router status"

deploy: validate backup
	@echo "🚀 Deploying configuration to $(LIVE_DIR)..."
	@rsync -av --delete --exclude='acme' --exclude='certs' --exclude='backups' ./ $(LIVE_DIR)/
	@echo "✅ Config synced. Restarting proxy..."
	@docker restart coolify-proxy || (echo "❌ Failed to restart proxy" && exit 1)
	@echo "✅ Deployment complete. Check logs with 'make logs'"

validate:
	@echo "🔍 Validating YAML syntax..."
	@for file in $$(find . -name "*.yml" -o -name "*.yaml" | grep -v backups); do \
		echo "  Checking $$file"; \
		python3 -c "import yaml; yaml.safe_load(open('$$file'))" || exit 1; \
	done
	@echo "✅ All YAML files are valid."

backup:
	@echo "💾 Backing up current live configuration..."
	@mkdir -p $(BACKUP_DIR)
	@tar -czf $(BACKUP_DIR)/proxy-backup-$(TIMESTAMP).tar.gz -C $(LIVE_DIR) . --exclude=acme --exclude=certs
	@echo "✅ Backup saved: $(BACKUP_DIR)/proxy-backup-$(TIMESTAMP).tar.gz"

restore:
	@echo "📋 Available backups:"
	@ls -1 $(BACKUP_DIR)/proxy-backup-*.tar.gz 2>/dev/null || echo "No backups found"
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
		echo "❌ File not found."; \
	fi

restart:
	@echo "🔄 Restarting Coolify proxy..."
	@docker restart coolify-proxy
	@echo "✅ Proxy restarted."

logs:
	@docker logs -f coolify-proxy

clean-deprecated:
	@echo "🗑️  This will delete deprecated files from old location: /root/site/websites/compose/traefik"
	@read -p "Continue? (y/N) " CONFIRM; \
	if [ "$$CONFIRM" = "y" ] || [ "$$CONFIRM" = "Y" ]; then \
		cd /root/site/websites/compose/traefik 2>/dev/null && \
		rm -f default_redirect_503.yaml \
		      docker-compose.2026-06-14_01-05-20.7f6c943b.yml \
		      docker-compose.2026-06-13_22-53-21.1dd471e8.yml \
		      acme_backup_20260602_180625.json \
		      backup-metadata.txt \
		      COMPLETION_REPORT.md \
		      README.md \
		      SSL_CERTIFICATE_MANAGEMENT.md \
		      backup-certs.sh \
		      cert-backup.sh \
		      manage-certs.sh \
		      restore-certs.sh \
		      generate-certs.sh \
		      "middlewares copy.yml" \
		      "media-servers copy.yml" \
		      "docs copy.yml" \
		      "ctc-research copy.yml" \
		      "structa-cloud copy.yml" \
		      "vresume copy.yml" \
		      "catchall copy.yml" \
		      "traefik-dashboard copy.yml" \
		      "services copy.yml" \
		      services.yml && \
		echo "✅ Deprecated files removed."; \
	else \
		echo "Cancelled."; \
	fi

status:
	@echo "📊 Proxy status:"
	@docker ps --filter name=coolify-proxy --format "table {{.Names}}\t{{.Status}}"
	@echo ""
	@echo "🔐 Certificate expiry (from live acme.json):"
	@docker exec coolify-proxy cat /traefik/acme/acme.json | jq -r '.letsencrypt.Certificates[] | "\(.domain.main) expires: \(.certificate.notAfter)"' 2>/dev/null || echo "  (jq not available or no certificates yet)"
	@echo ""
	@echo "🌐 Routers loaded:"
	@docker exec coolify-proxy traefik healthcheck --ping || echo "  (dashboard might be needed)"
