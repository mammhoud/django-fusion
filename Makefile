# ============================================================================
# django-fusion — Asset Build Targets
# ============================================================================
# Builds the webpack bundle for component SCSS/JS.
#
# Prerequisites: Node.js >= 18, npm >= 9
#
# Common commands:
#   make build         → Production build (one-shot, CI-ready)
#   make watch         → Development + file watcher
#   make dev           → Development build (no minification, source maps)
#   make clean         → Remove all generated assets
#
# Integration:
#   The output lands in static/bundles/ and webpack-stats.json.
#   Django sites consume it via django-webpack-loader:
#     {% load render_bundle from webpack_loader %}
#     {% render_bundle 'fusion' 'css' %}
#     {% render_bundle 'fusion' 'js' %}
# ============================================================================

SHELL := /bin/bash

.PHONY: help build watch dev clean install reinstall info check docs plugin-template

# ── Help alias ─────────────────────────────────────────────────────────────────
help: info

# ── Default target ────────────────────────────────────────────────────────────

# ── Default target ────────────────────────────────────────────────────────────
build: install
	@echo "→ Building django-fusion assets (production)..."
	npm run build
	@echo "✅ Build complete:"
	@ls -lh static/bundles/*.css static/bundles/*.js 2>/dev/null; echo "   webpack-stats.json: $$(wc -c < webpack-stats.json) bytes"

# ── Development ───────────────────────────────────────────────────────────────
watch: install
	@echo "→ Watching for changes (dev mode)..."
	npm run watch

dev: install
	@echo "→ Building django-fusion assets (development)..."
	npm run dev
	@echo "✅ Dev build complete"

# ── Clean ─────────────────────────────────────────────────────────────────────
clean:
	@echo "→ Removing generated webpack assets..."
	rm -rf static/bundles/*.js static/bundles/*.css static/bundles/*.map \
	       static/bundles/fonts/ static/bundles/images/ webpack-stats.json
	mkdir -p static/bundles
	touch static/bundles/.gitkeep
	@echo "✅ Clean complete"

# ── Install dependencies ──────────────────────────────────────────────────────
install:
	@echo "→ Installing npm dependencies..."
	@if [ ! -d "node_modules" ]; then \
		npm install --silent; \
	else \
		echo "   node_modules exists — skipping install (run 'make reinstall' to force)"; \
	fi

reinstall:
	@echo "→ Reinstalling npm dependencies..."
	rm -rf node_modules package-lock.json
	npm install
	@echo "✅ Reinstall complete"

# ── Checks ────────────────────────────────────────────────────────────────────
# Two passes, both stdlib-only (no venv, no npm install):
#   1. generated package docs under src/django_fusion/ must be up to date, and
#   2. every `django_fusion.*` reference in the library docs must resolve to a
#      real module, or a name that module actually exposes.
# A moved package therefore cannot leave a stale path behind in either the
# generated docs or the hand-written guides; the gate exits non-zero and CI
# (fusion-ci) fails.
# Two gates, both stdlib-only so they run in a bare CI job with no venv:
#   1. stale `django_fusion.*` package paths across the library docs
#   2. plugin PRODUCT.md descriptions vs the catalog (missing/drift is a failure)
check:
	@echo "→ Checking docs for stale django_fusion.* package paths..."
	@python3 scripts/generate_design_docs.py --check
	@echo "→ Checking plugin descriptions against the catalog..."
	@python3 scripts/generate_plugin_products.py --check

# Regenerate them after a move/rename (writes in place):
docs:
	@echo "→ Regenerating package docs..."
	@python3 scripts/generate_design_docs.py
	@echo "→ Listing plugin description state..."
	@python3 scripts/generate_plugin_products.py --list
	@echo "✅ Docs regenerated"

# Scaffold a description for a plugin that does not have one yet:
#   make plugin-template PLUGIN=myplugin
plugin-template:
	@test -n "$(PLUGIN)" || { echo "✖ usage: make plugin-template PLUGIN=<name>"; exit 2; }
	@python3 scripts/generate_plugin_products.py --template $(PLUGIN)

# ── Info ──────────────────────────────────────────────────────────────────────
info:
	@echo "django-fusion Asset Pipeline"
	@echo "════════════════════════════"
	@echo "  Entry point:  src/django_fusion/assets/entry.js"
	@echo "  SCSS entry:   src/django_fusion/assets/fusion.scss"
	@echo "  Output dir:   static/bundles/"
	@echo "  Stats file:   webpack-stats.json"
	@echo ""
	@echo "  Targets:"
	@echo "    make build  → Production bundle (content-hashed)"
	@echo "    make dev    → Dev bundle (fast, no minification)"
	@echo "    make watch  → Dev + file watcher"
	@echo "    make clean  → Remove generated assets"
	@echo "    make check  → Fail on stale module paths in the generated docs"
	@echo "    make docs   → Regenerate package docs (design.md + README.md)"
	@echo "    make info   → Show this message"
	@echo ""
	@echo "  Component SCSS partials:"
	@ls -1 src/django_fusion/comp/*/_*.scss 2>/dev/null || echo "    (none yet)"
	@echo "  Asset partials:"
	@ls -1 src/django_fusion/assets/*/_*.scss 2>/dev/null || echo "    (none yet)"
