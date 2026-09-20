# Plan: Formint Source Code Scaffolding

## Status: Separate Plan · Version: 1.0 · Date: 2026-09-20

This plan covers scaffolding all 5 Formint editions from PlanInc patterns. Companion to the [Unified Development Organization Plan](../unified-dev-organization.md).

---

## Objective

Create the complete Formint source code structure under `projects/formint-dev/`, with all 5 editions populated using PlanInc as the template.

---

## Edition Structure

| Edition | Directory | Stack | Database | Desktop |
|---|---|---|---|---|
| Formint (main) | `formint-dev/formint/` | React + HeroUI + Rust | SQLite | Tauri v2 |
| Pro | `formint-dev/formint-pro/` | React + HeroUI + Django | PostgreSQL | Optional |
| Standard | `formint-dev/formint-standard/` | React + HeroUI + Django | PostgreSQL | Optional |
| Cloud | `formint-dev/formint-cloud/` | React + HeroUI + Django | PostgreSQL | No |
| Client | `formint-dev/formint-client/` | React + HeroUI + Rust | SQLite | Tauri v2 |

---

## Phase 1: Directory Scaffolding

### Commands

```bash
mkdir -p projects/formint-dev/
mkdir -p projects/formint-dev/formint/{frontend/src,frontend/src-tauri/src,frontend/tauri-plugin-formint/src,src}
mkdir -p projects/formint-dev/formint-pro/{backend/apps,frontend/src}
mkdir -p projects/formint-dev/formint-standard/{backend/apps,frontend/src}
mkdir -p projects/formint-dev/formint-cloud/{backend/apps,frontend/src}
mkdir -p projects/formint-dev/formint-client/{frontend/src,src-tauri/src,src}
mkdir -p projects/formint-dev/tests/pos-e2e/{formint,pro,standard,cloud,client}
mkdir -p projects/formint-dev/brandkit/{logo,colors,icons}
mkdir -p projects/formint-dev/docs
```

### Expected Directory Structure

```
projects/formint-dev/
├── formint/                          # Rust/SQLite desktop edition
│   ├── frontend/                     # React + HeroUI + Tauri
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── components/           # Product-specific components
│   │   │   ├── hooks/                # Product-specific hooks
│   │   │   ├── lib/
│   │   │   ├── pages/
│   │   │   ├── platform/
│   │   │   ├── store/                # MobX stores
│   │   │   ├── styles/
│   │   │   └── main.tsx
│   │   ├── src-tauri/                # Tauri v2 Rust shell
│   │   │   ├── src/
│   │   │   ├── Cargo.toml
│   │   │   ├── capabilities/
│   │   │   ├── icons/
│   │   │   └── tauri.conf.json
│   │   ├── tauri-plugin-formint/     # Custom Tauri plugin
│   │   ├── public/
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.js
│   │   └── tsconfig.json
│   │
│   ├── src/                          # Rust/SQLite core
│   │   ├── main.rs
│   │   ├── lib.rs
│   │   ├── db.rs
│   │   ├── models.rs
│   │   └── error.rs
│   ├── Cargo.toml
│   ├── Makefile
│   └── package.json
│
├── formint-pro/                      # Python/Django professional edition
│   ├── backend/
│   │   ├── apps/
│   │   ├── settings/
│   │   ├── manage.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── AGENTS.md
│   ├── frontend/
│   │   ├── src/
│   │   ├── templates/
│   │   └── assets/
│   ├── package.json
│   └── Makefile
│
├── formint-standard/                 # Python/Django standard edition
│   ├── backend/
│   ├── frontend/
│   ├── package.json
│   └── Makefile
│
├── formint-cloud/                    # Python/Django cloud master
│   ├── backend/
│   ├── frontend/
│   ├── package.json
│   └── Makefile
│
├── formint-client/                   # Tauri/Rust desktop client
│   ├── frontend/
│   │   ├── src/
│   │   └── package.json
│   ├── src/                          # Rust/SQLite core
│   ├── src-tauri/
│   ├── Cargo.toml
│   └── Makefile
│
├── tests/
│   └── pos-e2e/
│       ├── formint/
│       ├── pro/
│       ├── standard/
│       ├── cloud/
│       ├── client/
│       └── shared/
│
├── brandkit/
│   ├── logo/
│   ├── colors/
│   └── icons/
│
├── docs/
│   ├── getting-started.md
│   ├── architecture.md
│   ├── deployment.md
│   └── INDEX.md
│
├── package.json                      # Root workspace package
├── Makefile                          # Product-specific targets
└── AGENTS.md
```

---

## Phase 2: Populate from PlanInc Patterns

### 2.1 Formint Main Edition (`formint-dev/formint/`)

**Template source:** `projects/planinc/frontend/`

**Actions:**
1. Copy PlanInc's `frontend/src/` structure as the template
2. Adapt `frontend/src-tauri/` for SQLite instead of SurrealDB
3. Create `frontend/tauri-plugin-formint/` from PlanInc's `tauri-plugin-planinc/`
4. Replace PlanInc-specific components with Formint POS components
5. Update `package.json` with Formint-specific dependencies
6. Create `Cargo.toml` for Rust/SQLite core using `rusqlite`

**Key differences from PlanInc:**
- Backend uses SQLite (rusqlite) instead of SurrealDB
- Tauri plugin uses `tauri-plugin-formint` naming
- POS-specific UI components replace planning/ticket/study/graph components
- Formint brand colors replace PlanInc brand colors

### 2.2 Formint Pro (`formint-dev/formint-pro/`)

**Template source:** `projects/planinc/backend/` + `libs/django-fusion/`

**Actions:**
1. Create Django backend using `libs/django-fusion/` patterns
2. Create React + HeroUI + HTMX frontend
3. Set up PostgreSQL database configuration
4. Create `manage.py`, `settings/`, `apps/` structure
5. Create `requirements.txt` with Django dependencies
6. Create `Dockerfile` for deployment

**Key differences:**
- Django views use `django_fusion.routes.core.base.Viewset` pattern
- Frontend uses HTMX for server-rendered partials
- PostgreSQL instead of SQLite
- Professional features (reports, analytics, advanced settings)

### 2.3 Formint Standard (`formint-dev/formint-standard/`)

**Template source:** `projects/formint-dev/formint-pro/` (simplified)

**Actions:**
1. Copy `formint-pro` structure with reduced feature set
2. Remove professional-only features
3. Keep core POS functionality (sales, inventory, orders)
4. Same Django backend and React frontend
5. Same PostgreSQL database

**Key differences:**
- Reduced feature set vs Pro
- No advanced analytics or reporting
- Same core architecture

### 2.4 Formint Cloud (`formint-dev/formint-cloud/`)

**Template source:** `projects/formint-dev/formint-pro/` (API-first)

**Actions:**
1. Create Django backend serving API only
2. Create React + HeroUI frontend for web browser
3. No desktop/Tauri component
4. API-first architecture with REST/GraphQL endpoints
5. Cloud deployment configuration (Docker, Kubernetes)

**Key differences:**
- No Tauri desktop app
- No SQLite — PostgreSQL only
- API-first, cloud-hosted
- No local file system access

### 2.5 Formint Client (`formint-dev/formint-client/`)

**Template source:** `projects/formint-dev/formint/`

**Actions:**
1. Copy Formint main edition structure
2. Adapt for offline-first architecture
3. Enhanced local SQLite storage
4. Tauri v2 desktop shell
5. Service worker for offline capabilities

**Key differences:**
- Offline-first design
- Enhanced local storage
- Desktop-focused UX
- Same Rust/SQLite core as Formint main

---

## Phase 3: Shared Code Integration

### 3.1 Frontend Integration

Each Formint edition's frontend references the shared libraries from the [Shared Libraries Extraction Plan](./shared-libs-extraction-plan.md):

```json
// Example: formint-dev/formint/frontend/package.json
{
  "name": "@formint/main",
  "dependencies": {
    "@heroui/react": "2.8.0-beta.1",
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "i18next": "^25.6.0",
    "mobx": "^6.15.0"
  }
}
```

### 3.2 Tauri Plugin Integration

Each desktop edition creates its own Tauri plugin that depends on shared plugin core:

```bash
# Formint main edition
cd projects/formint-dev/formint/frontend
bun create tauri-plugin-formint

# Formint Client edition
cd projects/formint-dev/formint-client/frontend
bun create tauri-plugin-formint
```

### 3.3 Makefile Integration

Each edition gets a `Makefile` with standard targets:

```makefile
# Example: formint-dev/formint/Makefile
SHELL := /bin/bash
PRODUCT := formint
VERSION ?= 1.0.0

.PHONY: help dev build test clean check lint

help:
	@echo 'Formint main commands'

dev:
	cd frontend && bun run dev

build:
	cd frontend && bun run build
	cd src && cargo build --release

test:
	cd frontend && bun run test
	cd src && cargo test

clean:
	cd frontend && bun run clean
	cd src && cargo clean
```

---

## Phase 4: Cross-Edition E2E Tests

### Test Structure

```
projects/formint-dev/tests/pos-e2e/
├── shared/
│   ├── helpers.ts              # Shared test utilities
│   ├── fixtures.ts             # Test data fixtures
│   └── config.ts               # Test configuration
├── formint/
│   └── sales-flow.test.ts      # Formint-specific tests
├── pro/
│   └── order-management.test.ts
├── standard/
│   └── core-pos.test.ts
├── cloud/
│   └── api-integration.test.ts
├── client/
│   └── offline-mode.test.ts
```

### Cross-Edition Test Patterns

- **Shared tests:** Sales flow, inventory management, order processing
- **Edition-specific tests:** Desktop features (Formint, Client), API tests (Cloud), Django tests (Pro, Standard)
- **Shared fixtures:** Product data, user accounts, order templates

---

## Phase 5: Infrastructure Connection

### 5.1 Root Makefile Updates

Update `/home/Makefile` to include Formint targets:

```makefile
FORMINT_DEV_DIR := projects/formint-dev

.PHONY: formint-dev formint-dev-check formint-dev-test formint-dev-build formint-dev-deploy

formint-dev:
	cd $(FORMINT_DEV_DIR) && make check-all

formint-dev-check:
	@for edition in formint pro standard cloud client; do \
		cd $(FORMINT_DEV_DIR)/formint-$$edition && make check || exit 1; \
	done
```

### 5.2 Bun Workspace Integration

Add to `/home/bunfig.toml`:

```toml
[workspace]
members = [
  "projects/formint-dev",
  "projects/formint-dev/formint",
  "projects/formint-dev/formint/frontend",
  "projects/formint-dev/formint-pro",
  "projects/formint-dev/formint-pro/frontend",
  "projects/formint-dev/formint-standard",
  "projects/formint-dev/formint-cloud",
  "projects/formint-dev/formint-client",
]
```

### 5.3 Nx Workspace

Add to `nx.json`:

```json
{
  "projects": {
    "formint-dev": {
      "tags": ["type:product", "platform:web+desktop"]
    },
    "formint-pro": {
      "tags": ["type:product", "platform:web"]
    }
  }
}
```

### 5.4 Theme Integration

Register Formint's POS theme in `projects/assets/theme/`:

```
projects/assets/theme/pos/
├── _index.scss
├── tokens/_fu-pos-theme.scss
├── components/
├── design-systems/
└── templates/
```

---

## Phase 6: Documentation

### 6.1 Product Documentation

Create `projects/formint-dev/docs/`:

- `getting-started.md` — Quick start guide for all editions
- `architecture.md` — System architecture overview
- `deployment.md` — Deployment instructions for each edition
- `INDEX.md` — Documentation index

### 6.2 Agent Skills

Create `.agents/skills/formint-skill/`:

- Skill definition for Formint development patterns
- Template snippets for common Formint tasks
- Configuration presets for each edition

---

## Verification Checklist

### After Scaffolding

- [ ] All 5 edition directories exist under `projects/formint-dev/`
- [ ] Each edition has a `package.json` and `Makefile`
- [ ] Each desktop edition has `Cargo.toml` and `src-tauri/`
- [ ] Each Django edition has `backend/` with `manage.py`
- [ ] `bun install` works for all editions
- [ ] `make check` works for all editions
- [ ] Root Makefile has all Formint targets
- [ ] `bunfig.toml` workspace members include all editions
- [ ] No symlinks exist in the Formint directory structure

### After Population

- [ ] Formint main edition builds and runs (Tauri + SQLite)
- [ ] Formint Pro builds and runs (Django + PostgreSQL)
- [ ] Formint Cloud builds and runs (Django API-only)
- [ ] Cross-edition E2E tests pass
- [ ] Shared libraries are correctly referenced via `workspace:*`
- [ ] `bun install --check` passes

---

## License

AGPL-3.0
