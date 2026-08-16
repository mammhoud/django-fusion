# precis-landing — project-level orchestration (frontend + backend)
# Usage: make dev | make build | make check | make backend-dev | make backend-seed

NODE_BIN := $(shell ls -d $(HOME)/.nvm/versions/node/v22.* 2>/dev/null | sort -V | tail -1)/bin
export PATH := $(NODE_BIN):$(PATH)

.PHONY: help install dev build build-prod preview check css clean e2e \
        install-assets build-assets build-assets-dev skeleton-manifest \
        backend-help backend-dev backend-check backend-migrate backend-seed backend-test

help:
	@echo "precis-landing — frontend (Astro) + backend (Django/Wagtail)"
	@echo "  Build:    make build (full) | build-prod | css"
	@echo "  Assets:   make install-assets | build-assets | build-assets-dev"
	@echo "  Skeleton: make skeleton-manifest"
	@echo "  Dev:      make dev | preview | check"
	@echo "  Clean:    make clean"
	@echo "  Backend:  make backend-help | backend-dev | backend-check | backend-migrate | backend-seed | backend-test"

# ── Frontend (Astro) ───────────────────────────────────────────────
install:
	cd frontend && npm install

dev:
	cd frontend && npm run dev

build: install-assets build-assets css
	cd frontend && npm run build

# Full production build — same as `build` but explicit for CI pipelines
build-prod: build

# Compile the shared design system (frontend/src/styles/globals.css) into
# the backend-served assets/static/css/fusion.css. globals.css declares
# @source for the Django templates, so the backend render gets the same
# Tailwind utilities + components as the Astro build. Committed to git so
# fresh clones and the Django render always have the compiled stylesheet.
css:
	cd frontend && npx @tailwindcss/cli -i src/styles/globals.css -o ../assets/static/css/fusion.css --minify

preview:
	cd frontend && npm run preview

check:
	cd frontend && npm run check

e2e:
	@echo "The Django backend and Astro dev server must be running before this browser smoke test."
	cd frontend && npm run test:e2e

clean:
	cd frontend && rm -rf dist .astro node_modules
	rm -rf backend/assets/static/bundles node_modules

# ── Webpack Asset Build (Django-side SCSS/JS) ──────────────────────
# Extends projects/webpack/base.config.js — see webpack/precis-landing.config.js
install-assets:
	npm install

build-assets: skeleton-manifest
	npx webpack --config webpack/precis-landing.config.js --mode=production

build-assets-dev:
	npx webpack --config webpack/precis-landing.config.js --mode=development

# ── Skeleton Manifest ──────────────────────────────────────────────
# Runs the Django management command to produce a static JSON manifest
# consumed by the Astro frontend (SkeletonBridge.astro). Depends on
# webpack having been run first so the manifest can resolve CSS/JS deps.
skeleton-manifest:
	$(MAKE) -C backend skeleton-manifest

# ── Backend (Django + Wagtail) ─────────────────────────────────────
backend-help backend-dev backend-check backend-migrate backend-seed backend-test:
	$(MAKE) -C backend $(@:backend-%=%)
