# Precis Account App Templates — AI Agent Instructions

**Scope:** `projects/structa.cloud/backend/apps/pages/accounts/templates/`

Read `projects/structa.cloud/backend/AGENTS.md` and the root `AGENTS.md` first. These
are account/registration templates owned by the Precis accounts feature.

Preserve allauth context, CSRF, validation errors, redirects, translations,
permissions, HTMX modal targets, and email-confirmation/password-reset flows.
Use `{% comp %}` for registered components and `fragment_name` for fragment
identifiers/context keys. Keep BEM classes and no IDs for styling.

Before editing, inspect the accounts URLs, adapters/views, relevant allauth
base templates, and focused auth tests. Do not move new account templates into
obsolete `plugins/accounts/` paths.
