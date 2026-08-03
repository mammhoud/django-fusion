# landing-fusion — project-level orchestration (frontend + backend)
# Usage: make dev | make build | make check | make backend-dev | make backend-seed

NODE_BIN := $(shell ls -d $(HOME)/.nvm/versions/node/v22.* 2>/dev/null | sort -V | tail -1)/bin
export PATH := $(NODE_BIN):$(PATH)

.PHONY: help install dev build preview check clean \
        backend-help backend-dev backend-check backend-migrate backend-seed backend-test

help:
	@echo "landing-fusion — frontend (Astro) + backend (Django/Wagtail)"
	@echo "  Frontend: make install | dev | build | preview | check | clean"
	@echo "  Backend:  make backend-help | backend-dev | backend-check | backend-migrate | backend-seed | backend-test"

# ── Frontend (Astro) ───────────────────────────────────────────────
install:
	cd frontend && npm install

dev:
	cd frontend && npm run dev

build:
	cd frontend && npm run build

preview:
	cd frontend && npm run preview

check:
	cd frontend && npm run check

clean:
	cd frontend && rm -rf dist .astro node_modules

# ── Backend (Django + Wagtail) ─────────────────────────────────────
backend-help backend-dev backend-check backend-migrate backend-seed backend-test:
	$(MAKE) -C backend $(@:backend-%=%)
