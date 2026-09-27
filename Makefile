# ============================================================================
# django-fusion — asset build + release targets
# ============================================================================
# Two groups of targets:
#
#   Assets   — build the webpack bundle for component SCSS/JS (needs Node).
#   Release  — build, validate, and publish the Python distribution.
#
# Prerequisites: Node.js >= 18 / npm >= 9 for assets; uv for release targets.
#
# Assets output lands in static/bundles/ and webpack-stats.json, and is
# consumed by django-webpack-loader:
#     {% load render_bundle from webpack_loader %}
#     {% render_bundle 'fusion' 'css' %}
#
# Publishing is documented end to end in docs/23-publishing.md (DF-023).
# ============================================================================

SHELL := /bin/bash

.PHONY: help build watch dev clean install reinstall info \
        version dist check-dist publish-test publish test lint

# ── Help alias ────────────────────────────────────────────────────────────────
help: info

# ── Asset build ───────────────────────────────────────────────────────────────

build: install
	@echo "→ Building django-fusion assets (production)..."
	npm run build
	@echo "✅ Build complete:"
	@ls -lh static/bundles/*.css static/bundles/*.js 2>/dev/null; echo "   webpack-stats.json: $$(wc -c < webpack-stats.json) bytes"

watch: install
	@echo "→ Watching for changes (dev mode)..."
	npm run watch

dev: install
	@echo "→ Building django-fusion assets (development)..."
	npm run dev
	@echo "✅ Dev build complete"

clean:
	@echo "→ Removing generated webpack assets..."
	rm -rf static/bundles/*.js static/bundles/*.css static/bundles/*.map \
	       static/bundles/fonts/ static/bundles/images/ webpack-stats.json
	mkdir -p static/bundles
	touch static/bundles/.gitkeep
	@echo "✅ Clean complete"

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

info:
	@echo "django-fusion"
	@echo "════════════════════════════"
	@echo "  Version:      $$(make -s version)"
	@echo "  Entry point:  src/django_fusion/assets/entry.js"
	@echo "  SCSS entry:   src/django_fusion/assets/fusion.scss"
	@echo "  Output dir:   static/bundles/"
	@echo ""
	@echo "  Asset targets:"
	@echo "    make build        → Production bundle (content-hashed)"
	@echo "    make dev          → Dev bundle (fast, no minification)"
	@echo "    make watch        → Dev + file watcher"
	@echo "    make clean        → Remove generated assets"
	@echo "    make info         → Show this message"
	@echo ""
	@echo "  Release targets:"
	@echo "    make version      → Print the version from pyproject.toml"
	@echo "    make test         → Run the test suite"
	@echo "    make lint         → Run ruff over src and tests"
	@echo "    make dist         → Build sdist + wheel into dist/"
	@echo "    make check-dist   → twine check the built artifacts"
	@echo "    make publish-test → Upload to TestPyPI"
	@echo "    make publish      → Upload to PyPI (requires a clean tree at the tag)"
	@echo ""
	@echo "  See docs/23-publishing.md for the full release runbook."
	@echo ""
	@echo "  Component SCSS partials:"
	@ls -1 src/django_fusion/assets/*/_*.scss 2>/dev/null || echo "    (none found)"

# ── Test / lint ───────────────────────────────────────────────────────────────

test:
	uv run --extra test pytest -q

lint:
	uv run --with ruff ruff check src tests

# ── Release ───────────────────────────────────────────────────────────────────

# Reads the version from pyproject.toml without importing the package, so it
# works before dependencies are installed.
version:
	@python3 -c "import re,pathlib; print(re.search(r'^version\s*=\s*\"([^\"]+)\"', pathlib.Path('pyproject.toml').read_text(), re.M).group(1))"

dist:
	@echo "→ Cleaning previous artifacts..."
	rm -rf dist build src/*.egg-info
	@echo "→ Building sdist + wheel for $$(make -s version)..."
	uv build
	@echo "✅ Built:"
	@ls -lh dist/

check-dist:
	@test -d dist || { echo "❌ dist/ is missing — run 'make dist' first"; exit 1; }
	uv run --with twine twine check dist/*

# TestPyPI first, always. Versions on both indexes are permanent.
publish-test: check-dist
	@echo "→ Uploading $$(make -s version) to TestPyPI..."
	uv run --with twine twine upload --repository testpypi dist/*

# Guarded: the tree must be clean and HEAD must be exactly the v<version> tag,
# so the published artifact is provably the tagged commit.
publish: check-dist
	@VERSION="$$(make -s version)"; \
	if [ -n "$$(git status --porcelain)" ]; then \
		echo "❌ Working tree is dirty — commit or stash before publishing"; \
		exit 1; \
	fi; \
	if ! git rev-parse -q --verify "refs/tags/v$$VERSION" >/dev/null; then \
		echo "❌ Missing tag v$$VERSION — create it first (see docs/23-publishing.md)"; \
		exit 1; \
	fi; \
	if [ "$$(git rev-parse HEAD)" != "$$(git rev-parse "v$$VERSION^{commit}")" ]; then \
		echo "❌ HEAD is not v$$VERSION — check out the tagged commit before publishing"; \
		exit 1; \
	fi; \
	echo "→ Uploading $$VERSION to PyPI (tag v$$VERSION)..."; \
	uv run --with twine twine upload dist/*
