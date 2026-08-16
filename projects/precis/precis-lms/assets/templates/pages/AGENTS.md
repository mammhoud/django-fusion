# Precis Page Templates — AI Agent Instructions

**Scope:** `projects/precis/precis-lms/assets/templates/pages/`

Read `projects/precis/precis-lms/backend/AGENTS.md` and the root `AGENTS.md` first. This is
a Precis-owned page/template asset scope.

## Ownership

- Put site-wide shells and deliberate global overrides in
  `projects/precis/precis-lms/backend/templates/`.
- Put page-feature templates next to their owning app under
  `projects/precis/precis-lms/backend/apps/pages/<feature>/templates/`.
- Keep this asset directory for Precis-specific page assets, includes, or
  presentation templates that are explicitly loaded by Precis settings.
- Do not use obsolete `plugins/<app>/templates/` paths in new files.
- Do not place Landing-Fusion, Syntara, or POS page templates here.

## Rules

- Confirm the active template loader and caller before adding or overriding a
  file.
- Preserve Wagtail page context, StreamField values, URL names, translations,
  permissions, and HTMX fragment behavior.
- Use `{% comp %}` for registered components and `{% include_block %}` for
  Wagtail blocks.
- Use `fragment_name` for fragment identifiers/context keys.
- Keep overrides thin, use BEM classes, and do not use IDs for styling.
- Check the nearest app template and django-fusion equivalent before copying
  markup; avoid duplicate implementations.
