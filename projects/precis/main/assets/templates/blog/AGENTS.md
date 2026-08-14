# Precis Blog Asset Templates — AI Agent Instructions

**Scope:** `projects/precis/main/assets/templates/blog/`

Read `projects/precis/main/backend/AGENTS.md` and the root `AGENTS.md` first. This
folder contains Precis blog presentation assets or compatibility templates.

## Ownership and placement

New blog behavior belongs in the active blog application under
`projects/precis/main/backend/apps/pages/blog/` when that app is enabled. Keep this
folder for templates explicitly loaded from the Precis asset tree; do not
invent `plugins/blog/` paths or move blog logic into templates.

## Rules

- Preserve post/category/tag/comment context, Wagtail fields, pagination, and
  permissions.
- Preserve normal-page and HTMX search/result rendering when both are used.
- Use `{% comp %}` for registered components and `fragment_name` for fragments.
- Use BEM classes, no styling IDs, and pass only required context to includes.
- Check the owning app templates and django-fusion components before adding a
  duplicate.
- Test blog index/detail/search/comment paths affected by a template change.
