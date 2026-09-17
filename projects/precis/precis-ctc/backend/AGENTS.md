# CTC Research Backend — AI Agent Instructions

**Path:** `projects/precis/precis-ctc/backend/`
**Product:** CTC Research / medical research center
**Stack:** Django 5.2 + Wagtail 7.4 + django-fusion + allauth + HTMX/Alpine integration

Read `/AGENTS.md` and `/projects/AGENTS.md` first. This file applies to the
CTC Research backend only; it does not describe the retired `projects/precis-lms/`
boundary, the separate Precis/LMS project, or the Precis Landing backend.

## Directory structure

```text
backend/
├── apps/
│   ├── content/             # Wagtail/content hooks, tasks, content behavior
│   ├── learning/            # Courses, catalog, enrollment, progress, certificates
│   ├── pages/               # Page/domain feature package and URL aggregation
│   ├── handlers/            # Request handlers, renderers, signals, email helpers
│   ├── auth/                # Allauth adapters and authentication integration
│   ├── core/                # Shared routes, renderers, signals, services, URLs
│   ├── domain/              # Site/domain configuration
│   └── components/          # Backend-owned reusable component templates
├── templates/               # Backend/site-root templates and overrides
├── assets/                  # Backend runtime fixtures/static support
├── migrations/              # Backend-owned migrations where applicable
├── settings.py              # Backend settings and app registration
├── urls.py                  # Root URL configuration
├── manage.py                # Django CLI
├── server.py                # Server entry point
├── __main__.py              # Project command entry point
└── tests/                   # Backend-focused test suite and fixtures
```

The repository has migrated away from the old `plugins.*`/`www.*` layout in
active code. Use the actual `apps.*` packages and inspect `settings.py` before
assuming an app exists.

## App ownership

- `apps/learning/` owns learning domain models, applications, viewsets,
  signals, Wagtail hooks, and learning URLs.
- `apps/pages/` owns page-oriented product features such as blog, profile,
  accounts, products, and page models when present in the checkout.
- `apps/content/` owns shared content behavior, Wagtail hooks, and content
  tasks; it should not become a generic domain dump.
- `apps/handlers/` owns request/fragment rendering integration and handler
  middleware. Keep URL-facing orchestration thin.
- `apps/core/` owns genuinely cross-feature backend primitives. Avoid placing
  product-specific learning logic here.
- `apps/auth/` owns Precis-specific allauth adapters and auth integration.

Before adding an app or moving a model, check `INSTALLED_APPS`, migrations,
URL includes, Wagtail hooks, and existing imports with `rg`.

## URL and rendering flow

The root URL configuration is the source of truth. In general, routes include:

```text
admin / django-admin / documents
accounts and auth
learning application
page/content feature URLs
API and HTMX fragment endpoints
Wagtail page catch-all
```

Use django-fusion's `Application`, `PageHandler`, `RoutableComponent`, and
fragment helpers when the surrounding app already uses them. Keep
`fragment_name` stable. A request can be a full document, an HTMX fragment, or
an API response; preserve the existing detection and response contracts.

## Templates and assets

There are several template roots. Confirm `settings.py` and the nearest
`AGENTS.md` before adding or overriding a file:

1. `backend/templates/` — site-root shells, errors, events, admin overrides,
   and deliberate project-wide overrides.
2. `backend/apps/**/templates/` — app-owned templates close to their views.
3. `structa.cloud/assets/templates/` — project asset/template source where configured.
4. `libs/django-fusion/src/django_fusion/templates/` — framework fallback.

Do not put app-specific templates in the backend root merely because they are
convenient. Do not duplicate django-fusion components. Use `{% comp %}` for
registered components, `{% include_block %}` for Wagtail blocks, and `{% include
%}` for dynamic/local includes. Preserve translation tags, permissions,
context names, inheritance, and HTMX attributes.

Keep SCSS/source assets separate from compiled CSS and collected static files.
CTC Research-specific branding and styles belong under `projects/precis/precis-ctc/assets/` or
the owning frontend, not in the framework library.

## Commands

```bash
cd projects/precis/precis-ctc/backend
make check
make test
make migrate
make collectstatic

# Workspace dispatcher
cd projects
make show-config WEBSITE=precis-ctc
make check WEBSITE=precis-ctc
make test WEBSITE=precis-ctc
```

Read the backend Makefile before running migration, fixture, seed, or server
targets. Use a test/SQLite database for local tests where supported. Do not
load fixtures or migrate a shared/production database without explicit intent.

## Testing

Backend tests cover settings, API smoke behavior, fixture contracts, learning
search/detail/progress, page rendering, and domain invariants. A model, page,
URL, or template contract change should update the smallest relevant test and
then run `make check` plus the focused test module.

For cross-product behavior, use `tests/` rather than importing Precis internals
into unrelated products. For framework behavior, use `libs/django-fusion/tests/`
and a consuming-product regression test.

## Do not

- Do not use old `plugins.*`, `www.*`, or `projects/precis-lms/` paths in new
  imports or files.
- Do not move Precis Landing-only APIs or templates into Precis.
- Do not hand-edit generated static bundles.
- Do not modify migrations to hide a schema mismatch; reproduce it and create a
  real migration.
- Do not add compatibility re-exports when a canonical import already exists.
