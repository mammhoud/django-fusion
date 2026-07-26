# lms-fusion — Assets, Templates & Legacy Cleanup Plan

**Short name:** `fusion-assets-templates-cleanup`
**Master plan:** [`docs/plans.md`](../../../docs/plans.md)
**Date:** 2026-07-26
**Status:** In progress — Phases 1b, 6, and 7 implemented; pending full stack test, Phase 8, and earlier asset/template migration work.

## Objective

Make `lms-fusion` self-contained for templates and static assets, remove
duplicate content from the legacy `cms/lms-full/`, `lms/cms/`, and `lms/lms/`
trees, and verify that `django-fusion` customization hooks work for this project.

## Scope

- Move project-specific design source assets from `projects/assets/` into
  `projects/lms-fusion/assets/` (sibling of `backend/` and `frontend/`):
  `styles/`, `images/`, `branding/`, `fonts/`.
- Move backend runtime assets into `projects/lms-fusion/backend/assets/`
  (`static/`, `media/`, `fixtures/`, `locale/`, `emails/`, `templates/`).
- Move app-specific templates from `backend/templates/` into
  `backend/plugins/<app>/templates/` or `backend/www/<app>/templates/`.
- Delete duplicate files from `projects/cms/lms-full/`, `projects/lms/cms/`,
  and `projects/lms/lms/` after verification.
- Update `lms-fusion` AGENTS.md and settings to reflect the new layout.
- Share SCSS, logos, and branding between Next.js and Django from a single
  source of truth under `assets/`.

## Phases

### Phase 0 — Discovery
- [x] Inventory every `projects/assets/` reference in `lms-fusion/backend`. (see `docs/ASSETS_MIGRATION_INVENTORY.md`)
- [ ] Generate diff matrices between `lms-fusion/backend` and:
  - `cms/lms-full/`
  - `lms/cms/`
  - `lms/lms/`
- [ ] Tag data-only or migration files that must not be deleted.

### Phase 1 — Asset Migration
- [ ] Copy/move project-specific design source assets into `lms-fusion/assets/`
  (`styles/`, `images/`, `branding/`, `fonts/`).
- [ ] Copy/move backend runtime assets into `lms-fusion/backend/assets/`
  (`static/`, `media/`, `fixtures/`, `locale/`, `emails/`, `templates/`).
- [ ] Move framework-level templates/components to `libs/django-fusion` if they belong there. Do **not** move styles, logos, or branding into `libs/django-fusion`; those stay in the project-level `assets/` directory.
- [ ] Create a single SCSS source-of-truth in `lms-fusion/assets/styles/` and
  configure both Next.js and Django to consume it.
- [ ] Place logos and branding in `lms-fusion/assets/branding/` and
  copy/symlink them to `frontend/public/branding/` and
  `backend/assets/static/branding/`.
- [ ] Update `STATICFILES_DIRS` and build scripts in `lms-fusion/backend/settings.py`
  and `frontend/package.json` / webpack / Next.js config.
- [ ] Add an npm script or Makefile target that copies/symlinks
  `lms-fusion/assets/branding/` to `frontend/public/branding/` and
  `backend/assets/static/branding/`.

### Phase 1b — SCSS / Branding Pipeline
- [x] Install `sass` in `frontend/package.json`.
- [x] Import `lms-fusion/assets/styles/fusion-theme.scss` from
  `frontend/src/app/layout.tsx`.
- [x] Configure the build to compile SCSS to
  `backend/assets/static/css/fusion.css` for Django.
- [x] Add Tailwind custom colors in `frontend/tailwind.config.js` that reference
  the same CSS variables emitted by `fusion-theme.scss`.
- [ ] Place lms-fusion brand assets under `assets/branding/`:
  - Primary: `#00a1b3`
  - Secondary: `#008080`

### Phase 2 — Template Reorganization
- [ ] Move app templates from `backend/templates/` to:
  - `backend/plugins/accounts/templates/`
  - `backend/plugins/blog/templates/`
  - `backend/plugins/lms/templates/`
  - `backend/plugins/profile/templates/`
  - `backend/plugins/pages/templates/`
  - `backend/plugins/products/templates/`
  - `backend/www/core/templates/`
- [ ] Keep only site-root entry templates in `backend/templates/`.
- [ ] Update `TEMPLATES['DIRS']` in `settings.py`.

### Phase 3 — Legacy Cleanup
- [ ] Delete exact-duplicate files from `cms/lms-full/`, `lms/cms/`, and `lms/lms/`.
- [ ] Update or remove stale `AGENTS.md` files in legacy directories.

### Phase 4 — django-fusion Customization Audit
- [ ] Verify `FUSION_LAYOUTS` and `FUSION_DEFAULT_LAYOUT` overrides work.
- [ ] Verify component registry overrides work.
- [ ] Document project-specific override examples in `AGENTS.md`.

### Phase 5 — Validation
- [ ] `make check WEBSITE=lms-fusion`
- [ ] `make test WEBSITE=lms-fusion`
- [x] Next.js frontend build: `cd projects/lms-fusion/frontend && npm run build`
- [ ] Template-resolution audit (no unintended `projects/assets/` fallbacks)
- [ ] Smoke test on the running frontend

#### Phase 6 — Build Pipeline / Webpack
- [ ] Decide whether the Django admin needs custom assets; if so, add a minimal
  webpack config under `backend/webpack.config.js`.
- [x] Import `lms-fusion/assets/styles/fusion-theme.scss` from the Next.js root
  layout.
- [x] Add an npm script to copy/symlink `assets/` into `frontend/public/`.
- [x] Add a Makefile or CI step to compile SCSS to
  `backend/assets/static/css/fusion.css`.
- [x] Verify Django templates reference the compiled CSS via
  `{% static 'css/fusion.css' %}`.

#### Phase 7 — Docker-Compose & Proxy
- [x] Create a top-level `lms-fusion/docker-compose.yml` with `backend`,
  `frontend`, and optional `worker` services.
- [x] Remove or archive the stale `backend/docker-compose.yml` that references
  `ctc-research`.
- [x] Add `applications/proxy/traefik/dynamic/lms-fusion.yml` with routers for
  the lms-fusion backend and frontend.
- [x] Use a unique backend port (`5074`) and expose the Next.js frontend
  on a distinct port (`3001`) for local development.
- [x] Configure health checks and ensure Traefik picks up the new router file.
- [ ] Test the full stack locally with `docker compose up`.

#### Phase 8 — Shared Media / Static Serving
- [ ] Route uploaded media to the global `shared-media` Nginx container.
- [ ] Mount the shared media volume in the `lms-fusion` backend container and
  `shared-media`.
- [ ] Keep frontend source assets build-time only; do not expose
  `lms-fusion/assets/` directly.
- [ ] Document which URLs route to Next.js, Django, or `shared-media`.

## Deliverables

1. Asset migration report for `lms-fusion`.
2. Template reorganization report (old path → new path).
3. List of duplicate files deleted from `cms/lms-full/`, `lms/cms/`, and `lms/lms/`.
4. Updated `projects/lms-fusion/backend/AGENTS.md`.

## Success Criteria

- [ ] `lms-fusion` no longer depends on `projects/assets/` for its own templates or static files.
- [ ] App-specific templates live under `plugins/<app>/templates/` or `www/<app>/templates/`.
- [ ] `backend/templates/` contains only site-root entry templates and project-wide overrides.
- [ ] Duplicate files copied into `lms-fusion` are removed from legacy directories.
- [ ] `lms-fusion` passes `make check`, tests, frontend build, and smoke tests.
