# Precis Profile App Templates — AI Agent Instructions

**Scope:** `projects/structa.cloud/backend/apps/pages/profile/templates/`

Read `projects/structa.cloud/backend/AGENTS.md` and the root `AGENTS.md` first. These
templates belong to the Precis profile feature.

Preserve authenticated-user/profile context, permissions, forms, notifications,
MFA/security flows, translations, and HTMX targets. Use `{% comp %}` for
registered components, `fragment_name` for fragment identifiers/context keys,
BEM classes, and no IDs for styling.

Inspect profile URLs/views and focused tests before changing template contracts.
Do not use obsolete `plugins/profile/` paths in new code.
