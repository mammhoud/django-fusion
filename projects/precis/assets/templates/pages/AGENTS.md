# Site Template Root

Scope: site-root entry templates, error pages, and project-wide overrides.

## Lookup Strategy

Templates in this directory resolve before app templates loaded via Django's
`APP_DIRS`. Keep files here only when they are intentional site-specific entry
points, branded shells, or templates that must shadow app/django-fusion
behavior.

## What belongs here

- `base.html`, `base_page.html`, `index.html`
- `errors/` — site-wide error pages
- `events/` — site-root event templates (no dedicated plugin)
- `wagtailadmin/` — Wagtail admin overrides
- Project-wide overrides for app templates (use sparingly)

## What does NOT belong here

- App-specific templates — those live in `plugins/<app>/templates/<app>/`.
- Reusable UI components — those live in `libs/django-fusion/src/django_fusion/templates/`.

## Override Rules

- Prefer deleting exact duplicates and allowing Django to load the app or
  django-fusion equivalent.
- Keep thin overrides for branded variations; move reusable repeated markup into
  shared includes under `libs/django-fusion/src/django_fusion/templates/components/`.
- Preserve existing template names, include names, block names, and context variables to avoid breaking Wagtail/Django rendering.
- Use `fragment_name` for fragment identifiers and context keys; do not introduce alternate fragment naming.
- When adding or changing a site override, compare the same relative path in
  `libs/django-fusion/src/django_fusion/templates/` and the relevant
  `plugins/<app>/templates/` first.

## Notes

App-specific template directories previously located here (`blog/`, `lms/`,
`pages/`, `products/`, `auth/`, `account/`, `registration/`, `learning/`,
`certification/`, `courses/`, `about/`, `home/`, `team/`, `contact/`,
`services/`) have been moved to the appropriate `plugins/<app>/templates/`
locations. See the project-level `backend/AGENTS.md` for the full layout.
