# 🏛️ Project Structure — Complete Reference

> Full directory tree with remarks, references, customization guides, and instance setup notes.
> Generated: 2026-08-10 | Branch: `generic`

---

## Complete Project Tree

```
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
├── docs/                                   # 📚 Documentation project (Docus + Nuxt Content)
│   ├── docus/                              #   Docus Nuxt app and locale sources
│   │   ├── nuxt.config.ts                  #     English + Arabic routing
│   │   ├── app.config.ts                  #     Branding, search, SEO
│   │   ├── ar-content/                     #     Authored Arabic core guides
│   │   └── scripts/prepare-content.mjs     #     Builds English content tree
│   ├── index.html                          #   Redirect to the Docus locale route
│   ├── README.md                           #   Documentation hub
│   ├── overview.md                         #   Repo overview + name migration reference
│   ├── _sidebar.md                         #   Sidebar navigation
│   ├── recommendations.md                  #   Priority recommendations
│   ├── recent-changes.md                   #   Changelog / session log
│   ├── assets/                             #   📸 Documentation assets
│   │   ├── README.md                       #     Naming conventions + inventory
│   │   ├── screenshots/formints/           #     Formint admin + frontend screenshots
│   │   │   ├── admin-dashboard.jpg
│   │   │   ├── admin-products.jpg
│   │   │   ├── admin-customers.jpg
│   │   │   ├── admin-sales.jpg
│   │   │   ├── admin-loyalty.jpg
│   │   │   ├── admin-settings.jpg
│   │   │   ├── frontend-home.jpg
│   │   │   └── frontend-data.jpg
│   │   └── previews/formints/              #     Formint product preview images
│   │       ├── standard-front.jpg
│   │       ├── standard-back.jpg
│   │       ├── pro-admin-dashboard.jpg
│   │       ├── pro-admin-products.jpg
│   │       └── standard-walkthrough.gif
│   ├── guides/                             #   📖 Step-by-step walkthroughs
│   │   ├── README.md
│   │   ├── 00-quickstart.md
│   │   ├── 01-setup.md
│   │   ├── 02-auth.md
│   │   ├── 03-dev.md                       #     POS development
│   │   ├── 04-deploy.md
│   │   ├── 05-customize.md
│   │   ├── 06-clone-site.md
│   │   ├── 07-best-practices.md
│   │   ├── fixture-loading.md
│   │   └── 09-fusion-assets-health.md
│   ├── plans/                              #   🗺️ Canonical plan registry
│   │   ├── README.md                       #     Active plan index
│   │   ├── recommendations.md
│   │   ├── document-lifecycle.md
│   │   ├── deletion-manifest.md
│   │   ├── repository/                     #     Cross-repository plans
│   │   ├── editions/                       #     Formint edition chain
│   │   ├── pos/                            #     POS product plans
│   │   ├── landing-fusion/                 #     Landing site plans
│   │   ├── django-fusion/                  #     Framework plans
│   │   ├── cms-fusion/                     #     CMS plans (merged)
│   │   ├── lms-fusion/                     #     LMS plans (→ Precis)
│   │   ├── legacy/                         #     Read-only historical evidence
│   │   └── migrated/                       #     Migrated plan archives
│   ├── projects/                           #   📁 Per-project references
│   │   ├── precis/                         #     Precis LMS docs
│   │   ├── landing-fusion/                 #     Landing-Fusion docs
│   │   └── libs/                           #     Library docs
│   ├── ai/                                 #   🤖 AI agents & prompts
│   │   ├── README.md
│   │   ├── agents.md                       #     AGENTS.md inventory + .agents/skills
│   │   ├── prompts.md                      #     Prompt templates
│   │   └── mcp-integration.md              #     MCP server integration
│   ├── dev/                                #   🛠️ Developer references
│   │   ├── README.md
│   │   ├── customization/
│   │   ├── databases/
│   │   ├── infrastructure/
│   │   │   ├── deployment.md
│   │   │   ├── proxy.md
│   │   │   ├── routing-proxy.md
│   │   │   ├── shared-worker.md
│   │   │   ├── worker-stack.md
│   │   │   └── docker/
│   │   ├── technical/
│   │   │   ├── architecture/
│   │   │   ├── components/
│   │   │   └── django-fusion-enhancements.md
│   │   ├── back-env/
│   │   ├── sessions/
│   │   ├── libs/
│   │   ├── deployment/
│   │   └── pre-restructure/
│   ├── auth/                               #   Auth documentation
│   ├── changelogs/                         #   Changelog files
│   ├── publish/                            #   Publishing & CI/CD
│   ├── features/                           #   Feature matrix
│   ├── fixtures/                           #   Fixture docs
│   ├── pos/                                #   POS comprehensive docs
│   ├── design/                             #   Design system
│   ├── portfolio/                          #   Portfolio docs
│   ├── shared/                             #   Shared methods
│   ├── tests/                              #   Testing docs
│   ├── cypercloud/                         #   Cypercloud/Syntara docs
│   ├── lms/                                #   Legacy LMS docs
│   ├── guides/                             #   Guides directory
│   └── Dockerfile                          #   Standalone Docus static container
│
├── projects/                               # 🔵 All product code + shared Django config
│   ├── AGENTS.md                           #   Project-level conventions
│   ├── Makefile                            #   Canonical dispatcher (WEBSITE=)
│   ├── pyproject.toml                      #   Python workspace deps + pytest config
│   │
│   ├── precis/                             # 📘 PRECIS LMS — Learning platform
│   │   ├── backend/                        #     Django + Wagtail backend
│   │   │   ├── AGENTS.md                   #       Backend agent instructions
│   │   │   ├── settings.py                #       Django settings
│   │   │   ├── urls.py                    #       Root URL configuration
│   │   │   ├── manage.py                  #       Django CLI
│   │   │   ├── server.py                  #       Server entry point
│   │   │   ├── Makefile                   #       Backend commands
│   │   │   ├── apps/
│   │   │   │   ├── content/               #       Wagtail content hooks, tasks
│   │   │   │   ├── learning/              #       Courses, enrollment, progress
│   │   │   │   ├── pages/                 #       Page features: blog, profile, accounts
│   │   │   │   │   ├── accounts/templates/auth/
│   │   │   │   │   │   └── AGENTS.md      #         Auth template conventions
│   │   │   │   │   ├── profile/templates/profile/
│   │   │   │   │   │   └── AGENTS.md      #         Profile template conventions
│   │   │   │   │   ├── blog/templates/
│   │   │   │   │   │   └── AGENTS.md      #         Blog template conventions
│   │   │   │   │   └── templatetags/
│   │   │   │   │       └── menu_tags.py   #         Menu tag library
│   │   │   │   ├── handlers/              #       Request handlers, renderers
│   │   │   │   ├── auth/                  #       Allauth adapters
│   │   │   │   ├── core/                  #       Shared routes, services
│   │   │   │   ├── domain/                #       Site/domain configuration
│   │   │   │   └── components/            #       Backend component templates
│   │   │   ├── templates/                 #       Site-root templates, overrides
│   │   │   │   └── AGENTS.md
│   │   │   ├── tests/                     #       Backend test suite
│   │   │   └── migrations/                #       Django migrations
│   │   ├── assets/                        #     Project templates, static, media
│   │   │   ├── templates/
│   │   │   │   ├── AGENTS.md              #       Template root conventions
│   │   │   │   ├── blog/AGENTS.md
│   │   │   │   ├── pages/AGENTS.md
│   │   │   │   ├── lms/AGENTS.md
│   │   │   │   ├── components/AGENTS.md
│   │   │   │   ├── profile/AGENTS.md
│   │   │   │   ├── plugins/AGENTS.md
│   │   │   │   ├── partials/header/       #       Header partials
│   │   │   │   └── layout/                #       Layout templates
│   │   │   ├── static/                    #       Static assets
│   │   │   │   ├── images/                #         Default images, brand, elements
│   │   │   │   ├── fonts/                 #         Font icons, flags
│   │   │   │   └── videos/                #         Home page video
│   │   │   └── media/images/              #       Wagtail-managed media
│   │   └── frontend/                      #     Astro frontend shell
│   │       └── public/favicon.svg
│   │
│   ├── landing-fusion/                    # 🌐 LANDING-FUSION — Marketing/Catalog site
│   │   ├── AGENTS.md                      #       Project agent instructions
│   │   ├── Makefile                       #       Frontend + backend orchestration
│   │   ├── README.md
│   │   ├── frontend/                      #       Astro 5 + Tailwind 4 frontend
│   │   │   ├── astro.config.mjs
│   │   │   ├── src/
│   │   │   │   ├── pages/                 #         Marketing/catalog routes
│   │   │   │   ├── layouts/               #         Document shell, SEO, theme
│   │   │   │   ├── fusion/                #         HTMX, fragments, SSE helpers
│   │   │   │   ├── lib/                   #         API, config, translations
│   │   │   │   └── styles/                #         Tokens/global styles
│   │   │   ├── public/
│   │   │   │   └── static/
│   │   │   │       ├── previews/formints/  #        Formint preview images
│   │   │   │       └── related/formints/   #        Formint feature images
│   │   │   └── e2e/                       #         Playwright tests
│   │   ├── backend/                       #       Django + Wagtail backend
│   │   │   ├── apps/
│   │   │   │   ├── content/               #         StreamField blocks, content APIs
│   │   │   │   ├── pages/                 #         Wagtail page models, APIs
│   │   │   │   ├── handlers/              #         PageHandlers, middleware
│   │   │   │   ├── learning/              #         Catalog, enrollment, progress
│   │   │   │   └── auth/                  #         Allauth adapters
│   │   │   ├── settings.py
│   │   │   ├── urls.py
│   │   │   ├── Makefile
│   │   │   └── assets/static/
│   │   │       ├── previews/formints/
│   │   │       └── related/formints/
│   │   ├── assets/                        #       Project SCSS, compiled CSS
│   │   ├── docs/                          #       Product design, use cases, ADRs
│   │   └── docker-compose.yml
│   │
│   ├── syntara/                           # 🤖 SYNTARA — AI Chat/Customizer
│   │   ├── AGENTS.md                      #       Project agent instructions
│   │   ├── chat/                          #       Conversation, streaming, discovery
│   │   │   ├── models.py                 #         Conversation/message persistence
│   │   │   ├── views.py                  #         Chat and template-discovery
│   │   │   ├── views_stream.py           #         SSE/streaming endpoints
│   │   │   ├── services.py               #         Conversation/AI business logic
│   │   │   ├── site_data.py              #         Site/template discovery
│   │   │   ├── customizer.py             #         Template catalog helpers
│   │   │   └── ceptor.py                 #         Provider integration boundary
│   │   ├── templates/
│   │   │   ├── AGENTS.md
│   │   │   ├── base.html
│   │   │   ├── chat.html
│   │   │   ├── components/                #         Chat/editor/navigation
│   │   │   └── fragments/                 #         HTMX response fragments
│   │   ├── assets/                        #       Source JS/CSS + Webpack
│   │   ├── configs/                       #       YAML model/provider settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── server.py
│   │   └── Makefile
│   │
│   ├── formints/                          # 💰 FORMINTS — Multi-edition POS platform
│   │   ├── AGENTS.md                      #       POS-wide agent instructions
│   │   ├── Makefile                       #       Edition dispatcher
│   │   ├── README.md
│   │   ├── docs/                          #       POS architecture + screenshots
│   │   │   ├── architecture/
│   │   │   │   ├── editions.md            #         Edition comparison
│   │   │   │   ├── pos-architecture.md    #         Full architecture
│   │   │   │   └── table-column-comparison.md
│   │   │   ├── SERVER_V2.md
│   │   │   └── screenshots/               #         (source of docs/assets copies)
│   │   ├── formintA/                      #       Community (Tauri + React + Rust)
│   │   │   └── AGENTS.md
│   │   ├── formint/                       #       Professional (Astro + Django + Tauri)
│   │   │   ├── server/                    #         Django/Robyn boundary, APIs
│   │   │   ├── frontend/                  #         Astro + Alpine/HTMX shell
│   │   │   └── src-tauri/                 #         Native desktop shell
│   │   ├── formint-cloud/                 #       Cloud master (Django + Channels)
│   │   │   ├── backend/                   #         Django backend + WebSocket
│   │   │   │   ├── apps/core/             #           Models, Ninja API, viewsets
│   │   │   │   ├── apps/domain/           #           Sync broker, queue, resolver
│   │   │   │   ├── apps/handlers/         #           Consumers, WebSocket
│   │   │   │   └── configs/               #           Settings, ASGI, URLs
│   │   │   └── frontend/                  #         Community UI + dashboards
│   │   │       └── AGENTS.md
│   │   ├── formintC/                      #       POS Client (Tauri + Vue 3)
│   │   ├── formint-standard/              #       Standard edition
│   │   │   └── AGENTS.md
│   │   ├── formint-pro/                   #       Pro edition (merged)
│   │   │   └── src-tauri/icons/           #         App icons (iOS, Android, desktop)
│   │   ├── formint-client/                #       Client frontend
│   │   ├── tests/                         #       Shared POS E2E + API tests
│   │   │   └── pos-e2e/AGENTS.md
│   │   ├── packages/formints-client/      #       @formints/client TS SDK
│   │   └── scripts/                       #       Build/release/dev tooling
│   │
│   ├── configs/                           # ⚙️ Shared Django settings
│   │   ├── base/                          #       Base Django config
│   │   │   └── templates.py              #         Template engine configuration
│   │   ├── default/                       #       Default settings
│   │   └── workers/                       #       Worker settings
│   │
│   ├── assets/                            # 🎨 Shared static/templates/locale
│   ├── scripts/                           # 📜 Project-local automation
│   └── webpack/                           # 📦 Shared/legacy asset configuration
│
├── libs/                                  # 📚 Reusable libraries (submodules)
│   └── django-fusion/                     #   Shared Django/Wagtail components
│       ├── AGENTS.md                      #     Framework agent instructions
│       ├── src/django_fusion/
│       │   ├── comp/                      #       Component system
│       │   │   └── templatetags/          #         routable_components, components
│       │   ├── tables/                    #       Data tables
│       │   ├── forms/                     #       Form handling
│       │   ├── fragments/                 #       HTMX fragments
│       │   └── routing/                   #       URL routing
│       └── tests/                         #     Framework tests
│
├── applications/                          # 🏗️ Infrastructure + tooling
│   ├── AGENTS.md                          #   Infrastructure agent instructions
│   ├── proxy/                             #   Traefik reverse proxy configs
│   │   └── traefik/dynamic/               #     Dynamic routing configs
│   ├── databases/                         #   PostgreSQL + Redis compose
│   ├── agents/                            #   Kilo MCP server
│   │   ├── AGENTS.md                      #     Kilo agent instructions
│   │   ├── mcp_server.py                  #     FastAPI MCP endpoints
│   │   ├── agent/                         #     Agent role definitions
│   │   ├── commands/                      #     Agent commands
│   │   └── skills/                        #     Operational skills
│   ├── templates/                         #   Coder/Terraform templates
│   │   ├── dev-workspace/main.tf              #     Coder + FileGator + internal AppFlowy workspace
│   │   └── website/main.tf                #     Website workspace
│   └── scripts/                           #   Automation scripts
│
├── tests/                                 # 🧪 Workspace integration tests
│   ├── AGENTS.md                          #   Workspace testing conventions
│   ├── integration/                       #   Cross-project integration tests
│   ├── browser/                           #   Browser/E2E tests
│   └── fixtures/                          #   Test fixtures
│
├── .agents/                               # 🤖 AI agent skills + configuration
│   ├── skills/                            #   21 reusable skill definitions
│   │   ├── design-taste-frontend/SKILL.md
│   │   ├── gpt-taste/SKILL.md
│   │   ├── high-end-visual-design/SKILL.md
│   │   ├── shadcn/SKILL.md
│   │   ├── brandkit/SKILL.md
│   │   ├── imagegen-frontend-web/SKILL.md
│   │   ├── imagegen-frontend-mobile/SKILL.md
│   │   ├── image-to-code/SKILL.md
│   │   ├── documentation/SKILL.md
│   │   ├── deployment-documentation/SKILL.md
│   │   ├── content-strategy/SKILL.md
│   │   ├── content-production/SKILL.md
│   │   ├── content-creator/SKILL.md
│   │   ├── explore-data/SKILL.md
│   │   ├── use-case-triage/SKILL.md
│   │   ├── minimalist-ui/SKILL.md
│   │   ├── industrial-brutalist-ui/SKILL.md
│   │   ├── stitch-design-taste/SKILL.md
│   │   ├── redesign-existing-projects/SKILL.md
│   │   ├── design-taste-frontend-v1/SKILL.md
│   │   └── full-output-enforcement/SKILL.md
│   └── kiro/settings/
│       └── mcp.json                      #   MCP server configuration
│
└── .archives/                            # 🗄️ Historical archives (excluded from dev)
    ├── ctc-research/
    ├── ceptor-ai/
    └── cms-fusion/
```

---

## Product Boundaries Reference

| Product | Path | Port | Stack | Key AGENTS.md |
|---|---|---|---|---|
| **Precis LMS** | `projects/precis/` | — | Django + Wagtail + django-fusion | `projects/precis/backend/AGENTS.md` |
| **Landing-Fusion** | `projects/landing-fusion/` | 8074 | Astro 5 + Django + Wagtail | `projects/landing-fusion/AGENTS.md` |
| **Syntara** | `projects/syntara/` | 5073 | Django + CeptorAI + Ollama | `projects/syntara/AGENTS.md` |
| **Formint Community** | `projects/formints/formintA/` | — | Tauri 2 + React 19 + Rust/Diesel | `projects/formints/formintA/AGENTS.md` |
| **Formint Professional** | `projects/formints/formint/` | — | Astro + Django Ninja + Tauri | `projects/formints/AGENTS.md` |
| **Formint Cloud** | `projects/formints/formint-cloud/` | 8767 | Django + Channels + Unfold | `projects/formints/formint-cloud/frontend/AGENTS.md` |
| **Formint Client** | `projects/formints/formintC/` | — | Tauri 2 + Vue 3 | `projects/formints/AGENTS.md` |
| **django-fusion** | `libs/django-fusion/` | — | Python package | `libs/django-fusion/AGENTS.md` |
| **Kilo MCP** | `applications/agents/` | 8100 | FastAPI | `applications/agents/AGENTS.md` |

---

## Customization Guide

### Per-Product Customization Matrix

| Layer | What to Customize | Where | Safe Level |
|---|---|---|---|
| **Brand colors/logos** | SCSS variables, static assets | `projects/<product>/assets/` | 🟢 Safe |
| **Templates** | Component templates, layouts | `projects/<product>/assets/templates/` or `backend/apps/*/templates/` | 🟢 Safe |
| **Wagtail StreamFields** | Block definitions, page models | `backend/apps/pages/` | 🟡 Extensible |
| **Django settings** | Site config, installed apps | `backend/settings.py` or `configs/` | 🟡 Config-only |
| **URLs/routing** | Route registration | `backend/urls.py` | 🟡 Extensible |
| **django-fusion components** | Component templates, behavior | `libs/django-fusion/` | 🔵 Template-level |
| **Database schema** | Models, migrations | `backend/apps/*/models.py` | 🔴 Core — needs migrations |
| **Auth system** | Allauth adapters | `backend/apps/auth/` | 🟡 Adapter-based |
| **Infrastructure** | Proxy, Docker, Compose | `applications/` | 🔴 Infrastructure |
| **Build tooling** | Webpack, pnpm, Cargo | Per-product Makefile | 🟡 Config-only |

### Instance Setup Guide

#### 1. Clone and Initialize
```bash
git clone --recurse-submodules <repo-url>
cd structa.cloud
uv sync
```

#### 2. Select Your Product

```bash
# Precis LMS
cd projects/precis/backend
make check && make migrate && make seed

# Landing-Fusion
cd projects/landing-fusion
make install && make backend-migrate && make backend-seed

# Formint Cloud
cd projects/formints/formint-cloud
make install && make migrate

# Formint Community
cd projects/formints/formintA
pnpm install && pnpm tauri dev

# Syntara
cd projects/syntara
python manage.py migrate
```

#### 3. Run Development Servers

```bash
# Landing-Fusion (frontend + backend)
cd projects/landing-fusion
make dev                     # Astro frontend (default port)
make backend-dev             # Django backend (:8074)

# Formint Professional
cd projects/formints/formint
make env                     # Backend (:8767) + Frontend (:4321) in tmux

# Formint Cloud
cd projects/formints/formint-cloud
make dev-backend             # Django (:8767)
make dev-frontend            # Community UI
```

#### 4. Run Tests

```bash
# Per-product
cd projects/precis/backend && make test
cd projects/landing-fusion && make backend-test
cd projects/formints/formint && make test

# Library
cd libs/django-fusion && uv run pytest

# Workspace
cd projects && make test WEBSITE=lms-fusion
```

---

## Name Migration Quick Reference

| Legacy Name | Current Name | Current Path | Notes |
|---|---|---|---|
| `ctc-research` | Precis LMS | `projects/precis/` | `WEBSITE=ctc-research` alias preserved |
| `lms-fusion` | Precis LMS (alias) | `projects/precis/` | `WEBSITE=lms-fusion` dispatcher alias |
| `lms` | Precis LMS | `projects/precis/` | Legacy docs reference |
| `cms-fusion` | Merged | — | Split into Precis + Landing-Fusion |
| `portfolio` / `VResume` | Merged into Precis | `projects/precis/` | Resume builder merged |
| `cypercloud` | Syntara | `projects/syntara/` | Runtime alias preserved |
| `core/` | `projects/` | `projects/` | Renamed 2026 |
| `core/libs/` | `libs/` | `libs/` | Moved to repo root |
| `pos-mini` / `forge-pos` | Formint Community | `projects/formints/formintA/` | |
| `pos-solo` / `pos-full` | Formint Professional | `projects/formints/formint/` | Merged editions |
| `pos-cloud` / `formintB` | Formint Cloud | `projects/formints/formint-cloud/` | Renamed 2026-08 |
| `formint-pos` / `formint-community` | Formint Community | `projects/formints/formintA/` | Published package |
| `formint-pos-backend` | Formint Professional | `projects/formints/formint/server/` | Package name |
| `formint-pos-frontend` | Formint Professional | `projects/formints/formint/frontend/` | Package name |

---

## Related

- [`../AGENTS.md`](../AGENTS.md) — full repository rules and safety
- [`docs/README.md`](README.md) — documentation hub
- [`docs/overview.md`](overview.md) — repo overview with architecture
- [`docs/ai/agents.md`](ai/agents.md) — complete AGENTS.md inventory
- [`docs/guides/05-customize.md`](guides/05-customize.md) — customization guide
- [Formint editions](https://github.com/mammhoud/structa.cloud/blob/generic/projects/formints/docs/architecture/editions.md)
