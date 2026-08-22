# precis-landing — project-level orchestration (frontend + backend)
# Usage: make dev | make build | make check | make backend-dev | make backend-seed

NODE_BIN := $(shell ls -d $(HOME)/.nvm/versions/node/v22.* 2>/dev/null | sort -V | tail -1)/bin
export PATH := $(NODE_BIN):$(PATH)

UV_BIN := $(shell which uv 2>/dev/null || (test -x $(HOME)/.local/bin/uv && echo $(HOME)/.local/bin/uv) || echo /root/.local/bin/uv)
UV := $(UV_BIN) --project ../..
UV_RUN := $(UV) run

.PHONY: help install dev build build-prod preview check css clean e2e \
        install-assets build-assets build-assets-dev skeleton-manifest \
        config-show config-check config-front front-config back-config \
        backend-help backend-dev backend-check backend-migrate backend-seed backend-test \
        backend-superuser backend-shell backend-collectstatic superuser

help:
	@echo "precis-main — frontend (Astro) + backend (Django/Wagtail)"
	@echo "  Build:    make build (full) | build-prod | css"
	@echo "  Assets:   make install-assets | build-assets | build-assets-dev"
	@echo "  Skeleton: make skeleton-manifest"
	@echo "  Config:   make config-show | config-check | config-front   (config cascade, static plan, frontend wire)"
	@echo "  Dev:      make dev | preview | check"
	@echo "  Clean:    make clean"
	@echo "  Backend:  make backend-help | backend-dev | backend-check | backend-migrate | backend-seed | backend-test | backend-superuser | backend-shell | backend-collectstatic"
	@echo "  Superuser: make superuser — create Django admin (interactive, or non-interactive with DJANGO_SUPERUSER_* env)"

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

# Full project check — config cascade + frontend (Astro) + backend (Django).
check: config-check
	cd frontend && npm run check
	$(MAKE) -C backend check

e2e:
	@echo "The Django backend and Astro dev server must be running before this browser smoke test."
	cd frontend && npm run test:e2e

clean:
	cd frontend && rm -rf dist .astro node_modules
	rm -rf backend/assets/static/bundles node_modules

# ── Config Cascade (YAML defaults + .env) ──────────────────────────
# Merges shared Env YAML (projects/precis/configs/Env) → configs/*.yml →
# Env/_site.yml → .env → environment variables (highest). See configs/README.md
# and docs/guides/config-cascade.md for the full contract.
config-show: ## Print the merged config + resolved front/back views + static plan
	@$(UV_RUN) python -c "from pathlib import Path; from django_fusion.config.project import load_config, staticfiles_plan; root = Path('.').resolve(); c = load_config(root); print('PROJECT CONFIG —', c.get('SITE.name', 'precis-main'), '| env:', c.env); [print(f'  {k}: {v}') for k in ('DEBUG', 'ALLOWED_HOSTS', 'PORT', 'FRONTEND_PORT', 'FUSION_RENDER_FIRST', 'SITE_DOMAIN', 'DOMAIN_NAME') if (v := c.get(k)) is not None]; print('  SITE:', c.section('SITE') or {}); print('  ADMIN:', c.section('ADMIN') or {}); print('  CSS_PANEL:', c.section('CSS_PANEL') or {}); print('  DATABASE (type-wired; password resolves from .env, never shown):', c.section('DATABASE') or {}); print('  resolved back (http://localhost:8074):'); [print(f'    {k}: {v}') for k, v in c.resolve('http://localhost:8074', 'back').get('SITE', {}).items()]; print('  resolved front (http://localhost:3000):'); [print(f'    {k}: {v}') for k, v in c.resolve('http://localhost:3000', 'front').get('SITE', {}).items()]; print(); print(staticfiles_plan(root, overrides=c.section('STATIC')).render())"

config-check: ## Validate required identity + database keys resolve from the config
	@$(UV_RUN) python -c "from django_fusion.config.project import load_config; c = load_config('.'); req = {'SITE.name': 'precis-main', 'SITE.primary_domain': 'structa.cloud', 'SITE.domains': 'structa.cloud', 'ADMIN.panel_path': '/admin/', 'DATABASE.type': 'sqlite|postgres', 'DATABASE.sqlite.name': 'db path or name', 'DATABASE.postgres.name': 'db name (from .env)'}; missing = [k for k, _ in req.items() if not c.get(k)]; print('CONFIG CHECK — OK ✅' if not missing else f'CONFIG CHECK — MISSING: {missing}'); raise SystemExit(1 if missing else 0)"

# Wires the project config cascade into the Astro frontend: dumps the merged
# identity/admin/css-panel sections to frontend/src/config/project.json, which
# the Astro module frontend/src/config/project.ts reads. Regenerate after any
# edit to configs/*.yml or .env (env vars are NOT baked — they stay runtime).
config-front: ## Generate frontend/src/config/project.json from the config cascade
	@$(UV_RUN) python -c "from pathlib import Path; import json; from django_fusion.config.project import load_config; c = load_config('.'); data = {k: c.section(k) for k in ('SITE', 'ADMIN', 'CSS_PANEL', 'STATIC') if c.section(k)}; data.update({k: c.get(k) for k in ('DEBUG', 'FUSION_RENDER_FIRST', 'FRONTEND_PORT') if c.get(k) is not None}); out = Path('frontend/src/config/project.json'); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n'); print('✅ wrote', out)"

# Delegation alias — front/back config targets.
front-config: config-front ## Alias for config-front
back-config: config-show ## Alias for config-show (backend view)

# ── Superuser (createsuperuser) ────────────────────────────────────
# Interactive by default; non-interactive when DJANGO_SUPERUSER_EMAIL and
# DJANGO_SUPERUSER_PASSWORD are set in the environment (see backend/Makefile).
superuser: ## Create a Django superuser (delegates to the backend Makefile)
	$(MAKE) -C backend superuser


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
# backend-<target> delegates to the backend Makefile (same target name), so
# `make backend-superuser` → `make -C backend superuser`, etc.
backend-help backend-dev backend-check backend-migrate backend-seed backend-test \
backend-superuser backend-shell backend-collectstatic:
	$(MAKE) -C backend $(@:backend-%=%)
