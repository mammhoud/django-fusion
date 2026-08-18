---
name: structa-backend
description: "Structa Cloud backend conventions — Django + Wagtail + django-fusion. Use for any backend work in this monorepo: models, services, viewsets/PageHandlers, HTMX fragments, {% comp %} components, routing, migrations, and management commands. Encodes the real package architecture (src/django_fusion/comp, routes, fragments, core), product app layout (models/services/handlers/api), canonical django_fusion.* imports (no re-export shims), and the repo's validation workflow (make check / manage.py check / pytest)."
argument-hint: "<backend feature or area>"
---

# Structa Backend — Django/Wagtail/django-fusion Conventions for Structa Cloud

## 1. Skill Meta

**Name:** Structa Backend
**Description:** The repo's backend engineering standards. Most web products
run Django + Wagtail + django-allauth + HTMX on top of the local `django-fusion`
library. This skill encodes where code belongs, how the framework is used, and
how to validate changes.

## 2. Where Code Belongs (ownership)

- **Product code** → the owning product under `projects/<product>/` (e.g. `projects/precis/precis-lms/backend/`, `projects/precis/precis-ctc/backend/`).
- **Shared Django settings** → `projects/precis/configs/` ONLY when multiple products genuinely consume the same behavior.
- **Shared framework behavior** → `libs/django-fusion/` (component registry, viewsets, fragments, forms, tables, routing).
- **Product app layout** — prefer existing boundaries: `models`, `services`, `handlers`, `api`, `components`, `management`, `domain`. Do not grow large view functions into service layers.
- **Canonical imports:** `from django_fusion.comp import ...`, `from django_fusion.routes import ...`, `from django_fusion.fragments import ...` — import the real symbol from its owning module. **No re-export shims, alias modules, or forwarding `__init__.py` re-exports.** Delete empty/forwarding-only modules rather than leaving placeholder `__init__.py` files.

## 3. django-fusion Package Architecture (real layout)

```text
libs/django-fusion/src/django_fusion/
├── comp/                 # component registry, tags, loaders, cache
├── routes/               # applications, viewsets, handlers, renderers
├── fragments/            # fragment views, forms, tables, analyzer
├── management/           # commands, handlers, managers, filters, utils
├── core/                 # middleware, context, assets, health, rendering
├── models/               # shared models and mixins
├── services/             # reusable service layer
├── plugins/              # HTMX, debug, API, Webpack, Unpoly, Robyn hooks
├── contrib/              # admin, privacy, branding, integrations
├── assets/               # SCSS/JS source and design tokens
└── templates/            # framework layouts and components
```

Check `libs/django-fusion/AGENTS.md` (and its `docs/`, `PROMPTS.md`,
`QUICKSTART.md`) before reaching for a framework feature — the framework may
already provide it.

## 4. Core Patterns

### Request flow
```
→ project urls.py → middleware (sessions, auth, CSRF, locale, HTMX, site middleware)
→ PageHandler / Viewset / Wagtail page / API endpoint
→ model / service / query layer
→ template, fragment, JSON, or stream response
```

### Templates & components
- Use `{% comp "name" /%}` for registered django-fusion components (with `{% prop %}`, `{% slot %}`, `{% var %}`).
- Use `{% include %}` ONLY for genuinely dynamic template names or local includes that are not registered components.
- Use `fragment_name` for fragment identifiers and context keys.
- Preserve Wagtail context, translation tags, permissions, and HTMX attributes.
- BEM-style classes for reusable UI; never use IDs for styling.

### Dual rendering
Landing-Fusion and Formint use a render-first/data-API contract: a request may
receive complete server-rendered HTML, an HTMX fragment, or JSON for an Astro
client. Preserve explicit endpoint contracts and headers. Do NOT replace a
server-rendered fragment with a client-only mock.

### Background work
PostgreSQL is the primary relational DB; Redis backs queues/cache (Celery/Dramatiq
workers). Do not run migrations, destructive fixture loads, or production
commands against a shared environment without explicit user direction.

## 5. Validation Workflow (narrowest first)

```bash
# Python/Django lint + system check
cd projects/precis/precis-lms/backend && make check   # ruff check + manage.py check
python manage.py check

# Focused tests
cd projects/precis/precis-lms/backend && make test
cd libs/django-fusion && uv run pytest                # framework tests

# Dispatcher-level
cd projects && make check WEBSITE=precis-lms
make test WEBSITE=precis-lms
```

Report any checks you couldn't run. Never run migrations or fixture loads
against shared environments without explicit permission.

## 6. Change Checklist (backend)

- [ ] Read the nearest `AGENTS.md` (root → projects → product → backend).
- [ ] Confirmed the owning product and current path (check `projects/Makefile` aliases; e.g. `WEBSITE=precis-lms` → `projects/precis/precis-lms/`).
- [ ] Searched for existing helpers/components/routes/services with `rg` before adding new ones.
- [ ] Imported real symbols from `django_fusion.*` — no re-export shims.
- [ ] Kept business logic in services/managers/domain, not in view functions or templates.
- [ ] Used `{% comp %}` for registered components, `fragment_name` for fragment identifiers.
- [ ] Ran the narrowest check (`make check` / `python manage.py check` / targeted pytest) and reported results.
- [ ] Updated the relevant docs (see structa-docs) if routes, models, or contracts changed.
- [ ] Reviewed diff for stale paths, secrets, scope leakage into other products.
