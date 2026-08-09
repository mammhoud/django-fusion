# Precis Backend App Templates — AI Agent Instructions

**Scope:** `projects/precis/backend/apps/templates/`

Read `projects/precis/backend/AGENTS.md` and the root `AGENTS.md` first. This is
an app-owned template scope within Precis. New templates should normally live
in the specific app directory that owns their view/model, for example:

```text
apps/learning/templates/
apps/pages/blog/templates/
apps/pages/profile/templates/
apps/pages/accounts/templates/
apps/handlers/templates/
```

Use this root only when the active app loader explicitly owns it. Do not use
obsolete `plugins/` or `www/` paths in new files. Preserve context variables,
Wagtail fields, translation tags, permissions, URL names, HTMX attributes, and
fragment contracts. Prefer `{% comp %}` for registered components, use
`fragment_name` consistently, and keep styling BEM-based without IDs.
