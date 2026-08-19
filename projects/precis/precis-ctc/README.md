# CTC Research — medical research center

> **Status:** 🟢 Standalone project — `projects/precis/precis-ctc/`
> **Tags:** #research #django #wagtail #fusion #evidence #medical
> **Stack:** Django 5.2 + Wagtail 7.4 + django-fusion + Astro 5 + Stripe

CTC Research is the standalone medical research center site serving
`ctc-research.com`. It owns its own backend, Astro frontend, Compose stack,
and database (`db_ctc`) — it does not share Precis/LMS runtime state.

The medical research catalog (clinical trial design, biostatistics,
evidence synthesis, medical AI, manuscript writing, research integrity) is
seeded from `backend/apps/learning/fixtures/medical_research_catalog.json` and
`backend/assets/fixtures/dump-data.json`.

---

## Editions

| Edition | Price | Features |
|---------|:-----:|----------|
| **Solo** | $29/mo | Unlimited courses, certificates, priority support, analytics, SSO, role management, high-end design |
| **Business** | $99/mo | Everything in Solo + custom branding, API access |

---

## Repository Layout

```
projects/precis/precis-ctc/
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

> 📖 Full step-by-step setup & build: [`docs/SETUP_AND_BUILD.md`](docs/SETUP_AND_BUILD.md)

### Backend

```bash
cd projects/precis/precis-ctc/backend
uv run --project ../.. python manage.py migrate
uv run --project ../.. python manage.py runserver 0.0.0.0:8073
```

### Frontend

```bash
cd projects/precis/precis-ctc/frontend
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
| `backend/assets/fixtures/ctc-research-media.json` | Archive media metadata and dump-compatible aliases |
| `backend/apps/core/management/commands/prepare_ctc_media.py` | Non-destructive archive-to-website media preparation |
| `docs/MEDIA_ARCHIVE.md` | Media topology, preparation, content and visual review guide |
| `backend/assets/templates/` | Site-specific Wagtail templates |
| `compose/Dockerfile.backend` | Production backend Dockerfile |
| `compose/Dockerfile.frontend` | Production frontend Dockerfile |

---

## Related

| Resource | Link |
|----------|------|
| **Setup & Build guide** | [`docs/SETUP_AND_BUILD.md`](docs/SETUP_AND_BUILD.md) — full step-by-step startup/build instructions |
| Landing-Fusion docs | [`../precis/precis-landing/README.md`](../precis/precis-landing/README.md) |
| django-fusion | [`../../libs/django-fusion/README.md`](../../libs/django-fusion/README.md) |
| Docs sidebar | [`../../docs/_sidebar.md`](../../docs/_sidebar.md) |
| Infrastructure | [`../../docs/infrastructure/`](../../docs/infrastructure/) |
