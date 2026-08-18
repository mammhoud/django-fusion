# 🏛️ Project Structure — Complete Reference

> Full directory tree with remarks, references, customization guides, instance
> setup notes, and recommendations for how to use the latest structure.
> Generated: 2026-08-10 | Corrected: 2026-08-16 | Branch: `generic`

---

## Complete Project Tree

```text
structa.cloud/                              # Root: monorepo for Structa Cloud platform
│
├── AGENTS.md                               # 🔴 ROOT: Repository-wide AI agent instructions
│                                           #   - Product boundaries, name rules, safety
│                                           #   - Change checklist, commands, architecture
│                                           #   - READ FIRST before any code change
│
├── Makefile                                # Root deployment dispatcher
│                                           #   make deploy, deploy-databases, deploy-app, etc.
│
├── pyproject.toml                          # Root Python workspace (uv + pytest + ruff)
│
├── .gitmodules                             # Submodule definitions (django-fusion)
│
├── .github/                                # CI/CD workflows and composite actions
│   └── workflows/                          # GitHub Actions workflow files
│
├── docs/                                   # 📚 Documentation project
│   ├── docus/                              #   Docus Nuxt app and locale sources
│   ├── index.html                          #   Redirect to the Docus locale route
│   ├── README.md                           #   Documentation hub
│   ├── overview.md                         #   Repo overview + name migration reference
│   ├── project-structure.md                #   This file — canonical tree
│   ├── ARCHITECTURE.md                     #   Request lifecycle, components, tasks, MCP
│   ├── _sidebar.md                         #   Sidebar navigation
│   ├── recommendations.md                  #   Priority recommendations
│   ├── recent-changes.md                   #   Changelog / session log
│   ├── assets/                             #   📸 Documentation assets
│   ├── guides/                             #   📖 Step-by-step walkthroughs
│   ├── plans/                              #   🗺️ Canonical plan registry
│   │   ├── README.md                       #     Active plan index
│   │   ├── document-lifecycle.md           #     Status/archive/deletion policy
│   │   ├── deletion-manifest.md            #     Approval + rollback register
│   │   ├── marketing-claims.md             #     Evidence-backed claims register
│   │   ├── repository/                     #     Cross-repository plans
│   │   ├── editions/                       #     Formint edition chain (canonical)
│   │   ├── precis-landing/                 #     Landing site plans
│   │   ├── loop-crm/                       #     Loop-CRM merge + finance plans
│   │   └── django-fusion/                  #     Framework plans
│   ├── projects/                           #   📁 Per-project references
│   ├── ai/                                 #   🤖 AI agents & prompts
│   ├── dev/                                #   🛠️ Developer references
│   ├── auth/                               #   Auth documentation
│   ├── changelogs/                         #   Changelog files
│   ├── publish/                            #   Publishing & CI/CD
│   ├── features/                           #   Feature matrix
│   ├── fixtures/                           #   Fixture docs
│   ├── design/                             #   Design system
│   ├── shared/                             #   Shared methods
│   ├── tests/                              #   Testing docs
│   └── Dockerfile                          #   Standalone Docus static container
│
├── projects/                               # 🔵 All product code + shared Django config
│   ├── AGENTS.md                           #   Project-level conventions
│   ├── Makefile                            #   Canonical dispatcher (WEBSITE=)
│   ├── Makefile.md                         #   Dispatcher usage + aliases
│   ├── pyproject.toml                      #   Python workspace deps + pytest config
│   ├── manage.py                           #   Shared Django CLI entry
│   │
│   ├── precis/                             # 📘 Precis group — LMS, marketing, research
│   │   ├── main/                           #     Precis LMS (WEBSITE=precis-main)
│   │   │   ├── backend/                    #       Django + Wagtail backend
│   │   │   ├── assets/                     #       Templates, static, media
│   │   │   └── frontend/                   #       Astro frontend shell
│   │   ├── lnd-structa/                    #     Landing-Fusion (WEBSITE=precis-landing)
│   │   │   ├── backend/                    #       Django + Wagtail backend
│   │   │   ├── frontend/                   #       Astro 5 + Tailwind 4 frontend
│   │   │   └── assets/                     #       SCSS, compiled CSS
│   │   ├── lms-ctc/                        #     CTC Research (WEBSITE=precis-ctc)
│   │   │   ├── backend/                    #       Django + Wagtail backend
│   │   │   └── frontend/                   #       Frontend
│   │   ├── assets/                         #     Group-shared templates/static
│   │   └── configs/                        #     Shared Django settings (base, Env, settings)
│   │
│   ├── formints/                           # 💰 FORMINTS — Multi-edition POS platform
│   │   ├── AGENTS.md                       #     POS-wide agent instructions
│   │   ├── Makefile                        #     Edition dispatcher
│   │   ├── community/                      #     Community (offline-first Tauri + React + Rust)
│   │   ├── standard/                       #     Standard edition
│   │   ├── pro/                            #     Professional (Django + Astro + Tauri)
│   │   │   ├── server/                     #       Django/Robyn boundary, APIs
│   │   │   └── frontend/                   #       Astro + Alpine/HTMX shell
│   │   ├── cloud/                          #     Cloud master (Django + Channels)
│   │   │   ├── backend/                    #       Django backend + WebSocket
│   │   │   └── frontend/                   #       Cloud UI + dashboards
│   │   ├── client/                         #     POS Client (Tauri + Vue 3)
│   │   ├── packages/                       #     @formints/* SDK packages
│   │   ├── scripts/                        #     Build/release/dev tooling
│   │   ├── tests/                          #     Shared POS E2E + API tests
│   │   └── docs/                           #     POS architecture + screenshots
│   │
│   ├── syntara/                            # 🤖 SYNTARA — AI Chat/Customizer
│   │   ├── AGENTS.md                       #     Project agent instructions
│   │   ├── chat/                           #     Conversation, streaming, discovery
│   │   ├── templates/                      #     Base, components, fragments
│   │   ├── assets/                         #     Source JS/CSS + Webpack
│   │   ├── configs/                        #     YAML model/provider settings
│   │   └── Makefile
│   │
│   ├── loop-crm/                           # 🧩 LOOP-CRM — Unified CRM + social scheduling
│   │   ├── backend/                        #     Django + django-fusion modular monolith
│   │   │   └── apps/                       #       core, crm, marketing, attribution, finance, pos
│   │   ├── frontend/                       #     Astro 5 + Tailwind 4 + React islands
│   │   ├── docker-compose.yml              #     Django + Postgres + Redis + worker
│   │   └── Makefile
│   │
│   ├── assets/                            # 🎨 Shared static/templates/locale
│   ├── scripts/                           # 📜 Project-local automation
│   └── webpack/                           # 📦 Shared/legacy asset configuration
│
├── libs/                                  # 📚 Reusable libraries (submodules)
│   └── django-fusion/                     #   Shared Django/Wagtail components
│       ├── AGENTS.md                      #     Framework agent instructions
│       ├── src/django_fusion/             #     comp, tables, forms, fragments, routing, tasks, mcp
│       └── tests/                         #     Framework tests
│
├── applications/                          # 🏗️ Infrastructure + tooling
│   ├── AGENTS.md                          #   Infrastructure agent instructions
│   ├── proxy/                             #   Traefik reverse proxy configs
│   ├── databases/                         #   PostgreSQL + Redis compose
│   ├── agents/                            #   Kilo MCP server
│   ├── templates/                         #   Coder/Terraform templates
│   │   └── workspace/                     #     Coder template: mounted monorepo + AFFiNE devcontainer
│   └── scripts/                           #   Automation scripts
│
├── tests/                                 # 🧪 Workspace integration tests
│   ├── AGENTS.md                          #   Workspace testing conventions
│   ├── integration/                       #   Cross-project integration tests
│   ├── browser/                           #   Browser/E2E tests
│   └── fixtures/                          #   Test fixtures
│
├── .agents/                               # 🤖 AI agent skills + configuration
│   ├── skills/                            #   Reusable skill definitions
│   └── kiro/settings/mcp.json             #   MCP server configuration
│
└── .archives/                            # 🗄️ Historical archives (excluded from dev)
```

---

## Product Boundaries Reference

| Product | Path | Stack | Key AGENTS.md |
|---|---|---|---|
| **Precis LMS** | `projects/precis/precis-main/` | Django + Wagtail + django-fusion | `projects/precis/precis-main/backend/AGENTS.md` |
| **Landing-Fusion** | `projects/precis/precis-landing/` | Astro 5 + Django + Wagtail | `projects/precis/precis-landing/AGENTS.md` |
| **CTC Research** | `projects/precis/precis-ctc/` | Django + Wagtail | `projects/precis/precis-ctc/AGENTS.md` |
| **Syntara** | `projects/syntara/` | Django + CeptorAI + Ollama | `projects/syntara/AGENTS.md` |
| **Loop-CRM** | `projects/loop-crm/` | Django + django-fusion + Astro | `projects/loop-crm/backend/AGENTS.md` |
| **Formint Community** | `projects/formints/formint-community/` | Tauri 2 + React 19 + Rust/Diesel | `projects/formints/formint-community/AGENTS.md` |
| **Formint Standard** | `projects/formints/formint-standard/` | Tauri + Astro | `projects/formints/formint-standard/AGENTS.md` |
| **Formint Professional** | `projects/formints/formint-pro/` | Astro + Django + Tauri | `projects/formints/formint-pro/AGENTS.md` |
| **Formint Cloud** | `projects/formints/formint-cloud/` | Django + Channels + Unfold | `projects/formints/formint-cloud/AGENTS.md` |
| **Formint Client** | `projects/formints/formint-client/` | Tauri 2 + Vue 3 | `projects/formints/formint-client/AGENTS.md` |
| **django-fusion** | `libs/django-fusion/` | Python package | `libs/django-fusion/AGENTS.md` |
| **Kilo MCP** | `applications/agents/` | FastAPI | `applications/agents/AGENTS.md` |

---

## Customization Guide

### Per-Product Customization Matrix

| Layer | What to Customize | Where | Safe Level |
|---|---|---|---|
| **Brand colors/logos** | SCSS variables, static assets | `projects/<product>/assets/` | 🟢 Safe |
| **Templates** | Component templates, layouts | `projects/<product>/assets/templates/` or `backend/apps/*/templates/` | 🟢 Safe |
| **Wagtail StreamFields** | Block definitions, page models | `backend/apps/pages/` | 🟡 Extensible |
| **Django settings** | Site config, installed apps | `backend/settings.py` or `projects/precis/configs/` | 🟡 Config-only |
| **URLs/routing** | Route registration | `backend/urls.py` | 🟡 Extensible |
| **django-fusion components** | Component templates, behavior | `libs/django-fusion/` | 🔵 Template-level |
| **Database schema** | Models, migrations | `backend/apps/*/models.py` | 🔴 Core — needs migrations |
| **Auth system** | Allauth adapters | `backend/apps/auth/` | 🟡 Adapter-based |
| **Infrastructure** | Proxy, Docker, Compose | `applications/` | 🔴 Infrastructure |
| **Build tooling** | Webpack, pnpm, Cargo | Per-product Makefile | 🟡 Config-only |

### Instance Setup Guide

```bash
git clone --recurse-submodules <repo-url>
cd structa.cloud
uv sync
```

```bash
# Precis LMS
cd projects/precis/precis-main/backend
make check && make migrate && make seed

# Landing-Fusion
cd projects/precis/precis-landing
make install && make backend-migrate && make backend-seed

# Loop-CRM
cd projects/loop-crm/backend
make check && make migrate && make test

# Formint Cloud
cd projects/formints/formint-cloud
make install && make migrate

# Formint Community
cd projects/formints/formint-community
pnpm install && pnpm tauri dev

# Syntara
cd projects/syntara
python manage.py migrate
```

### Run Development Servers

```bash
# Landing-Fusion (frontend + backend)
cd projects/precis/precis-landing
make dev                     # Astro frontend
make backend-dev             # Django backend

# Loop-CRM
cd projects/loop-crm
make dev                     # Django + Astro + worker

# Formint Professional
cd projects/formints/formint-pro
make env                     # Backend + Frontend

# Formint Cloud
cd projects/formints/formint-cloud
make dev-backend
make dev-frontend
```

### Run Tests

```bash
# Per-product
cd projects/precis/precis-main/backend && make test
cd projects/precis/precis-landing && make backend-test
cd projects/loop-crm/backend && make test
cd projects/formints/formint-cloud && make test

# Library
cd libs/django-fusion && uv run pytest

# Workspace dispatcher
cd projects && make test WEBSITE=loop-crm
cd projects && make check WEBSITE=precis-main   # maps to projects/precis/precis-main
```

---

## Name Migration Quick Reference

| Legacy Name | Current Name | Current Path | Notes |
|---|---|---|---|
| `precis-lms` / `lms` | Precis LMS (alias) | `projects/precis/precis-main/` | `WEBSITE=precis-main` dispatcher alias |
| `precis-landing` | Landing-Fusion | `projects/precis/precis-landing/` | `WEBSITE=precis-landing` |
| `precis-ctc` / `ctc` | CTC Research | `projects/precis/precis-ctc/` | `WEBSITE=precis-ctc` |
| `cms-fusion` | Merged | — | Split into Precis + Landing-Fusion |
| `portfolio` / `VResume` | Merged into Precis | `projects/precis/precis-main/` | Resume builder merged |
| `cypercloud` | Syntara | `projects/syntara/` | Runtime alias preserved |
| `pos-mini` / `forge-pos` / `formintA` / `formint-community` | Formint Community | `projects/formints/formint-community/` | Offline-first edition |
| `formint-standard` | Formint Standard | `projects/formints/formint-standard/` | |
| `pos-solo` / `pos-full` / `formint` / `formint-pro` | Formint Professional | `projects/formints/formint-pro/` | Merged editions |
| `pos-cloud` / `formintB` / `formint-cloud` | Formint Cloud | `projects/formints/formint-cloud/` | Cloud master |
| `pos-client` / `formintC` / `formint-client` | Formint Client | `projects/formints/formint-client/` | |
| `core/` | `projects/` | `projects/` | Renamed 2026 |
| `core/libs/` | `libs/` | `libs/` | Moved to repo root |
| `core/configs/` | `projects/precis/configs/` | `projects/precis/configs/` | Shared Django settings regrouped |

---

## Remarks, Recommendations & How to Use

> This section explains **how to work with the latest structure** and the
> conventions that make the monorepo easier to navigate with standard tooling.

### 1. Where things live now

- **LMS/marketing/research are one group:** `projects/precis/` holds
  `main/` (Precis LMS), `lnd-structa/` (Landing-Fusion) and `lms-ctc/`
  (CTC Research). Their shared Django settings live in `projects/precis/configs/`.
  The **runtime identity is unchanged** — use `WEBSITE=precis-main`,
  `WEBSITE=precis-landing`, or `WEBSITE=precis-ctc` and let
  `projects/Makefile` resolve the filesystem path.
- **POS editions use short names:** `community/`, `standard/`, `pro/`,
  `cloud/`, `client/` under `projects/formints/`. The old `formintA`,
  `formint`, `formint-cloud`, `formintC` and `formint-*` names are aliases
  only — do not add new code under them.
- **Loop-CRM is its own modular monolith** at `projects/loop-crm/` with
  `backend/apps/{core,crm,marketing,attribution,finance,pos}`.
- **Shared framework code** stays in `libs/django-fusion/` (submodule). Never
  copy framework code into a product.

### 2. Use the dispatcher, not hard-coded paths

`projects/Makefile` is the canonical entry point. Prefer:

```bash
cd projects
make check WEBSITE=loop-crm
make test  WEBSITE=precis-landing
make run-dev WEBSITE=precis-ctc
```

over `cd`-ing into `projects/precis/precis-landing` directly, so the `SITE` /
`PROJECT_DIR` mapping stays the single source of truth. Add a new alias there
(not in a doc) when a path moves.

### 3. One toolchain per language

| Language | Tool | Config |
|---|---|---|
| Python | `uv` (workspace in root + `projects/pyproject.toml`) | `pyproject.toml`, `uv.lock` |
| Frontend | `pnpm` | per-project `package.json` |
| Rust/Tauri | `cargo` | `src-tauri/Cargo.toml` |
| Lint/format | `ruff` | `pyproject.toml` |
| Tests | `pytest` + Django `manage.py test` | per-project |

Run the **narrowest check first** (`ruff check`, `manage.py check`, targeted
`pytest`), then widen only if needed.

### 4. Component/template conventions

- Use `{% comp "name" /%}` for registered django-fusion components; `{% include %}`
  only for genuinely dynamic template names or local includes.
- Add a resource by extending `RESOURCES` in a product's `resources.py` so both
  the render-first and data-API roads pick it up automatically.
- Keep generated output (`dist/`, `bundles/`, `static/css/*.css`, `target/`,
  `node_modules/`) out of git — edit source only.

### 5. Theme & asset organization

- Each product owns its theme under `<project>/assets/styles/` (or
  `frontend/src/styles/`); shared tokens stay in `projects/assets/` only when
  ≥2 products genuinely consume them. See `docs/plans/THEME_DIRECTORY_STRATEGY.md`.
- One `workspace.js` (webpack) per project is the single style/script bundle
  seam; `.astro` is compiled by Astro itself, never by webpack.

### 6. Plan & doc governance

- All active plans live in `docs/plans/<scope>/` and are indexed in
  `docs/plans/README.md`. Completed/retired plans are deleted (git history is the archive).
- Record every removal in `docs/plans/deletion-manifest.md` before deleting.
- Never create new plans in `docs/dev/plans/`, `docs/plans/migrated/`, or
  project-local `plan/` directories.

### 7. Recommended structure improvements (for better tooling)

1. **Keep one source of truth per path** — update `projects/Makefile`,
   `AGENTS.md`, and `docs/project-structure.md` together whenever a directory
   is renamed; stale docs are worse than missing docs.
2. **Adopt a workspace `justfile`/`Makefile` per product family** (Precis,
   Formints, Loop-CRM) so `make check`/`make test`/`make run-dev` behave
   identically across editions.
3. **Centralize generated-artifact gitignore** (already partly done for
   `.pnpm-store`, `backups/`) so build output never lands in diffs.
4. **Prefer app boundaries over catch-all modules** — `models`, `services`,
   `handlers`, `api`, `components`, `management` per product app.
5. **Link docs to code, don't duplicate** — plans should reference source
   paths and verification commands, not re-paste implementations.

---

## Related

- [`../AGENTS.md`](../AGENTS.md) — full repository rules and safety
- [`docs/README.md`](README.md) — documentation hub
- [`docs/overview.md`](overview.md) — repo overview with architecture
- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) — request lifecycle, components, tasks, MCP
- [`docs/recommendations.md`](recommendations.md) — priority recommendations
- [`docs/plans/README.md`](plans/README.md) — canonical plan registry
- [`docs/ai/agents.md`](ai/agents.md) — complete AGENTS.md inventory
