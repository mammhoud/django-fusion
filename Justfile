# ============================================================
# Structa Cloud — Justfile (user-facing command layer)
# ============================================================
# `just` is the friendly front-end for the monorepo. Complex deploy
# and backend commands delegate to the canonical Makefile dispatchers
# and the Nx workspace (single source of truth — no duplicated logic).
#
#   just install          # full workspace install (Python + JS + POS)
#   just check            # run all workspace checks
#   just deploy           # full stack deploy (postgres-first)
#   just nx <target>      # delegate to nx (e.g. just nx run docs:build)
#
# Run `just --list` for the full command catalog.

set shell := ["bash", "-uc"]

# Directory layout — mirrors Makefile
WORKSPACE_ROOT := "."
PROXY_DIR := "application/proxy"
SERVICES_DIR := "application/tools"
DATABASES_DIR := "application/databases"
FORMINTS_DIR := "projects/formints"
PRECIS_DIR := "projects/precis"

# ---------------------------------------------------------------
# Meta
# ---------------------------------------------------------------

# List every recipe with its doc comment
default:
    @just --list

# Show the underlying Makefile help (deploy/cert/infra detail)
help:
    @make help

# ---------------------------------------------------------------
# Install
# ---------------------------------------------------------------

# Full workspace install: uv sync + frontends + formints + docs
install:
    @echo "🧪 Syncing Python workspace deps..."
    @uv sync
    @echo "📦 Installing JS frontends..."
    @npm run install:projects
    @echo "📦 Installing Formints editions..."
    @cd {{FORMINTS_DIR}} && make install-all
    @echo "📦 Installing docs (Docus)..."
    @cd docs && npm install --no-audit --no-fund
    @echo "✅ Install complete"

# Install only the Python workspace deps (uv sync)
install-python:
    @uv sync

# Install only the JS frontends (npm run install:projects)
install-js:
    @npm run install:projects

# Install only the Formints editions (all editions + SDK)
install-formints install-formints-all:
    @cd {{FORMINTS_DIR}} && make install-all

# Install docs (Docus) dependencies
install-docs:
    @cd docs && npm install --no-audit --no-fund

# ---------------------------------------------------------------
# Check / test / build
# ---------------------------------------------------------------

# Run every workspace check (nx run-many check + Python checks)
check:
    @echo "🧪 Running workspace checks..."
    @npm run check

# Run every workspace test (nx run-many test + Python suites)
test:
    @echo "🧪 Running workspace tests..."
    @npm run test

# Check the docs project (Docus config + locale sources)
check-docs:
    @nx run docs:check

# Build the docs project (Docus Nuxt server, container builds internally)
build-docs:
    @nx run docs:build

# ---------------------------------------------------------------
# Nx delegation
# ---------------------------------------------------------------

# Delegate any target to nx: just nx <args...> (e.g. just nx run docs:build)
nx *args:
    @node_modules/.bin/nx {{args}}

# Nx graph visualization
nx-graph:
    @node_modules/.bin/nx graph

# ---------------------------------------------------------------
# Deploy (complex commands — delegate to root Makefile)
# ---------------------------------------------------------------

# Full stack deploy (postgres-first order)
deploy:
    @make deploy

# Deploy only the reverse proxy (Traefik)
deploy-proxy:
    @make deploy-proxy

# Deploy the docs service (Docus) — uses nx check + docker compose
deploy-docs:
    @nx run docs:deploy

# Deploy all self-hosted tools (affine, adminer, mailpit, monitoring, ollama)
deploy-tools:
    @make deploy-tools

# Deploy the shared-proxy Nginx (tools + docs + media front door)
deploy-media:
    @make deploy-media

# Deploy databases (PostgreSQL + Redis)
deploy-databases:
    @make deploy-databases

# Deploy the Coder platform
deploy-coder:
    @make deploy-coder

# Deploy application containers (precis-main, ctc)
deploy-app:
    @make deploy-app

# Deploy a single tool by name: just deploy-tool <name>
deploy-tool name:
    @make -C {{SERVICES_DIR}}/{{name}} up

# ---------------------------------------------------------------
# Backend commands (product-scoped, delegate to project Makefiles)
# ---------------------------------------------------------------

# Precis (unified) backend check
backend-check-precis:
    @cd {{PRECIS_DIR}}/precis-main/backend && make check

# Precis (unified) backend test
backend-test-precis:
    @cd {{PRECIS_DIR}}/precis-main/backend && make test

# Precis (unified) backend migrate
backend-migrate-precis:
    @cd {{PRECIS_DIR}}/precis-main/backend && make migrate

# Formints: check all editions
check-formints:
    @cd {{FORMINTS_DIR}} && make check-all

# Formints: test all editions
test-formints:
    @cd {{FORMINTS_DIR}} && make test-all

# Formints professional backend check
backend-check-pro:
    @cd {{FORMINTS_DIR}}/formint-pro && make check

# Formints professional backend test
backend-test-pro:
    @cd {{FORMINTS_DIR}}/formint-pro && make test

# Formints cloud backend check
backend-check-cloud:
    @cd {{FORMINTS_DIR}}/formint-cloud && make check

# Formints cloud backend test
backend-test-cloud:
    @cd {{FORMINTS_DIR}}/formint-cloud && make test

# CTC backend check
backend-check-ctc:
    @cd {{PRECIS_DIR}}/precis-ctc/backend && make check

# ---------------------------------------------------------------
# Docs & tools
# ---------------------------------------------------------------

# Validate the docs content (prepare + validate)
docs-validate:
    @cd docs && make check

# Run the Docus dev server (localhost)
docs-dev:
    @cd docs && npm run dev

# Show status of all containers
status:
    @make status

# Tail logs from a service: just logs <service>
logs service:
    @docker compose ps -q {{service}} >/dev/null 2>&1 && docker logs -f --tail=100 {{service}} || docker logs -f --tail=100 {{service}}

# Probe every site's health endpoint
probe-health:
    @make probe-health

# ---------------------------------------------------------------
# Utilities (safe — never touches volumes)
# ---------------------------------------------------------------

# Prune stopped containers + dangling images + build cache (keeps volumes)
cleanup:
    @make cleanup

# Create the shared Docker networks
create-networks:
    @make create-networks

# Validate the Traefik config
validate-proxy:
    @python3 {{PROXY_DIR}}/scripts/validate-traefik-config.py

# Show the workspace status overview
overview:
    @echo "structa.cloud — command layer"
    @echo "  just install        → full workspace install"
    @echo "  just check          → all workspace checks"
    @echo "  just deploy         → full stack deploy"
    @echo "  just deploy-docs    → deploy Docus via nx"
    @echo "  just deploy-tools   → deploy self-hosted tools"
    @echo "  just nx <args>      → delegate to Nx"
    @just --list

# ---------------------------------------------------------------
# Legacy/alias helpers
# ---------------------------------------------------------------

# Alias of install — `just install` is canonical, `just setup` works too
setup: install
