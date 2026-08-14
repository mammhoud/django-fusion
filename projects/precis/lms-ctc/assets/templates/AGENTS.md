# Precis Asset Templates — AI Agent Instructions

**Scope:** `projects/precis/main/assets/templates/`

Read `projects/precis/main/backend/AGENTS.md` and the root `AGENTS.md` first. These
are Precis-owned asset templates, not automatically shared templates for every
Structa Cloud product.

## Role and resolution

This directory may be included by Precis settings as a project asset template
root. Verify the active `TEMPLATES['DIRS']` and app loaders before relying on a
specific precedence. In general, the intended ownership order is:

```text
Precis backend/templates/             # deliberate site-root overrides
Precis backend/apps/**/templates/     # app-owned templates
Precis assets/templates/              # Precis asset/template source
libs/django-fusion/.../templates/    # framework fallback
```

Do not document this directory as `projects/assets/templates/`; that is a
separate path. Do not place Landing-Fusion, Syntara, or POS templates here.

## Rules

- Keep templates specific to Precis assets, branding, content blocks, and
  project-owned presentation.
- Preserve Wagtail `value`/StreamField contracts and Django context names.
- Use `{% comp %}` for registered django-fusion components and
  `{% include_block %}` for Wagtail blocks.
- Use `fragment_name` for HTMX fragments and context keys.
- Preserve i18n, permissions, escaping, and full-page/fragment behavior.
- Use BEM classes; never use IDs for styling.
- Search for an existing component and check the nearest scoped AGENTS file
  before adding a duplicate.
