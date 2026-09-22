# Unified Development Organization Plan — PlanInc & Formint

## Status: Draft · Version: 4.1 · Date: 2026-09-20

This document establishes a unified file organization for both PlanInc and Formint within the Structa Cloud monorepo at `/home/`. No symlinks are used. Shared libraries and extraction plans are handled in a separate document. This plan focuses on directory structure, product organization, commands, and developer workflow.

### FlyonUI Integration (v4.1)
FlyonUI (`flyonui` npm v2.4.1) has been added as a Tailwind CSS plugin in PlanInc as a potential replacement for `@heroui/react` (v2.8.0-beta.1). It provides 80+ semantic-class components with built-in headless JS plugins, 800+ examples, Tailwind v4 compatibility, and MIT licensing. See §9 below for migration notes.

---

## 1. Current State Summary

### PlanInc (to be integrated into monorepo)
- **Current location:** `/home/application/tools/PlanInc/` (standalone repo, outside `/home/`)
- **Stack:** React 18 + Vite + TailwindCSS + HeroUI (FlyonUI as optional replacement) + MobX + Tauri v2 + Express/tRPC + SurrealDB
- **Package manager:** Bun
- **Key directories:** `src/frontend/`, `src/server/`, `src/frontend/src-tauri/`, `src/frontend/tauri-plugin-planinc/`, `runtime/`, `brandkit/`, `docs/`
- **Notable:** Has `planinc-types/`, `src/app/` (React/Vite/Tauri)

### Formint (source missing — to be created)
- **Referenced at:** `projects/formints/` by root `Makefile` (`POS_DIR`) and `projects/Makefile` (`website-formints`)
- **Not present on filesystem**
- **5 editions:** Formint main (Rust/SQLite), Pro (Python/Django), Standard (Python/Django), Cloud (Python/Django), Client (Tauri/Rust)
- **Patterns:** Same frontend stack as PlanInc, same design tokens, same BEM conventions

### Existing Shared Infrastructure (kept as-is, not part of this plan)
- `libs/django-fusion/` — Shared Django/Wagtail components
- `projects/assets/theme/` — 15+ themes with OKLCH four-tier design tokens (includes `pos/` theme)
- `projects/webpack/` — Shared webpack configs
- `tests/` — Shared pytest fixtures

---

## 2. Unified Directory Tree

```
/home/                                  # Monorepo root
├── projects/                           # All product code
│   ├── planinc/                        # ← NEW: PlanInc product
│   │   ├── backend/                    # Express + tRPC server (Bun)
│   │   │   ├── src/                    # Server source (moved from src/server/)
│   │   │   │   ├── aiServer/
│   │   │   │   ├── jobs/
│   │   │   │   ├── lib/
│   │   │   │   ├── middleware/
│   │   │   │   ├── routerExpress/
│   │   │   │   ├── routerTrpc/
│   │   │   │   ├── types/
│   │   │   │   └── seed/
│   │   │   ├── package.json
│   │   │   ├── tsconfig.json
│   │   │   └── Dockerfile
│   │   │
│   │   ├── frontend/                   # React + Vite + Tauri frontend
│   │   │   ├── src/                    # React source
│   │   │   │   ├── App.tsx
│   │   │   │   ├── components/         # Product-specific components
│   │   │   │   ├── hooks/              # Product-specific hooks
│   │   │   │   ├── lib/                # Frontend utilities
│   │   │   │   ├── pages/              # Page-level components
│   │   │   │   ├── platform/           # Platform detection
│   │   │   │   ├── store/              # MobX stores
│   │   │   │   ├── styles/             # Global styles
│   │   │   │   └── main.tsx
│   │   │   ├── src-tauri/              # Tauri v2 Rust desktop shell
│   │   │   │   ├── src/
│   │   │   │   ├── Cargo.toml
│   │   │   │   ├── capabilities/
│   │   │   │   ├── icons/
│   │   │   │   └── tauri.conf.json
│   │   │   ├── tauri-plugin-planinc/   # Custom Tauri plugin
│   │   │   ├── public/
│   │   │   ├── package.json
│   │   │   ├── vite.config.ts
│   │   │   ├── tailwind.config.js
│   │   │   └── tsconfig.json
│   │   │
│   │   ├── planinc-types/              # Type definitions (keep)
│   │   ├── runtime/                    # Deployed runtime (Express + SurrealDB)
│   │   ├── brandkit/                   # Logo assets, colors, icons
│   │   ├── docs/                       # 14 hand-written docs
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.prod.yml
│   │   ├── Dockerfile
│   │   ├── Makefile                    # Product-specific targets
│   │   ├── package.json                # Root workspace package
│   │   ├── tsconfig.json
│   │   ├── turbo.json                  # Turborepo pipeline config
│   │   ├── bun.lock
│   │   └── AGENTS.md                   # Product-specific agent guidance
│   │
│   ├── formint-dev/                    # ← NEW: Formint POS product (renamed from formints/)
│   │   ├── formint/                    # Rust/SQLite desktop edition (renamed from formint-community/)
│   │   │   ├── frontend/               # React + HeroUI frontend
│   │   │   │   ├── src/
│   │   │   │   ├── src-tauri/          # Tauri v2 Rust shell
│   │   │   │   ├── tauri-plugin-formint/  # Custom Tauri plugin
│   │   │   │   ├── package.json
│   │   │   │   └── vite.config.ts
│   │   │   ├── src/                    # Rust/SQLite core (NOT Python)
│   │   │   ├── Cargo.toml
│   │   │   └── Makefile
│   │   │
│   │   ├── formint-pro/                # Python/Django professional edition
│   │   │   ├── backend/                # Django backend
│   │   │   │   ├── apps/
│   │   │   │   ├── settings/
│   │   │   │   ├── manage.py
│   │   │   │   ├── Dockerfile
│   │   │   │   └── requirements.txt
│   │   │   ├── frontend/               # React + HeroUI + HTMX
│   │   │   │   ├── src/
│   │   │   │   ├── templates/          # Django templates
│   │   │   │   └── assets/
│   │   │   └── package.json
│   │   │
│   │   ├── formint-standard/           # Python/Django standard edition
│   │   │   ├── backend/
│   │   │   ├── frontend/
│   │   │   └── package.json
│   │   │
│   │   ├── formint-cloud/              # Python/Django cloud master
│   │   │   ├── backend/                # Django serving API
│   │   │   ├── frontend/
│   │   │   └── package.json
│   │   │
│   │   ├── formint-client/             # Tauri/Rust desktop client
│   │   │   ├── frontend/
│   │   │   ├── src/                    # Rust/SQLite core
│   │   │   └── src-tauri/
│   │   │
│   │   ├── tests/                      # Formint test suites
│   │   │   └── pos-e2e/                # Cross-edition E2E tests
│   │   ├── brandkit/                   # Logo assets, colors, icons
│   │   ├── docs/                       # Documentation
│   │   ├── package.json                # Root workspace package for Formint
│   │   ├── Makefile                    # Product-specific targets
│   │   └── AGENTS.md
│   │
│   ├── assets/                         # Existing monorepo shared assets
│   │   ├── theme/                      # 15+ themes (includes pos/)
│   │   │   ├── pos/                    # POS-specific theme assets
│   │   │   │   ├── tokens/
│   │   │   │   ├── components/
│   │   │   │   ├── design-systems/
│   │   │   │   └── templates/
│   │   │   ├── default/
│   │   │   ├── enterprise/
│   │   │   └── _index.scss
│   │   └── ...
│   │
│   ├── webpack/                        # Existing shared webpack configs
│   ├── configs/                        # Shared Django settings
│   └── Makefile                        # Existing dispatcher
│
├── libs/                               # Existing libraries (not part of this plan)
│   ├── django-fusion/                  # Shared Django/Wagtail framework
│   │   ├── src/django_fusion/
│   │   ├── js/fusion-js/               # Shared TypeScript library
│   │   └── AGENTS.md
│   └── ...                             # Future libs extracted in separate plan
│
├── tests/                              # Shared test fixtures
├── docs/                               # Repository documentation
├── scripts/                            # Automation scripts
│
├── .github/                            # CI workflows
├── .agents/                            # Agent skills and MCP config
│   └── skills/
│       ├── structa-backend/            # Backend conventions
│       ├── structa-doc-authoring/      # Documentation conventions
│       ├── structa-industrial-ui/      # Industrial UI design system
│       ├── planinc-skill/              # PlanInc-specific skill
│       └── formint-skill/              # Formint-specific skill
│
├── Makefile                            # Root deployment dispatcher
├── pyproject.toml                      # Root Python workspace
├── nx.json                             # Nx workspace config
├── package.json                        # Root workspace package
├── bunfig.toml                         # Bun workspace configuration
├── turbo.json                          # Turborepo pipeline config
└── AGENTS.md                           # Repository-wide instructions
```

---

## 3. Naming Conventions

### 3.1 Directory Renames

| Old Name | New Name | Location |
|---|---|---|
| `projects/formints/` | `projects/formint-dev/` | Main Formint project directory |
| `formint-community/` | `formint/` | Rust/SQLite desktop edition |

### 3.2 Edition Names

| Edition | Directory | Stack | Notes |
|---|---|---|---|
| Formint (main) | `formint-dev/formint/` | React + HeroUI + Rust/SQLite + Tauri v2 | Desktop, offline-first |
| Formint Pro | `formint-dev/formint-pro/` | React + HeroUI + Django + PostgreSQL | Professional features |
| Formint Standard | `formint-dev/formint-standard/` | React + HeroUI + Django + PostgreSQL | Core POS features |
| Formint Cloud | `formint-dev/formint-cloud/` | React + HeroUI + Django + PostgreSQL | Cloud-hosted, API-first |
| Formint Client | `formint-dev/formint-client/` | React + HeroUI + Rust/SQLite + Tauri v2 | Desktop-focused |

### 3.3 Naming Rules

- All product directories use **lowercase with hyphens** (`planinc`, `formint-dev`, `formint-pro`)
- All edition directories use **lowercase with hyphens** (`formint`, `formint-pro`, `formint-standard`)
- All library directories use **lowercase with hyphens** (`django-fusion`)
- No uppercase letters in directory names
- The main Formint product directory is `formint-dev/` (not `formints/`)

---

## 4. Updated Path References (All Commands and Environment)

### 4.1 Root Makefile (`/home/Makefile`)

```makefile
# ── Product selectors ──
PRODUCT ?= all
PLANINC_DIR := projects/planinc
FORMINT_DEV_DIR := projects/formint-dev

# ── PlanInc targets ──
.PHONY: planinc planinc-dev planinc-build planinc-test planinc-deploy planinc-down planinc-logs planinc-status

planinc: planinc-dev

planinc-dev:
	cd $(PLANINC_DIR) && bun run dev

planinc-build:
	cd $(PLANINC_DIR) && bun run build:web && cd $(PLANINC_DIR)/frontend && bun run tauri:desktop:build

planinc-test:
	cd $(PLANINC_DIR) && bun run test

planinc-deploy: planinc-build
	cd $(PLANINC_DIR) && docker compose up -d

planinc-down:
	cd $(PLANINC_DIR) && docker compose down

planinc-logs:
	cd $(PLANINC_DIR) && docker compose logs -f

planinc-status:
	cd $(PLANINC_DIR) && docker compose ps

# ── Formint targets ──
.PHONY: formint-dev formint-dev-check formint-dev-test formint-dev-build formint-dev-deploy \
        formint formint-pro formint-standard formint-cloud formint-client \
        formint-dev-check-all formint-dev-test-all

formint-dev: formint-check

formint-check:
	cd $(FORMINT_DEV_DIR) && make check-all

formint-dev-test:
	cd $(FORMINT_DEV_DIR) && make test-all

formint-dev-build:
	cd $(FORMINT_DEV_DIR) && make build-all

formint-dev-deploy: formint-dev-build
	cd $(FORMINT_DEV_DIR) && make deploy-all

# Individual edition targets
formint:
	cd $(FORMINT_DEV_DIR)/formint && make dev

formint-pro:
	cd $(FORMINT_DEV_DIR)/formint-pro && make dev

formint-standard:
	cd $(FORMINT_DEV_DIR)/formint-standard && make dev

formint-cloud:
	cd $(FORMINT_DEV_DIR)/formint-cloud && make dev

formint-client:
	cd $(FORMINT_DEV_DIR)/formint-client && make dev

formint-dev-check-all:
	@for edition in formint pro standard cloud client; do \
		echo "==> Checking formint-$$edition"; \
		cd $(FORMINT_DEV_DIR)/formint-$$edition && make check || exit 1; \
	done

formint-dev-test-all:
	@for edition in formint pro standard cloud client; do \
		echo "==> Testing formint-$$edition"; \
		cd $(FORMINT_DEV_DIR)/formint-$$edition && make test || exit 1; \
	done

# ── Unified workspace targets ──
.PHONY: all-check all-test all-build all-deploy all-clean all-clean-unused

all-check: planinc-check formint-dev-check
	@echo "✅ All products pass checks"

all-test: planinc-test formint-dev-test
	@echo "✅ All product tests pass"

all-build: planinc-build formint-dev-build
	@echo "✅ All products built"

all-deploy: planinc-deploy formint-dev-deploy
	@echo "✅ All products deployed"

all-clean: planinc-down formint-dev-down
	@echo "✅ All products stopped"

all-clean-unused: planinc-clean-unused formint-dev-clean-unused
	@echo "✅ All products cleaned"
```

### 4.2 Formint Product Makefile (`projects/formint-dev/Makefile`)

```makefile
SHELL := /bin/bash
PRODUCT := formint-dev

.PHONY: help check check-all test test-all build build-all deploy deploy-all \
        dev dev:formint dev:pro dev:standard dev:cloud dev:client \
        clean clean-unused down status logs install \
        formint-* pro-* standard-* cloud-* client-*

help:
	@echo 'Formint commands (make TARGET)'
	@echo '  check          - Run checks for all editions'
	@echo '  check-all      - Check each edition individually'
	@echo '  test           - Run tests for all editions'
	@echo '  test-all       - Test each edition individually'
	@echo '  build          - Build all editions'
	@echo '  build-all      - Build each edition individually'
	@echo '  dev            - Start all editions'
	@echo '  dev:formint    - Formint edition (Rust/SQLite)'
	@echo '  dev:pro        - Pro edition (Python/Django)'
	@echo '  dev:standard   - Standard edition (Python/Django)'
	@echo '  dev:cloud      - Cloud edition (Python/Django)'
	@echo '  dev:client     - Client edition (Tauri/Rust)'
	@echo '  deploy         - Deploy all editions'
	@echo '  clean          - Stop all editions (volumes kept)'
	@echo '  clean-unused   - Full cleanup'
	@echo '  status         - Show all edition status'
	@echo '  logs           - Tail logs from all editions'

check:
	@$(MAKE) check-all

check-all:
	@for edition in formint pro standard cloud client; do \
		echo "==> Checking formint-$$edition"; \
		cd $$edition && $(MAKE) check || exit 1; \
	done

test:
	@$(MAKE) test-all

test-all:
	@for edition in formint pro standard cloud client; do \
		echo "==> Testing formint-$$edition"; \
		cd $$edition && $(MAKE) test || exit 1; \
	done

build:
	@$(MAKE) build-all

build-all:
	@for edition in formint pro standard cloud client; do \
		echo "==> Building formint-$$edition"; \
		cd $$edition && $(MAKE) build || exit 1; \
	done

dev:
	@$(MAKE) dev-all

dev-all:
	@for edition in formint pro standard cloud client; do \
		echo "==> Starting formint-$$edition"; \
		cd $$edition && $(MAKE) dev & \
	done; wait

dev:formint:
	cd formint && $(MAKE) dev

dev:pro:
	cd formint-pro && $(MAKE) dev

dev:standard:
	cd formint-standard && $(MAKE) dev

dev:cloud:
	cd formint-cloud && $(MAKE) dev

dev:client:
	cd formint-client && $(MAKE) dev

formint-*:
	cd formint && $(MAKE) $(word 2,$(MAKECMDGOALS))

pro-*:
	cd formint-pro && $(MAKE) $(word 2,$(MAKECMDGOALS))

standard-*:
	cd formint-standard && $(MAKE) $(word 2,$(MAKECMDGOALS))

cloud-*:
	cd formint-cloud && $(MAKE) $(word 2,$(MAKECMDGOALS))

client-*:
	cd formint-client && $(MAKE) $(word 2,$(MAKECMDGOALS))

deploy:
	@$(MAKE) deploy-all

deploy-all:
	@for edition in formint pro standard cloud client; do \
		echo "==> Deploying formint-$$edition"; \
		cd $$edition && $(MAKE) deploy || exit 1; \
	done

clean:
	@for edition in formint pro standard cloud client; do \
		cd $$edition && $(MAKE) clean; \
	done

clean-unused: clean
	@docker container prune -f 2>/dev/null || true
	@docker image prune -af 2>/dev/null || true

status:
	@for edition in formint pro standard cloud client; do \
		echo "==> Status for formint-$$edition"; \
		cd $$edition && $(MAKE) status || true; \
	done

logs:
	@for edition in formint pro standard cloud client; do \
		echo "==> Logs for formint-$$edition"; \
		cd $$edition && $(MAKE) logs || true; \
	done

install:
	@for edition in formint pro standard cloud client; do \
		echo "==> Installing formint-$$edition"; \
		cd $$edition && $(MAKE) install || true; \
	done
```

### 4.3 Root Makefile Integration Points

```makefile
# Add to existing .PHONY list:
.PHONY: ... planinc planinc-dev planinc-build planinc-test planinc-deploy \
        formint-dev formint-dev-check formint-dev-test formint-dev-build formint-dev-deploy \
        formint formint-pro formint-standard formint-cloud formint-client \
        formint-dev-check-all formint-dev-test-all ...

# Add to existing deploy targets:
deploy: deploy-all
deploy-all: deploy-databases deploy-coder deploy-media deploy-app deploy-tasks deploy-docs deploy-proxy
	$(MAKE) planinc-deploy
	$(MAKE) formint-dev-deploy

# Add to existing check/test targets:
check-all:
	$(MAKE) -C structa.cloud check
	$(MAKE) -C loop-crm check
	$(MAKE) -C $(PLANINC_DIR) check
	$(MAKE) -C $(FORMINT_DEV_DIR) formint-dev-check-all

test-all:
	$(MAKE) -C structa.cloud test
	$(MAKE) -C loop-crm test
	$(MAKE) -C $(PLANINC_DIR) test
	$(MAKE) -C $(FORMINT_DEV_DIR) formint-dev-test-all
```

### 4.4 Justfile Integration (`/home/Justfile`)

```justfile
# ── PlanInc ──
planinc := "cd projects/planinc &&"
planinc-dev:
    {{planinc}} bun run dev
planinc-build:
    {{planinc}} bun run build:web && {{planinc}} cd frontend && bun run tauri:desktop:build
planinc-test:
    {{planinc}} bun run test
planinc-deploy:
    {{planinc}} make deploy
planinc-clean:
    {{planinc}} make clean

# ── Formint ──
formint-dev := "cd projects/formint-dev &&"
formint-dev-check:
    {{formint-dev}} make check-all
formint-dev-test:
    {{formint-dev}} make test-all
formint-dev-build:
    {{formint-dev}} make build-all
formint-dev-deploy:
    {{formint-dev}} make deploy-all
formint:
    cd projects/formint-dev/formint && make dev
formint-pro:
    cd projects/formint-dev/formint-pro && make dev
formint-cloud:
    cd projects/formint-dev/formint-cloud && make dev

# ── Unified ──
check-all:
    just planinc-check
    just formint-dev-check
test-all:
    just planinc-test
    just formint-dev-test
deploy-all:
    just planinc-deploy
    just formint-dev-deploy
```

### 4.5 Developer Workflow Commands

#### PlanInc Development
```bash
cd projects/planinc
bun install
make dev
cd frontend && bun run dev:frontend   # Vite dev server on :5173
cd backend && bun run dev:backend      # Express + tRPC on :1111
cd frontend && bun run tauri:dev       # Tauri desktop app
```

#### Formint Development
```bash
cd projects/formint-dev

# Formint main edition (Rust/SQLite desktop)
cd formint
bun install
cargo build
bun run tauri:dev

# Pro edition (Python/Django)
cd formint-pro
uv sync
make dev
cd frontend && bun install
bun run dev:frontend

# Standard edition
cd formint-standard
uv sync
make dev

# Cloud edition
cd formint-cloud
uv sync
make dev

# Client edition (Tauri/Rust)
cd formint-client
cargo build
bun run tauri:dev
```

### 4.6 Environment Variables

All environment files reference the new paths:

```bash
# Root .env references
FORMINT_DIR=projects/formint-dev
FORMINT_EDITION=formint
PLANINC_DIR=projects/planinc

# Formint edition environment
FORMINT_MAIN_DIR=projects/formint-dev/formint
FORMINT_PRO_DIR=projects/formint-dev/formint-pro
FORMINT_STANDARD_DIR=projects/formint-dev/formint-standard
FORMINT_CLOUD_DIR=projects/formint-dev/formint-cloud
FORMINT_CLIENT_DIR=projects/formint-dev/formint-client
```

---

## 5. Workspace Configuration

### 5.1 Bun Workspaces (`/home/bunfig.toml`)

```toml
[install]
path = "bun.lock"

[workspace]
members = [
  "libs/*",
  "projects/planinc",
  "projects/planinc/frontend",
  "projects/planinc/backend",
  "projects/formint-dev",
  "projects/formint-dev/formint",
  "projects/formint-dev/formint/frontend",
  "projects/formint-dev/formint-pro",
  "projects/formint-dev/formint-pro/frontend",
  "projects/formint-dev/formint-standard",
  "projects/formint-dev/formint-cloud",
  "projects/formint-dev/formint-client",
  "projects/assets",
  "projects/webpack"
]

[resolution]
"@heroui/react" = "2.8.0-beta.1"
"react" = "18.3.1"
"react-dom" = "18.3.1"
"i18next" = "^25.6.0"
"mobx" = "^6.15.0"
```

### 5.2 Root Package.json (`/home/package.json`)

```json
{
  "name": "structa-cloud",
  "private": true,
  "workspaces": [
    "libs/*",
    "projects/planinc/*",
    "projects/formint-dev/*",
    "projects/assets",
    "projects/webpack"
  ]
}
```

### 5.3 Turborepo Pipeline (`/home/turbo.json`)

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*", "**/package.json", "**/bun.lock"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^lint"]
    },
    "test": {
      "dependsOn": ["^test"]
    },
    "check": {
      "dependsOn": ["lint", "typecheck"]
    },
    "typecheck": {
      "dependsOn": ["^build"]
    }
  }
}
```

### 5.4 Product package.json References

Each product's `package.json` uses `workspace:*` for its own sub-packages. Example for `projects/formint-dev/formint/package.json`:

```json
{
  "name": "@formint/main",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "tauri:dev": "tauri dev",
    "tauri:build": "tauri build"
  },
  "dependencies": {
    "@heroui/react": "2.8.0-beta.1",
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "i18next": "^25.6.0",
    "mobx": "^6.15.0"
  }
}
```

### 5.5 Bun Workspace Validation

Run `bun install --check` to verify all workspace references resolve correctly. No symlinks are used — Bun resolves workspace packages automatically.

---

## 6. Proposed Directory Tree (Consolidated View)

```
/home/
│
├── .agents/
│   └── skills/
│       ├── structa-backend/
│       ├── structa-doc-authoring/
│       ├── structa-industrial-ui/
│       ├── planinc-skill/
│       └── formint-skill/
│
├── libs/                               # Existing libraries only
│   ├── django-fusion/
│   │   ├── src/django_fusion/
│   │   ├── js/fusion-js/
│   │   └── AGENTS.md
│   └── ...                             # Shared libs extracted in separate plan
│
├── projects/
│   ├── assets/                         # Existing monorepo shared assets
│   │   ├── theme/
│   │   └── ...
│   ├── configs/                        # Shared Django settings
│   ├── webpack/                        # Shared webpack configs
│   │
│   ├── planinc/                        # PlanInc product
│   │   ├── backend/
│   │   ├── frontend/
│   │   │   ├── src/
│   │   │   │   ├── components/
│   │   │   │   ├── hooks/
│   │   │   │   ├── platform/
│   │   │   │   ├── store/
│   │   │   │   ├── pages/
│   │   │   │   └── App.tsx
│   │   │   ├── src-tauri/
│   │   │   ├── tauri-plugin-planinc/
│   │   │   └── package.json
│   │   ├── planinc-types/
│   │   ├── runtime/
│   │   ├── brandkit/
│   │   ├── docs/
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile
│   │   ├── Makefile
│   │   ├── package.json
│   │   ├── turbo.json
│   │   ├── bun.lock
│   │   └── AGENTS.md
│   │
│   └── formint-dev/                    # Formint POS product (renamed from formints/)
│       ├── formint/                    # Rust/SQLite desktop (renamed from formint-community/)
│       │   ├── frontend/
│       │   │   ├── src/
│       │   │   ├── src-tauri/
│       │   │   ├── tauri-plugin-formint/
│       │   │   ├── package.json
│       │   │   └── vite.config.ts
│       │   ├── src/
│       │   ├── Cargo.toml
│       │   └── Makefile
│       │
│       ├── formint-pro/
│       │   ├── backend/
│       │   │   ├── apps/
│       │   │   ├── settings/
│       │   │   ├── manage.py
│       │   │   ├── Dockerfile
│       │   │   └── requirements.txt
│       │   ├── frontend/
│       │   │   ├── src/
│       │   │   ├── templates/
│       │   │   └── assets/
│       │   └── package.json
│       │
│       ├── formint-standard/
│       │   ├── backend/
│       │   ├── frontend/
│       │   └── package.json
│       │
│       ├── formint-cloud/
│       │   ├── backend/
│       │   ├── frontend/
│       │   └── package.json
│       │
│       ├── formint-client/
│       │   ├── frontend/
│       │   ├── src/
│       │   └── src-tauri/
│       │
│       ├── tests/
│       │   └── pos-e2e/
│       ├── brandkit/
│       ├── docs/
│       ├── package.json
│       ├── Makefile
│       └── AGENTS.md
│
├── tests/                              # Shared test fixtures
├── docs/                               # Repository documentation
├── scripts/                            # Automation scripts
├── .github/                            # CI workflows
├── Justfile                            # Root Justfile
├── Makefile                            # Root deployment dispatcher
├── nx.json                             # Nx workspace config
├── pyproject.toml                      # Root Python workspace
├── package.json                        # Root workspace package
├── bunfig.toml                         # Bun workspace configuration
├── turbo.json                          # Turborepo pipeline config
└── AGENTS.md                           # Repository-wide instructions
```

---

## 7. Addressing Missing Formint Source Code

### 7.1 Current Situation

Formint source code does not exist on the filesystem. The monorepo references `projects/formints/` in:
- Root `Makefile`: `POS_DIR := projects/formints` (to be updated to `projects/formint-dev`)
- Root `Makefile`: `make check-formints`, `make test-formints`, `make community-*`, `make pro-*`, etc. (to be renamed)
- `projects/Makefile`: `website-formints` target

### 7.2 Action Plan

**Phase 1: Scaffold and Rename (immediate)**
```bash
# Rename existing formints directory if it exists
mv projects/formints projects/formint-dev 2>/dev/null || true

# Rename formint-community to formint
mv projects/formint-dev/formint-community projects/formint-dev/formint 2>/dev/null || true

# Create the full directory structure
mkdir -p projects/formint-dev/{formint/frontend/src,formint/src-tauri,formint/src,formint-pro/backend/apps,formint-pro/frontend/src,formint-standard/backend/apps,formint-standard/frontend/src,formint-cloud/backend/apps,formint-cloud/frontend/src,formint-client/frontend/src,formint-client/src,tests/pos-e2e,brandkit,docs}
```

**Phase 2: Populate from PlanInc patterns**

Since Formint shares the same patterns as PlanInc, scaffold each edition by:

1. **Copy PlanInc's frontend structure** as the template for each Formint edition's frontend
2. **Adapt PlanInc's `tauri-plugin-planinc`** as the template for `tauri-plugin-formint`
3. **Create Django backends** for Pro/Standard/Cloud editions using `libs/django-fusion/` patterns
4. **Create Rust backends** for Formint/Client editions using PlanInc's `src-tauri/` as template

**Phase 3: Connect to existing infrastructure**

1. Update root `Makefile` to use `projects/formint-dev` instead of `projects/formints`
2. Update `projects/Makefile` to include Formint targets with new names
3. Register Formint themes in `projects/assets/theme/`
4. Add Formint to the Nx workspace
5. Update all CI paths to reference `formint-dev` and `formint`

**Phase 4: Separate Plan for Shared Code**

Shared libraries, design tokens, UI components, and Tauri plugin cores are extracted in a separate plan document. This plan does not define those structures.

### 7.3 Formint Edition Specifications

| Edition | Directory | Frontend | Backend | Database | Desktop | Notes |
|---|---|---|---|---|---|---|
| Formint (main) | `formint-dev/formint/` | React + HeroUI | Rust | SQLite | Tauri v2 | Desktop, offline-first |
| Pro | `formint-dev/formint-pro/` | React + HeroUI | Django | PostgreSQL | Optional | Professional features |
| Standard | `formint-dev/formint-standard/` | React + HeroUI | Django | PostgreSQL | Optional | Core POS features |
| Cloud | `formint-dev/formint-cloud/` | React + HeroUI | Django | PostgreSQL | No | Cloud-hosted, API-first |
| Client | `formint-dev/formint-client/` | React + HeroUI | Rust | SQLite | Tauri v2 | Desktop-focused |

---

## 8. Migration Checklist

### Phase 1: Scaffold and Rename

- [ ] Rename `projects/formints/` → `projects/formint-dev/`
- [ ] Rename `formint-community/` → `formint/`
- [ ] Update root `Makefile`: `POS_DIR := projects/formint-dev`
- [ ] Update all `formint-*` make targets to use `formint-dev` paths
- [ ] Update Justfile with new paths
- [ ] Create all 5 Formint edition directories with package.json and Makefile

### Phase 2: Move PlanInc into Monorepo

- [ ] Move `/home/application/tools/PlanInc/` → `projects/planinc/`
- [ ] Update all internal paths in PlanInc configuration files
- [ ] Create `projects/planinc/Makefile`
- [ ] Add PlanInc to root Makefile and Justfile

### Phase 3: Infrastructure Updates

- [ ] Update `bunfig.toml` workspace members to use `projects/formint-dev/*`
- [ ] Update `package.json` workspaces array
- [ ] Update `nx.json` to include both products
- [ ] Update `projects/Makefile` dispatcher
- [ ] Update CI workflow paths

### Phase 4: Agent Skills and Documentation

- [ ] Create `projects/planinc/AGENTS.md`
- [ ] Create `projects/formint-dev/AGENTS.md`
- [ ] Create `.agents/skills/planinc-skill/`
- [ ] Create `.agents/skills/formint-skill/`

### Phase 5: Shared Code (Separate Plan)

- [ ] Shared UI components → separate plan
- [ ] Shared design tokens → separate plan
- [ ] Shared Tauri plugin → separate plan
- [ ] Cross-edition shared types → separate plan
- [ ] All shared library extraction handled in separate document

---

## 9. Path Reference Summary

All paths in this document use the following canonical names:

| Product | Base Path | Edition Path Example |
|---|---|---|
| PlanInc | `projects/planinc/` | `projects/planinc/frontend/` |
| Formint (main) | `projects/formint-dev/` | `projects/formint-dev/formint/` |
| Formint Pro | `projects/formint-dev/` | `projects/formint-dev/formint-pro/` |
| Formint Standard | `projects/formint-dev/` | `projects/formint-dev/formint-standard/` |
| Formint Cloud | `projects/formint-dev/` | `projects/formint-dev/formint-cloud/` |
| Formint Client | `projects/formint-dev/` | `projects/formint-dev/formint-client/` |

### Shell Environment Variables

```bash
# Set active product
export PRODUCT=planinc          # or: export PRODUCT=formint-dev

# Set active Formint edition
export FORMINT_EDITION=formint  # or: pro, standard, cloud, client

# Quick navigation
alias pc='cd projects/planinc'
alias fd='cd projects/formint-dev'
alias ff='cd projects/formint-dev/formint'
alias fp='cd projects/formint-dev/formint-pro'
```

---

## 9. Responsive Design Token System

### 9.1 Overview

The PlanInc design token system now includes responsive border-radius, edge-rounding, curves, and motion timing that scale across the 8-tier responsive system (xs 360px → 4xl 2560px).

All responsive values are gated on `html[data-tier="..."]` attributes (defined in `src/platform/responsive.ts` and mirrored in `styles/platform.css`).

### 9.2 Responsive Border-Radius Scale

| Token | xs (360px) | sm (480px) | md (768px) | lg (1024px) | xl (1280px) | 2xl (1600px) | 3xl (1920px) | 4xl (2560px) |
|---|---|---|---|---|---|---|---|---|
| `--radius` | 0.375rem | 0.4rem | 0.45rem | 0.5rem | 0.55rem | 0.625rem | 0.7rem | 0.8rem |
| `--pi-radius-sm` | 2px | 3px | 4px | 5px | 6px | 7px | 8px | 9px |
| `--pi-radius-md` | 4px | 5px | 6px | 7px | 8px | 9px | 10px | 12px |
| `--pi-radius-lg` | 6px | 7px | 8px | 9px | 10px | 11px | 12px | 14px |
| `--pi-radius-xl` | 8px | 9px | 10px | 12px | 14px | 16px | 18px | 20px |
| `--pi-radius-2xl` | 12px | 13px | 14px | 16px | 18px | 20px | 22px | 24px |
| `--pi-radius-3xl` | 16px | 17px | 18px | 20px | 22px | 24px | 26px | 28px |

### 9.3 Responsive Component Edge Attributes

| Attribute | xs | md | lg | 4xl |
|---|---|---|---|---|
| `--chip-radius` | 4px | 6px | 7px | 12px |
| `--contextmenu-radius` | 10px | 14px | 16px | 24px |
| `--contextmenu-item-radius` | 6px | 10px | 12px | 20px |
| `--card-radius` | var(--pi-radius-md) | var(--pi-radius-lg) | var(--pi-radius-xl) | var(--pi-radius-3xl) |
| `--surface-radius` | var(--pi-radius-sm) | var(--pi-radius-md) | var(--pi-radius-lg) | var(--pi-radius-3xl) |
| `--modal-radius` | var(--pi-radius-lg) | var(--pi-radius-2xl) | var(--pi-radius-3xl) | calc(var(--pi-radius-3xl) * 1.6) |
| `--sheet-radius` | var(--pi-radius-xl) | var(--pi-radius-3xl) | var(--pi-radius-3xl) | calc(var(--pi-radius-3xl) * 1.6) |
| `--input-radius` | var(--pi-radius-sm) | var(--pi-radius-md) | var(--pi-radius-md) | var(--pi-radius-md) |
| `--button-radius` | var(--pi-radius-sm) | var(--pi-radius-md) | var(--pi-radius-md) | var(--pi-radius-lg) |
| `--scrollbar-radius` | 2px | 2px | 2px | 2px |

### 9.4 Responsive Motion Curves

| Tier | `--motion-fast` | `--motion-base` | `--curve-enter` | `--curve-exit` |
|---|---|---|---|---|
| xs | 150ms | 250ms | `cubic-bezier(0.4,0,0.2,1)` | `cubic-bezier(0.4,0,0.2,1)` |
| sm | 150ms | 300ms | `cubic-bezier(0.16,1,0.3,1)` | `cubic-bezier(0.4,0,0.2,1)` |
| md | 200ms | 350ms | `cubic-bezier(0.16,1,0.3,1)` | `cubic-bezier(0.4,0,0.2,1)` |
| lg | 200ms | 400ms | `cubic-bezier(0.16,1,0.3,1)` | `cubic-bezier(0.4,0,0.2,1)` |
| xl | 250ms | 450ms | `cubic-bezier(0.16,1,0.3,1)` | `cubic-bezier(0.4,0,0.2,1)` |
| 2xl | 250ms | 500ms | `cubic-bezier(0.16,1,0.3,1)` | `cubic-bezier(0.4,0,0.2,1)` |
| 3xl/4xl | 300ms | 550ms | `cubic-bezier(0.16,1,0.3,1)` | `cubic-bezier(0.4,0,0.2,1)` |

### 9.5 Additional Curve Variables

- `--curve-sharp`: `cubic-bezier(0.4, 0, 0.2, 1)` — instant transitions
- `--curve-smooth`: `cubic-bezier(0.16, 1, 0.3, 1)` — smooth entrance (default)
- `--curve-bounce`: `cubic-bezier(0.34, 1.56, 0.64, 1)` — bounce effect
- `--curve-elastic`: `cubic-bezier(0.68, -0.55, 0.265, 1.55)` — elastic overshoot

### 9.6 Files Modified

- `src/frontend/src/styles/tokens.css` — Added responsive edge/curve/radius system (tier 4)
- `src/frontend/src/styles/globals.css` — Updated `.planinc-tag`, `.contextmenu`, `.mermaid-wrapper`, `.echarts-wrapper`, `::-webkit-scrollbar-thumb` to use responsive attributes
- `src/frontend/src/styles/platform.css` — Updated `.pi-mobile-header` border-radius to use `--card-radius`
- `src/frontend/tailwind.config.js` — Added responsive radius comment and HeroUI layout notes

### 9.7 Rules

1. All border-radius values reference CSS custom properties — never hardcoded pixel values in component CSS
2. Responsive overrides use `html[data-tier="..."]` attribute selectors (not media queries)
3. Each tier only overrides radii that change; smaller tiers inherit from base
4. Dark mode remaps are in `.dark` and do not affect responsive scaling
5. `prefers-reduced-motion` always overrides responsive motion values

---

## 10. FlyonUI Integration (Optional Replacement for HeroUI)

### 10.1 Overview

FlyonUI (`flyonui` npm v2.4.1) has been added as a Tailwind CSS v4 plugin in PlanInc as a potential replacement for `@heroui/react` (v2.8.0-beta.1). It provides 80+ semantic-class components, 800+ examples, built-in headless JS plugins, MIT licensing, and full Tailwind v4 compatibility.

### 10.2 What FlyonUI Replaces

| Current Package | FlyonUI Replacement | Status |
|---|---|---|
| `@heroui/react` (^2.8.0) | `flyonui` | ✅ Added to package.json |
| `@heroui/dropdown` (^2.3.27) | FlyonUI dropdown plugin | ✅ Covered |
| `@heroui/popover` (^2.3.27) | FlyonUI overlay/modal | ✅ Covered |
| `@headlessui/tailwindcss` (^0.2.2) | FlyonUI headless plugins | ✅ Covered |
| `tailwindcss-animate` (^1.0.7) | FlyonUI built-in animations | ✅ Covered |
| `rctx-contextmenu` (^1.4.1) | FlyonUI context menu | ✅ Covered |

### 10.3 What FlyonUI Does NOT Replace

- `tailwindcss` (^4.1.4) — FlyonUI is a plugin for Tailwind, not a replacement
- `framer-motion` (^11.0.0) / `motion` (^12.7.3) — Advanced animation library
- `react-masonry-css` (^1.0.16) — No masonry in FlyonUI
- `clsx` (^2.1.1) / `tailwind-merge` (^3.3.1) — Class utility helpers
- `autoprefixer`, `@tailwindcss/vite`, `@tailwindcss/typography` — Build tooling
- `next-themes` (^0.4.6) — Theme switching utility
- `echarts`, `mermaid`, `katex` — Specialized chart/math libraries
- `@iconify/react` — Icon library
- Tauri plugins

### 10.4 Configuration Changes Made

**`src/frontend/package.json`:**
- Added `"flyonui": "^2.4.1"` to both `dependencies` and `devDependencies`

**`src/frontend/tailwind.config.js`:**
- Added `const flyonui = require('flyonui/plugin')`
- Added `flyonui` to `plugins` array
- Added `'../node_modules/flyonui/dist/**/*.{js,ts,jsx,tsx}'` to `content` array

**`src/frontend/src/styles/globals.css`:**
- Added `@plugin "flyonui"` after `@import "tailwindcss"`
- Added `@import "flyonui/variants.css"` for variant support

### 10.5 Migration Strategy (Future)

1. **Phase 1 — Coexistence** (current): FlyonUI added alongside HeroUI; no components migrated yet
2. **Phase 2 — Component-by-component**: Replace HeroUI components with FlyonUI equivalents one-by-one, starting with Button, Card, Dropdown, Modal, Input, Navbar
3. **Phase 3 — Full removal**: Remove `@heroui/react`, `@heroui/dropdown`, `@heroui/popover`, `@headlessui/tailwindcss` once all components are migrated
4. **Phase 4 — Shared lib**: Extract shared UI components from FlyonUI into `libs/shared-ui-components/`

### 10.6 Rules

1. Do not remove HeroUI packages until all components using them are migrated
2. New components should prefer FlyonUI semantic classes over HeroUI classes
3. FlyonUI variants (`@import "flyonui/variants.css"`) must be imported before any component CSS
4. Test both HeroUI and FlyonUI side-by-side before full migration

---

## Appendix: Full Makefile Reference

### Root Makefile — Formint Targets (Updated)

```makefile
# ── Formint targets ──
.PHONY: formint-dev formint-dev-check formint-dev-test formint-dev-build formint-dev-deploy \
        formint formint-pro formint-standard formint-cloud formint-client \
        formint-dev-check-all formint-dev-test-all

formint-dev: formint-check

formint-check:
	cd $(FORMINT_DEV_DIR) && make check-all

formint-dev-test:
	cd $(FORMINT_DEV_DIR) && make test-all

formint-dev-build:
	cd $(FORMINT_DEV_DIR) && make build-all

formint-dev-deploy: formint-dev-build
	cd $(FORMINT_DEV_DIR) && make deploy-all

formint:
	cd $(FORMINT_DEV_DIR)/formint && make dev

formint-pro:
	cd $(FORMINT_DEV_DIR)/formint-pro && make dev

formint-standard:
	cd $(FORMINT_DEV_DIR)/formint-standard && make dev

formint-cloud:
	cd $(FORMINT_DEV_DIR)/formint-cloud && make dev

formint-client:
	cd $(FORMINT_DEV_DIR)/formint-client && make dev

formint-dev-check-all:
	@for edition in formint pro standard cloud client; do \
		echo "==> Checking formint-$$edition"; \
		cd $(FORMINT_DEV_DIR)/formint-$$edition && make check || exit 1; \
	done

formint-dev-test-all:
	@for edition in formint pro standard cloud client; do \
		echo "==> Testing formint-$$edition"; \
		cd $(FORMINT_DEV_DIR)/formint-$$edition && make test || exit 1; \
	done
```

### Root Makefile — PlanInc Targets (Unchanged)

```makefile
PLANINC_DIR := projects/planinc

.PHONY: planinc planinc-dev planinc-build planinc-test planinc-deploy planinc-down planinc-logs planinc-status

planinc: planinc-dev
planinc-dev:
	cd $(PLANINC_DIR) && bun run dev
planinc-build:
	cd $(PLANINC_DIR) && bun run build:web && cd $(PLANINC_DIR)/frontend && bun run tauri:desktop:build
planinc-test:
	cd $(PLANINC_DIR) && bun run test
planinc-deploy: planinc-build
	cd $(PLANINC_DIR) && docker compose up -d
planinc-down:
	cd $(PLANINC_DIR) && docker compose down
planinc-logs:
	cd $(PLANINC_DIR) && docker compose logs -f
planinc-status:
	cd $(PLANINC_DIR) && docker compose ps
```

### Root Makefile — Unified Targets

```makefile
.PHONY: all-check all-test all-build all-deploy all-clean all-clean-unused

all-check: planinc-check formint-dev-check
	@echo "✅ All products pass checks"

all-test: planinc-test formint-dev-test
	@echo "✅ All product tests pass"

all-build: planinc-build formint-dev-build
	@echo "✅ All products built"

all-deploy: planinc-deploy formint-dev-deploy
	@echo "✅ All products deployed"

all-clean: planinc-down formint-dev-down
	@echo "✅ All products stopped"

all-clean-unused: planinc-clean-unused formint-dev-clean-unused
	@echo "✅ All products cleaned"
```
