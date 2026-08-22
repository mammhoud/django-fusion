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

.PHONY: help build watch dev clean install reinstall info

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
	@echo "    make info   → Show this message"
	@echo ""
	@echo "  Component SCSS partials:"
	@ls -1 src/django_fusion/comp/*/_*.scss 2>/dev/null || echo "    (none yet)"
	@echo "  Asset partials:"
	@ls -1 src/django_fusion/assets/*/_*.scss 2>/dev/null || echo "    (none yet)"
