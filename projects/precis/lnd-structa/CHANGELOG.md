# Landing-Fusion changelog

All notable Landing-Fusion changes are recorded here.

## 2026-08-11 - Active project closeout

### Changed

- Confirmed `projects/precis/landi/` as the canonical landing project after
  the former CMS-Fusion migration.
- Kept Astro 5, Tailwind 4, HTMX, Alpine.js, Django, and Wagtail as the active
  stack. No retired Next.js/FlyonUI plan was silently reintroduced.
- Reconciled the project README and canonical plan links with the current
  project boundary.
- Documented the project as a content-first rendering surface: Wagtail data,
  semantic Astro documents, and HTMX/Alpine progressive enhancement.

### Verification

- Backend checks and content tests remain the required gate before changing
  page/block contracts.
- Frontend `npm run check` and `npm run build` remain the required frontend
  gates.
- Docker and Traefik rollout remains a separate deployment gate and is not
  claimed complete by this documentation-only closeout.

## 2026-07-30 - Initial AHA landing slice

- Astro landing pages with Tailwind, HTMX, and Alpine.js.
- Django/Wagtail editable page models and seed content.
- django-fusion handlers and fragment rendering.
- Dark mode, skeleton loading, SEO metadata, and semantic header/footer.
