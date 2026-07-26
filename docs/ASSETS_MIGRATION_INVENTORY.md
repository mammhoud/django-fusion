# Asset & Template Migration Inventory

**Scope:** Identify every reference to `projects/assets/` inside the `cms-fusion` and
`lms-fusion` backends so we can move project-specific assets into each project,
move framework-level assets into `libs/django-fusion`, and keep only true
cross-site design assets in `projects/assets/`.

**Document:** `docs/ASSETS_MIGRATION_INVENTORY.md`  
**Date:** 2026-07-26  
**Status:** Discovery — static inventory complete; runtime disconnect pending  
**Owner:** Assign before Phase 1

---

## Methodology

1. **Static search** — `rg "projects/assets/"` across `projects/cms-fusion/` and
   `projects/lms-fusion/`.
2. **Repo-wide docs scan** — `rg "projects/assets/" .github/ docs/ AGENTS.md`
   (and any other monorepo-level docs) for references that also need updating.
3. **Runtime disconnect** (pending) — temporarily drop `projects/assets/` from
   `TEMPLATES['DIRS']` / `STATICFILES_DIRS` in the fusion `settings.py` files and
   record every `TemplateDoesNotExist` and 404 static error.
4. **Diff against local trees** — for each shared template, decide whether the
   fusion project already has an override, an exact duplicate, or a true dependency.

---

## Static Reference Summary

| Site | Matches | Categories |
|------|---------|------------|
| `cms-fusion/backend` | 30 | AGENTS.md docs, event template comment |
| `lms-fusion/backend` | 30 | AGENTS.md docs, event template comment |
| `cms-fusion/frontend` | 0 | — |
| `lms-fusion/frontend` | 0 | — |

**Note:** No frontend code hard-codes `projects/assets/`. All references are in
backend documentation or template comments.

---

## 1. Hardcoded References to Clean Up

### 1.1 Per-File Cleanup Checklist

These files mention `projects/assets/templates/AGENTS.md` or the shared template
layer. They should be rewritten once the shared layer is relocated.

**Action for all AGENTS.md files:** Remove/replace references to
`projects/assets/templates/` and rewrite guidance to the project-local +
django-fusion resolution order.

Affected files:

- `projects/cms-fusion/backend/AGENTS.md`
- `projects/cms-fusion/backend/plugins/accounts/templates/AGENTS.md`
- `projects/cms-fusion/backend/plugins/profile/templates/AGENTS.md`
- `projects/cms-fusion/backend/plugins/templates/AGENTS.md`
- `projects/cms-fusion/backend/plugins/lms/templates/AGENTS.md`
- `projects/cms-fusion/backend/plugins/blog/templates/AGENTS.md`
- `projects/cms-fusion/backend/www/core/templates/AGENTS.md`
- `projects/cms-fusion/backend/templates/AGENTS.md`
- `projects/cms-fusion/backend/assets/templates/AGENTS.md`
- `projects/lms-fusion/backend/AGENTS.md`
- `projects/lms-fusion/backend/plugins/accounts/templates/AGENTS.md`
- `projects/lms-fusion/backend/plugins/profile/templates/AGENTS.md`
- `projects/lms-fusion/backend/plugins/templates/AGENTS.md`
- `projects/lms-fusion/backend/plugins/lms/templates/AGENTS.md`
- `projects/lms-fusion/backend/plugins/blog/templates/AGENTS.md`
- `projects/lms-fusion/backend/www/core/templates/AGENTS.md`
- `projects/lms-fusion/backend/templates/AGENTS.md`
- `projects/lms-fusion/backend/assets/templates/AGENTS.md`

**Template comments to rewrite:**

- `projects/cms-fusion/backend/templates/events/event_page.html`
- `projects/lms-fusion/backend/templates/events/event_page.html`

---

## 2. Actual Shared Asset Inventory

These counts come from a live scan of `projects/assets/` and help prioritize
which directories to migrate first.  
**Important:** the "Proposed Destination" column is a hypothesis that must be
verified during the runtime disconnect and diff-matrix steps before any files
are moved.

### 2.1 `projects/assets/templates/`

**Top-level directories:**

| Directory | File Count | Proposed Destination (pending verification) |
|-----------|-----------:|-----------------------------------------------|
| `blocks/` | 33 | `libs/django-fusion` (framework components) — verify usage |
| `plugins/` | 45 | Split: framework-agnostic → `libs/django-fusion`; project-specific → each fusion project |
| `layout/` | 50 | `libs/django-fusion` (base layouts) — verify usage |
| `components/` | 16 | `libs/django-fusion` — verify usage |
| `emails/` | 22 | Split by project + `libs/django-fusion` base email templates |
| `partials/` | 14 | `libs/django-fusion` — verify usage |
| `wagtailadmin/` | 11 | `libs/django-fusion` — verify usage |
| `auth/` | 9 | `libs/django-fusion` — verify usage |
| `socialaccount/` | 8 | `libs/django-fusion` — verify usage |
| `events/` | 6 | Split: `cms-fusion` / `lms-fusion` |
| `generic/` | 5 | `libs/django-fusion` — verify usage |
| `registration/` | 3 | `libs/django-fusion` — verify usage |
| `content/` | 2 | `libs/django-fusion` (generic content templates) — verify usage |
| `ui/` | 2 | `libs/django-fusion` — verify usage |
| `usersessions/` | 1 | `libs/django-fusion` — verify usage |
| `wagtailcore/` | 1 | `libs/django-fusion` — verify usage |
| `account/` | 1 | `libs/django-fusion` — verify usage |

**Top-level files:**

- `AGENTS.md`
- `README.md`
- `__init__.py`
- `allauth.md`
- `base.html`
- `base_auth.html`
- `base_email.html`
- `base_profile.html`
- `index.html`
- `robots.txt`
- `todo`

### 2.2 `projects/assets/static/`

**Top-level directories:**

| Directory | File Count | Proposed Destination (pending verification) |
|-----------|-----------:|-----------------------------------------------|
| `fonts/` | 696 | Keep in `projects/assets/` as cross-site font library unless a project needs a custom font |
| `images/` | 87 | Split: generic → keep; project-specific → move to `<project>/assets/images/` |
| `js/` | 83 | Framework JS → `libs/django-fusion`; project JS → each fusion project |
| `styles/` | 73 | Keep legacy `main.scss` in `projects/assets/`; fusion projects use their own `fusion-theme.scss` |
| `videos/` | 1 | Move to each project if used |

**Top-level files:**

- `__init__.py`
- `static.js`
- `styles.js`

### 2.3 Other `projects/assets/` directories (not yet scanned)

| Directory | Notes |
|-----------|-------|
| `scripts/` | `workspace.mjs` and shared build scripts; verify whether fusion builds or CI still invoke them |
| `locale/` | Shared translation files; verify if `cms-fusion` / `lms-fusion` load these locales |
| `fixtures/` | `events.json` and similar; verify usage before moving or deleting |

---

## 3. Runtime Disconnect Procedure

The static search found only documentation references, so the real dependencies
must be discovered by running the backends without the shared layer.

### 3.1 Steps

1. Open the fusion settings file:
   - `projects/cms-fusion/backend/settings.py`
   - `projects/lms-fusion/backend/settings.py`
2. Locate the `TEMPLATES['DIRS']` and `STATICFILES_DIRS` entries that include
   `projects/assets/templates/` and `projects/assets/static/`. Temporarily comment
   them out so the backends no longer fall back to the shared layer. Example:
   ```python
   TEMPLATES = [
       {
           ...
           "DIRS": [
               BASE_DIR / "templates",
               # BASE_DIR.parent.parent / "assets" / "templates",  # disabled for runtime disconnect
           ],
           ...
       }
   ]

   STATICFILES_DIRS = [
       BASE_DIR / "assets" / "static",
       # BASE_DIR.parent.parent / "assets" / "static",  # disabled for runtime disconnect
   ]
   ```
3. Run the development server or test suite:
   ```bash
   cd projects
   make dev WEBSITE=cms-fusion
   # in another terminal
   make dev WEBSITE=lms-fusion
   ```
   If a project alias is not registered in the root `Makefile`, run the dev
   server directly from the project directory.
4. Capture every error:
   - `TemplateDoesNotExist`
   - `django.templatetags.staticfiles.StaticFileNotFound` / 404 for static files
5. Re-enable the shared layer and record the failing templates/static files in a
   new section of this inventory.
6. Categorize each failure as:
   - **Framework-level** → move to `libs/django-fusion`
   - **Project-specific** → copy to the appropriate fusion project
   - **Legacy/unused** → leave in `projects/assets/` or delete

### 3.2 Expected Artifact

A new section, **"Runtime Dependency List"**, appended to this file with the
exact template/static paths discovered and their target destination.

---

## 4. Proposed Migration Order

1. **Runtime disconnect test** to discover all implicit dependencies.
2. **Migrate framework-level templates** to `libs/django-fusion/src/django_fusion/templates/`.
3. **Copy project-specific templates** to `cms-fusion/backend/templates/` and
   `lms-fusion/backend/templates/` (or appropriate app dirs).
4. **Move/copy required static assets** to each project's `backend/assets/static/`.
5. **Remove `projects/assets/` from fusion settings** (`TEMPLATES['DIRS']`,
   `STATICFILES_DIRS`).
6. **Clean up hardcoded references** listed in section 1.
7. **Run validation** (Django checks, template resolution, frontend builds).

---

## 5. Legacy Deletion Caution

The plan calls for deleting duplicate files from legacy directories
(`cms/cms-full/`, `cms/lms-full/`, `lms/cms/`, `lms/lms/`). Before deleting
anything:

- Confirm the file is an exact duplicate (same content, not just same name) of a
  file already moved into a fusion project.
- Verify non-fusion sites and CI pipelines do not reference the legacy path.
- Keep data-only files, migrations, and fixtures unless explicitly migrated.

> **Rule:** Delete only confirmed duplicates. Entire-directory deletion is out of
> scope for this plan unless approved separately.

---

## 6. Open Questions

- Which exact shared templates are still rendered by `cms-fusion` and
  `lms-fusion` at runtime?
- Are the legacy icon fonts used, or can the fusion projects rely on Tailwind
  + inline SVGs?
- Should `projects/assets/scripts/workspace.mjs` be kept for non-fusion sites
  and a separate build script created for fusion projects?
- Which locales under `projects/assets/locale/` are actually loaded by the
  fusion projects?

---

## 7. Next Steps

- [ ] Run repo-wide docs scan (`rg "projects/assets/" .github/ docs/ AGENTS.md`) and add findings to section 1.
- [ ] Run runtime disconnect for `cms-fusion` and append the dependency list to this file.
- [ ] Run runtime disconnect for `lms-fusion` and append the dependency list to this file.
- [ ] Update the 18 AGENTS.md files and 2 event template comments.
- [ ] Produce a diff matrix: `cms-fusion/backend` vs `cms/cms-full/` and `lms-fusion/backend` vs `cms/lms-full/`, `lms/cms/`, `lms/lms/`.
- [ ] Verify `scripts/`, `locale/`, and `fixtures/` usage before moving them.
