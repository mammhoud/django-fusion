SHELL := /bin/bash

# =============================================================================
# Proxy / Traefik Makefile
# =============================================================================
# Targets for starting, stopping, reloading, and inspecting the default-proxy,
# plus helpers for switching between local-development TLS strategies.
# =============================================================================

# Default values for local development.
PROXY_DIR           := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
CERTS_DIR           := $(PROXY_DIR)data/certs
DYNAMIC_DIR         := $(PROXY_DIR)configs/traefik/dynamic
DYNAMIC_CERTS_FILE  := $(DYNAMIC_DIR)/certs.yml
COMPOSE_FILE        := $(PROXY_DIR)docker-compose.traefik.yml
DEFAULT_PROXY_NAME  := default-proxy
HOSTS_FILE          := /etc/hosts
LOCAL_HOSTS         := fusion.localhost cms-fusion.localhost precis-lms.localhost code.localhost coder.localhost space.localhost
LOCAL_CERT_SANS      := DNS:fusion.localhost,DNS:cms-fusion.localhost,DNS:precis-lms.localhost,DNS:code.localhost,DNS:coder.localhost,DNS:space.localhost,DNS:localhost,IP:127.0.0.1,IP:::1

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

.PHONY: proxy-up
proxy-up:
	@echo "Starting Traefik proxy..."
	@cd $(PROXY_DIR) && docker compose -f $(COMPOSE_FILE) up -d
	@$(MAKE) --no-print-directory proxy-status

.PHONY: proxy-down
proxy-down:
	@echo "Stopping Traefik proxy..."
	@cd $(PROXY_DIR) && docker compose -f $(COMPOSE_FILE) down

.PHONY: proxy-restart
proxy-restart:
	@echo "Restarting Traefik proxy..."
	@cd $(PROXY_DIR) && docker compose -f $(COMPOSE_FILE) restart
	@$(MAKE) --no-print-directory proxy-status

.PHONY: proxy-logs
proxy-logs:
	@docker logs -f $(DEFAULT_PROXY_NAME)

.PHONY: proxy-status
proxy-status:
	@echo "=== Traefik container status ==="
	@docker ps --filter name=$(DEFAULT_PROXY_NAME) --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
	@echo ""
	@echo "=== Health check ==="
	@curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8080/ping || true

# ---------------------------------------------------------------------------
# Reload / validation
# ---------------------------------------------------------------------------

.PHONY: proxy-reload
proxy-reload:
	@echo "Reloading Traefik dynamic configuration..."
	@cd $(PROXY_DIR) && docker compose -f $(COMPOSE_FILE) restart
	@$(MAKE) --no-print-directory proxy-status

.PHONY: proxy-validate
proxy-validate:
	@python3 $(PROXY_DIR)scripts/validate-traefik-config.py

# Pre-issuance DNS gate: warns when a HTTP-01 certResolver domain has an
# off-host A/AAAA record (the cause of `acme: error: tls ... internal error`).
.PHONY: proxy-dns-check
proxy-dns-check:
	@python3 $(PROXY_DIR)scripts/check-dns-records.py

# ---------------------------------------------------------------------------
# Dashboard helpers
# ---------------------------------------------------------------------------

.PHONY: proxy-dashboard
proxy-dashboard:
	@echo "Traefik dashboard is exposed on port 8080."
	@echo "Open: http://127.0.0.1:8080/dashboard/"
	@echo "Note: the dashboard must be accessed from localhost or via a trusted host."

# ---------------------------------------------------------------------------
# Certificate strategies
# ---------------------------------------------------------------------------

.PHONY: proxy-certs-selfsigned
proxy-certs-selfsigned:
	@echo "Generating self-signed certificate for: $(LOCAL_HOSTS)"
	@mkdir -p $(CERTS_DIR)
	@openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout $(CERTS_DIR)/localhost-ca.key -out $(CERTS_DIR)/localhost-ca.crt -subj "/O=Structa Cloud/OU=Local Dev/CN=Structa Local CA"
	@openssl req -new -nodes -newkey rsa:2048 -keyout $(CERTS_DIR)/localhost.key -out $(CERTS_DIR)/localhost.csr -subj "/O=Structa Cloud/OU=Local Dev/CN=fusion.localhost"
	@openssl x509 -req -in $(CERTS_DIR)/localhost.csr -CA $(CERTS_DIR)/localhost-ca.crt -CAkey $(CERTS_DIR)/localhost-ca.key -CAcreateserial -out $(CERTS_DIR)/localhost.crt -days 3650 -extfile <(printf "subjectAltName=$(LOCAL_CERT_SANS)\n")
	@rm -f $(CERTS_DIR)/localhost.csr $(CERTS_DIR)/localhost.srl
	@chmod 600 $(CERTS_DIR)/localhost.key $(CERTS_DIR)/localhost-ca.key
	@echo "Self-signed certificate generated in $(CERTS_DIR)"
	@$(MAKE) --no-print-directory proxy-reload

.PHONY: proxy-certs-mkcert
proxy-certs-mkcert:
	@echo "Using mkcert to generate locally-trusted certificates..."
	@command -v mkcert >/dev/null 2>&1 || { echo "mkcert not found. Install it first: https://github.com/FiloSottile/mkcert"; exit 1; }
	@mkdir -p $(CERTS_DIR)
	@mkcert -cert-file $(CERTS_DIR)/localhost.crt -key-file $(CERTS_DIR)/localhost.key $(LOCAL_HOSTS) localhost 127.0.0.1 ::1
	@mkcert -CAROOT > $(CERTS_DIR)/mkcert-root-ca.txt 2>/dev/null || true
	@echo "mkcert certificate generated in $(CERTS_DIR)"
	@$(MAKE) --no-print-directory proxy-reload

.PHONY: proxy-certs-default
proxy-certs-default:
	@echo "Switching to Traefik default certificate..."
	@if [ -f $(DYNAMIC_CERTS_FILE) ]; then mv $(DYNAMIC_CERTS_FILE) $(DYNAMIC_DIR)/certs.yml.selfsigned; fi
	@echo "Static certs file moved to certs.yml.selfsigned. Restarting proxy..."
	@$(MAKE) --no-print-directory proxy-reload

.PHONY: proxy-certs-selfsigned-enable
proxy-certs-selfsigned-enable:
	@echo "Re-enabling self-signed certificate..."
	@if [ -f $(DYNAMIC_DIR)/certs.yml.selfsigned ]; then mv $(DYNAMIC_DIR)/certs.yml.selfsigned $(DYNAMIC_CERTS_FILE); fi
	@$(MAKE) --no-print-directory proxy-reload

.PHONY: proxy-certs-info
proxy-certs-info:
	@echo "=== Certificate files ==="
	@ls -la $(CERTS_DIR)
	@echo ""
	@echo "=== Certificate SANs ==="
	@openssl x509 -in $(CERTS_DIR)/localhost.crt -noout -ext subjectAltName 2>/dev/null || true

# ---------------------------------------------------------------------------
# Local /etc/hosts helpers
# ---------------------------------------------------------------------------

.PHONY: proxy-hosts-check
proxy-hosts-check:
	@echo "Checking $(HOSTS_FILE) entries..."
	@grep -E "$(subst $(space),|,$(LOCAL_HOSTS))" $(HOSTS_FILE) || echo "No local host entries found."

.PHONY: proxy-hosts-add
proxy-hosts-add:
	@for host in $(LOCAL_HOSTS); do if ! grep -q "127.0.0.1\s*$$host" $(HOSTS_FILE); then echo "127.0.0.1  $$host" | sudo tee -a $(HOSTS_FILE); else echo "$$host already present"; fi; done; if ! grep -q "127.0.0.1\s*traefik.structa.cloud" $(HOSTS_FILE); then echo "127.0.0.1  traefik.structa.cloud" | sudo tee -a $(HOSTS_FILE); fi

# ---------------------------------------------------------------------------
# End-to-end verification
# ---------------------------------------------------------------------------

.PHONY: proxy-verify
proxy-verify:
	@echo "=== DNS / hosts ==="
	@getent hosts $(LOCAL_HOSTS) || true
	@echo ""
	@echo "=== HTTP -> HTTPS redirect ==="
	@for host in $(LOCAL_HOSTS); do echo -n "$$host: "; curl -s -o /dev/null -w "%{http_code}\n" -H "Host: $$host" http://127.0.0.1/; done
	@echo ""
	@echo "=== HTTPS response ==="
	@for host in $(LOCAL_HOSTS); do echo -n "$$host: "; curl -s -o /dev/null -w "%{http_code}\n" -H "Host: $$host" -k https://127.0.0.1/; done
	@echo ""
	@echo "=== TLS certificate info ==="
	@for host in $(LOCAL_HOSTS); do echo "--- $$host ---"; echo | openssl s_client -connect 127.0.0.1:443 -servername $$host 2>/dev/null | openssl x509 -noout -subject -dates -ext subjectAltName; done
