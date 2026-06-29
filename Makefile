# ============================================================
# Unified Workspace & Coolify Deployment Makefile
# Centralised command delegation for all deployment components
# ============================================================

SHELL := /bin/bash

# -----------------------------------------------------------------
# Directory layout – adjust these if your structure differs
# -----------------------------------------------------------------
WORKSPACE_ROOT    := .
APPLICATIONS_DIR  := applications
PROXY_DIR         := proxy
SERVICES_DIR      := services
DATABASES_DIR     := databases
SOURCE_DIR        := source

# -----------------------------------------------------------------
# Convenience vars
# -----------------------------------------------------------------
COMPOSE_CMD := docker compose -f docker-compose.yml
# Networks that must exist before any service can come up.
NETWORKS := common traefik-net internal utilities-net warehouse-net ollama-net

# -----------------------------------------------------------------
# Deploy-order selector — CI/release scripts should set this explicitly:
#   make deploy DEPLOY_ORDER=postgres-first   # default, robust
#   make deploy DEPLOY_ORDER=legacy           # back-compat, warns
# Any other value aborts the deploy with a clear error.
#
# `VALID_DEPLOY_ORDERS` is the single source-of-truth list. validate-deploy
# iterates it; deploy-all's chain branch keys off `legacy` only (the rest of
# the list falls through to the postgres-first chain, so adding a new order
# here only requires updating this list + the chain branch if it has its own).
# -----------------------------------------------------------------
# Order names must not contain whitespace or `|`:
#  - Make expansion tokenises on whitespace, so spaces inside a value would
#    split it into multiple words.
#  - Bash `case` uses `|` as the alternative-pattern separator, so `|` inside a
#    value would split it into multiple patterns.
VALID_DEPLOY_ORDERS := postgres-first legacy
DEPLOY_ORDER ?= postgres-first
space :=
empty :=
# Build a `postgres-first|legacy` pattern string for the `case` statement.
DEPLOY_ORDER_PATTERNS := $(subst $(space),|,$(VALID_DEPLOY_ORDERS))

# -----------------------------------------------------------------
# Preflight compose files – smoke-tested by `make deploy-preflight`.
# Add new files here as the stack grows. Missing files are tolerated
# (skipped with a note), but files that exist and fail `docker compose
# config` will fail the preflight and abort the deploy.
# -----------------------------------------------------------------
PREFLIGHT_COMPOSE_FILES := \
	$(DATABASES_DIR)/docker-compose.yml \
	$(PROXY_DIR)/docker-compose.yml \
	compose/docker-compose.applications.yml

# -----------------------------------------------------------------
# Component Makefiles are invoked explicitly via delegation targets below.
# Do not include nested Makefiles here; doing so overrides root targets.

# -----------------------------------------------------------------
# PHONY targets – always run
# -----------------------------------------------------------------
.PHONY: help deploy deploy-all deploy-proxy deploy-app deploy-media deploy-tasks deploy-docs
.PHONY: deploy-databases deploy-coder deploy-utilities deploy-ollama deploy-mailpit
.PHONY: deploy-coolify restart-coolify build-coolify list-coolify
.PHONY: upgrade-coolify upgrade-postgres-coolify start-coolify stop-coolify
.PHONY: backup-coolify backup-restore-coolify validate-coolify run-infra-coolify
.PHONY: deploy-preflight deploy-ci preflight-network check-docker create-networks status logs logs-common stop restart
.PHONY: prune prune-containers prune-volumes prune-images clean
.PHONY: cert cert-generate cert-backup cert-restore cert-validate cert-check
.PHONY: build build-app build-media build-docs
.PHONY: validate verify-release help-all compose-up compose-down compose-merged-up compose-merged-down
.PHONY: ctc-research structa vresume proxy services databases
.PHONY: bump-action-patch bump-action-minor bump-action-major
.PHONY: bump-app-patch bump-app-minor bump-app-major

# -----------------------------------------------------------------
# Help – comprehensive overview
# -----------------------------------------------------------------
help:
	@echo "🚀 Structa Cloud Deployment System"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Available commands:"
	@echo "  make deploy-preflight  - Validate compose files + DEPLOY_ORDER; auto-runs as a prereq of 'make deploy'"
	@echo "                            (also usable standalone for a quick gate without the chain)"
	@echo "  make preflight-network - Lint \$$(NETWORKS) names + probe daemon; auto-runs as a prereq of 'make deploy'"
	@echo "                            (also usable standalone for a quick gate without the chain)"
	@echo "  make deploy-ci         - CI-only gate: runs preflight-network + deploy-preflight, exits. Does NOT deploy."
	@echo "                            Wire as a CI lint step BEFORE 'make deploy' so failures surface as CI failures."
	@echo "  make deploy            - Deploy all components in dependency order (DB → media → apps → proxy)"
	@echo "                            Runs preflight-network + deploy-preflight first as cheap fail-fast gates (no opt-out)."
	@echo "                            Override order:  make deploy DEPLOY_ORDER=postgres-first  (default)"
	@echo "                                              make deploy DEPLOY_ORDER=legacy"
	@echo "  make deploy-app        - Build and start application services"
	@echo "  make deploy-proxy      - Deploy and restart reverse proxy"
	@echo "  make deploy-media      - Build and start media server"
	@echo "  make deploy-tasks      - Start background task workers"
	@echo "  make deploy-docs       - Start documentation service"
	@echo "  make deploy-databases  - Deploy databases (Postgres, Redis)"
	@echo "  make deploy-coder      - Deploy Coder platform (coder.com) on top of Postgres"
	@echo "  make create-networks   - Create all required Docker networks (idempotent)"
	@echo "  make deploy-all        - Deploy all services (alias for deploy)"
	@echo ""
	@echo "Coolify management:"
	@echo "  make deploy-coolify          - Deploy Coolify using its docker compose"
	@echo "  make restart-coolify         - Restart Coolify service"
	@echo "  make build-coolify           - Rebuild Coolify images"
	@echo "  make list-coolify            - List running Coolify containers"
	@echo "  make upgrade-coolify         - Upgrade Coolify to latest"
	@echo "  make upgrade-postgres-coolify - Upgrade Coolify's internal Postgres"
	@echo "  make start-coolify / stop-coolify  - Start / stop the Coolify service"
	@echo "  make backup-coolify / backup-restore-coolify  - Backup / restore Coolify data"
	@echo "  make validate-coolify        - Validate Coolify compose files"
	@echo "  make run-infra-coolify       - Deploy the full Coolify infrastructure"
	@echo ""
	@echo "Compose orchestration:"
	@echo "  make compose-up        - Start combined docker-compose.yml (+ custom if exists)"
	@echo "  make compose-down      - Stop combined stack"
	@echo "  make compose-merged-up - Start all compose files found recursively"
	@echo "  make compose-merged-down - Stop all compose files found recursively"
	@echo ""
	@echo "Management commands:"
	@echo "  make status            - Show deployment status"
	@echo "  make logs              - Show logs from all services"
	@echo "  make stop              - Stop all services"
	@echo "  make restart           - Restart all services"
	@echo ""
	@echo "Maintenance:"
	@echo "  make prune-containers  - Remove stopped containers"
	@echo "  make prune-volumes     - Remove unused volumes"
	@echo "  make prune-images      - Remove unused images"
	@echo "  make clean             - Stop and remove all containers, volumes, and images"
	@echo "  make verify-release    - Sanity-check a published Composite Action tag (default v1.0.0) end-to-end"
	@echo "  make bump-action-{patch|minor|major} - Bump the deploy-preflight Composite Action version (uvx bumpver)"
	@echo "  make bump-app-{patch|minor|major}    - Bump the applications workspace version (uvx bumpver)"
	@echo ""
	@echo "Certificate management (Proxy component):"
	@echo "  make cert-generate     - Generate self-signed certificates"
	@echo "  make cert-backup       - Backup current certificates"
	@echo "  make cert-restore      - Restore certificates"
	@echo "  make cert-validate     - Validate certificate/key pairs"
	@echo "  make cert-check        - Check certificate expiry status"
	@echo ""
	@echo "Per-app shortcuts (delegate to component Makefiles):"
	@echo "  make ctc-research      - Delegate to applications/Makefile with WEBSITE=ctc-research"
	@echo "  make structa           - Delegate to applications/Makefile with WEBSITE=structa"
	@echo "  make vresume           - Delegate to applications/Makefile with WEBSITE=vresume"
	@echo "  make proxy             - Run proxy's Makefile"
	@echo "  make services          - Run services' Makefile"
	@echo "  make databases         - Run databases' Makefile"
	@echo ""
	@echo "Aspirational (require scaffolded component dirs):"
	@echo "  make deploy-utilities  - Deploy monitoring stack (needs services/utilities/)"
	@echo "  make deploy-ollama     - Deploy Ollama + Open WebUI (needs services/ollama/)"
	@echo "  make deploy-mailpit    - Deploy Mailpit (needs services/mailpit/)"
	@echo ""
	@echo "See individual component Makefiles for more details."

# -----------------------------------------------------------------
# Deployment targets
# -----------------------------------------------------------------
deploy: deploy-all

# -----------------------------------------------------------------
# DEPLOY_ORDER selects the chain ordering (default: postgres-first).
# CI/release scripts should set it explicitly:
#   make deploy DEPLOY_ORDER=postgres-first   # database first (robust)
#   make deploy DEPLOY_ORDER=legacy           # back-compat (warns)
#
# Rationale for postgres-first ordering:
#   1. databases          – Postgres must exist first; everything
#                           (Django apps, Coder, Celery workers) hits it.
#   2. coder              – depends_on: postgres: service_healthy.
#   3. media              – shared-media volume server must publish
#                           before Django apps mount it for uploads.
#   4. app + tasks        – Django apps + Celery workers (need DB + media).
#   5. docs               – independent (no DB / no media).
#   6. proxy              – Traefik last so apps + media register their
#                           labels on first boot rather than after.
#
# After the var-selected chain, the aspirational trio (utilities, ollama,
# mailpit) and `deploy-coolify` (separate stack, trailing so its
# `--remove-orphans` only touches Coolify's own project) run regardless.
#
# Preflight gates (auto-invoked prereqs of `deploy-all`):
#   - preflight-network  – lints $(NETWORKS) names + probes daemon via
#                         `check-docker`; aborts before any
#                         `docker network create` if a name is bad.
#   - deploy-preflight   – validates DEPLOY_ORDER + parses the compose
#                         files in PREFLIGHT_COMPOSE_FILES; aborts
#                         before any `docker compose up` if a file is
#                         broken.
# Both pull in `validate-deploy-order` + `create-networks` transitively,
# so the cheap-but-meaningful gates run BEFORE any docker-mutation step.
# (Make deduplicates transitive prereqs; explicit listing of
# `validate-deploy-order create-networks` was therefore intentionally
# removed — they're still visited via the preflight targets.)
# -----------------------------------------------------------------
validate-deploy-order: # internal prereq of deploy-all (not .PHONY — never user-facing)
	@case "$(DEPLOY_ORDER)" in \
		$(DEPLOY_ORDER_PATTERNS)) ;; \
		*) echo "❌ DEPLOY_ORDER must be one of: $(VALID_DEPLOY_ORDERS) (got: '$(DEPLOY_ORDER)')"; exit 1 ;; \
	esac
	@if [ "$(DEPLOY_ORDER)" = "legacy" ]; then \
		echo "  ⚠️  LEGACY order: proxy/app/media come up BEFORE databases."; \
		echo "  ⚠️  Django apps will likely crash on first boot. Prefer DEPLOY_ORDER=postgres-first."; \
	else \
		echo "📋 Deploy order: postgres-first (DB → media → apps → docs → proxy)"; \
	fi

deploy-all: preflight-network deploy-preflight
	@echo "🚀 Deploying all services..."
	@if [ "$(DEPLOY_ORDER)" = "legacy" ]; then \
		$(MAKE) --no-print-directory deploy-proxy; \
		$(MAKE) --no-print-directory deploy-app; \
		$(MAKE) --no-print-directory deploy-media; \
		$(MAKE) --no-print-directory deploy-tasks; \
		$(MAKE) --no-print-directory deploy-docs; \
		$(MAKE) --no-print-directory deploy-databases; \
		$(MAKE) --no-print-directory deploy-coder; \
	else \
		$(MAKE) --no-print-directory deploy-databases; \
		$(MAKE) --no-print-directory deploy-coder; \
		$(MAKE) --no-print-directory deploy-media; \
		$(MAKE) --no-print-directory deploy-app; \
		$(MAKE) --no-print-directory deploy-tasks; \
		$(MAKE) --no-print-directory deploy-docs; \
		$(MAKE) --no-print-directory deploy-proxy; \
	fi
	@$(MAKE) --no-print-directory deploy-utilities
	@$(MAKE) --no-print-directory deploy-ollama
	@$(MAKE) --no-print-directory deploy-mailpit
	@$(MAKE) --no-print-directory deploy-coolify
	@echo "✅ All services deployed"

deploy-app:
	@$(MAKE) -C $(APPLICATIONS_DIR) docker-up

deploy-tasks:
	@docker compose -f compose/docker-compose.tasks.yml up -d

deploy-media:
	@docker rm -f shared-media 2>/dev/null || true
	# NOTE: no host-wide `docker volume prune` here — that would wipe volumes
	# from other projects. If you need to prune, run `make prune-volumes`.
	@docker compose -f $(SERVICES_DIR)/docker-compose.media.yml up -d

deploy-docs:
	@docker compose -f compose/docker-compose.docs.yml up -d

deploy-proxy:
	@cd $(PROXY_DIR) && $(MAKE) deploy

deploy-databases:
	@$(MAKE) -C $(DATABASES_DIR) deploy-db

deploy-coder:
	@echo "🚀 Deploying Coder platform..."
	@$(MAKE) -C $(DATABASES_DIR) deploy-coder
	@echo "✅ Coder platform deployed"

# -----------------------------------------------------------------
# Aspirational deploy targets — component directories not in repo yet.
# Targets are wired so adding services/<X>/Makefile "just works".
# -----------------------------------------------------------------
deploy-utilities:
	@if [ -d "$(SERVICES_DIR)/utilities" ]; then \
		$(MAKE) -C $(SERVICES_DIR)/utilities up; \
	else \
		echo "  (skip) $(SERVICES_DIR)/utilities not present"; \
	fi

deploy-ollama:
	@if [ -d "$(SERVICES_DIR)/ollama" ]; then \
		$(MAKE) -C $(SERVICES_DIR)/ollama up; \
	else \
		echo "  (skip) $(SERVICES_DIR)/ollama not present"; \
	fi

deploy-mailpit:
	@if [ -d "$(SERVICES_DIR)/mailpit" ]; then \
		$(MAKE) -C $(SERVICES_DIR)/mailpit up; \
	else \
		echo "  (skip) $(SERVICES_DIR)/mailpit not present"; \
	fi

# -----------------------------------------------------------------
# Coolify management
# -----------------------------------------------------------------
deploy-coolify:
	@echo "🚀 Deploying Coolify..."
	@if [ -f "$(SOURCE_DIR)/docker-compose.yml" ]; then \
		docker network rm coolify 2>/dev/null || true; \
		docker compose -f $(SOURCE_DIR)/docker-compose.yml up -d --remove-orphans; \
	else \
		echo "  (Coolify compose not available at $(SOURCE_DIR)/docker-compose.yml)"; \
	fi

restart-coolify:
	@echo "🔄 Restarting Coolify..."
	@if [ -f "$(SOURCE_DIR)/docker-compose.yml" ]; then \
		docker compose -f $(SOURCE_DIR)/docker-compose.yml restart coolify; \
	else \
		echo "  (Coolify compose not available at $(SOURCE_DIR)/docker-compose.yml)"; \
	fi

build-coolify:
	@echo "🔧 Building Coolify images..."
	@if [ -f "$(SOURCE_DIR)/docker-compose.yml" ]; then \
		docker compose -f $(SOURCE_DIR)/docker-compose.yml build --no-cache; \
		echo "✅ Build complete"; \
	else \
		echo "  (Coolify compose not available at $(SOURCE_DIR)/docker-compose.yml)"; \
	fi

list-coolify:
	@docker ps --filter name=coolify --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

upgrade-coolify:
	@echo "⬆️  Upgrading Coolify..."
	@if [ -f "$(SOURCE_DIR)/upgrade.sh" ]; then \
		bash $(SOURCE_DIR)/upgrade.sh; \
	else \
		echo "  (No $(SOURCE_DIR)/upgrade.sh — drop in the Coolify upgrade script to enable)"; \
	fi

upgrade-postgres-coolify:
	@echo "🐘 Upgrading Coolify's internal PostgreSQL..."
	@if [ -f "$(SOURCE_DIR)/upgrade-postgres.sh" ]; then \
		bash $(SOURCE_DIR)/upgrade-postgres.sh; \
	else \
		echo "  (No $(SOURCE_DIR)/upgrade-postgres.sh — drop in the Coolify postgres-upgrade script to enable)"; \
	fi

start-coolify:
	@echo "▶️ Starting Coolify..."
	@if [ -f "$(SOURCE_DIR)/docker-compose.yml" ]; then \
		docker compose -f $(SOURCE_DIR)/docker-compose.yml start coolify; \
	else \
		echo "  (Coolify compose not available at $(SOURCE_DIR)/docker-compose.yml)"; \
	fi

stop-coolify:
	@echo "⏹ Stopping Coolify..."
	@if [ -f "$(SOURCE_DIR)/docker-compose.yml" ]; then \
		docker compose -f $(SOURCE_DIR)/docker-compose.yml stop coolify; \
	else \
		echo "  (Coolify compose not available at $(SOURCE_DIR)/docker-compose.yml)"; \
	fi

backup-coolify:
	@echo "💾 Backing up Coolify data..."
	@if [ -f "$(SOURCE_DIR)/docker-compose.yml" ]; then \
		docker compose -f $(SOURCE_DIR)/docker-compose.yml exec -T coolify backup; \
	else \
		echo "  (Coolify compose not available at $(SOURCE_DIR)/docker-compose.yml)"; \
	fi

backup-restore-coolify:
	@echo "↩️  Restoring Coolify data..."
	@if [ -f "$(SOURCE_DIR)/docker-compose.yml" ]; then \
		docker compose -f $(SOURCE_DIR)/docker-compose.yml exec -T coolify restore; \
	else \
		echo "  (Coolify compose not available at $(SOURCE_DIR)/docker-compose.yml)"; \
	fi

validate-coolify:
	@echo "🔍 Validating Coolify compose files..."
	@if [ -f "$(SOURCE_DIR)/docker-compose.yml" ]; then \
		docker compose -f $(SOURCE_DIR)/docker-compose.yml config -q; \
	else \
		echo "  (Coolify compose not available at $(SOURCE_DIR)/docker-compose.yml)"; \
	fi

run-infra-coolify:
	@echo "🏗  Deploying full Coolify infrastructure..."
	@if [ -f "$(SOURCE_DIR)/docker-compose.yml" ]; then \
		docker compose -f $(SOURCE_DIR)/docker-compose.yml up -d --remove-orphans; \
	else \
		echo "  (Coolify compose not available at $(SOURCE_DIR)/docker-compose.yml)"; \
	fi

# -----------------------------------------------------------------
# Docker presence guard – shared by create-networks and
# deploy-preflight so an uninstalled docker fails with one clear
# message instead of a chain of cryptic `docker network` /
# `docker compose` errors.
#
# Scope (deliberately narrow): only `create-networks` and
# `deploy-preflight` depend on this. Other docker-using targets
# (`deploy-coolify`, `prune-containers`, `prune-volumes`,
# `prune-images`, `clean`, `stop`) intentionally don't — add
# `check-docker` as a prereq of those if you want broader coverage.
# -----------------------------------------------------------------
check-docker:
	@command -v docker >/dev/null 2>&1 || { \
		echo "❌ docker binary not found in PATH — install Docker before running 'make deploy'."; \
		exit 1; \
	}
	# Pure-bash 5s daemon-liveness probe — avoids depending on GNU `timeout`,
	# which is missing from stock macOS (it's `gtimeout` only after `brew
	# install coreutils`). Background the call, sleep 5s, kill if still alive.
	@docker info >/dev/null 2>&1 & \
	pid=$$! ; \
	sleep 5 ; \
	if kill -0 $$pid 2>/dev/null; then \
		kill $$pid 2>/dev/null ; \
		wait $$pid 2>/dev/null ; \
		timed=1 ; \
	else \
		wait $$pid ; \
		timed=$$? ; \
	fi ; \
	if [ $$timed -ne 0 ]; then \
		echo "❌ docker is installed but the daemon isn't responding (or user can't reach it)."; \
		exit 1 ; \
	fi

# -----------------------------------------------------------------
# Network creation – idempotent; runs before deploy-all
# -----------------------------------------------------------------
create-networks: check-docker
	@echo "🌐 Creating Docker networks..."
	@for net in $(NETWORKS); do \
		if ! docker network inspect $$net >/dev/null 2>&1; then \
			echo "  ✅ Creating network: $$net"; \
			docker network create $$net; \
		else \
			echo "  ⏭️  Network $$net already exists"; \
		fi; \
	done
	@echo "✅ All networks are ready"

# -----------------------------------------------------------------
# preflight-network — cheap name-only probe of $(NETWORKS) BEFORE
# create-networks. Catches:
#   1. Names that exceed Docker's 64-char limit.
#   2. Names that don't match Docker's
#      ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$  regex
#      (the official network-name identifier; rejects spaces,
#      `:` / `@` typos, and names starting with `-` / `_` / `.`).
#   3. Names that look fine but aren't referenced by any compose
#      file in $(PREFLIGHT_COMPOSE_FILES) — informational warning
#      (NOT a failure) so the user can prune dead networks.
#
# Doesn't depend on `docker network create --dry-run` because that
# flag isn't supported by Docker 29.x; instead the recipe probes
# via `docker network ls` to mark "already exists" vs "to create".
# Doesn't actually create any network — create-networks still owns
# the apply step.
#
# Daemon probe vs. name lookup:
#   `ls_names` captures the live network list; `ls_rc` separates
#   "daemon probe failed" from "name simply doesn't exist yet", so
#   the per-name diagnostic isn't misleading when the socket is
#   unreachable.
#
# Future opt-in:
#   A `PREFLIGHT_NETWORK_STRICT=1` env flag could promote the
#   dead-network advisory to a hard fail (useful for guarding
#   stale `$(NETWORKS)` entries after a rename). Left out here
#   to keep this target advisory-only.
# -----------------------------------------------------------------
preflight-network: check-docker
	@echo "🔍 Preflight: validating $(words $(NETWORKS)) network name(s)..."
	@re='^[a-zA-Z0-9][a-zA-Z0-9_.-]*$$' ; \
	max=64 ; \
	ls_names=$$(docker network ls --format '{{.Name}}' 2>/dev/null) ; \
	ls_rc=$$? ; \
	if [ $$ls_rc -ne 0 ]; then \
		echo "  ⚠️  Docker network ls returned non-zero (rc=$$ls_rc); daemon probe failed." ; \
		echo "  ⚠️  Cannot verify which names already exist — labels below will read \"probe failed\"." ; \
	fi ; \
	fail=0 ; \
	for net in $(NETWORKS); do \
		len=$$(printf '%s' "$$net" | wc -c) ; \
		if [ $$len -gt $$max ]; then \
			echo "  ❌ $$net (length $$len > $$max — Docker network names max 64 chars)"; \
			fail=1 ; \
			continue ; \
		fi ; \
		if [[ "$$net" =~ $$re ]]; then \
			: ; \
		else \
			echo "  ❌ $$net (chars don't match Docker's network-name identifier set)"; \
			fail=1 ; \
			continue ; \
		fi ; \
		if [ $$ls_rc -ne 0 ]; then \
			exist_icon="⚠️" ; exist_label="probe failed (see rc above)" ; \
		elif printf '%s\n' "$$ls_names" | grep -Fxq -- "$$net"; then \
			exist_icon="✅" ; exist_label="exists on daemon" ; \
		else \
			exist_icon="➕" ; exist_label="will be created by create-networks" ; \
		fi ; \
		ref_count=0 ; \
		for cf in $(PREFLIGHT_COMPOSE_FILES); do \
			if [ -f "$$cf" ] && grep -Fq -- "$$net" "$$cf"; then \
				ref_count=$$((ref_count + 1)) ; \
			fi ; \
		done ; \
		if [ $$ref_count -eq 0 ]; then \
			echo "  ⚠️  $$net ($$exist_icon $$exist_label, NOT referenced by any known compose file)"; \
		else \
			echo "  ✅ $$net ($$exist_icon $$exist_label, referenced by $$ref_count compose file(s))"; \
		fi ; \
	done ; \
	if [ $$fail -ne 0 ]; then \
		echo "❌ preflight-network failed — fix the invalid names above." ; \
		exit 1 ; \
	fi ; \
	echo "✅ preflight-network OK — all network names are syntactically valid."

# -----------------------------------------------------------------
# Preflight — runs the cheap-but-meaningful checks BEFORE the full
# deploy chain so CI / dev scripts fail fast on misconfiguration.
#
# Sequence:
#   1. validate-deploy-order  (DEPLOY_ORDER value is one of the accepted
#                              list; no network creation runs yet)
#   2. create-networks        (idempotent; safe if networks already exist)
#   3. docker compose config  (parse + render every known compose file
#                              in $(PREFLIGHT_COMPOSE_FILES); tolerates
#                              missing files but fails on parse errors)
# -----------------------------------------------------------------
deploy-preflight: validate-deploy-order create-networks
	@echo "🔍 Preflight: smoke-testing compose files..."
	@fail=0; \
	for f in $(PREFLIGHT_COMPOSE_FILES); do \
		if [ ! -f $$f ]; then \
			echo "  ⏭️  $$f (missing — skipping)"; \
			continue; \
		fi; \
		if docker compose -f $$f config -q 2>/dev/null; then \
			echo "  ✅ $$f"; \
		else \
			echo "  ❌ $$f"; \
			fail=1; \
		fi; \
	done; \
	if [ $$fail -ne 0 ]; then \
		echo "❌ Preflight failed; fix the compose errors above before running 'make deploy'."; \
		exit 1; \
	fi
	@echo "✅ Preflight OK — safe to run 'make deploy'"

# -----------------------------------------------------------------
# deploy-ci — CI preflight ONLY; does not deploy.
#
# Wire this into a CI lint job (the GitHub Actions template at
# .github/workflows/deploy-ci.yml does exactly that) that runs
# BEFORE any job that invokes `make deploy`. The result: misconfig
# failures show up as a failed lint step instead of aborting mid-
# deploy, which is far cheaper to debug.
#
# Runs preflight-network + deploy-preflight as prereqs (Make
# dedupes; `validate-deploy-order` and `create-networks` still fire
# transitively through `deploy-preflight`).
# -----------------------------------------------------------------
deploy-ci: preflight-network deploy-preflight
	@echo "🛡️  CI preflight gate — no deploy will happen."

# -----------------------------------------------------------------
# Management commands
# -----------------------------------------------------------------
status:
	@echo "📊 Deployment Status"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Proxy Status:"
	@cd $(PROXY_DIR) && $(MAKE) status || echo "  (Proxy not available)"
	@echo ""
	@echo "Application Services:"
	@$(MAKE) -C $(APPLICATIONS_DIR) show-config || echo "  (Config not available)"
	@docker ps --filter "name=structa-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  (No containers running)"
	@echo ""
	@echo "Media Server:"
	@docker ps --filter "name=shared-media" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "  (Media server not running)"
	@echo ""
	@echo "Databases:"
	@docker ps --filter "name=postgres" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "  (Postgres not running)"
	@docker ps --filter "name=redis" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "  (Redis not running)"

logs:
	@echo "📝 Service Logs"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "Proxy Logs (tail 50):"
	@docker logs default-proxy --tail 50 2>/dev/null || echo "  (Proxy container not found)"
	@echo ""
	@echo "Application Logs:"
	@docker logs ctc-research-website --tail 20 2>/dev/null || echo "  (ctc-research-website not found)"
	@docker logs lms-demo-website --tail 20 2>/dev/null || echo "  (lms-demo-website not found)"
	@docker logs vresume-website --tail 20 2>/dev/null || echo "  (vresume-website not found)"
	@echo ""
	@echo "Media Server Logs:"
	@docker logs shared-media --tail 20 2>/dev/null || echo "  (shared-media not found)"
	@echo ""
	@echo "Coder Logs (tail 50):"
	@docker logs coder --tail 50 2>/dev/null || echo "  (Coder container not found)"
	@echo ""
	@echo "Coolify Logs (tail 200):"
	@docker logs coolify --tail 200 2>/dev/null || echo "  (Coolify not found)"

logs-common:
	@echo "📝 Coolify logs (tail 200)..."
	@docker logs coolify --tail 200 -f

stop:
	@echo "🛑 Stopping all services..."
	@cd $(PROXY_DIR) && $(MAKE) stop || true
	@$(MAKE) -C $(APPLICATIONS_DIR) docker-down || true
	@docker compose -f $(SERVICES_DIR)/docker-compose.media.yml down 2>/dev/null || true
	@docker compose -f $(DATABASES_DIR)/docker-compose.yml down 2>/dev/null || true
	@docker compose -f $(SOURCE_DIR)/docker-compose.yml down 2>/dev/null || true
	@echo "✅ All services stopped"

restart:
	@echo "🔄 Restarting all services..."
	@$(MAKE) stop
	@$(MAKE) deploy
	@echo "✅ All services restarted"

# -----------------------------------------------------------------
# Pruning & cleanup
# -----------------------------------------------------------------
prune: prune-containers prune-volumes prune-images

prune-containers:
	@echo "🗑️  Removing stopped containers..."
	@docker container prune -f
	@echo "✅ Containers pruned"

prune-volumes:
	@echo "🗑️  Removing unused volumes..."
	@docker volume prune -f
	@echo "✅ Volumes pruned"

prune-images:
	@echo "🗑️  Removing unused images..."
	@docker image prune -f
	@echo "✅ Images pruned"

# Aggressive teardown — strips the project containers, volumes, and images.
# Scoped to this compose project so it won't nuke other tenants on the host.
clean:
	@echo "🧹 Removing all containers, volumes, and images for this project..."
	@if [ -f docker-compose.yml ]; then \
		$(COMPOSE_CMD) down -v --rmi all --remove-orphans; \
	else \
		echo "  (no docker-compose.yml at root; refusing to do an unscoped system prune)"; \
		echo "  Run \`make prune-containers prune-volumes prune-images\` for a scoped prune."; \
		exit 1; \
	fi
	@echo "✅ Clean complete"

# -----------------------------------------------------------------
# Certificate management (Proxy)
# -----------------------------------------------------------------
cert: cert-generate

cert-generate:
	@cd $(PROXY_DIR)/scripts && ./generate-certs.sh production
	@cd $(PROXY_DIR) && $(MAKE) restart
	@echo "✅ Certificates generated and proxy restarted"

cert-backup:
	@cd $(PROXY_DIR)/scripts && ./manage-certs.sh backup
	@echo "✅ Certificates backed up"

cert-restore:
	@read -p "Enter backup filename to restore: " FILE; \
	if [ -f "$(PROXY_DIR)/scripts/certs/$$FILE" ]; then \
		cd $(PROXY_DIR)/scripts && ./manage-certs.sh restore certs/"$$FILE"; \
	else \
		echo "❌ File not found: certs/$$FILE"; \
		echo "Available backups:"; \
		ls -1 $(PROXY_DIR)/scripts/certs/certs-backup-*.tar.gz 2>/dev/null || echo "  None found"; \
	fi

cert-validate:
	@cd $(PROXY_DIR)/scripts && ./manage-certs.sh validate
	@echo "✅ Certificates validated"

cert-check:
	@cd $(PROXY_DIR)/scripts && ./manage-certs.sh check-expiry
	@echo "✅ Certificate check complete"

# -----------------------------------------------------------------
# Build targets
# -----------------------------------------------------------------
build: build-app build-media build-docs

build-app:
	@$(MAKE) -C $(APPLICATIONS_DIR) docker-build

build-media:
	@cd $(SERVICES_DIR) && docker compose -f docker-compose.media.yml build

build-docs:
	@docker compose -f compose/docker-compose.docs.yml build

# -----------------------------------------------------------------
# Validation
# -----------------------------------------------------------------
validate:
	@echo "🔍 Validating all configuration files..."
	@cd $(PROXY_DIR) && $(MAKE) validate || echo "  (Proxy validation skipped)"
	@echo "✅ Configuration validation complete"

# -----------------------------------------------------------------
# verify-release — end-to-end sanity check that the published
# Composite Action tag (default v1.0.0) is correctly published AND
# the underlying Makefile chain still works locally.
#
# Three gates, run sequentially:
#   1. `git ls-remote origin refs/tags/$TAG` — confirms the tag is
#      on the remote (network roundtrip required).
#   2. Inspect `action.yml` at the remote SHA — confirms both the
#      `make-target` AND `working-directory` inputs are present in
#      the published file (catches a "tag published but stale" bug).
#   3. `make deploy-ci` — runs the SAME preflight chain that the
#      published Composite Action runs inside `uses:` steps. If
#      this fails, the published action would also fail for any
#      consumer whose Makefile uses `deploy-ci` as the gate.
#
# Override the tag with `make verify-release TAG=v1.1.0-rc1`.
# -----------------------------------------------------------------
verify-release:
	@echo "🔍 Verifying release at tag $(or $(TAG),v1.0.0) on origin..."
	@remote_sha=$$(git ls-remote origin refs/tags/$(or $(TAG),v1.0.0) | awk '{print $$1}') ; \
	if [ -z "$$remote_sha" ]; then \
		echo "  ❌ Remote tag '$(or $(TAG),v1.0.0)' not found on origin" ; \
		exit 1 ; \
	fi ; \
	echo "  ✅ Remote tag exists, SHA=$$remote_sha" ; \
	action=$$(git show $$remote_sha:.github/actions/deploy-preflight/action.yml) ; \
	if echo "$$action" | grep -q '^  make-target:'; then \
		echo "  ✅ action.yml at $$remote_sha has 'make-target' input" ; \
	else \
		echo "  ❌ action.yml missing 'make-target' input - published tag is broken" ; \
		exit 1 ; \
	fi ; \
	if echo "$$action" | grep -q '^  working-directory:'; then \
		echo "  ✅ action.yml at $$remote_sha has 'working-directory' input" ; \
	else \
		echo "  ❌ action.yml missing 'working-directory' input - published tag is broken" ; \
		exit 1 ; \
	fi ; \
	echo "  🧪 Now running local smoke: make deploy-ci (the action's actual recipe)" ; \
	$(MAKE) deploy-ci || { echo "❌ deploy-ci failed - the published action would also fail for consumers"; exit 1; }
	@echo "✅ verify-release OK on tag $(or $(TAG),v1.0.0)"

# -----------------------------------------------------------------
# Versioning Shortcuts (require uv / uvx; bumpver config lives in
# .github/actions/deploy-preflight/bumpver.toml for the action and
# in applications/pyproject.toml [tool.bumpver] for the workspace).
#
# Pattern rules (`bump-action-%` / `bump-app-%`) match the trailing
# {patch|minor|major} and forward it via `$(*)` to bumpver's
# `--patch|--minor|--major` flag. bumpver reads the local bumpver.toml,
# updates the VERSION source-of-truth, commits, tags, and pushes.
# -----------------------------------------------------------------
.PHONY: bump-action-patch bump-action-minor bump-action-major
bump-action-%:
	@cd .github/actions/deploy-preflight && \
	if command -v uvx >/dev/null 2>&1; then \
		uvx bumpver update --$(*); \
	elif command -v uv >/dev/null 2>&1; then \
		uv run --with bumpver bumpver update --$(*); \
	else \
		echo "❌ install uv (https://docs.astral.sh/uv/) or bumpver manually"; exit 1; \
	fi

.PHONY: bump-app-patch bump-app-minor bump-app-major
bump-app-%:
	@cd $(APPLICATIONS_DIR) && \
	if command -v uvx >/dev/null 2>&1; then \
		uvx bumpver update --$(*); \
	elif command -v uv >/dev/null 2>&1; then \
		uv run --with bumpver bumpver update --$(*); \
	else \
		echo "❌ install uv (https://docs.astral.sh/uv/) or bumpver manually"; exit 1; \
	fi

# -----------------------------------------------------------------
# Extended help (component-specific)
# -----------------------------------------------------------------
help-all:
	@$(MAKE) --no-print-directory help
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "Individual Component Help:"
	@echo "  make -C $(APPLICATIONS_DIR) help    - Application service commands"
	@echo "  make -C $(PROXY_DIR) help           - Proxy management commands"
	@echo "  make -C $(SERVICES_DIR) help        - Service-specific commands"
	@echo "  make -C $(DATABASES_DIR) help       - Database commands"
	@echo "  make -C $(SOURCE_DIR) help          - Coolify source commands"
	@echo "═══════════════════════════════════════════════════════════════"

# -----------------------------------------------------------------
# Compose orchestration
# -----------------------------------------------------------------
compose-up:
	@cd $(WORKSPACE_ROOT) && \
	  if [ -f docker-compose.custom.yml ]; then \
	    docker compose -f docker-compose.yml -f docker-compose.custom.yml up -d; \
	  else \
	    docker compose -f docker-compose.yml up -d; \
	  fi

compose-down:
	@cd $(WORKSPACE_ROOT) && \
	  if [ -f docker-compose.custom.yml ]; then \
	    docker compose -f docker-compose.yml -f docker-compose.custom.yml down; \
	  else \
	    docker compose -f docker-compose.yml down; \
	  fi

compose-merged-up:
	@files=$$(find $(WORKSPACE_ROOT) -type f -name 'docker-compose*.yml' ! -path '*/node_modules/*'); \
	if [ -z "$$files" ]; then \
	  echo "No compose files found"; exit 1; \
	fi; \
	set -e; \
	args=""; for f in $$files; do args="$$args -f $$f"; done; \
	project=$(if $(ENV_PREFIX),$(ENV_PREFIX),coolify); \
	docker compose $$args -p $$project up -d

compose-merged-down:
	@files=$$(find $(WORKSPACE_ROOT) -type f -name 'docker-compose*.yml' ! -path '*/node_modules/*'); \
	if [ -z "$$files" ]; then \
	  echo "No compose files found"; exit 1; \
	fi; \
	set -e; \
	args=""; for f in $$files; do args="$$args -f $$f"; done; \
	project=$(if $(ENV_PREFIX),$(ENV_PREFIX),coolify); \
	docker compose $$args -p $$project down

# -----------------------------------------------------------------
# Per-app shortcuts (forward to individual component Makefiles)
# -----------------------------------------------------------------
ctc-research:
	@$(MAKE) -C $(APPLICATIONS_DIR) WEBSITE=ctc-research

structa:
	@$(MAKE) -C $(APPLICATIONS_DIR) WEBSITE=structa

vresume:
	@$(MAKE) -C $(APPLICATIONS_DIR) WEBSITE=vresume

proxy:
	@$(MAKE) -C $(PROXY_DIR)

services:
	@$(MAKE) -C $(SERVICES_DIR)

databases:
	@$(MAKE) -C $(DATABASES_DIR)

# -----------------------------------------------------------------
# Generic forwarder – any unknown target routes to applications/Makefile
# (so `make check`, `make test-local`, `make runserver-local`, etc. work)
# -----------------------------------------------------------------
%:
	@$(MAKE) -C $(APPLICATIONS_DIR) $*
