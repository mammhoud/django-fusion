# Changelog

All notable changes to django-fusion are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
