# Precis Blog App Templates — AI Agent Instructions

**Scope:** `projects/precis/precis-main/backend/apps/pages/blog/templates/`

Read `projects/precis/precis-main/backend/AGENTS.md` and the root `AGENTS.md` first. These
templates belong to the Precis blog feature.

Preserve post/category/tag/comment context, Wagtail fields, pagination,
permissions, translations, normal-page rendering, and HTMX search/comment
responses. Use `{% comp %}` for registered components, `fragment_name` for
fragment identifiers/context keys, BEM classes, and no styling IDs.

Check blog URLs/views/services and focused tests before changing template names,
blocks, context variables, or response targets. Do not use obsolete
`plugins/blog/` paths in new code.
