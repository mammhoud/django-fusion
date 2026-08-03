# Changelog

## 2026-08-02 — lms-fusion container recovery: mounts, migrations, templates

### docker (lms-fusion + cms-fusion compose)

- Fixed stale container mounts that shadowed the shared configs package with an
  empty `projects/lms-fusion/configs/` dir (caused `ModuleNotFoundError: No module
  named 'configs.site'` at boot). Containers now mount `../configs` (shared),
  `../assets` (workspace shared assets), and `./backend` per the current compose.
- `docker-compose.yml` (LMS + CMS): added `../assets:/app/assets` mounts for
  backend and worker so workspace-level shared templates resolve in containers.

### migrations

- Fixed `accounts/0002_remove_message_recipient_content_type_and_more.py` (LMS):
  `AlterUniqueTogether(name='sharednote', unique_together=None)` now runs before
  the `RemoveField('note')` / `RemoveField('user')` operations. The prior ordering
  made Django's state projection fail with `SharedNote has no field named 'note'`
  during `migrate` (Django requires the fields present in the from-state to drop
  the composed unique index). Legacy `accounts_*` tables are now cleanly dropped
  and `handlers.0002` applies.

### templates & settings

- `projects/configs/base/templates.py`: added `BASE_DIR / "apps" / "templates"` to
  `TEMPLATES_DIRS` (the canonical home/about/contact/services/team template tree
  was unreachable).
- Created missing `services/includes/*` component templates (page_title,
  services_section, counter_section, testimonial_section, pricing_section,
  clients_section) and `events/main.html` + `events/includes/events_grid.html`
  for both LMS and CMS — all dynamic (backend context), defensive, no static
  content. Removed stale broken duplicates in `assets/templates/events/` that
  referenced a dead `plugins:event-detail` URL.
- `cms-fusion tests/test_assets_contract.py`: the canonical asset-path settings
  now resolve from the shared `projects/configs/base/assets.py` after the configs
  consolidation.

## 2026-07-30 — ceptor-ai migration complete + enhanced test coverage + plan consolidation

### ceptor-ai dependency: fully removed across all 6 projects

**ctc-research** (~90 files, 44 imports, Phases 1-4 complete):
- Created local package `plugins/core/` with models (DefaultBase, ContentBase, Organization,
  Contact, ContactEmail, ContactPhone, Team, Workspace, CachingStorage, TokenService),
  middleware (PrivacyConsentMiddleware), services (dispatch_job), and site mixins
- Person → AUTH_USER_MODEL across 25+ files; blocks → Wagtail-native `plugins/blocks/`
- PersonTag/PersonTagCategory stubs; CachingStorage classmethod signatures fixed
- 3 peoples.py User.ProfileType safe fallbacks added
- Contact.added_company CASCADE → SET_NULL fix
- 0 ceptor_ai imports remaining; project moved to `archives/ctc-research/`

**cms-fusion & lms-fusion**: Already clean (0 imports); newsletter native from start

**cypercloud**: 6 AI/MCP/chat imports → local `ceptor_stubs.py` (AIIntegrationRegistry,
  _StubMCPServer, CraftsClient, ChatBubble with relative imports `from ..ceptor_stubs`)

**ceptor-ai library**: Removed from `libs/`, `.gitmodules`, and `INSTALLED_APPS`

### test: cms-fusion + lms-fusion — 113 tests each, 0 failures

- Existing: 86 tests (smoke, API, domain models, fixture content)
- Enhanced: `test_enhanced_api.py` — 27 new tests across 10 classes
  - CORS headers, HTMX handling (HX-Request), error handling (404/405/400)
  - Trailing slash redirects for all endpoints
  - Branding detail validation (hex colors, site_name)
  - Pages fragment/data sub-endpoints
  - Courses filters structure, Content-Type verification
  - Security headers (X-Content-Type-Options), fusion assets endpoint
- Fixed: 3 trailing-slash failures in test_fixture_content.py

### docs: plan file consolidation

- 24 plan .md files consolidated into `docs/plans/` organized by project:
  - `docs/plans/cms-fusion/` — 8 plans (migration, dashboard, frontend, flyonui, etc.)
  - `docs/plans/lms-fusion/` — 1 plan (migration)
  - `docs/plans/pos/` — 7 plans (forge-pos, pos-solo, cloud, django-fusion)
  - `docs/plans/legacy/` — 2 plans (cleanup, merge)
  - Top-level: ceptor-ai cleanup, ctc-research migration, webpack, worker
- `docs/plans/README.md` — plan index (was `docs/plans.md`)
- Per-project CHANGELOGs created: `projects/cms-fusion/CHANGELOG.md`,
  `projects/lms-fusion/CHANGELOG.md`

  → See also: [`projects/cms-fusion/CHANGELOG.md`](projects/cms-fusion/CHANGELOG.md),
  [`projects/lms-fusion/CHANGELOG.md`](projects/lms-fusion/CHANGELOG.md),
  [`docs/plans/`](docs/plans/) — consolidated plan index with status

## 2026-07-19 — infrastructure restructuring + POS-KO gaming center + project documentation

### restructure: `core/` → `projects/` + `libs/` move to repo root

Complete monorepo reorganization for standard conventions:
- `core/` renamed to `projects/` — clearer monorepo project root
- `core/libs/django-fusion` moved to `libs/django-fusion` — libraries at repo root
- `core/libs/ceptor-ai` moved to `libs/ceptor-ai` — standard submodule convention
- `core/lms-demo/` renamed to `projects/lms/` — shorter, canonical name
- `core/VResume/` renamed to `projects/portfolio/` — descriptive project name
- `core/tinker/` renamed to `projects/cypercloud/` — new brand for AI customizer

### feat: POS-KO Gaming Center

New gaming center module for the POS desktop app:
- Token-based gaming sessions with time tracking
- Game station management and session scheduling
- Integrated billing and receipt generation

### feat: POS 3-Edition System

- **Minimal Edition** (`pos-minimal/`) — Core POS (React + Tauri + Rust + SQLite)
- **Solo Edition** (`pos-solo/`) — Core + Python/Sanic sidecar API + Cloud CRM sync
- **Full Edition** (`pos-full/`) — Core + sidecar + Django ORM + WebSocket + Cloud CRM master

### feat: POS Cloud CRM Architecture

- Standalone Cloud CRM server in Full edition (`shared-portal/cloud/`, port 8766)
- Solo edition sync client pushes products, sales, customers to cloud
- Sync proxy on cloud server accepts generic entity pushes
- Rust broadcast-based change signal system for real-time updates

### feat: POS Django Portal

Shared Django portal with django-fusion viewsets across all editions:
- Portal admin interface for managing POS data via web
- Node API views for solo/minimal editions
- Cloud CRM master views for Full edition

### docs: project documentation overhaul

- All 61+ project READMEs enhanced with consistent structure
- POS CHANGELOG.md created with full version history
- `docs/recent-changes.md` updated with restructuring details
- `docs/features/` updated with POS-KO and edition features
- `docs/_sidebar.md` and `mkdocs.yml` updated for new pages
- All `AGENTS.md` files updated with new canonical paths

## 2026-07-01 — docs cross-link sweep + CI gates

### docs: fix every broken relative cross-link in legacy READMEs

- `libs/django-fusion/docs/legacy-django-fusion/README.md`
  - Line 65: stale `venv/libs/…` path corrected to `../../README.md`
  - Line 71: `[ceptor-ai](../ceptor-ai/)` corrected to `[ceptor-ai](../../../ceptor-ai/)`
  - Line 73: removed broken `[django-fusion](../django-fusion/)` (target `docs/django-fusion/` absent)
  - Renamed "Related Packages" → "Related Package" (singular — the monorepo has exactly two libs)
- `libs/ceptor-ai/docs/legacy-django-ceptor/README.md`
  - Line 77: `../../../venv/libs/ceptor-ai/README.md` → `../../README.md`
  - Line 80: `../django-fusion/` → `../../../django-fusion/`
  - Line 81: removed duplicate broken link with stale "Testing infrastructure" description
- `libs/django-fusion/docs/legacy-django-grep/hypothesis.md`
  - Line 57: removed dead `[Auth Testing](../auth/testing.md)` link
- `libs/django-fusion/docs/legacy-django-fusion/django-allauth.md`
  - Lines 24, 50: removed dead `[Auth Adapter](../auth/adapter.md)` and `[Auth Templates](../auth/templates.md)` links
- `libs/ceptor-ai/docs/legacy-ceptor-ai/README.md`
  - Quick Start: stale `CraftsClient` → `CeptorClient` (matching actual `ceptor_ai.chat.client` API)
  - `ChatBubble(client=client)` → `ChatBubble(server_url=…)` (matching actual constructor kwarg)
  - Install extras: `openai`, `anthropic`, `faker` → `mcp`, `test` (matching `pyproject.toml` `[project.optional-dependencies]`)

### feat: CI gates for docs validation

- **`applications/scripts/check_markdown_links.py`** — validates every Markdown filesystem-relative link + HTTP HEAD (stdlib-only, Python 3.11+ for tomllib). Exit 0 clean / 1 broken / 2 bad interpreter.
- **`applications/scripts/check_extras_in_docs.py`** — validates every `uv add "pkg[extras]"` / `pip install "pkg[extras]"` line against the corresponding `pyproject.toml` `[project.optional-dependencies]`. Exit 0 clean / 1 drift / 2 bad interpreter.
- **`.github/workflows/deploy-ci.yml`** — added `markdown-links` job (Python 3.11, runs `check_markdown_links.py`) triggered on `libs/**/*.md` changes. Deleted the now-redundant standalone `.github/workflows/check-links.yml`.
- **`.github/workflows/check-extras.yml`** — runs `check_extras_in_docs.py` (Python 3.11) on PRs touching `libs/**/*.md`, `**/pyproject.toml`, or the script itself.

### feat: test scaffolding

- `libs/django-fusion/tests/django_grep/test_ceptor_ai/conftest.py` — wires `apps/libs/ceptor-ai/src` onto `sys.path` for the renamed `test_ceptor_ai.py`.
- `libs/django-fusion/tests/test_register_include_path_render_equivalence.py` — lights-up test confirming render equivalence across `{% include %}`, `{% comp "path" /%}`, and `{% comp name /%}`.

### fix: `_LazyIncludeTemplate.template` returns inner `django.template.Template`

- `libs/django-fusion/src/django_fusion/comp/registry.py` — fixed `_LazyIncludeTemplate.template` to return the inner `django.template.Template` (matching the layer that has `.nodelist`) instead of the outer `DjangoTemplate` wrapper. All four consumer sites (`Component.nodelist`, `Component.path`, `Component.source`, `BoundComponent.render`) now converge through the same path the eager `from_name` resolution always used.

### rename: legacy codenames → actual package names

- `test_nawaai/` → `test_ceptor_ai/`, `legacy_crafts_ai/` → `legacy_ceptor_ai/`, `legacy-crafts-ai/` → `legacy-ceptor-ai/` (directories)
- Removed empty `ceptor-ai/crafts-ai/` dir (the only empty dir in libs)
- 13 source files swept: `nawaai` → `ceptor-ai`, `crafts_ai`/`craftsai`/`crafts-ai`/`crafts.ai` → `ceptor_ai`/`ceptor-ai`

## 2026-06-30 — template reorganization, settings inlining, test fixes

See commit `10aa572d`.
