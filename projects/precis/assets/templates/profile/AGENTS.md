# Precis Profile Asset Templates — AI Agent Instructions

**Scope:** `projects/precis/assets/templates/profile/`

Read `projects/precis/backend/AGENTS.md` and the root `AGENTS.md` first. New
profile behavior belongs in the active profile app under
`projects/precis/backend/apps/pages/profile/` when enabled. This asset folder
is for Precis-specific templates explicitly loaded from the asset tree.

Preserve user/profile context, authorization, forms, notifications, HTMX
targets, translations, and MFA/security state. Use `{% comp %}` for registered
components, `fragment_name` for fragments, BEM classes, and no styling IDs.
Check the profile views/URLs and tests before changing markup or context.
