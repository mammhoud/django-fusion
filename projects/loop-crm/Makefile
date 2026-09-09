# loop-crm — project-level orchestration (frontend + backend)
# Usage: make dev | make build | make check | make backend-dev | make migrate
# Nx:     make nx-check | make nx-test | make nx-build | make nx-dev | make nx-graph
#         (delegates to `npx nx run loop-crm:<target>` at the workspace root)

NODE_BIN := $(shell ls -d $(HOME)/.nvm/versions/node/v22.* 2>/dev/null | sort -V | tail -1)/bin
export PATH := $(NODE_BIN):$(PATH)

UV_BIN := $(shell which uv 2>/dev/null || (test -x $(HOME)/.local/bin/uv && echo $(HOME)/.local/bin/uv) || echo /root/.local/bin/uv)
UV := $(UV_BIN) --project ../..
UV_RUN := $(UV) run

.PHONY: help install dev build preview check clean clean-unused \
        backend-help backend-dev backend-check backend-migrate backend-test \
        backend-erd backend-erd-all \
        backend-seed backend-seed-pages backend-lint backend-format backend-shell \
        configs validate-env env-example config-show config-check \
        nx-help nx-dev nx-build nx-preview nx-check nx-test \
        nx-backend-dev nx-backend-check nx-backend-test nx-backend-migrate nx-graph

help:
	@echo "loop-crm — frontend (Astro) + backend (Django + django-fusion)"
	@echo "  Build:    make build"
	@echo "  Dev:      make dev | preview | check"
	@echo "  Clean:    make clean"
	@echo "  Backend:  make backend-help | backend-dev | backend-check | backend-migrate | backend-test"
	@echo "            make backend-seed | backend-lint | backend-format | backend-shell"
	@echo "  Configs:  make configs | validate-env | env-example (env contract, see configs/)"
	@echo "            make config-show | config-check (YAML cascade + static-files plan)"
	@echo "  Nx:       make nx-check | nx-test | nx-build | nx-dev | nx-graph (runs through Nx at repo root)"

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

# Everything generated: frontend build outputs + caches (source untouched).
clean-unused: clean
	@echo "🧹 Removing caches and logs (source untouched)..."
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	@rm -rf logs 2>/dev/null || true
	@echo "✅ clean-unused complete"

# ── Configs (env contract, dependency-free) ───────────────────────
# The configs/ package is the canonical environment catalog; validate-env
# checks the current environment against it and env-example regenerates
# .env.example from the same source of truth.
configs:
	@python3 -c "import sys; sys.path.insert(0, 'configs'); from configs import env_defaults; print('configs OK —', len(env_defaults()), 'env vars catalogued')"

validate-env:
	@python3 -c "import sys; sys.path.insert(0, 'configs'); from configs import validate_environment; p = validate_environment(); print('\n'.join('  - '+x for x in p) if p else 'Loop-CRM environment OK.')"

env-example:
	@python3 -c "import sys; sys.path.insert(0, 'configs'); from configs.validate import render_env_example; print(render_env_example())" > .env.example.generated
	@echo "wrote .env.example.generated (compare with .env.example)"

# ── YAML config cascade (django-fusion config.project) ──────────────
# Merges configs/*.yml → Env/_site.yml → .env → env vars (highest). The
# backend seeds its env defaults from the SITE/ADMIN sections; these targets
# show and validate the merged result.
config-show: ## Print the merged config + resolved front/back views + static plan
	@$(UV_RUN) python -c "from pathlib import Path; from django_fusion.config.project import load_config, staticfiles_plan; root = Path('.').resolve(); c = load_config(root); print('PROJECT CONFIG —', c.get('SITE.name', 'loop-crm'), '| env:', c.env); [print(f'  {k}: {v}') for k in ('DEBUG', 'ALLOWED_HOSTS', 'PORT', 'FRONTEND_PORT', 'FUSION_RENDER_FIRST', 'SITE_DOMAIN', 'DOMAIN_NAME') if (v := c.get(k)) is not None]; print('  SITE:', c.section('SITE') or {}); print('  ADMIN:', c.section('ADMIN') or {}); print('  CSS_PANEL:', c.section('CSS_PANEL') or {}); print('  resolved back (https://crm.structa.cloud):'); [print(f'    {k}: {v}') for k, v in c.resolve('https://crm.structa.cloud', 'back').get('SITE', {}).items()]; print(); print(staticfiles_plan(root, overrides=c.section('STATIC')).render())"

config-check: ## Validate required identity keys resolve from the config
	@$(UV_RUN) python -c "from django_fusion.config.project import load_config; c = load_config('.'); req = {'SITE.name': 'loop-crm', 'SITE.primary_domain': 'crm.structa.cloud', 'SITE.domains': 'crm.structa.cloud', 'ADMIN.panel_path': '/admin/'}; missing = [k for k, _ in req.items() if not c.get(k)]; print('CONFIG CHECK — OK ✅' if not missing else f'CONFIG CHECK — MISSING: {missing}'); raise SystemExit(1 if missing else 0)"

# ── Backend (Django + django-fusion) ──────────────────────────────
backend-help backend-dev backend-check backend-migrate backend-test \
backend-erd backend-erd-all \
backend-seed backend-seed-pages backend-lint backend-format backend-shell:
	$(MAKE) -C backend $(@:backend-%=%)

# ── Nx integration (delegates to the Nx workspace at repo root) ───
# These run the same project targets through Nx, so the Nx cache and
# dependency graph apply. `nx run-many --target=X --all` still works from
# the repo root; these targets are the project-local entrypoints.
NX := cd ../.. && npx nx

nx-help:
	@echo "loop-crm Nx targets: nx-dev nx-build nx-preview nx-check nx-test"
	@echo "  nx-backend-dev nx-backend-check nx-backend-test nx-backend-migrate nx-graph"

nx-dev:
	$(NX) run loop-crm:dev

nx-build:
	$(NX) run loop-crm:build

nx-preview:
	$(NX) run loop-crm:preview

nx-check:
	$(NX) run loop-crm:check

nx-test:
	$(NX) run loop-crm:test

nx-backend-dev:
	$(NX) run loop-crm:backend-dev

nx-backend-check:
	$(NX) run loop-crm:backend-check

nx-backend-test:
	$(NX) run loop-crm:backend-test

nx-backend-migrate:
	$(NX) run loop-crm:backend-migrate

nx-graph:
	$(NX) graph
