# Precis LMS — Architecture Decision Record

> **Status:** Active (2026-08-10)
> **Product:** Precis LMS / learning platform
> **Stack:** Django 5.2 + Wagtail 7.4 + django-fusion + Astro 5 + HTMX + Alpine.js
> **Updated:** 10 August 2026
> **Path:** `projects/precis/precis-main/`

---

## Context

Precis LMS is the learning management product powering structa.cloud. Learners
browse a course catalog, enroll, watch lessons, complete quizzes, and earn
certificates. Content editors manage course structure through Wagtail's
StreamField blocks. The system is content-driven: Wagtail pages define the
catalog, blog, and marketing surface; django-fusion provides the component
pipeline for reusable UI.

## Goals

- **Content-driven courses.** Wagtail pages own the catalog layout; learning
  models own enrollments, progress, and certificates.
- **Hybrid rendering.** Full Django pages for SEO, HTMX fragments for
  interactivity, Astro for the learner dashboard and marketing pages.
- **Background processing.** Long-running tasks (video transcoding, email
  digests, course completion sync) run via `django_fusion.tasks.@task`.
- **Skeleton loading.** Build-time skeleton manifest → Astro bridge → RUM
  metrics for perceived performance.
- **Per-project isolation.** Templates, assets, and static files are scoped to
  `projects/precis/precis-main/`, never shared with precis-landing or formints.

---

## Architecture Decisions

### ADR-1: Django + Wagtail as the content backbone

**Decision:** Wagtail Page models own the course catalog layout; a separate
`apps/learning/` Django app owns domain models (enrollments, progress,
certificates, payments). They communicate through Wagtail hooks and signals,
not through tight ORM coupling.

**Rationale:**
- Wagtail gives editors a familiar CMS for course landing pages, blog, and
  marketing content.
- Separating domain models into `apps/learning/` keeps the data layer
  testable and prevents StreamField migration lock-in.
- django-fusion `PageHandler` bridges the two: a Wagtail page can delegate to
  a learning viewset for the data payload.

**Trade-offs:**
- Two model layers instead of one; requires discipline about which layer owns
  which concern.
- Wagtail page revisions don't cascade to learning data — intentional, as
  course metadata changes shouldn't trigger enrollment re-validation.

### ADR-2: Hybrid rendering (Django + Astro)

**Decision:** Public-facing pages (catalog, blog, marketing) render
server-side through Django/Wagtail. The learner dashboard and interactive
course player use Next.js with API data from Django endpoints.

**Rendering matrix:**

| Surface | Technology | Rendering | Data source |
|:--------|:-----------|:----------|:------------|
| Course catalog | Wagtail + django-fusion | Server (SEO) | Wagtail pages + learning viewsets |
| Course detail | Wagtail + HTMX fragments | Server + partial swap | Learning models |
| Blog | Wagtail blog pages | Server (SEO) | Wagtail pages |
| Learner dashboard | Astro (SSG/SSR) | Hybrid | REST API (`/api/learning/`) |
| Course player | Astro + HTMX | Client + fragment | Lesson API + progress tracking |
| Authentication | Allauth + HTMX modals | Server + fragment | Django sessions |

**Rationale:**
- SEO-critical pages (catalog, blog) need server rendering for search engines.
- Astro provides SSG/SSR hybrid rendering — static where possible, server
  where needed — for the learner dashboard and marketing pages.
- HTMX fragments handle lightweight interactions (enroll, add to wishlist)
  without full-page reloads.
- django-allauth with HTMX modals keeps auth flow server-rendered while
  avoiding page transitions.

### ADR-3: Learning domain in `apps/learning/`

**Decision:** All learning-specific data lives in `apps/learning/models/`,
organized by subdomain:

```
apps/learning/models/
├── courses/                  # Course, Module, Lesson, CourseTag
│   ├── detail.py             # Module, ContentBlock
│   ├── specification.py      # Lesson, quiz stubs
│   └── tag.py                # CourseTag
├── enrollment.py             # Enrollment, progress tracking
├── certificate.py            # Certificate
├── payments.py               # PaymentTransaction, PaymentRefund, PaymentWebhookLog
├── wishlist.py               # Wishlist
├── quiz.py                   # Quiz models (future)
├── review.py                 # Course reviews
└── schemas/                  # Pydantic response schemas
    ├── lms.py                # FeatureResponse, DashboardResponse, etc.
    └── courses.py            # CourseResponse, CategoryResponse
```

**Rationale:**
- Single app for all learning concerns — easy to reason about.
- Subdirectories for hot domains (courses, payments) prevent a 2000-line
  `models.py`.
- Pydantic schemas in `schemas/` provide typed API contracts separate from
  ORM models.

### ADR-4: Background tasks via `@task` decorator

**Decision:** All async work uses `django_fusion.tasks.@task`, not Celery.
The InProcessBackend runs synchronously in dev/test; DramatiqBackend handles
production workloads via Redis.

**Task modules:**

| Module | Tasks | Trigger |
|:-------|:------|:--------|
| `apps/tasks/email_tasks.py` | `send_enrollment_confirmation`, `send_certificate`, `send_password_reset` | Signal / view |
| `apps/tasks/course_tasks.py` | `generate_course_progress_report`, `sync_course_completion_rates`, `send_weekly_learning_digest` | Schedule / admin |
| `apps/tasks/content_tasks.py` | `process_uploaded_video`, `generate_ai_course_description` | Upload signal |

**Rationale:**
- Eliminates Celery dependency — simpler deploy, fewer moving parts.
- `InProcessBackend` runs synchronously in tests, eliminating `CELERY_ALWAYS_EAGER`
  configuration.
- Shared worker pool with precis-landing (single Dramatiq worker per host)
  reduces resource cost.

### ADR-5: Astro frontend with django-fusion bridge

**Decision:** The frontend uses Astro 5 for both content pages (SSG) and the
learner dashboard (SSR). Astro components consume Django APIs via `fetch()`
in `onLoad`, HTMX fragments for partial swaps, and FusionCodec (`FusionDecoder`)
for base64-encoded payloads.

**Rationale:**
- Astro ships zero JS by default — marketing pages load fast.
- Island architecture: interactive widgets (course player, progress charts)
  hydrate independently.
- Same `LiveFragment.astro` / `SkeletonBridge.astro` components as
  precis-landing — shared django-fusion frontend contract.
- `FusionDecoder` + `Site` class in `src/lib/site.ts` mirror the precis-landing
  frontend pattern, reducing training cost.

**Key Astro pages:**

| Page | Rendering | Data source |
|:-----|:----------|:------------|
| `index.astro` | SSG | Django API → Hero/Features/CTA blocks |
| `courses/index.astro` | SSR | `/api/learning/courses/` |
| `courses/[slug].astro` | SSR | `/api/learning/courses/{slug}/` |
| `blog/[slug].astro` | SSG/SSR | Wagtail blog pages |
| `pricing.astro` | SSG | Static + Stripe checkout |

### ADR-6: Skeleton pipeline for perceived performance

**Decision:** Precis uses the django-fusion skeleton pipeline — a build-time
manifest that maps page paths → component skeleton variants. At runtime,
`SkeletonBridge.astro` renders placeholders that swap out when real content
arrives.

**Pipeline:**

```
make build-assets
  ├─ make skeleton-manifest
  │   └─ python manage.py generate_skeleton_manifest
  │       --output assets/static/skeleton-manifest.json
  │       → 5 pages processed (blog, courses, catalog)
  │
  └─ npx webpack --config webpack/precis.config.js
      → 3 entrypoints: main, app, precis
      → Output: assets/bundles/
```

**Rationale:**
- No per-page skeleton code — the manifest is auto-generated from template
  scans.
- 16 variant templates cover hero, grid, card, form, CTA, etc.
- RUM metrics (`window.__FUSION_PERF__`) track skeleton → content swap latency.

### ADR-7: Webpack-based asset pipeline

**Decision:** Precis uses webpack (via `projects/webpack/base.config.js`) with
project-specific config at `projects/precis/precis-main/webpack/precis.config.js`.
Per-project webpack aliases (`@precis`, `@precis-styles`, `@precis-js`) keep
imports scoped.

**Entrypoints:**

| Entry | Output | Contents |
|:------|:-------|:---------|
| `main` | `main.*.js` / `main.*.css` | Base styles, utilities, theme |
| `app` | `app.*.js` / `app.*.css` | Auth, navigation, modals |
| `precis` | `precis.*.js` / `precis.*.css` | Precis-specific: course cards, progress bars, certificates |

**Rationale:**
- Three entrypoints enable code splitting — most pages only load `main` +
  one additional bundle.
- `django-webpack-loader` → `{% render_bundle 'main' %}` in Django templates.
- Same webpack base config as precis-landing, reducing drift.

---

## Data Model (Core)

### Learning domain

```
Course (Wagtail Page)
  ├── title, description, image, category
  ├── price, currency, discount
  ├── instructor, duration, level
  └── → has many Module(s)

Module (Orderable, ClusterableModel)
  ├── title, description, order
  └── → has many Lesson(s)

Lesson (Orderable, ClusterableModel)
  ├── title, video_url, content (StreamField)
  ├── duration, is_free_preview
  └── → progress tracked per-user

Enrollment
  ├── user FK, course FK
  ├── status: active | completed | cancelled
  ├── enrolled_at, completed_at
  └── → has many LessonProgress entries

LessonProgress
  ├── enrollment FK, lesson FK
  ├── status: not_started | in_progress | completed
  ├── watched_seconds, total_seconds
  └── completed_at

Certificate
  ├── user FK, course FK, enrollment FK
  ├── certificate_id (UUID), issued_at
  └── → PDF generation via @task
```

### Payment domain

```
PaymentTransaction
  ├── user FK, course FK, enrollment FK
  ├── stripe_session_id, amount, currency, status
  └── → webhook updates via PaymentWebhookLog

PaymentRefund
  ├── payment FK, amount, reason, status
  └── → processed via Stripe API

PaymentWebhookLog
  ├── stripe_event_id, event_type, raw_payload
  └── → append-only audit log
```

---

## Request Lifecycle

```
Client (Browser / Next.js SPA)
  │
  ▼
┌─ Traefik / Docker ───────────────────────────────────────────────────┐
│  Routes by Host header → precis container (:8000)                    │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌─ Django Middleware ─────────────────────────────────────────────────┐
│  Session → Auth → Site → CSRF → Locale → HTMX → Access Control      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
        Wagtail Page     PageHandler       API/Viewset
        (catalog, blog)  (hybrid render)   (JSON endpoints)
              │                │                 │
              │                ├─ Accept: text/html → full page
              │                ├─ HX-Request → HTMX fragment
              │                └─ Accept: json → FusionCodec response
              │                │                 │
              └────────────────┼─────────────────┘
                               │
                               ▼
┌─ Template ──────────────────────────────────────────────────────────┐
│  {% comp "blocks/course-card.html" /%}                              │
│  {% fusion_page_skeleton template_path="courses/catalog.html" %}    │
│  {% render_bundle 'precis' %}                                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
                         HTML / JSON / Stream
```

---

## Build & Deploy Pipeline

```
make build
  ├─ ① install-assets          → npm install
  ├─ ② skeleton-manifest       → generate_skeleton_manifest
  ├─ ③ build-assets            → npx webpack --mode=production
  └─ ④ docker compose build    → Docker images (backend + worker + frontend)
```

### Docker Compose services

| Service | Image | Port | Purpose |
|:--------|:------|:----:|:--------|
| `backend` | `precis-backend` | 8000 | Django WSGI (gunicorn) |
| `worker` | `precis-worker` | — | Dramatiq task worker |
| `frontend` | `precis-frontend` | 4321 | Astro development server |
| `db` | `postgres:16` | 5432 | PostgreSQL (production) |
| `redis` | `redis:7` | 6379 | Dramatiq broker + cache |

---

## Template Resolution Order

```
1. projects/precis/precis-main/backend/templates/          # Site-root shells, errors
2. projects/precis/precis-main/backend/apps/*/templates/   # App-owned templates
3. projects/precis/precis-main/assets/templates/           # Shared asset templates
4. libs/django-fusion/src/django_fusion/templates/  # Framework fallback
```

---

## Frontend Architecture

```
projects/precis/precis-main/frontend/
├── src/
│   ├── pages/                     # Astro pages (SSG + SSR)
│   │   ├── index.astro            # Homepage
│   │   ├── courses/               # Course catalog + detail
│   │   ├── blog/                  # Blog listing + detail
│   │   ├── pricing.astro          # Pricing page
│   │   └── 404.astro              # Error page
│   ├── components/
│   │   ├── blocks/                # 12 block components (Hero, CTA, FAQ, etc.)
│   │   ├── layout/                # Header, Footer
│   │   └── ui/                    # 20+ UI primitives (Card, Modal, Toast, etc.)
│   ├── layouts/
│   │   └── Layout.astro           # Root layout shell
│   └── lib/
│       └── site.ts                # Site configuration
```

---

## Key Conventions

### Imports

```python
# Task decorator — canonical path
from django_fusion.tasks import task

# Component tag in templates — canonical path
{% load components from django_fusion.comp.tags %}

# Webpack bundles in templates
{% load render_bundle from webpack_loader %}
{% render_bundle 'precis' 'css' %}
{% render_bundle 'precis' 'js' %}
```

### App ownership

| App | Owns | Must not own |
|:----|:-----|:-------------|
| `apps/learning/` | Courses, enrollment, progress, certs, payments | Wagtail page routing, blog |
| `apps/pages/` | Blog, profile, accounts, domain pages | Learning models, course logic |
| `apps/content/` | Wagtail hooks, content behaviors | Domain data, payment logic |
| `apps/handlers/` | PageHandler views, email services | URL orchestration, models |
| `apps/auth/` | Allauth adapters, registration flow | Learning permissions |
| `apps/tasks/` | Background task definitions | Synchronous business logic |

### Testing

```bash
cd projects/precis/precis-main/backend
make check          # ruff + django check
make test           # pytest (167 tests)
make migrate        # Apply migrations (SQLite in dev)

# Quick focused test
DJANGO_SETTINGS_MODULE=settings pytest apps/learning/tests/ -v
```

### Commands reference

```bash
cd projects/precis/precis-main

# Asset build
make install-assets     # npm install
make skeleton-manifest  # Generate skeleton-manifest.json
make build-assets       # Webpack production build

# Full build
make build              # install-assets + skeleton-manifest + webpack + docker

# Dev servers
make backend-dev        # Django runserver
make frontend-dev       # Astro dev server
```

### Do not

- Do not import `apps/learning/` from `apps/pages/` (or vice versa) — use
  Wagtail hooks and signals.
- Do not put Precis-specific templates in `libs/django-fusion/`.
- Do not share static assets with precis-landing or formints.
- Do not reference "Next.js" in new code or docs — the frontend is Astro.
  (The README stack line may be stale; trust the source code.)
- Do not use the old `django_fusion.comp.templatetags` import path — use
  `django_fusion.comp.tags` instead.
- Do not hand-edit generated `bundles/` output — edit source in `assets/`.

---

## Related

- [`/docs/ARCHITECTURE.md`](/docs/ARCHITECTURE.md) — Monorepo-wide architecture
- [`projects/precis/precis-main/backend/AGENTS.md`](/projects/precis/precis-main/backend/AGENTS.md) — Backend agent instructions
- [`projects/precis/precis-main/README.md`](/projects/precis/precis-main/README.md) — Project README (note: stack line references Next.js; source is Astro)
- [`/docs/ARCHITECTURE.md`](/docs/ARCHITECTURE.md) — Monorepo MCP integration (Kilo server, designer/task tools)
- [`docs/plans/django-fusion/django-fusion-tasks-mcp-plan.md`](/docs/plans/django-fusion/django-fusion-tasks-mcp-plan.md) — Tasks & MCP plan
- [`docs/plans/django-fusion/django-fusion-analyzer-skeleton-assets-plan.md`](/docs/plans/django-fusion/django-fusion-analyzer-skeleton-assets-plan.md) — Skeleton pipeline plan
