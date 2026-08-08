# landing-fusion — project-level orchestration (frontend + backend)
# Usage: make dev | make build | make check | make backend-dev | make backend-seed

NODE_BIN := $(shell ls -d $(HOME)/.nvm/versions/node/v22.* 2>/dev/null | sort -V | tail -1)/bin
export PATH := $(NODE_BIN):$(PATH)

.PHONY: help install dev build preview check css clean e2e \
        backend-help backend-dev backend-check backend-migrate backend-seed backend-test

help:
	@echo "landing-fusion — frontend (Astro) + backend (Django/Wagtail)"
	@echo "  Frontend: make install | dev | build | preview | check | css | clean"
	@echo "  Backend:  make backend-help | backend-dev | backend-check | backend-migrate | backend-seed | backend-test"

# ── Frontend (Astro) ───────────────────────────────────────────────
install:
	cd frontend && npm install

dev:
	cd frontend && npm run dev

build: css
	cd frontend && npm run build

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

# ── Backend (Django + Wagtail) ─────────────────────────────────────
backend-help backend-dev backend-check backend-migrate backend-seed backend-test:
	$(MAKE) -C backend $(@:backend-%=%)
