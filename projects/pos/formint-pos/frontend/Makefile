# ============================================================================
# Formint POS — Frontend Makefile (Astro + Alpine.js + HTMX)
# ============================================================================
# Delegated from ../Makefile via `make frontend-<target>`.
#
# The dev server proxies /api, /htmx and /fusion to the backend (default
# 127.0.0.1:8767) — see astro.config.mjs. Start both with `make env` at the
# formint-pos root.

.PHONY: help install dev build preview check test clean

.DEFAULT_GOAL := help

# Resolve node from PATH first (avoids hard-coding an .nvm version glob).
NODE_BIN := $(shell dirname $$(command -v node 2>/dev/null) 2>/dev/null)
export PATH := $(NODE_BIN):$(PATH)

PORT := 4321

help: ## Show frontend commands
	@echo 'Formint POS Frontend (Astro + Alpine + HTMX)'
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  %-14s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Install npm dependencies
	npm install

dev: ## Astro dev server (:PORT, default 4321)
	npm run dev -- --port $(PORT) --host 0.0.0.0

build: ## Production build
	npm run build

preview: ## Preview the production build
	npm run preview -- --port $(PORT) --host 0.0.0.0

check: ## Astro type check (0 errors expected)
	npm run check

test: ## Frontend contract tests (vitest)
	npm run test

clean: ## Remove build artifacts + node_modules
	rm -rf dist .astro node_modules
	@echo '✅ Frontend artifacts cleaned'
