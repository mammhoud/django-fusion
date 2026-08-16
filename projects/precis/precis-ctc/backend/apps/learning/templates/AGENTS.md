# Precis Learning App Templates — AI Agent Instructions

**Scope:** `projects/precis/precis-lms/backend/apps/learning/templates/`

Read `projects/precis/precis-lms/backend/AGENTS.md` and the root `AGENTS.md` first. These
are templates owned by the Precis learning app.

Preserve course/catalog, enrollment, progress, certificate, search, and learner
profile context. Keep templates compatible with Wagtail fields, authentication,
permissions, translations, full-page rendering, and HTMX fragments.

Use `{% comp %}` for registered django-fusion components, `{% include_block %}`
for StreamField blocks, and `fragment_name` for fragment identifiers/context
keys. Keep reusable styles BEM-based and do not use IDs for styling. Check the
learning URL/viewset and focused tests before changing a template contract.
