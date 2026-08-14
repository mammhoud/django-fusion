# Landing Fusion — Backend API

> Django 5.2 + Wagtail 7.4 backend for the Structa Cloud landing site.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|:------:|-------------|
| `/apis/navigation/` | GET | Site navigation tree (with children) |
| `/apis/pages/<slug>/` | GET | Full page data (hero, body, sections) |
| `/apis/content/languages/` | GET | Active language catalog (7 languages) |
| `/apis/pages/home/` | GET | Home page content |
| `/apis/render-mode/` | GET | Current fusion render mode |
| `/apis/site/settings/` | GET | Site-wide settings (branding, SEO) |
| `/apis/contact/` | POST | Contact form submission |
| `/htmx/*` | GET/POST | HTMX fragment endpoints |
| `/accounts/*` | GET/POST | Authentication (login, signup, password reset) |
| `/learning/*` | GET/POST | Course catalog, enrollment, progress |

---

## Key Modules

### `apps/pages/api.py`

Main API views serving page content, navigation, languages, and site settings.
Uses django-fusion's component system for fragment rendering.

### `apps/handlers/views.py`

PageHandler views that unify fragment and full-page rendering. HTMX requests get
`pages/fragments/page.html`; plain requests get the full document layout.

### `apps/learning/`

Course catalog, enrollment, progress tracking, certificates, wishlist. Uses
django-fusion's form/table mixins and HTMX for interactive fragments.

### `apps/content/`

StreamField block types, language model (SiteLanguage snippet), translation
overlays (PageTranslation snippet), newsletter, and site settings.

---

## Quick Commands

```bash
cd projects/precis/landi/backend

# Run dev server
uv run --project ../.. python manage.py runserver 0.0.0.0:8074

# Seed pages
uv run --project ../.. python manage.py seed_pages

# Seed learning catalog
uv run --project ../.. python manage.py seed_learning

# Run tests
uv run --project ../.. python manage.py test

# Check
uv run --project ../.. python manage.py check
```

---

## Related

- [`../README.md`](../README.md) — project overview
- [`frontend.md`](frontend.md) — Astro frontend docs
- [`deployment.md`](deployment.md) — Docker deployment
