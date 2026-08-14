# Precis LMS

> **Status:** 🟢 Production — learning platform powering structa.cloud
> **Tags:** #lms #django #wagtail #fusion #courses #learning
> **Stack:** Django 5.2 + Wagtail 7.4 + django-fusion + Astro 5 + Stripe

Precis LMS is a content-driven learning management system. Courses, enrollments,
payments, progress tracking, and certificates — all built on django-fusion's
component pipeline with an Astro frontend (hybrid rendering: SSG + SSR via the django-fusion bridge).

---

## Editions

| Edition | Price | Features |
|---------|:-----:|----------|
| **Solo** | $29/mo | Unlimited courses, certificates, priority support, analytics, SSO, role management, high-end design |
| **Business** | $99/mo | Everything in Solo + custom branding, API access |

---

## Repository Layout

```
projects/precis/main/
├── backend/                   # Django 5.2 + Wagtail
│   ├── apps/
│   │   ├── content/           # StreamField blocks + content templates
│   │   ├── learning/          # Learning/LMS app (courses, enrollments, progress)
│   │   ├── pages/             # Page models, profile, accounts
│   │   ├── domain/            # Domain models (contacts, locations, users, newsletter)
│   │   └── handlers/          # django-fusion PageHandler views
│   ├── assets/                # Static, media, templates, fixtures
│   ├── settings.py            # Site configuration (Dynaconf)
│   └── manage.py
├── frontend/                  # Astro 5 (hybrid SSG + SSR)
│   ├── src/
│   │   ├── pages/             # Course catalog, detail, dashboard, profile
│   │   └── components/        # Reusable Astro + React components
│   └── package.json
├── compose/                   # Dockerfiles + entrypoint scripts
├── Env/                       # Environment YAML configs
├── Makefile
└── docker-compose.yml
```

---

## Quick Start

### Backend

```bash
cd projects/precis/main/backend
uv run --project ../.. python manage.py migrate
uv run --project ../.. python manage.py runserver 0.0.0.0:8073
```

### Frontend

```bash
cd projects/precis/main/frontend
npm install
npm run dev
```

---

## Key Features

- **Content-driven courses** — Lessons, quizzes, certificates composed in Wagtail StreamFields
- **Payment built-in** — Stripe checkout for courses, enrollments, subscriptions
- **Fragment-rendered UI** — django-fusion HTMX fragments keep the app server-rendered
- **Progress tracking** — Per-lesson completion, enrollment status, certificates
- **Wishlist** — Save courses for later
- **Multilingual** — Arabic + English editorial overlays via PageTranslation snippet
- **Email workflows** — Welcome, enrollment confirmation, certificate issuance

---

## Key Files

| Path | Purpose |
|------|---------|
| `backend/apps/learning/` | LMS views, course catalog, enrollments |
| `backend/apps/pages/profile/` | User profile, learning record |
| `backend/apps/pages/accounts/` | Auth adapters, registration flow |
| `backend/apps/domain/models/` | Core domain models (users, contacts, locations) |
| `backend/apps/handlers/` | PageHandler views, fragment rendering |
| `backend/assets/templates/` | Site-specific Wagtail templates |
| `compose/Dockerfile.backend` | Production backend Dockerfile |
| `compose/Dockerfile.frontend` | Production frontend Dockerfile |

---

## Related

| Resource | Link |
|----------|------|
| Landing-Fusion docs | [`../precis/landi/README.md`](../precis/landi/README.md) |
| django-fusion | [`../../libs/django-fusion/README.md`](../../libs/django-fusion/README.md) |
| Docs sidebar | [`../../docs/_sidebar.md`](../../docs/_sidebar.md) |
| Infrastructure | [`../../docs/infrastructure/`](../../docs/infrastructure/) |
