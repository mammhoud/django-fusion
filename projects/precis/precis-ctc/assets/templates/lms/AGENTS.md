# Precis Learning Asset Templates — AI Agent Instructions

**Scope:** `projects/precis/precis-main/assets/templates/lms/`

Read `projects/precis/precis-main/backend/AGENTS.md` and the root `AGENTS.md` first. This is
Precis-owned learning presentation/compatibility template content.

New learning behavior belongs in `projects/precis/precis-main/backend/apps/learning/` and
its app templates. Keep this directory only for templates explicitly resolved
from the Precis asset tree; do not add obsolete `plugins/lms/` paths.

Preserve course, enrollment, progress, certification, search, and learner
profile context. Keep full-page and HTMX fragment responses compatible, use
`fragment_name` for fragment identifiers, `{% comp %}` for registered
components, BEM classes, and no IDs for styling. Check learning URL/viewset
callers and tests before changing template contracts.
