# Precis Legacy Plugin Template Scope — AI Agent Instructions

**Scope:** `projects/precis/precis-lms/assets/templates/plugins/`

Read `projects/precis/precis-lms/backend/AGENTS.md` and the root `AGENTS.md` first. This
folder is a legacy/template compatibility scope inside Precis assets. It is not
the canonical location for new Django app templates.

## Canonical ownership for new work

- Auth/account templates: `projects/precis/precis-lms/backend/apps/auth/` or the owning
  account feature under `backend/apps/pages/`.
- Learning templates: `projects/precis/precis-lms/backend/apps/learning/`.
- Blog/profile/product/page templates: the corresponding
  `backend/apps/pages/<feature>/templates/` directory.
- Site-root overrides: `projects/precis/precis-lms/backend/templates/`.
- Generic framework components: `libs/django-fusion/`.

Only modify this directory when an existing Precis loader or compatibility
contract demonstrably still consumes it. Do not create new `plugins/<app>/`
trees merely to follow old documentation.

## Template rules

- Preserve existing context, inheritance, translations, permissions, Wagtail
  fields, email variables, and HTMX contracts.
- Use `{% comp %}` when a registered component exists and `fragment_name` for
  fragment identifiers/context keys.
- Keep generated/transactional email content escaped and data-driven.
- Use BEM classes and no IDs for styling.
- Search all callers and the active `TEMPLATES` configuration before moving or
  deleting a template.
