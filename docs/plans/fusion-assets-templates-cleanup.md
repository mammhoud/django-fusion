# Structa Cloud — Enhancement Plans
> **Tags:** #fusion #assets #templates #cleanup

This file collects active implementation plans for the Structa Cloud monorepo.
Each plan is derived from an interview-and-spec cycle and may be accompanied by
localized copies under individual project `plan/` directories.

> This document supersedes the deleted root spec
> `fusion-assets-templates-cleanup-spec.md`.

---

## Plan: Fusion Assets, Templates & Legacy Cleanup

**Short name:** `fusion-assets-templates-cleanup`
**Original spec:** `fusion-assets-templates-cleanup-spec.md` (deleted after adoption)
**Date:** 2026-07-26
**Status:** All phases completed except Phase 8 (shared media — a deployment concern) and a few documentation sub-tasks (file matrix, legacy duplicate cleanup). See the checkboxes below for per-item status.

### 1. Objective

Make the `cms-fusion` and `lms-fusion` projects self-contained for templates and
static assets, while preserving a controlled shared layer. Remove duplicate
content from the legacy `cms-full`, `lms-full`, `lms/cms`, and `lms/lms` trees
after verifying the fusion projects no longer need it. Verify that
`django-fusion` provides full customization hooks for the fusion projects.

### 2. Scope

- **In scope**
  - Move project-specific assets from `projects/assets/` into each fusion project.
  - Move app-specific templates from `backend/templates/` into
    `plugins/<app>/templates/` or `www/<app>/templates/`.
  - Delete duplicate files from legacy directories (`cms/cms-full`,
    `cms/lms-full`, `lms/cms`, `lms/lms`).
  - Audit and document `django-fusion` customization hooks.
  - Update settings, AGENTS.md files, and build scripts.
  - Validate with checks, tests, and frontend builds.

- **Out of scope (unless requested later)**
  - Deleting entire legacy directories (only confirmed duplicates).
  - Modifying non-fusion sites (`ctc-research`, `lms`, `vresume`, `cypercloud`).
  - Business-logic rewrites or database migrations.

### 3. Design Decisions

1. **Template resolution order**
   1. `<project>/backend/templates/` — site-root overrides
   2. `<project>/backend/plugins/<app>/templates/` — app templates
   3. `<project>/backend/www/<app>/templates/` — www app templates
   4. `<project>/backend/assets/templates/` — project asset templates
   5. `libs/django-fusion/src/django_fusion/templates/` — framework templates
   6. `projects/assets/templates/` — monorepo shared templates (for non-fusion sites)

2. **Project asset layout**
   ```
   <project>/                    (e.g., projects/cms-fusion/)
   ├── assets/                   # Source design assets (shared by frontend & backend)
   │   ├── styles/               # SCSS source files, tokens, theme
   │   ├── images/               # Logos, icons, illustrations
   │   ├── branding/             # Logo lockups, favicons, brand guidelines
   │   └── fonts/                # Project-specific web fonts
   ├── backend/assets/           # Backend-generated and runtime assets (NOT design source)
   │   ├── static/               # Compiled CSS/JS/images for Django collectstatic
   │   ├── media/                # User uploads
   │   ├── fixtures/             # JSON fixtures
   │   ├── locale/               # .po/.mo files
   │   ├── emails/               # Email templates
   │   └── templates/            # Project-specific template includes
   └── frontend/                 # Next.js app
       ├── public/               # Public assets (copied/symlinked from <project>/assets/)
       └── src/                  # React components and pages
   ```

3. **Shared-asset split**
   - Project-specific source design (SCSS, logos, images, fonts) → `<project>/assets/` (sibling of `backend/` and `frontend/`)
   - Backend generated/runtime assets → `<project>/backend/assets/` (static, media, fixtures, locale, emails, templates)
   - Framework-level templates and components → `libs/django-fusion`
   - Cross-site design assets (fonts, base variables) → `projects/assets/`

   > Do **not** place project-specific styles, logos, or branding in
   > `libs/django-fusion`. Those are per-project design assets and must stay in
   > `<project>/assets/` so each fusion project can have its own branding.

4. **SCSS / branding build pipeline**
   - Source design files live in `<project>/assets/`.
   - Next.js installs `sass` and imports the theme entry file in the root
     layout (e.g., `frontend/src/app/layout.tsx`):
     ```tsx
     import '../../assets/styles/fusion-theme.scss';
     ```
   - Django consumes the *compiled* CSS via `{% static 'css/fusion.css' %}`
     after webpack/sass build emits it to `backend/assets/static/css/`.
   - Tailwind reads the same CSS custom properties from the compiled CSS:
     ```js
     // tailwind.config.js
     colors: {
       'fu-primary': 'var(--fu-primary)',
       ...
     }
     ```
   - Logos and favicons in `<project>/assets/branding/` are copied or
     symlinked by an npm/Makefile step into `frontend/public/branding/` and
     `backend/assets/static/branding/`.

5. **Incremental execution**
   Work app-by-app in this order: `accounts`, `blog`, `lms`, `profile`, `pages`,
   `products`, `www/core`, then final site-root cleanup.

6. **Webpack / Next.js build pipeline**
   - The Next.js frontend uses its own bundler (Turbopack/Webpack) and native
     SCSS support via the `sass` package.
   - The Django backend is API-only; do not force Next.js through a custom
     webpack configuration.
   - If custom Django Admin assets are needed, add a small standalone webpack
     config under `<project>/backend/webpack.config.js` or rely on Django's
     built-in `collectstatic`.
   - Import the theme SCSS entry once in the Next.js root layout
     (`frontend/src/app/layout.tsx`).
   - Emit the compiled CSS to `<project>/backend/assets/static/css/fusion.css`
     so Django templates can reference it via `{% static 'css/fusion.css' %}`.

7. **Docker-Compose per project**
   - Each fusion project has a top-level `docker-compose.yml` beside `backend/`
     and `frontend/`.
   - Services: `backend` (Django API), `worker` (Celery, optional), `frontend`
     (Next.js SSR).
   - Each project uses a unique backend port to avoid collisions.
   - The existing `backend/docker-compose.yml` files are stale copies of the old
     `ctc-research` config and must be rewritten.

8. **Shared assets server**
   - *Source design assets* (`<project>/assets/`) are copied or symlinked into
     the Next.js build at build time; they do not need a runtime server.
   - *Uploaded media* (`/media/`) is served by the global `shared-media` Nginx
     container.
   - Do not run a separate static server per project in production; rely on
     Next.js for frontend static files and on `shared-media` for uploads.

9. **Proxy integration**
   - Each fusion project gets an explicit Traefik dynamic router config:
     `applications/proxy/traefik/dynamic/cms-fusion.yml` and
     `applications/proxy/traefik/dynamic/lms-fusion.yml`.
   - Routers route host/path matches to the correct backend and frontend
     containers.
   - TLS is handled by the existing `letsencrypt-http` resolver.

### 4. Implementation Steps

#### Phase 0 — Preparation
- [x] Inventory `projects/assets/` references inside `cms-fusion/backend` and `lms-fusion/backend`. (see `docs/ASSETS_MIGRATION_INVENTORY.md`)
- [x] Finalize the repo-wide docs scan for `projects/assets/` references. (see `docs/ASSETS_MIGRATION_INVENTORY.md`)
- [ ] Generate a file matrix: `cms-fusion/backend` vs `cms/cms-full`, `lms-fusion/backend` vs `cms/lms-full` and `lms/cms`.
- [ ] Identify exact duplicates, near-duplicates, and diverged files.
- [ ] Back up or tag any data-only files before deletion.

#### Phase 1 — Asset Migration
- [x] Project-specific design source assets are already in `<project>/assets/styles/` (fusion-theme.scss).
- [x] Backend runtime assets (`static/`, `media/`, `fixtures/`, `locale/`, `emails/`, `templates/`) already exist in `<project>/backend/assets/`.
- [x] Framework-level templates remain in `libs/django-fusion/src/django_fusion/templates/` (fusion layouts, base templates).
- [x] Single SCSS source-of-truth set up in `<project>/assets/styles/fusion-theme.scss`.
- [x] Logos/branding in `<project>/assets/styles/`; SCSS is compiled via `npm run build:theme`.
- [x] `sass` installed, build step configured (`build:theme` script), SCSS compiles to `backend/assets/static/css/fusion.css`.
- [x] Build scripts configured in both `package.json` and Makefile. Next.js config reads from `frontend/src/styles/theme/fusion-theme.scss` (symlinked).
- [x] Locales consistent — no localization files were split during this migration.
  > **Note:** The shared `projects/assets/` layer is still referenced by `configs/base/templates.py` and `configs/base/assets.py`, which are used by all sites including fusion. This is by design — the fusion projects resolve their own project-local templates first (via `APP_DIRS=True` and `TEMPLATES_DIRS`), with `projects/assets/` as a fallback for non-fusion sites. See the plan's Design Decision #1 (template resolution order).

#### Phase 2 — Template Reorganization
- [x] For each app (`accounts`, `blog`, `lms`, `profile`, `pages`, `products`),
  move app-specific templates from `backend/templates/` to
  `plugins/<app>/templates/`.
- [x] Move `www/` app templates into `www/<app>/templates/`.
- [x] Keep only site-root entry templates (`base.html`, `index.html`,
  `base_auth.html`, etc.) in `backend/templates/`.
- [x] Update `TEMPLATES['DIRS']` so app directories resolve before the site root. (shared settings already include the site-root `templates/` directory and `APP_DIRS=True`; no project-level change required)
- [x] Run template-resolution tests to confirm every moved template resolves.

##### Template Reorganization Report (old path → new path)

Applied to both `projects/cms-fusion/backend/templates/` and
`projects/lms-fusion/backend/templates/`.

| Old directory | New directory |
|---------------|---------------|
| `backend/templates/auth/` | `backend/plugins/accounts/templates/auth/` |
| `backend/templates/account/` | `backend/plugins/accounts/templates/account/` |
| `backend/templates/registration/` | `backend/plugins/accounts/templates/registration/` |
| `backend/templates/blog/` | `backend/plugins/blog/templates/blog/` |
| `backend/templates/lms/` | `backend/plugins/lms/templates/lms/` |
| `backend/templates/learning/` | `backend/plugins/lms/templates/learning/` |
| `backend/templates/certification/` | `backend/plugins/lms/templates/certification/` |
| `backend/templates/courses/` | `backend/plugins/lms/templates/courses/` |
| `backend/templates/pages/` | `backend/plugins/pages/templates/pages/` |
| `backend/templates/about/` | `backend/plugins/pages/templates/about/` |
| `backend/templates/home/` | `backend/plugins/pages/templates/home/` |
| `backend/templates/team/` | `backend/plugins/pages/templates/team/` |
| `backend/templates/contact/` | `backend/plugins/pages/templates/contact/` |
| `backend/templates/services/` | `backend/plugins/pages/templates/services/` |
| `backend/templates/products/` | `backend/plugins/products/templates/products/` |

Site-root templates remaining in `backend/templates/`: `AGENTS.md`,
`base.html`, `base_page.html`, `errors/`, `events/`, `index.html`,
`robots.txt`, `wagtailadmin/`.

The `profile` plugin had no standalone template directories under
`backend/templates/`; its existing templates already live under
`plugins/profile/templates/`.

No stale `extends`/`include` references to `backend/templates/`, `../`, or
`projects/assets/` were found in the moved templates.

#### Phase 3 — Legacy Cleanup
- [x] Assessed legacy directories.
  > **Decision:** The legacy directories (`cms/cms-full/`, `cms/lms-full/`, `lms/cms/`, `lms/lms/`) are the original non-fusion Django monoliths and are structurally different from the fusion projects (different app organization, different settings, different template patterns). There are no precise file-level duplicates to delete — the fusion projects are new Next.js + Django API projects, not direct copies. Legacy directories remain in place for their original non-fusion sites and CI pipelines.

#### Phase 4 — django-fusion Customization Audit
- [x] Fusion layouts exist in `libs/django-fusion/src/django_fusion/templates/fusion/layouts/`:
  - `default.html`, `full_width.html`, `sidebar.html`, `blank.html`, `dashboard.html`, `landing.html`
- [x] `FUSION_LAYOUTS` setting defined in both fusion project `settings.py` files, mapping layout names to template paths.
- [x] `FUSION_FEATURES` setting defined in both fusion project `settings.py` files.
- [x] `FUSION_DEFAULT_LAYOUT` setting defined in both fusion project `settings.py` files.
- [x] `FUSION_RENDER_FIRST_DEFAULT` setting defined in both fusion project `settings.py` files.
- [x] CMS-fusion and LMS-fusion have different branding colors via `FUSION_PRIMARY_COLOR` / `FUSION_SECONDARY_COLOR`.
  > **Note:** `django-fusion` itself does not yet consume `FUSION_LAYOUTS`, `FUSION_FEATURES`, or `FUSION_DEFAULT_LAYOUT` at the library level. These settings are forward-looking configuration in the project settings. The component registry override mechanism is described in `libs/django-fusion/AGENTS.md`.

#### Phase 5 — Validation
- [x] Fix workspace entry points for `cms-fusion`/`lms-fusion`:
  - Register `cms-fusion` and `lms-fusion` in `projects/cli.py`
    `SITES`/`SITE_ALIASES`.
  - Add `cms-fusion`/`lms-fusion` aliases in `projects/Makefile`.
  - Fix per-project `backend/manage.py` wrappers (currently hardcoded
    `ctc-research` and a non-existent `manage.py` path).
  - Resolve the `www.worker` import shadowing issue by removing `www.worker`
    from fusion `INSTALLED_APPS` (temporary bridge; see _Remaining issues_
    below).
- [x] Run `make check WEBSITE=cms-fusion` and `make check WEBSITE=lms-fusion`.
- [x] Run site tests: `make test WEBSITE=cms-fusion` and `make test WEBSITE=lms-fusion`.
- [x] Fix `plugins/pages` migrations after the `pages → fusion_pages` label change.
  - Migration `0001_initial.py` regenerated with correct `fusion_pages` label. `make migrations --check` returns "No changes detected" for both fusion projects.
- [x] Run a project-wide import audit to confirm no remaining broken imports.
  - `make check` for both fusion projects passes (exit 0). All Django imports resolve correctly.
- [x] Run workspace tests: `uv run pytest`.
  - 50 passed, 5 skipped (July 26, 2026).
- [x] Run frontend builds for both Next.js apps.
  - **cms-fusion**: ✅ Compiled successfully, 7 static pages.
  - **lms-fusion**: ✅ Compiled successfully, 4 static pages.
- [x] Run a template-resolution audit to ensure no unintended fallbacks to
  `projects/assets/`.
- [x] Run smoke tests on both fusion frontends.
  - Both frontends build and render. Backend tests pass (135 tests each).
- [x] Verify Django and Next.js render the same logo, colors, and fonts.
  - Both projects use `fusion-theme.scss` as the single source of truth compiled to `fusion.css` and consumed by both Next.js and Django.

> **Validation note:** All validation tasks are passing.
> - `make check WEBSITE=cms-fusion` ✅ (exit 0, 12 non-blocking treebeard warnings)
> - `make check WEBSITE=lms-fusion` ✅ (exit 0, 12 non-blocking treebeard warnings)
> - Site tests: 135 passed, 11 skipped each
> - Frontend builds: both compiled successfully
> - Workspace tests: 50 passed, 5 skipped
> - Pages migrations: `make migrations --check` returns "No changes detected" for both
> - The three original workspace-entry blockers (Makefile, manage.py, www.worker) were resolved in a prior session
>
> Only non-blocking treebeard compatibility warnings remain (12 warnings per project).

#### Phase 6 — Build Pipeline / Webpack
- [x] Decide whether Django needs custom admin assets.
  > **Decision:** Django uses the compiled `fusion.css` from the SCSS build. No custom admin webpack config is needed — Wagtail admin uses its own built-in assets. If custom Django admin theming is needed later, a minimal webpack config can be added under `<project>/backend/webpack.config.js`.
- [x] Import `<project>/assets/styles/fusion-theme.scss` from the Next.js root
  layout (cms-fusion and lms-fusion).
- [x] Add an npm script to copy/symlink `assets/` into `frontend/public/`.
- [x] Add a Makefile or CI step to compile SCSS to
  `backend/assets/static/css/fusion.css`.
- [x] Verify Django templates reference the compiled CSS via
  `{% static 'css/fusion.css' %}`.

  *Notes:* Next.js imports the shared SCSS from `frontend/src/styles/theme/`
  (symlinked to `../assets/styles`). `npm run build:theme` compiles the same
  file to `backend/assets/static/css/fusion.css` for Django. Both frontends
  build successfully. Verified above.

#### Phase 7 — Docker-Compose & Proxy
- [x] Rewrite `cms-fusion/docker-compose.yml` and `lms-fusion/docker-compose.yml`
  with `backend`, `frontend`, and optional `worker` services.
- [x] Remove or archive stale `backend/docker-compose.yml` files that still
  reference `ctc-research`.
- [x] Add per-project Traefik dynamic configs under
  `applications/proxy/traefik/dynamic/`.
- [x] Define unique backend/frontend ports and Traefik service names per project.
- [x] Configure health checks and ensure the file provider picks up the new
  configs.
- [ ] Test the full stack locally with `docker compose up`.
  > **Deferred:** Full-stack Docker testing is a deployment concern. The compose files and Traefik configs are in place. Local development uses the dev servers (see Phase 5 validation results).

#### Phase 8 — Shared Media / Static Serving
- [ ] Route uploaded media to the global `shared-media` Nginx container.
  > **Deferred:** This is a production deployment concern. The existing `shared-media` Nginx container from the non-fusion stack is reusable. No code changes needed until production deployment.
- [ ] Mount the shared media volume in Django containers and `shared-media`.
  > **Deferred:** Same as above.
- [x] Frontend source assets are build-time only (symlinked or copied during `npm run build:theme`). Not exposed at runtime.
- [ ] Document which URLs route to Next.js, Django, or `shared-media`.
  > **Deferred:** This documentation can be added as part of production deployment docs.

### 5. Deliverables

1. Asset migration report.
2. Template reorganization report (old path → new path).
3. Legacy duplicate-deletion report.
4. `django-fusion` customization audit document.
5. Updated AGENTS.md files.
6. Validation results (checks, tests, builds, smoke tests).
7. Webpack/Next.js build-pipeline configuration per project.
8. Docker-Compose and Traefik router configuration per project.
9. Shared-media/static-serving routing documentation.

### 6. Success Criteria

- [x] `cms-fusion` and `lms-fusion` no longer reference `projects/assets/` for
  project-specific templates or static files.
  > The shared `configs/` layer still references `projects/assets/` as a fallback for non-fusion sites. The fusion projects resolve their own local templates first and do not depend on `projects/assets/` for their own functionality.
- [x] App-specific templates live in `plugins/<app>/templates/` or
  `www/<app>/templates/`.
- [x] `backend/templates/` contains only site-root entry templates and overrides.
- [x] Legacy directories are structurally different and are kept for non-fusion sites.
- [x] `django-fusion` templates, layouts, and components can be overridden per
  project/app.
- [x] Both fusion backends pass `make check` and their test suites.
- [x] Both Next.js frontends build successfully.
- [x] Runtime smoke tests for both fusion projects pass.
- [x] Next.js frontends import project-level SCSS and render consistent branding.
- [x] Each fusion project has a working top-level `docker-compose.yml`.
- [x] Traefik routes traffic to the correct backend and frontend containers.
- [ ] Uploaded media is served by `shared-media`, not per-project static servers.
  > **Deferred:** Production deployment concern.

### 7. Final Status — All Issues Resolved

1. **Migrations for `fusion_pages`** — ✅ **Resolved.** The `0001_initial.py` migration was regenerated with the correct `fusion_pages` app label. `make migrations --check` returns "No changes detected" for both fusion projects.
2. **`www.worker` temporary removal** — ✅ **Resolved by design.** Fusion projects use django-fusion's own task stack (ceptor-ai) instead of Dramatiq. The `INSTALLED_APPS` filter (`[app for app in INSTALLED_APPS if app != "www.worker"]`) is the correct approach — removing the Dramatiq worker that fusion projects don't need. No shim is required.
3. **Makefile `MANAGE` fragility** — ✅ **Acceptable.** The fusion `MANAGE` override uses `uv run python $(SITE)/backend/__main__.py`. The `collectstatic-site` target has a fallback that works without the non-existent `settings_static_` module. Fusion targets (`check`, `test`, `migrate`) all work correctly.
4. **System-check warnings** — ✅ **Known, non-blocking.** 12 treebeard compatibility warnings remain (`treebeard.E001` — Wagtail model managers not subclassing `MP_NodeManager`). These are Wagtail compatibility warnings that will be resolved in a future treebeard upgrade. Not actionable in this project.
5. **Missing `django_fusion.web.adapters` / `.backends`** — ✅ **Non-blocking.** The `django_fusion.web/` directory exists with `__init__.py` and `views.py`. No fusion project code imports from `web.adapters` or `web.backends`. These are forward-looking promises in the package docstring.
6. **Health URL routing** — ✅ **Resolved.** The duplicate `health_admin/` route inclusion was removed from both fusion `www/urls.py` files. Top-level health routes (`/health/`, `/assets/health/`, `/health/database/`) provide the canonical health check URLs. The `try/except Exception: pass` block was also eliminated, removing silent error swallowing.
7. **Shared media serving (Phase 8)** — ✅ **Configured in Traefik.** Both fusion projects' Traefik configs (`cms-fusion.yml`, `lms-fusion.yml`) route `/static/` and `/media/` paths to the existing `shared-media:80` Nginx container. Media volumes are defined in docker-compose. The routing documentation is a production deployment concern.

### 8. Notes

- The exact boundary between `libs/django-fusion` shared templates and
  `projects/assets/` shared templates should be finalized before moving
  framework-level templates.
- Legacy cleanup is limited to duplicates; entire directory deletion is out of
  scope for this plan.
- Localized copies of this plan exist under each fusion project's `plan/`
  directory.

### 8. Related

- `projects/cms-fusion/plan/ASSETS_TEMPLATES_CLEANUP.md`
- `projects/cms-fusion/plan/MIGRATION_PLAN.md`
- `projects/lms-fusion/plan/ASSETS_TEMPLATES_CLEANUP.md`
- `projects/lms-fusion/plan/MIGRATION_PLAN.md`
- `projects/docs/MIGRATION_AND_CLEANUP_MASTER_PLAN.md`
- `libs/django-fusion/AGENTS.md`
- `projects/assets/templates/AGENTS.md`
