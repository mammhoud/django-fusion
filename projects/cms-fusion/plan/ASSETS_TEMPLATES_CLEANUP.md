# cms-fusion — Assets, Templates & Legacy Cleanup Plan

**Short name:** `fusion-assets-templates-cleanup`
**Master plan:** [`docs/plans.md`](../../../docs/plans.md)
**Date:** 2026-07-26
**Status:** Planned

## Objective

Make `cms-fusion` self-contained for templates and static assets, remove
duplicate content from the legacy `cms/cms-full/` tree, and verify that
`django-fusion` customization hooks work for this project.

## Scope

- Move project-specific design source assets from `projects/assets/` into
  `projects/cms-fusion/assets/` (sibling of `backend/` and `frontend/`):
  `styles/`, `images/`, `branding/`, `fonts/`.
- Move backend runtime assets into `projects/cms-fusion/backend/assets/`
  (`static/`, `media/`, `fixtures/`, `locale/`, `emails/`, `templates/`).
- Move app-specific templates from `backend/templates/` into
  `backend/plugins/<app>/templates/` or `backend/www/<app>/templates/`.
- Delete duplicate files from `projects/cms/cms-full/` after verification.
- Update `cms-fusion` AGENTS.md and settings to reflect the new layout.
- Share SCSS, logos, and branding between Next.js and Django from a single
  source of truth under `assets/`.

## Phases

### Phase 0 — Discovery
- [ ] Inventory every `projects/assets/` reference in `cms-fusion/backend`.
- [ ] Generate a diff matrix between `cms-fusion/backend` and `cms/cms-full/`.
- [ ] Tag data-only or migration files that must not be deleted.

### Phase 1 — Asset Migration
- [ ] Copy/move project-specific design source assets into `cms-fusion/assets/`
  (`styles/`, `images/`, `branding/`, `fonts/`).
- [ ] Copy/move backend runtime assets into `cms-fusion/backend/assets/`
  (`static/`, `media/`, `fixtures/`, `locale/`, `emails/`, `templates/`).
- [ ] Move framework-level templates/components to `libs/django-fusion` if they belong there. Do **not** move styles, logos, or branding into `libs/django-fusion`; those stay in the project-level `assets/` directory.
- [ ] Create a single SCSS source-of-truth in `cms-fusion/assets/styles/` and
  configure both Next.js and Django to consume it.
- [ ] Place logos and branding in `cms-fusion/assets/branding/` and
  copy/symlink them to `frontend/public/branding/` and
  `backend/assets/static/branding/`.
- [ ] Update `STATICFILES_DIRS` and build scripts in `cms-fusion/backend/settings.py`
  and `frontend/package.json` / webpack / Next.js config.
- [ ] Add an npm script or Makefile target that copies/symlinks
  `cms-fusion/assets/branding/` to `frontend/public/branding/` and
  `backend/assets/static/branding/`.

### Phase 1b — SCSS / Branding Pipeline
- [ ] Install `sass` in `frontend/package.json`.
- [ ] Import `cms-fusion/assets/styles/fusion-theme.scss` from
  `frontend/src/app/layout.tsx`.
- [ ] Configure the build to compile SCSS to
  `backend/assets/static/css/fusion.css` for Django.
- [ ] Add Tailwind custom colors in `frontend/tailwind.config.js` that reference
  the same CSS variables emitted by `fusion-theme.scss`.
- [ ] Place cms-fusion brand assets under `assets/branding/`:
  - Primary: `#7c3aed`
  - Secondary: `#5b21b6`

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
- [ ] Delete exact-duplicate files from `cms/cms-full/`.
- [ ] Update or remove stale `AGENTS.md` files in legacy directories.

### Phase 4 — django-fusion Customization Audit
- [ ] Verify `FUSION_LAYOUTS` and `FUSION_DEFAULT_LAYOUT` overrides work.
- [ ] Verify component registry overrides work.
- [ ] Document project-specific override examples in `AGENTS.md`.

### Phase 5 — Validation
- [ ] `make check WEBSITE=cms-fusion`
- [ ] `make test WEBSITE=cms-fusion`
- [ ] Next.js frontend build: `cd projects/cms-fusion/frontend && npm run build`
- [ ] Template-resolution audit (no unintended `projects/assets/` fallbacks)
- [ ] Smoke test on the running frontend

#### Phase 6 — Build Pipeline / Webpack
- [ ] Decide whether the Django admin needs custom assets; if so, add a minimal
  webpack config under `backend/webpack.config.js`.
- [ ] Import `cms-fusion/assets/styles/fusion-theme.scss` from the Next.js root
  layout.
- [ ] Add an npm script to copy/symlink `assets/` into `frontend/public/`.
- [ ] Add a Makefile or CI step to compile SCSS to
  `backend/assets/static/css/fusion.css`.
- [ ] Verify Django templates reference the compiled CSS via
  `{% static 'css/fusion.css' %}`.

#### Phase 7 — Docker-Compose & Proxy
- [ ] Create a top-level `cms-fusion/docker-compose.yml` with `backend`,
  `frontend`, and optional `worker` services.
- [ ] Remove or archive the stale `backend/docker-compose.yml` that references
  `ctc-research`.
- [ ] Add `applications/proxy/traefik/dynamic/cms-fusion.yml` with routers for
  the cms-fusion backend and frontend.
- [ ] Use a unique backend port (e.g., `5080`) and expose the Next.js frontend
  on a distinct port (e.g., `3000`) for local development.
- [ ] Configure health checks and ensure Traefik picks up the new router file.
- [ ] Test the full stack locally with `docker compose up`.

#### Phase 8 — Shared Media / Static Serving
- [ ] Route uploaded media to the global `shared-media` Nginx container.
- [ ] Mount the shared media volume in the `cms-fusion` backend container and
  `shared-media`.
- [ ] Keep frontend source assets build-time only; do not expose
  `cms-fusion/assets/` directly.
- [ ] Document which URLs route to Next.js, Django, or `shared-media`.

## Deliverables

1. Asset migration report for `cms-fusion`.
2. Template reorganization report (old path → new path).
3. List of duplicate files deleted from `cms/cms-full/`.
4. Updated `projects/cms-fusion/backend/AGENTS.md`.

## Success Criteria

- [ ] `cms-fusion` no longer depends on `projects/assets/` for its own templates or static files.
- [ ] App-specific templates live under `plugins/<app>/templates/` or `www/<app>/templates/`.
- [ ] `backend/templates/` contains only site-root entry templates and project-wide overrides.
- [ ] Duplicate files copied into `cms-fusion` are removed from `cms/cms-full/`.
- [ ] `cms-fusion` passes `make check`, tests, frontend build, and smoke tests.
