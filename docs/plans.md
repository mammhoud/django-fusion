# Structa Cloud — Enhancement Plans

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
**Status:** In progress — Phase 0 (discovery) complete. Phases 6 (SCSS/build pipeline) and 7 (Docker-Compose & Proxy) implemented for both projects; stale backend compose files removed. Pending full stack test, Phase 8 (shared media), and earlier asset/template migration work.

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
- [ ] Generate a file matrix: `cms-fusion/backend` vs `cms/cms-full`, `lms-fusion/backend` vs `cms/lms-full` and `lms/cms`.
- [ ] Identify exact duplicates, near-duplicates, and diverged files.
- [ ] Back up or tag any data-only files before deletion.

#### Phase 1 — Asset Migration
- [ ] Copy/move project-specific design source assets from `projects/assets/` to
  `<project>/assets/` (`styles/`, `images/`, `fonts/`, `branding/`).
- [ ] Copy/move backend runtime assets to `<project>/backend/assets/`
  (`static/`, `media/`, `fixtures/`, `locale/`, `emails/`, `templates/`).
- [ ] Move framework-level shared assets into `libs/django-fusion` where appropriate.
- [ ] Set up a single SCSS source-of-truth in `<project>/assets/styles/` that is
  consumed by both Next.js and Django.
- [ ] Place logos and branding in `<project>/assets/branding/` and copy/symlink
  them to `frontend/public/branding/` and `backend/assets/static/branding/`.
- [ ] Install/configure `sass` for Next.js SCSS support and add a build step to
  compile SCSS into `backend/assets/static/css/` for Django.
- [ ] Update `STATICFILES_DIRS`, `TEMPLATES['DIRS']`, webpack, Next.js config,
  and build scripts.
- [ ] Verify locales remain consistent after the move.

#### Phase 2 — Template Reorganization
- [ ] For each app (`accounts`, `blog`, `lms`, `profile`, `pages`, `products`),
  move app-specific templates from `backend/templates/` to
  `plugins/<app>/templates/`.
- [ ] Move `www/` app templates into `www/<app>/templates/`.
- [ ] Keep only site-root entry templates (`base.html`, `index.html`,
  `base_auth.html`, etc.) in `backend/templates/`.
- [ ] Update `TEMPLATES['DIRS']` so app directories resolve before the site root.
- [ ] Run template-resolution tests to confirm every moved template resolves.

#### Phase 3 — Legacy Cleanup
- [ ] Delete exact-duplicate files from `cms/cms-full/` that now exist in
  `cms-fusion/backend/`.
- [ ] Delete exact-duplicate files from `cms/lms-full/` that now exist in
  `lms-fusion/backend/`.
- [ ] Delete exact-duplicate files from `lms/cms/` and `lms/lms/`.
- [ ] Update or remove stale `AGENTS.md` files in legacy directories that still
  describe the old shared layout.
- [ ] Leave non-duplicate files (migrations, data, site-specific fixtures)
  untouched.

#### Phase 4 — django-fusion Customization Audit
- [ ] Confirm every fusion layout can be overridden per project via `FUSION_LAYOUTS`.
- [ ] Confirm every fusion component can be overridden per app/project via the
  component registry.
- [ ] Verify `FUSION_FEATURES`, `FUSION_DEFAULT_LAYOUT`, and related settings are
  documented and working.
- [ ] Document the override mechanism in `libs/django-fusion/AGENTS.md` and the
  project-level `AGENTS.md` files.

#### Phase 5 — Validation
- [ ] Run `make check WEBSITE=cms-fusion` and `make check WEBSITE=lms-fusion`.
- [ ] Run site tests: `make test WEBSITE=cms-fusion` and `make test WEBSITE=lms-fusion`.
- [ ] Run workspace tests: `uv run pytest`.
- [ ] Run frontend builds for both Next.js apps.
- [ ] Run a template-resolution audit to ensure no unintended fallbacks to
  `projects/assets/`.
- [ ] Run smoke tests on both fusion frontends.
- [ ] Verify Django and Next.js render the same logo, colors, and fonts.

#### Phase 6 — Build Pipeline / Webpack
- [ ] Decide whether Django needs custom admin assets; if so, add a minimal
  webpack config under `<project>/backend/webpack.config.js`.
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
  build successfully.

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

#### Phase 8 — Shared Media / Static Serving
- [ ] Route uploaded media to the global `shared-media` Nginx container.
- [ ] Mount the shared media volume in Django containers and `shared-media`.
- [ ] Keep frontend source assets build-time only; do not expose
  `<project>/assets/` directly.
- [ ] Document which URLs route to Next.js, Django, or `shared-media`.

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

- [ ] `cms-fusion` and `lms-fusion` no longer reference `projects/assets/` for
  project-specific templates or static files.
- [ ] App-specific templates live in `plugins/<app>/templates/` or
  `www/<app>/templates/`.
- [ ] `backend/templates/` contains only site-root entry templates and overrides.
- [ ] Duplicate files copied into fusion projects are removed from legacy directories.
- [ ] `django-fusion` templates, layouts, and components can be overridden per
  project/app.
- [ ] Both fusion backends pass `make check` and their test suites.
- [ ] Both Next.js frontends build successfully.
- [ ] Runtime smoke tests for both fusion projects pass.
- [ ] Next.js frontends import project-level SCSS and render consistent branding.
- [ ] Each fusion project has a working top-level `docker-compose.yml`.
- [ ] Traefik routes traffic to the correct backend and frontend containers.
- [ ] Uploaded media is served by `shared-media`, not per-project static servers.

### 7. Notes

- The exact boundary between `libs/django-fusion` shared templates and
  `projects/assets/` shared templates should be finalized before moving
  framework-level templates.
- Legacy cleanup is limited to duplicates; entire directory deletion is out of
  scope for this plan.
- Localized copies of this plan exist under each fusion project's `plan/`
  directory.

### 8. Related

- `projects/cms-fusion/plan/ASSETS_TEMPLATES_CLEANUP.md`
- `projects/lms-fusion/plan/ASSETS_TEMPLATES_CLEANUP.md`
- `libs/django-fusion/AGENTS.md`
- `projects/assets/templates/AGENTS.md`
