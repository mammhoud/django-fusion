# Structa Cloud – AI Agent Instructions

## Project Overview
Structa Cloud is a Django monorepo under `applications/`, with multiple site projects, shared configuration, shared frontend assets, and local reusable Django libraries. Do not assume this repo uses a generic `core/customizer/design/components` app layout.

## Actual Monorepo Layout
- `applications/Makefile` is the primary Makefile for application, Django, asset, test, and site orchestration targets.
- `applications/configs/` contains shared Django configuration and settings used across sites.
- `applications/assets/` contains shared frontend assets, shared templates, static files, locale files, and asset scripts.
- `applications/libs/` contains local reusable libraries that are developed alongside the sites.
- `applications/scripts/`, `applications/tasks/`, and `applications/webpack/` contain shared automation, task, and build tooling.
- `applications/www/` contains shared/core Django code used by the application stack.

## Canonical Site Paths
Use these canonical paths when working on site-specific code:
- `applications/ctc-research/` — CTC Research site.
- `applications/lms-demo/` — Structa/LMS demo site.
- `applications/VResume/` — VResume site. Note the directory is capitalized, even though some Makefile aliases use `vresume`.

Each site can contain its own `assets/`, `plugins/`, `templates/`, `tests/`, `www/`, and site-level `Makefile` as applicable.

## Shared Settings
Shared settings live under `applications/configs/`:
- `applications/configs/base/` for base configuration modules.
- `applications/configs/settings/` for environment/site settings.
- `applications/configs/tests/` for test settings and test configuration helpers.

Prefer adding common settings in `applications/configs/` rather than duplicating them inside individual sites. Keep site-specific overrides in the relevant site path.

## Shared Frontend Assets
Shared frontend assets live under `applications/assets/`:
- `applications/assets/templates/` for templates shared across sites.
- `applications/assets/static/` for shared static files.
- `applications/assets/scripts/` for shared frontend/build scripts.
- `applications/assets/locale/` for shared localization assets.

When adding shared styles, scripts, images, or templates, place them in `applications/assets/` unless they are truly site-specific.

## Local Libraries
Local reusable libraries live under `applications/libs/`:
- `applications/libs/django-grep/`
- `applications/libs/django-osoul/`
- `applications/libs/django-rseal/`

Treat these as first-class local packages. Make reusable framework-level changes in the appropriate library instead of copying logic into site projects.

## Makefile Delegation
- The root `Makefile` should be a thin entrypoint that delegates application and site work to `applications/Makefile`.
- `applications/Makefile` is the canonical dispatcher for Django checks, tests, migrations, asset builds, Docker/site commands, and `WEBSITE=...` selection.
- Site Makefiles live in each `applications/<site>/` directory, for example:
  - `applications/ctc-research/Makefile`
  - `applications/lms-demo/Makefile`
  - `applications/VResume/Makefile`
- Prefer invoking site work through `applications/Makefile` unless a site Makefile target is explicitly needed.
- Preserve existing website aliases in `applications/Makefile`; do not invent new canonical site names without updating the dispatcher.

## Template Conventions
Template locations are intentionally layered. Check all relevant paths before adding or moving templates:
- Shared templates: `applications/assets/templates/`.
- Site root templates: `applications/<site>/templates/`.
- Site asset templates: `applications/<site>/assets/templates/`.
- Site Django app templates: `applications/<site>/www/**/templates/`.
- Plugin templates: any template paths under `applications/<site>/plugins/`, including plugin-level `templates/` directories.

Use `{% include %}` for reusable components and pass only the required context. Prefer shared templates for cross-site UI and site templates for site-specific presentation.

## Fragment Naming Convention
Use `fragment_name` only for fragment identifiers and context keys. Do not introduce alternate names such as `fragment`, `name`, `fragment_slug`, or `fragment_key` for the same concept unless maintaining backwards compatibility with existing code.

## Code Style & Standards
- **Python**: Follow PEP 8. Use type hints for new or modified functions where practical. Keep formatting compatible with Black's 88-character default.
- **Django**: Prefer class-based views where appropriate. Keep business logic out of views and in services/modules that match the existing local structure.
- **Wagtail/Django templates**: Follow the existing panel, model, and template patterns in the relevant site or library.
- **SCSS/CSS**: Follow existing project conventions and use BEM-style names for reusable component classes. Do not use IDs for styling.
- **Imports**: Never wrap imports in `try`/`except` blocks.

## Testing & Validation
- Use `rg` instead of recursive `grep` for code searches.
- Run the narrowest relevant checks first, then broader tests when practical.
- For Django site work, prefer commands delegated through `applications/Makefile` with the appropriate `WEBSITE=...` value.
- For shared library work, run tests or checks that cover both the library and affected sites when practical.
