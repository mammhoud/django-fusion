# Changelog

All notable changes to django-fusion are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.2] — 2026-09-28

> **Version note.** This release jumps to `2.0.2`. The `1.x` line and
> `2.0.0`/`2.0.1` were never published, so no upgrade path is being skipped.
> `2.0.2` is the first release cut after the repository was reduced to the
> library itself, and it continues the `0.5.0` line rather than replacing it:
> every change below `0.5.0` still applies.

### Removed — repository reduced to the library

The repository had accumulated a full copy of a surrounding application
workspace: product documentation trees, infrastructure Compose files, monorepo
CI, and agent tooling. None of it belonged to, or was reachable from, the
published package. Removed:

- **Monorepo and product documentation** (~700 files): `docs/agenda`,
  `docs/ar-content`, `docs/plans`, `docs/public`, `docs/pos`, `docs/precis`,
  `docs/startup`, `docs/loop-crm`, `docs/syntara`, `docs/design`,
  `docs/features`, `docs/changelogs`, `docs/audit`, `docs/shared`,
  `docs/guides`, `docs/dev`, `docs/tests`, `docs/scripts`, `docs/libs`,
  `docs/publish`, `docs/legacy`, `docs/ai`, `docs/ci`, `docs/assets`, plus the
  embedded Docus site (`nuxt.config.ts`, `app.config.ts`, `Dockerfile`,
  `docker-compose.yml`, `docs/Makefile`, `index.html`) and loose monorepo docs
  (`REFERENCE.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `overview.md`,
  `project-structure.md`, `recommendations.md`, `recent-changes.md`,
  `ENHANCEMENT_PLAN.md`).
- **Infrastructure**: `application/` (databases, proxy, tools), `docker-compose.yml`,
  `INFRASTRUCTURE.md`, `CONTEXT-MAP.md`, `.devcontainer/`, `.githooks/`.
- **The `js/fusion-js` npm workspace** (`js/`), an unreferenced TypeScript package.
  No Python module, template, Makefile target, or webpack entry imported it; the
  bundle entry point is `src/django_fusion/assets/entry.js`, which is untouched.
  Note that `webpack/` itself is **not** removed — it is library infrastructure
  and the shipped default workspace now works (see Fixed).
- **Monorepo configuration**: `Justfile`, `nx.json`, `project.json`,
  `tsconfig.json`, `skills-lock.json`, `uv.lock`, `.gitmodules`, `.env.example`,
  `.env.local.example`, `.dockerignore`, `features-and-pages.xlsx`, and a stray
  empty `root` file.
- **Agent tooling**: `.agents/` (MCP server, skills, prompt catalog).
- **Monorepo CI** (`.github/workflows/deploy-ci.yml`, `formint-client-ci.yml`,
  `js-test.yml`, `fusion-ci.yml`, `lint-quality.yml`, `pytest-core.yml`,
  `check-extras.yml`) and the `deploy-preflight` composite action. Replaced by a
  library-scoped `.github/workflows/ci.yml`.
- **Monorepo test infrastructure** under `tests/` (~90 entries): `apps/`,
  `ci/`, `configs/`, `core/`, `docker/`, `email/`, `fake_accounts/`,
  `fixtures/`, `http/`, `integration/`, `selenium/`, `selenium-detailed/`,
  `unit/`, `websites/`, `archived/`, `scripts/`, and the helper scripts and
  site YAMLs beside them (`setup_ctc.py`, `run_full_test_suite.sh`,
  `load_production_fixtures.sh`, `ctc-website-tests.yaml`, `lms-demo-tests.yaml`,
  `vresume-tests.yaml`, and similar).
- **Generated documentation stubs**: 44 `design.md` files plus 33 auto-generated
  namespace `README.md` files under `src/`. They were machine-written, described
  modules that do not exist, and pointed at a generator script that was not in
  the repository. Removed with their generator, `scripts/generate_design_docs.py`.
- **Stale `setup.py`**, which pinned `version = 0.1.0` and contradicted
  `pyproject.toml`.

### Removed — product vocabulary relocated to consumers

Six abstract model bases and three management commands encoded one product's
domain and forced every consumer to inherit vocabulary it did not use. They now
belong to the projects that define those concepts:

- `django_fusion.models.certificate` (`AbstractCertificate`)
- `django_fusion.models.certification` (`AbstractCertificationTemplate`)
- `django_fusion.models.coupon` (`AbstractCoupon`, `AbstractCouponUsage`)
- `django_fusion.models.newsletter` (`AbstractNewsletter`)
- `django_fusion.models.note` (`AbstractNote`, `AbstractSharedNote`)
- `django_fusion.models.workspace` (`AbstractWorkspace`)
- `django_fusion.management.commands.populate_courses`
- `django_fusion.management.commands.populate_content`
- `django_fusion.management.commands.populate_homepage`

All nine were **abstract or unregistered**, so no migration changes and no
consumer breakage — the names were not imported anywhere outside the package.

`django_fusion.models.interaction` (`Call`, `Notification`) deliberately
**stays**: those are concrete models already created by `0001_initial`, and
removing them would require a schema migration for existing installs.

### Fixed

- **`fragments.analyzer.scanner.scan()` returned filesystem-dependent order.**
  `os.walk` yields readdir order, so the scanned file list — and anything derived
  from it, including the skeleton and asset manifests — changed between machines
  and filesystems. `_walk()` now sorts directories and files, making the output
  deterministic.
- **The test suite was order-dependent.** 1,317 errors and zero passes were
  caused by pytest collecting monorepo helper scripts, and by test modules that
  replaced `settings.TEMPLATES` without restoring it. `tests/conftest.py` now
  restores the template setting and the component registry between modules.
  Clearing `engines._engines` is not sufficient on Django 5.2+: the handler also
  caches the `settings.TEMPLATES` reference in `engines._templates`, and a stale
  reference silently rebuilds the engine from the previous module's settings.
- **`tests/analyzer/test_views.py` silently skipped its end-to-end test.** The
  fixture walked up the tree looking for a `customizer/templates/fragments/` path
  that no longer exists. The real fragment is now checked in at
  `tests/analyzer/fixtures/page_card_grid.html`, byte-for-byte, so the test runs
  in a standalone checkout.
- **`tests/test_bolt_inprocess.py` errored instead of skipping.** It imported
  `jwt` before its `importorskip`, so a base install failed collection rather
  than skipping the optional-extra test.
- Removed the `import jwt` ordering hazard and the unrelated-helper pollution
  that made `pytest tests/*.py` fail wholesale.
- **`site.auth.mixins.AuthProcessorMixin.process_registration` raised
  `UnboundLocalError` on every invalid registration.** The module imports
  `gettext_lazy as _`, and the method later assigned a throwaway with
  `group, _ = Group.objects.get_or_create(...)`. That assignment makes `_` local
  to the whole method, so the earlier `_("Registration failed")` call referenced
  a local before it was bound. The throwaway is now `_created`. This is the path
  users hit most often and no test covered it.
- **Five modules referenced undefined names.** A pyflakes pass over the package
  found them:
  - `management.managers.tags` used `Q` in an `aggregate(filter=Q(...))` without
    importing it, so the tag-usage statistics method always raised `NameError`.
  - `management.commands.analyze_components_to_webpack` used a nonexistent
    `_FUSION_LIB_ROOT` constant for every relative path, so the webpack-entry
    generator crashed.
  - `plugins.debug_tools.base.is_debug_mode` referenced undefined `settings` and
    `tracker`; it now reads `settings.DEBUG` and falls back to the
    `DJANGO_DEBUG` environment variable when Django is not configured.
  - `comp._init` annotated a field with a forward reference to
    `_LazyIncludeTemplate` that was never imported; it is now imported under
    `TYPE_CHECKING`.
  - `routes.schemas.users.utils` was dead code that **could not be imported at
    all** (`NameError: name 'BaseModel' is not defined`) and used pydantic v1
    APIs (`ConfigDict(json_encoders=...)`, `@validator`) against the declared
    `pydantic>=2`. Removed.
- **`routes.schemas.users.token` and `.user` raised `ImportError` on import** in
  any base install: they build pydantic models that use `EmailStr`, and
  `email-validator` was not a declared dependency. `pydantic>=2.0` is now
  `pydantic[email]>=2.0`.
- **Ten bare `except:` clauses** now catch `Exception`, so `KeyboardInterrupt`
  and `SystemExit` are no longer swallowed. Two semicolon-joined statement lines
  were split, and one ambiguous loop variable was renamed.
- **`designer.webapp_enhancement_plan` discarded its resolved guidance.** It
  called `_project_guidance(project)` and dropped the result, so the plan could
  not expose the project's audit guidance that the website audit already
  returned. The plan now returns `guidance`.
- **Twenty-one documentation links pointed at pre-rename filenames.** When the
guides moved from loose uppercase names to the `DF-0NN` series, the
cross-references in `04-component-tag.md`, `15-viewflow-mapping.md`, and
`COMPONENT_CASE_STUDIES.md` were not updated: `COMPONENT_SYSTEM.md`,
`ROUTING_SYSTEM.md`, `ARCHITECTURE_OVERVIEW.md`, `VIEWFLOW_MAPPING.md`,
`FORMS_TABLES_INTEGRATION.md`, `COMPONENT_TAG.md`, and `API_REFERENCE.md` all
resolved to nothing. One link also pointed at
`comp/routes/fragments.py`, which has never existed in the package. All now
resolve, and `tests/test_docs_links.py` keeps them resolving.
- **The shipped webpack workspace pointed the `fusion` entry at a path that does
  not exist.** `webpack/workspaces/default.js` resolved the library root as
  `path.resolve(__dirname, "..")`, but the file lives in `webpack/workspaces/`,
  so both its entry and its output directory landed under `webpack/` instead of
  the repository root. Because `webpack.config.js` spreads the workspace entry
  *over* its own correct base entry, this was not a harmless fallback: `make
  build` aborted with `Cannot find module` before emitting a bundle. The library
  root is now resolved two levels up, so the default entry is
  `src/django_fusion/assets/entry.js` and output goes to `static/bundles/` as
  documented. `tests/test_asset_pipeline.py` pins both the file set and the
  upward depth.

### Changed

- **The wheel now actually contains the package data.** Nothing declared
  `package-data` or a `MANIFEST.in`, so a built wheel installed an importable
  package with **no component templates** — failing only at render time inside a
  consumer. Both are now explicit, and the wheel ships ~53 templates, 17 SCSS
  partials, compiled builder CSS/JS, and `py.typed`.
- **Metadata modernized for PyPI** (PEP 639): `license = "MIT"` with
  `license-files`, SPDX-clean classifiers, `maintainers`, Django 5.1/5.2 and
  Python 3.13 classifiers, `Development Status :: 5 - Production/Stable`, and
  project URLs for releases and contact channels. The build backend is pinned to
  `setuptools>=77`.
- **`INSTALLED_APPS` guidance corrected.** Previous docs listed
  `django_fusion.core`, `django_fusion.health`, `django_fusion.analyzer`, and
  `django_fusion.config`, none of which are Django apps. The real app configs are
  `django_fusion`, `django_fusion.comp`, `django_fusion.fragments.analyzer`, and
  `django_fusion.builder`.
- **`django_fusion.__init__` docstring corrected.** It documented
  `django_fusion.core.models`, `django_fusion.core.services`, `django_fusion.wagtail`,
  and `django_fusion.web` — none of which exist — and `comp.templatetags` instead
  of `comp.tags`. It now documents the real tree and the real canonical imports.
- **Documentation completed and pruned** to the 28 files that describe this
  library: the `DF-000`–`DF-022` set, the package guide, component case studies,
  the forms & tables guide, and the two designer/MCP references. Stale links to
  `projects/`, `applications/`, and `libs/...` paths are gone.
- **Linting is now self-contained.** The package had no ruff configuration, so
  `ruff check` silently inherited whatever config sat in a parent directory and
  reported ~2,300 findings from rules the source never targeted. `pyproject.toml`
  now pins the lint configuration for this package, selecting real errors and
  pyflakes (`E4`, `E7`, `E9`, `F`). `E402` is explicitly ignored with a documented
  reason: Django tag libraries must create their `register = template.Library()`
  before importing the submodules that register into it, and optional-dependency
  tests must call `pytest.importorskip()` before importing the dependency.
  `src` and `tests` are now clean under this config.

### Added

- **`docs/23-publishing.md` (DF-023)** — a complete release runbook: the three
  places a version must agree, the pre-flight checklist, `uv build`,
  `twine check`, a wheel-contents check, a clean-environment wheel smoke test,
  API-token and `~/.pypirc` setup, TestPyPI rehearsal, production upload,
  trusted publishing via GitHub OIDC, tagging, and a rollback/yank table.
- **Release targets in the `Makefile`**: `version`, `test`, `lint`, `dist`,
  `check-dist`, `publish-test`, and `publish`. `make publish` is guarded — it
  refuses to run unless the working tree is clean and `HEAD` is exactly the
  `v<version>` tag.
- **`MANIFEST.in`** describing the sdist contents — including the Node asset
  build (`package.json`, `package-lock.json`, `webpack.config.js`, and
  `webpack/workspaces/*.js`) and the test suite, so a source distribution can run
  `make build` and `make test` without a separate checkout.
- **Library CI** (`.github/workflows/ci.yml`): pytest across Python 3.11/3.12 ×
  Django 4.2/5.2, a package job that builds and runs `twine check` plus a wheel
  smoke test, and a `ruff` job.
- **`tests/test_documented_import_paths.py`** — imports every canonical path the
  README, docstring, and docs advertise, so a rename fails the build instead of
  silently breaking documentation.
- **`tests/test_imports.py` and `tests/test_site_management_commands.py`** now pin
  the product-boundary rules: product modules and product seed commands must not
  reappear in the library.
- **`tests/test_site_auth_regression.py`** — pins the gettext-shadowing fix by
  asserting `_` is not a local of `process_registration`, and pins the
  enhancement plan's `guidance` key.
- **`tests/test_docs_links.py`** — resolves every relative link in the shipped
  documentation, so renames cannot leave the guides pointing at files that no
  longer exist.
- **`tests/analyzer/fixtures/`** with the real `page_card_grid.html` fragment and
  a README recording its provenance.

### Added — feature work carried over from the pre-release block

- **`FUSION_RENDER_MODE` + mixed mode** — the render-first boolean is now a
  three-way string setting (`FUSION_RENDER_MODE`: `render` | `data` | `mixed`);
  `FUSION_RENDER_FIRST` remains a deprecated bool alias. New
  `resolve_render_mode()` chain adds an `X-Fusion-Render-Mode` header, a
  session mode, per-route overrides (`FUSION_RENDER_MODE_ROUTES`), and
  Accept-header negotiation for `mixed` (JSON clients get data, browsers get
  HTML). `coerce_render_mode` / `resolve_render_mode_setting` live in
  `django_fusion.config.conf`.

- **`fusion_view` dual-mode function decorator** — decorate a plain
  function view that returns a Python object and it answers as either a
  render-first component (`template_name`, `data` in context) or a data
  API (`{status, message, data: {encoded, data, view_name}}` via
  `FusionCodec`), resolved through the canonical `resolve_render_first`
  chain. Options: `template_name`, `fusion_render_first` (per-view
  default), `force_data_mode`, `message`, `context_processors`.
  `dual_mode` provided as a backwards-friendly alias.

- **Render-first aware asset loading** — `AssetPipelineOptions` now carries
  `fusion_render_first` (resolved from `FUSION_RENDER_FIRST`, legacy
  `FUSION_RENDER_FIRST_DEFAULT` / `COMPONENTS_FUSION_RENDER_FIRST_DEFAULT`
  still accepted) and the merged manifest exposes it as
  `fusion_render_first`. New `FUSION_PIPELINE["render_first_gates_assets"]`
  toggle trims webpack/skeleton links from the manifest in data-api mode.

### Changed

- **Simplified setting names** — `FUSION_ASSET_PIPELINE` → `FUSION_PIPELINE`,
  `FUSION_RENDER_FIRST_DEFAULT` → `FUSION_RENDER_FIRST`, and
  `FUSION_COMPONENT_ASSETS` → `FUSION_COMPONENTS`. The old names remain
  supported as fallbacks so existing projects keep working unmodified.
  The settings singleton exposes the shorter `render_first_default`
  attribute (legacy `FUSION_RENDER_FIRST_DEFAULT` property kept).

- **`django_fusion.mcp` package** — reusable FastAPI routers for django-fusion
  MCP servers:
  - `FusionMCPRouter` — `/health`, `/django-fusion/info`,
    `/django-fusion/viewsets`, `/auth/features` endpoints with lazy
    import-safe Django probes.
  - `django_fusion.mcp.prompts` — generalized prompt catalog loader with
    configurable `FUSION_MCP_PROMPT_CATALOG_PATH` Django setting, schema
    validation, and agent/skill cross-referencing. Falls back gracefully
    when django-fusion is unavailable so prompt tests remain import-safe.
- **`DesignerMCPRouter`** (`plugins/designer/mcp_router.py`) — FastAPI router
  with 6 GET endpoints and 1 POST JSON-RPC endpoint for the interactive
  designer:
  - `GET /designer/tools` — list all 8 designer tools with MCP metadata.
  - `GET /designer/component-catalog`, `/wagtail-field`, `/form-scaffold`,
    `/table-scaffold`, `/preview` — simplified query-param endpoints.
  - `POST /designer/tools/call` — full JSON-RPC `tools/call` endpoint for
    all 8 tools including complex `website_audit`, `webapp_enhancement_plan`,
    `validate`, and field-rich form/table scaffolds.
- **API-key authentication** on `DesignerMCPRouter` — two-tier auth policy
  mirroring `designer/views.py._is_allowed`:
  - API-key mode: when `FUSION_MCP_DESIGNER_API_KEY` is set (env, Django
    settings, or constructor), requires matching `X-API-Key` header.
  - Localhost fallback: when no key is configured, allows only `127.0.0.1`,
    `::1`, `localhost` callers; remote callers receive 403.
- **Analyzer schema extensions** (Phase 1.1) — `Component` gains `skeleton`
  and `skeleton_config` fields; `Page` gains `dependencies` and
  `load_priority`; `PageComponentUsage` gains `skeleton_order`. All
  backward-compatible with sensible defaults.
- **Per-project webpack support** — `projects/webpack/base.config.js` with
  django-fusion alias resolution, `@<project>` aliases per site, and
  `django-webpack-loader` integration for `{% render_bundle %}`.

### Changed

- **Designer moved to plugins.** `django_fusion.designer` is now a backward-
  compatible shim; canonical imports live at `django_fusion.plugins.designer`.
  All handlers, tools, views, and URLs were copied to the new location with
  forward-import shims left in the old package. No public API breakage.
- **Designer is project-generic.** Hardcoded project enums
  (`["precis-landing", "precis", "formint"]`) were removed from `tools.py` and
  `website.py`. The `project` field is now `{"type": "string", "minLength": 1}`
  — the designer works with any project. Projects customize audit guidance
  via `FUSION_AUDIT_GUIDANCE` in their Django settings.
- **`comp.templatetags` → `comp.tags`.** Template tag modules were moved from
  `comp/templatetags/` to `comp/tags/` with backward-compatible shims in the
  old location. All 59 references across source and tests were updated.
  Template tags continue to load via Django's `templatetags` auto-discovery.
- **Prompt catalog delegated to django-fusion.** The Kilo prompt catalog
  (`.agents/mcp/prompt_catalog.py`) now delegates to
  `django_fusion.mcp.prompts` when django-fusion is available, falling back
  to local implementation for standalone use.
- **Kilo MCP server simplified.** `.agents/mcp/mcp_server.py`
  reduced by ~250 lines. Now imports `FusionMCPRouter` and
  `DesignerMCPRouter` from django-fusion, keeping only Structa-Cloud-specific
  infrastructure endpoints (Docker, Traefik, OpenRouter, ceptor-ai).

## [0.5.0] — 2026-08-10

### Added

- **Unified asset pipeline options** via `AssetPipelineOptions` and
  `FUSION_PIPELINE`, merging explicit `FUSION_ASSETS`, component
  manifests, and webpack `bundles.json` links for API and template-tag use.
- **Canonical asset-link deduplication** for top CSS and bottom JS entries,
  preserving source/generated filesystem boundaries.

### Changed

- **Breaking: slot content now renders exactly once.** `{% slot %}` content
  supplied by the caller is stored as a raw `NodeList` by
  `BoundComponent.fill_slots` and rendered a single time by `SlotNode`.
  Previously the caller's nodelist was eagerly rendered to a string and then
  re-parsed as a brand-new template, double-rendering every `{{ }}` / `{% %}`
  sequence in the slot body. Empty caller nodelists now fall back to the
  component's own fallback body; legacy pre-rendered string slots are emitted
  verbatim. Components that intentionally echoed template syntax through a
  slot will render differently and must pass already-rendered markup instead.
- **Breaking: props are exposed as bare context variables.** Resolved props
  are pushed both as the `{{ props.name }}` mapping (unchanged) and as bare
  context variables (`{{ name }}`, django-cotton style), so component
  templates written either way resolve the same values. A declared-but-unpassed
  prop now resolves to `None` and *shadows* any outer-context variable of the
  same name; previously the name fell through to the parent context. Components
  that relied on implicit outer-context leakage of a prop name must now pass
  the value explicitly (e.g. `{% comp "x" name=name /%}`).
- **`{% prop name default=X %}` (kwarg-style) now resolves its default.** The
  `default=` bit was previously parsed and silently dropped, so the prop
  always resolved to `None`; the default is now applied. Both documented forms
  (`{% prop name="default" %}` and `{% prop name default="v" %}`) are
  supported.

### Removed

- Removed the `django_fusion.plugins.bolt` integration package (`FusionBoltAPI`,
  `FusionBoltAuthBackend`, `FusionBoltDualModeMixin`, `fusion_endpoint`, and
  `component_serializer`). API frameworks and authentication bridges now belong
  to consuming projects; django-fusion remains responsible for Django routing,
  components, fragments, and data-response primitives.
- Removed the unused `django_fusion.plugins.webpack.assets` forwarding package;
  asset views and URL patterns now have one canonical source under
  `django_fusion.core.assets`.
- Removed the LMS-only `/api/fusion/assets/` and `/apis/fusion/assets/` URL
  aliases. Sites should expose one project-owned mount of
  `django_fusion.core.assets.urls` (LMS uses `/fusion/assets/`; CMS uses
  `/apis/assets/`). Existing external clients must update their asset API URL.

### Fixed

- **`{% slot %}` content no longer double-renders.** `fill_slots` stored an
  eagerly rendered string that `SlotNode` then re-parsed as a new template,
  evaluating the caller's `{{ }}` / `{% %}` twice (and, for stored `SlotNode`
  objects, recursing infinitely via the `context["slots"]` lookup). Slots now
  hold raw nodelists rendered exactly once; a nested component's default slot
  passed through `{{ slot }}` is rendered a single time with the component
  context.
- `generate_asset_manifest` now imports the canonical implementation from
  `django_fusion.config.manifest` without a duplicate `comp.manifest` path.
- **Model-scoped cache invalidation** — `CachingStorage.clear_model_cache()`
  is now implemented (it was already referenced by
  `ModelCacheMixin.invalidate_all_cache()` but had no definition, raising
  `AttributeError` on model saves). Cached entries are tracked in a per-model
  key registry guarded by an in-process lock, so concurrent
  `cache_set`/`cache_delete` calls cannot lose registrations. Registries are
  bounded: entries whose data already expired are pruned once the registry
  exceeds `MAX_REGISTRY_KEYS`, and model-wide clearing skips (does not count)
  already-expired entries.

## [0.4.0] — 2026-07-28

### Added

- **`webpack_loader` optional dependency** — `pip install django-fusion[webpack]`
  installs `django-webpack-loader>=3.2.3` for webpack bundle integration.
- **Dual assets URL mount** — assets endpoints now served at both
  `/fusion/assets/` (original) and `/apis/fusion/assets/` (for Next.js
  API proxy compatibility).

### Fixed

- Assets endpoints return 200 at `/apis/fusion/assets/*` — previously
  only mounted at `/fusion/assets/*`, causing 404s when proxied through
  the Next.js API middleware.

## [0.3.0] — 2026-07-28

### Added

- **Assets pipeline** (`django_fusion.core.assets`) — API endpoints and
  template tags for dynamic asset manifests. Provides
  `GET /fusion/assets/top/`, `/bottom/`, and `/manifest/` endpoints
  that describe which CSS, font, and JS assets the frontend should load.
- **`fusion_assets` template tags** — `{% fusion_top_assets %}`,
  `{% fusion_bottom_assets %}`, `{% fusion_assets_manifest %}` for
  server-side asset injection in Django/Wagtail templates.
- **`FUSION_ASSETS` Django setting** — per-project configuration for
  top (CSS, fonts, preconnect) and bottom (JS, inline JS) assets.
- **`docs/16-assets.md` (DF-016)** — full documentation covering views,
  wiring, config, response shapes, template tags, and Next.js integration.

## [0.2.0] — 2025-07-11

### Added

- **MIT `LICENSE`** at repo root.
- **`CONTRIBUTING.md`** with local dev setup, `DJANGO_DEBUG_CONFTEST=1`
  diagnostic flag, commit conventions, and `DF-0NN` doc-ID discipline.
- **`CHANGELOG.md`** (this file), seeded with 0.2.0 + 0.1.0 entries.
- **GitHub Actions workflow** — staged at `docs/ci/tests.yml` and
  manually restorable at `.github/workflows/tests.yml` (see Workaround
  below). Runs `pytest` on Python 3.11 / 3.12 across Django 4.2 / 5.0.
- **`docs/INDEX.md`** (DF-000) — single source of truth for the doc
  library, with stable `DF-0NN` IDs. Replaces `docs/DOCUMENTATION_MAP.md`
  (removed).
- **Fifteen doc files** under `docs/` numbered by DF-ID, sourced from
  the real source tree under `src/django_fusion/`:
  - DF-001 Getting Started (install, INSTALLED_APPS, template builtins)
  - DF-002 Architecture (module map + Mermaid)
  - DF-003 Component System (Python side: registry, routes, fragments)
  - DF-004 `{% comp %}` Template Tag (renamed from COMPONENT_TAG.md)
  - DF-005 Routing (Site, Application, Viewset, ModelViewset family)
  - DF-006 Forms & Tables (deep reference, not a QUICKSTART repeat)
  - DF-007 Configuration (settings, Dynaconf, cache, middleware order)
  - DF-008 API Reference (generated from real docstrings)
  - DF-009 Health Checks (views, JSON shape, Docker/K8s probes)
  - DF-010 Wagtail Integration (blocks, snippets, viewsets)
  - DF-011 Best Practices (patterns from COMPONENT_CASE_STUDIES)
  - DF-012 Integration Examples (end-to-end walkthroughs)
  - DF-013 Troubleshooting (symptom→cause→fix from real test edge cases)
  - DF-014 FAQ (from real test edge cases)
  - DF-015 Viewflow / django-material Mapping (renamed from VIEWFLOW_MAPPING.md)
- **`docs/legacy/django-grep-legacy/`** — renamed from
  `docs/legacy-django-grep/` (deprecated; keep as historical reference only).

### Removed

- `docs/DOCUMENTATION_MAP.md` — superseded by `docs/INDEX.md`. Its many
  dead `✅ Complete` rows were the original motivating problem.
- Monorepo-path references (`applications/libs/django-fusion/...`) in
  `README.md`, `AGENTS.md`, `PROMPTS.md`, `QUICKSTART.md`, and existing
  docs. Replaced with repo-relative paths **and** documented dual
  install instructions (standalone PyPI + monorepo submodule).
- Empty `COMPONENT_CASE_STUDIES.md` was archived; its content is
  referenced from `docs/12-integration-examples.md` (DF-012). The
  archive copy lives at `docs/COMPONENT_CASE_STUDIES.md.bak`.

### Fixed

- Documentation index no longer lists ~20 missing files as
  `✅ Complete`. Every row in `docs/INDEX.md` reflects actual file
  existence.
- Install path: `pip install -e applications/libs/django-fusion`
  (broken outside the Structa Cloud monorepo) replaced by
  `pip install django-fusion` for standalone, with the monorepo
  `pip install -e projects/libs/django-fusion` variant documented.

### Changed (pyproject.toml for PyPI readiness)

- Added: `license = {text = "MIT"}`
- Added: `readme = "README.md"`
- Added: `authors = [{name = "Structa Cloud Team", email = "dev@structa.cloud"}]`
- Added: `classifiers` (Framework :: Django, OS :: POSIX, Python :: 3.11/3.12,
  Development Status :: 4 - Beta, License :: OSI Approved :: MIT License)
- Added: `[project.urls]` (Homepage, Repository, Issues, Documentation)
- Added: `pytest-django` to `[project.optional-dependencies].test`

### Workaround: GitHub Actions workflow staged in `docs/ci/`

While the v0.2.0 hygiene content is pushed via `make push-libs`
(parent Structa Cloud monorepo), the Personal Access Token configured
on the parent monorepo lacks the **`workflow`** OAuth scope required by
GitHub to create or update files under `.github/workflows/*.yml`.

GitHub refuses pushes with:

```
remote: Refusing to allow a Personal Access Token to create or update workflow
`.github/workflows/tests.yml` without `workflow` scope.
```

To unblock the rest of the v0.2.0 push without changing the PAT's scope
on this repo, the workflow definition lives at **`docs/ci/tests.yml`**
(staging area inside the repo — not active, not eligible to be
auto-triggered by GitHub). The stage-and-restore flow is:

```bash
# After `make push-libs` succeeds (which proves the v0.2.0 docs and
# pyproject landed), restore CI on .github/workflows/tests.yml:

mkdir -p .github/workflows
cp docs/ci/tests.yml .github/workflows/tests.yml

# Commit & push from inside the submodule, with a token that has the
# `workflow` scope:
git -C projects/libs/django-fusion add .github/workflows/tests.yml
git -C projects/libs/django-fusion commit -m "ci: restore GitHub Actions workflow from docs/ci staging"
git -C projects/libs/django-fusion push origin generic
```

If the v0.2.0 push succeeds and CI is otherwise healthy, this
restoration step may be skipped — `docs/ci/tests.yml` is also a
runnable workflow template when copied to `.github/workflows/`.

## [0.1.0] — 2024-12-01

Initial public release. Merged the former `django_fusion` compatibility shim
into the standalone `django-fusion` package.

### Features

- Component system: `RoutableComponent`, `FragmentComponent`, fragment
  registry, lazy/HTMX-safe template loaders.
- Routing: `Site`, `Application`, `AppMenuMixin`, `Viewset` /
  `BaseViewset` / `ViewsetMeta`, `Route` / `route`, `menu_path`,
  `viewprop`, ModelViewset family with CRUD mixins.
- Generic CBVs: `ListModelView`, `CreateModelView`, `UpdateModelView`,
  `DeleteModelView`, `DetailModelView`, `DeleteBulkActionView`,
  `SearchableViewMixin`, `TableView`.
- Component template tag `{% comp %}` with `{% prop %}`,
  `{% slot %}`, `{% var %}`, `{{ props.* }}`, `{{ vars.* }}`, `{{ attrs }}`,
  `fragment_name=` for HTMX scoping. (See DF-004.)
- Forms & tables mixins: `FormMixin`, `TableMixin`, `FormTableMixin`
  with template-resolution cascade. (See DF-006.)
- Site layer: auth mixins (allauth), context processors (`auth`,
  `cookies`, `htmx`, `languages`), notifications, pagination.
- Wagtail integration: StreamField blocks (`CallToActionBlock` and
  others), `AuthEmailTemplate` snippet, viewsets. (See DF-010.)
- Health checks: `HealthCheckView`, `DatabaseHealthView`,
  `AssetsHealthView` plus `health.urls` for `include(health_urls)` wiring.
  (See DF-009.)
- Contrib: custom admin, cache utils, debug tools,
  privacy/consent middleware, Pydantic schemas.
- Dynaconf-based multi-environment YAML config loader.
- Component analyzer/parser for templates.
- `DJANGO_DEBUG_CONFTEST=1` opt-in diagnostic flag in conftest.

[0.1.0]: https://github.com/mammhoud/django-fusion/releases/tag/v0.1.0
[0.2.0]: https://github.com/mammhoud/django-fusion/releases/tag/v0.2.0
[0.5.0]: https://github.com/mammhoud/django-fusion/releases/tag/v0.5.0
[2.0.2]: https://github.com/mammhoud/django-fusion/releases/tag/v2.0.2
