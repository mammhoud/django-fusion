# Fusion Assets, Templates & Legacy Cleanup — Specification

**Short name:** `fusion-assets-templates-cleanup`
**Spec file:** `fusion-assets-templates-cleanup-spec.md`
**Date:** 2026-07-26
**Status:** Draft — pending implementation planning

---

## 1. Request Summary

The user wants to reorganize the monorepo so that the two "fusion" projects — `cms-fusion` and `lms-fusion` — become self-contained with respect to templates and static assets, while still retaining a controlled shared layer. In parallel, legacy directories that have already been migrated into the fusion projects (`cms-full`, `lms-full`, the legacy `lms/cms` and `lms/lms` trees) should be cleaned up by removing duplicated content. Finally, the work should verify that `django-fusion` can be fully customized by these projects.

### Key goals
1. Move assets from the shared `projects/assets/` tree into each fusion project as needed.
2. Reorganize backend templates so they follow Django's app-level `templates/` convention (plus a small site-root override layer).
3. Delete content that has already been integrated into the fusion projects from the legacy `cms-full`, `lms-full`, `lms/cms`, and `lms/lms` directories.
4. Compare files across the legacy and fusion trees to identify what was duplicated, what diverged, and what can be safely removed or unified.
5. Ensure `django-fusion` provides full customization hooks (templates, settings, component registry) for the fusion projects.

---

## 2. Interview Findings

### 2.1 Asset move scope
**Question:** When you say "move any assets to each cms-fusion and lms-fusion from projects/assets," what is your intended scope?

**Answer:** Full self-containment — copy or move all shared assets (templates, SCSS, JS, fonts, locales, fixtures) into each fusion project so they no longer depend on `projects/assets/`.

**Implications:**
- Each fusion project must end up with its own `assets/static/`, `assets/templates/`, and `assets/fixtures/` trees.
- References to `projects/assets/` in `cms-fusion/backend` and `lms-fusion/backend` settings, templates, and build scripts must be removed or redirected.
- The shared `projects/assets/` tree may still exist for the non-fusion sites (`ctc-research`, `lms`, `vresume`, `cypercloud`), but the fusion projects should not use it directly.

### 2.2 Template organization
**Question:** For "organize all templates as django plateform to be at the app dir templates," what do you mean?

**Answer:** Per-app plus site root — move app-specific templates into each app's own `templates/` directory, but keep top-level site templates (`base.html`, `index.html`, registration/account shells, etc.) in `backend/templates/`.

**Implications:**
- `plugins/blog/templates/`, `plugins/lms/templates/`, `plugins/accounts/templates/`, `plugins/profile/templates/`, `www/core/templates/` should hold templates owned by those apps.
- `backend/templates/` remains for site-level overrides and entry-point templates.
- The current `backend/templates/` directory should shrink significantly; most files currently there are actually app-specific and should move.
- Django `TEMPLATES[0]['DIRS']` must be updated so that app directories are loaded before the site root, and `APP_DIRS` remains enabled.

### 2.3 Legacy cleanup scope
**Question:** When you say "complete delete what integrated to fusion from cms full and lms full dirs," how aggressive should the cleanup be?

**Answer:** Delete only duplicates — keep `cms-full`, `lms-full`, and the legacy `lms/cms`/`lms/lms` directories, but delete only the files and features that were copied into the fusion projects.

**Implications:**
- Do not remove entire legacy directories yet; instead, identify duplicate files and remove them.
- Files that still exist only in the legacy directories (e.g., migration history, site-specific fixtures, data) should be preserved until a later migration/backup step.
- The AGENTS.md and plan documents in legacy directories should be updated to note what is deprecated.

### 2.4 Shared-asset strategy
**Question:** For full self-containment, how should identical shared assets be handled across cms-fusion and lms-fusion?

**Answer:** Keep a common shared layer — move assets into each fusion project but still allow a small shared layer for truly common files.

**Implications:**
- Framework-level shared assets (e.g., `django-fusion` base templates, component skeletons, default layout tags) should live in `libs/django-fusion`.
- Cross-site design assets (e.g., icon fonts, color palettes that are not project-specific) may remain in `projects/assets/`.
- Project-specific assets must live in `projects/cms-fusion/backend/assets/` and `projects/lms-fusion/backend/assets/` (or `projects/<project>/assets/`).

### 2.5 django-fusion customization
**Question:** What does "make sure django-fusion has full customization" mean to you?

**Answer:** All of the above — template overrides, settings-driven behavior, and component registry extensibility.

**Implications:**
- Every `django-fusion` template, layout, and component must be overridable at the project or app level.
- Behavior such as `FUSION_FEATURES`, `FUSION_LAYOUTS`, and `FUSION_DEFAULT_LAYOUT` must remain settings-driven.
- The component registry (`django_fusion.comp.registry`) must allow projects to register, replace, or extend components without editing the library.

### 2.6 Diff/analysis scope
**Question:** For the diff/check between files, which comparison do you want?

**Answer:** All of the above — compare fusion vs. legacy, compare templates against `projects/assets/templates`, and identify references to `projects/assets/`.

**Implications:**
- Produce a matrix of duplicate/similar/diverged files.
- Generate an inventory of `projects/assets/` references inside the fusion projects.
- Use the comparison to decide which legacy files are safe to delete and which templates should be moved.

### 2.7 Shared-layer home
**Question:** You want to keep a common shared layer for assets. Where should that shared layer live after the move?

**Answer:** Hybrid: lib + project assets — framework-level shared assets in `django-fusion`, cross-site design assets in `projects/assets/`.

**Implications:**
- Move truly generic, framework-level templates (e.g., `fusion/base.html`, `fusion/layouts/*.html`, component loader templates) into `libs/django-fusion/src/django_fusion/templates/`.
- Keep cross-site design assets (fonts, icon packs, shared SCSS variables) in `projects/assets/`.
- Each fusion project keeps its own branding, overrides, and project-specific SCSS/JS.

### 2.8 Execution priority
**Question:** What is the execution priority for these tasks?

**Answer:** Incremental per app — work app by app (e.g., blog, lms, accounts), move templates/assets, delete duplicates, and verify before moving to the next app.

**Implications:**
- Break the work into phases: `accounts`, `blog`, `lms`, `profile`, `pages`, `products`, `www/core`.
- For each app: move templates, move static assets, update `TEMPLATES` / `STATICFILES_DIRS`, delete duplicate legacy files, run checks/tests, then proceed.
- Reduces blast radius and makes rollbacks easier.

### 2.9 Validation
**Question:** What validation should be required after the refactoring?

**Answer:** All of the above — run the full test suite, template resolution checks, and runtime smoke tests.

**Implications:**
- Django system checks (`make check WEBSITE=cms-fusion`, `make check WEBSITE=lms-fusion`).
- Unit and integration tests for both fusion backends.
- Verify no template falls back to `projects/assets/` unless explicitly intended.
- Frontend builds (`npm run build`) and runtime smoke tests for both Next.js frontends.

---

## 3. Current Codebase Context

### 3.1 Directory layout

```
projects/
├── assets/                          # Shared templates, SCSS, JS, fonts, locales
├── cms-fusion/
│   ├── backend/                     # Django + Wagtail backend
│   │   ├── assets/                  # Local static, templates, fixtures (small)
│   │   ├── plugins/<app>/templates/ # App templates
│   │   ├── templates/               # Site-root templates (large)
│   │   └── settings.py
│   ├── frontend/                    # Next.js app
│   └── plan/MIGRATION_PLAN.md
├── lms-fusion/
│   ├── backend/
│   │   ├── assets/
│   │   ├── plugins/<app>/templates/
│   │   ├── templates/
│   │   └── settings.py
│   ├── frontend/
│   └── plan/MIGRATION_PLAN.md
├── cms/
│   ├── cms-full/                    # Legacy full CMS, largely duplicated in cms-fusion
│   └── lms-full/                    # Legacy full LMS, duplicated in lms-fusion
└── lms/
    ├── cms/                           # Legacy LMS CMS, partially duplicated
    └── lms/                           # Legacy LMS frontend
```

### 3.2 Observed duplication

- `cms-fusion/backend` and `cms/cms-full` share a large number of templates, Python modules, and fixtures.
- `lms-fusion/backend` and `cms/lms-full` (and `lms/cms`) also share a large number of files.
- `cms-fusion/backend/templates/` and `lms-fusion/backend/templates/` are nearly identical and contain many app-specific templates that should move to `plugins/<app>/templates/`.
- `projects/assets/templates/` is still referenced as the shared template layer in AGENTS.md files and in templates such as `events/event_page.html`.

### 3.3 django-fusion customization hooks (existing)

- `FUSION_LAYOUTS` and `FUSION_DEFAULT_LAYOUT` in `settings.py`.
- `FUSION_FEATURES` toggles.
- `FUSION_RENDER_FIRST_DEFAULT`.
- `fusion_branding_context` context processor.
- `fusion_layout`, `fusion_branding`, `render_fusion_scripts`, `fusion_render_first_flag`, and `fusion_body_data` template tags.
- `RoutableComponent` / `FragmentComponent` for fragment rendering.
- `TemplateResolverMixin` for per-site template resolution.

---

## 4. Scope

### 4.1 In scope

1. **Asset migration**
   - Copy/move required shared assets from `projects/assets/` into `projects/cms-fusion/backend/assets/` and `projects/lms-fusion/backend/assets/`.
   - Move project-specific assets from `projects/assets/` (e.g., `styles/fusion-theme.scss`) into the appropriate fusion project.
   - Update `STATICFILES_DIRS`, `TEMPLATES['DIRS']`, webpack config, and build scripts to prefer local assets.

2. **Template reorganization**
   - Move app-specific templates from `backend/templates/` into `plugins/<app>/templates/` and `www/core/templates/`.
   - Keep site-root templates (`base.html`, `index.html`, `base_page.html`, `base_auth.html`, etc.) in `backend/templates/`.
   - Update Django `TEMPLATES` settings so app directories resolve before the site root.

3. **Legacy cleanup**
   - Compare `cms/cms-full` and `lms-fusion/backend` to identify exact duplicates.
   - Compare `cms/lms-full` and `lms-fusion/backend` to identify exact duplicates.
   - Compare `lms/cms` and `lms/lms` with the fusion projects.
   - Delete duplicate files from legacy directories after verification.
   - Update or remove AGENTS.md files that still describe the old shared layout.

4. **django-fusion customization audit**
   - Verify every fusion layout can be overridden per project.
   - Verify every fusion component can be overridden per app/project.
   - Document how to extend the component registry.
   - Ensure settings-driven behavior is complete and consistent.

5. **Validation**
   - Django system checks for both fusion projects.
   - Unit/integration tests for both fusion projects.
   - Template resolution audit (no unintended fallbacks to `projects/assets/`).
   - Frontend builds and runtime smoke tests.

### 4.2 Out of scope (unless requested)

- Deleting entire legacy directories (`cms-full`, `lms-full`, `lms/cms`, `lms/lms`) — only duplicates should be removed.
- Modifying non-fusion sites (`ctc-research`, `lms`, `vresume`, `cypercloud`) beyond ensuring `projects/assets/` still serves them.
- Rewriting business logic; this is a structural/refactoring task.
- Database migrations or data migration from legacy projects.

---

## 5. Design Decisions

### 5.1 Template resolution order (after reorganization)

```
1. <project>/backend/templates/                  # Site-root overrides (highest)
2. <project>/backend/plugins/<app>/templates/    # App templates
3. <project>/backend/www/<app>/templates/          # www app templates
4. <project>/backend/assets/templates/             # Project asset templates
5. libs/django-fusion/src/django_fusion/templates/ # Framework-level shared templates
6. projects/assets/templates/                      # Monorepo shared templates (kept for non-fusion sites)
```

### 5.2 Shared-asset split

| Category | Destination | Examples |
|----------|-------------|----------|
| Framework templates | `libs/django-fusion/src/django_fusion/templates/` | `fusion/base.html`, `fusion/layouts/*.html`, component skeletons |
| Cross-site design assets | `projects/assets/` | Icon fonts, shared color variables, base icon sets |
| Project-specific assets | `projects/<fusion>/backend/assets/` | Branding SCSS, project JS, project fixtures |

### 5.3 Incremental per-app phases

Phase order:
1. `accounts`
2. `blog`
3. `lms`
4. `profile`
5. `pages`
6. `products`
7. `www/core`
8. Site-root templates and final cleanup

For each phase:
1. Move templates from `backend/templates/` to `plugins/<app>/templates/`.
2. Move static assets from `projects/assets/` and `backend/assets/` to the project-local assets.
3. Update settings, imports, and template paths.
4. Delete duplicate files from legacy directories.
5. Run Django checks and targeted tests.

---

## 6. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Templates become unresolvable after moving | Use Django Debug Toolbar or a template-resolution test to verify every moved template resolves |
| Duplicate deletion removes a file still used by a legacy project | Only delete after confirming the file exists in the fusion project and is referenced locally |
| Frontends break because static paths changed | Update webpack/Next.js static paths and run frontend builds |
| Locales become inconsistent | Keep `.po` files versioned per project; use `django-admin makemessages` after moves |
| Tests reference old template paths | Update tests and fixtures that hard-code template paths |
| `django-fusion` customization gaps | Audit every fusion template tag and component for override hooks |

---

## 7. Deliverables

1. **Asset migration report** — list of assets moved from `projects/assets/` to each fusion project.
2. **Template reorganization report** — mapping of old `backend/templates/` paths to new `plugins/<app>/templates/` paths.
3. **Legacy duplicate deletion report** — list of files removed from `cms-full`, `lms-full`, `lms/cms`, and `lms/lms`.
4. **django-fusion customization audit** — document of which templates/components are overridable and how.
5. **Updated AGENTS.md files** — reflecting new template and asset locations.
6. **Validation results** — Django checks, tests, frontend builds, and smoke-test outcomes.

---

## 8. Success Criteria

- [ ] `cms-fusion` and `lms-fusion` no longer reference `projects/assets/` for project-specific templates or static files.
- [ ] All app-specific templates live in `plugins/<app>/templates/` or `www/<app>/templates/`.
- [ ] Site-root `backend/templates/` contains only top-level entry templates and project-wide overrides.
- [ ] Duplicate files that were copied into the fusion projects are removed from legacy directories.
- [ ] `django-fusion` templates, layouts, and components can be overridden per project/app.
- [ ] Both fusion backends pass `make check` and their test suites.
- [ ] Both Next.js frontends build successfully.
- [ ] Runtime smoke tests for both fusion projects pass.

---

## 9. Notes & Open Questions

- The user wants a hybrid shared layer (`libs/django-fusion` + `projects/assets/`). The exact boundary between these two shared layers should be confirmed before moving framework-level templates into `libs/django-fusion`.
- The legacy cleanup is "delete only duplicates" — the spec does not authorize deleting entire directories. This may leave behind empty or near-empty legacy directories that can be removed in a follow-up step.
- "django plateform" in the original request is interpreted as "Django app-level template directories plus a site-root override layer."
