# ============================================================
# Structa Cloud — Justfile (user-facing command layer)
# ============================================================
# `just` is the friendly front-end for the monorepo. After the
# Justfile→Make refactor, EVERY recipe below is a thin delegation
# to the root Makefile — the Makefile is the single source of
# truth for commands (no duplicated logic).
#
#   just install          # full workspace install (Python + JS + POS)
#   just check            # run all workspace checks
#   just deploy           # full stack deploy (postgres-first)
#   just clean            # generated files + logs + containers (volumes kept)
#   just clean-unused     # + prune unused docker resources (volumes kept)
#   just nx <args>        # delegate to nx (e.g. just nx run docs:build)
#
# Run `just --list` for the full command catalog. For everything
# else use `make help` (or `just help`) — every `just <recipe>`
# below is equivalent to `make <target>`.

set shell := ["bash", "-uc"]

# Directory layout — mirrors the root Makefile
WORKSPACE_ROOT := "."
# Default site for `just dev` / per-site delegations (ctc|precis-main|...)
# Override with: just --set WEBSITE precis-main dev
WEBSITE := "ctc"

# ---------------------------------------------------------------
# Meta
# ---------------------------------------------------------------

# List every recipe with its doc comment
default:
    @just --list

# Show the underlying Makefile help (full command catalog)
help:
    @make help

# Workspace command overview
overview:
    @make overview

# ---------------------------------------------------------------
# Install
# ---------------------------------------------------------------

# Full workspace install: uv sync + frontends + formints + docs
install:
    @make install

# Install only the Python workspace deps (uv sync)
install-python:
    @make install-python

# Install only the JS frontends
install-js:
    @make install-js

# Install only the Formints editions (all editions + SDK)
install-formints install-formints-all:
    @make install-formints

# Install docs (Docus) dependencies
install-docs:
    @make install-docs

# Alias of install
setup: install

# ---------------------------------------------------------------
# Check / test / build
# ---------------------------------------------------------------

# Run every workspace check (nx run-many check)
check:
    @make check

# Run every workspace test (nx run-many test)
test:
    @make test

# Check the docs project (Docus)
check-docs:
    @make check-docs

# Build the docs project (Docus)
build-docs:
    @make build-docs

# Validate docs content
docs-validate:
    @make docs-validate

# Run the Docus dev server (localhost)
docs-dev:
    @make docs-dev

# ---------------------------------------------------------------
# Nx delegation
# ---------------------------------------------------------------

# Delegate any target to nx: just nx <args...> (e.g. just nx run docs:build)
nx *args:
    @make nx NX_ARGS="{{args}}"

# Nx graph visualization
nx-graph:
    @make nx-graph

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
    @make deploy-docs

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

# Deploy a single tool by name: just deploy-tool affine
deploy-tool name:
    @make deploy-tool TOOL={{name}}

# ---------------------------------------------------------------
# Backend commands (product-scoped, delegate to project Makefiles)
# ---------------------------------------------------------------

# Precis (unified) backend check
backend-check-precis:
    @make backend-check-precis

# Precis (unified) backend test
backend-test-precis:
    @make backend-test-precis

# Precis (unified) backend migrate
backend-migrate-precis:
    @make backend-migrate-precis

# CTC backend check
backend-check-ctc:
    @make backend-check-ctc

# Formints: check all editions
check-formints:
    @make check-formints

# Formints: test all editions
test-formints:
    @make test-formints

# Formints professional backend check
backend-check-pro:
    @make backend-check-pro

# Formints professional backend test
backend-test-pro:
    @make backend-test-pro

# Formints cloud backend check
backend-check-cloud:
    @make backend-check-cloud

# Formints cloud backend test
backend-test-cloud:
    @make backend-test-cloud

# ---------------------------------------------------------------
# Local development & server entry points
# ---------------------------------------------------------------

# Run the Django dev server for the selected website: just dev WEBSITE=precis-main
dev:
    @make run-dev WEBSITE={{WEBSITE}}

run-dev:
    @make run-dev WEBSITE={{WEBSITE}}

run-local:
    @make run-local WEBSITE={{WEBSITE}}

# Per-site dev shortcuts
dev-ctc:
    @make dev-ctc

dev-precis:
    @make dev-precis

dev-loop-crm:
    @make dev-loop-crm

# Start the production server (container default)
server:
    @make server

# ---------------------------------------------------------------
# Docker delegation (per-site compose operations)
# ---------------------------------------------------------------

docker-up:
    @make docker-up

docker-down:
    @make docker-down

docker-build:
    @make docker-build

docker-logs:
    @make docker-logs

docker-status:
    @make docker-status

docker-restart:
    @make docker-restart

docker-stop:
    @make docker-stop

docker-start:
    @make docker-start

docker-prune:
    @make docker-prune

# ---------------------------------------------------------------
# Clean family (safe by default; destructive variants are explicit)
# ---------------------------------------------------------------

# Generated files only: caches, dist, old builds + logs + root compose teardown (volumes KEPT)
clean:
    @make clean

# Generated logs only (preserves .gitkeep)
clean-logs:
    @make clean-logs

# Stop known stacks + prune unused containers/images/build cache (volumes KEPT)
clean-docker:
    @make clean-docker

# clean + clean-docker — everything unused, volumes preserved
clean-unused:
    @make clean-unused

# Full teardown — also removes unused volumes (destructive)
clean-all:
    @make clean-all

# Legacy: prune stopped containers + dangling images + build cache (keeps volumes)
cleanup:
    @make cleanup

# ---------------------------------------------------------------
# Utilities (safe — never touches volumes)
# ---------------------------------------------------------------

# Create the shared Docker networks
create-networks:
    @make create-networks

# Validate the Traefik config
validate-proxy:
    @make validate-proxy

# Show status of all containers
status:
    @make status

# Tail logs from a service: just logs <service>
logs service:
    @make logs-service SERVICE={{service}}

# Probe every site's health endpoint
probe-health:
    @make probe-health
