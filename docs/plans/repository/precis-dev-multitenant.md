# Precis Dev — Multi-Tenant Course Center Platform Plan

> **Status:** Active — Phase 1 in progress
> **Date:** 2026-08-22
> **Product:** `projects/precis/precis-dev/`
> **Tags:** `#precis-dev` `#multi-tenant` `#django-tenants` `#course-center` `#lms` `#cms`
> **References:** [`formint-cloud` tenant pattern](../../../projects/formints/formint-cloud/backend/configs/__init__.py), [`editions/08-tenant-schemas.md`](../editions/08-tenant-schemas.md)

<!-- AI-generated: review needed -->

## Goal

Transform `precis-dev` into a **multi-tenant Course Center platform**. Every
organization signs up as a **Course Center** — it gets its own isolated
PostgreSQL schema, a branded Wagtail landing page with course listings,
built-in student/instructor auth, and the ability to offer multiple course
catalogs under one roof.

### What a Course Center is

A Course Center is an **organization that teaches**. It could be:

- A training company with 12 instructors and 50+ courses
- An independent instructor with 3 courses and a personal brand
- A university department running a continuing-education catalog
- A corporate L&D team with internal-only courses

Every center gets:

| Capability | Details |
|---|---|
| **Landing page** | Branded Wagtail page (logo, tagline, hero, about) at `/c/{slug}/` |
| **Course listings** | Public catalog with search, filters, and course detail pages |
| **Built-in auth** | Student signup/login, instructor dashboard, MFA, social auth providers (can bring own OAuth keys) |
| **Role system** | 4 roles per center: `admin`, `instructor`, `student`, `editor` |
| **Content CMS** | Wagtail admin for landing pages, blog, and rich StreamField content |
| **Multiple course domains** | One center can offer multiple branded course catalogs via extra CourseDomain entries |
| **Custom domain** | Pro-plan centers can use their own domain (e.g. `acme-training.com`) |

## Plan tiers

| Plan | Max courses | Max instructors | Max students | Custom domain | Custom branding | Analytics |
|---|---|---|---|---|---|---|
| **Free** | 5 | 1 | 50 | ✗ | ✗ | ✗ |
| **Starter** | 25 | 5 | 500 | ✗ | ✓ | ✗ |
| **Pro** | Unlimited | Unlimited | Unlimited | ✓ | ✓ | ✓ |

All plans auto-approve on email verification (no manual review for free/starter;
Pro undergoes a quick review).  Free plans have a 14-day inactivity grace period.

## Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                    Traefik default-proxy                      │
│  *.dev.structa.cloud  ──► PathCenterMiddleware → schema      │
│  dev.structa.cloud     ──► public schema (directory/register) │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│              PostgreSQL (db_precis_dev, shared cluster)       │
│                                                              │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ public  │  │  acme    │  │  codery  │  │  mededu  │ ... │
│  │ schema  │  │  schema  │  │  schema  │  │  schema  │     │
│  │         │  │          │  │          │  │          │     │
│  │ Centers │  │ Courses  │  │ Courses  │  │ Courses  │     │
│  │ Plans   │  │ Students │  │ Students │  │ Students │     │
│  │ Domain  │  │ Landing  │  │ Landing  │  │ Landing  │     │
│  │ Regs    │  │ Content  │  │ Content  │  │ Content  │     │
│  └─────────┘  └──────────┘  └──────────┘  └──────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### URL scheme (path-based)

| URL pattern | Schema | What |
|---|---|---|
| `dev.structa.cloud/` | public | Platform landing + center directory |
| `dev.structa.cloud/register/` | public | Center signup form |
| `dev.structa.cloud/centers/` | public | Center directory listing |
| `/c/{slug}/` | tenant | Center landing page (with course listing) |
| `/c/{slug}/courses/` | tenant | Full course catalog |
| `/c/{slug}/courses/{course}/` | tenant | Course detail + enroll |
| `/c/{slug}/accounts/login/` | tenant | Student/instructor login |
| `/c/{slug}/admin/` | tenant | Center Wagtail admin |
| `/c/{slug}/dashboard/` | tenant | Instructor/student dashboard |

> Path-based routing was chosen over host-based (`{slug}.dev.structa.cloud`)
> to simplify DNS (no wildcard cert needed in Phase 1) and to keep the Auth0/
> OAuth callback story simple (all requests go to the same origin).

### Roles per center (Django groups, inside each tenant schema)

| Role | Can do |
|---|---|
| `admin` | Manage center settings, users, billing, all content |
| `instructor` | Create & manage courses, modules, lessons, view student progress |
| `student` | Browse catalog, enroll, complete courses, view own progress |
| `editor` | Wagtail CMS pages, StreamField blocks, media library |

## Model map (public schema → `apps/tenants/models.py`)

| Model | django-tenants base | Purpose |
|---|---|---|
| `CenterPlan` | — | Subscription tier: free / starter / pro |
| `CourseCenter` | `TenantMixin` | One schema per org — `schema_name` = URL slug |
| `CourseDomain` | `DomainMixin` | Domain → center mapping (primary + custom domains) |
| `CenterRegistration` | — | Two-step signup: verify email → provision |

## Registration flow

```text
POST /apis/centers/register/
  → CenterRegistration(status=pending, verification_token=uuid)
  → Verification email sent
  → User clicks /register/verify/?token=...
  → CenterRegistration.status = "verified"
  → Auto-approved for free/starter; Pro → admin review
  → Signal fires → enqueue("system", "centers.provision")
  → Dramatiq worker:
      create CourseCenter + CourseDomain (public schema)
      CREATE SCHEMA {slug} (PostgreSQL only)
      migrate_schemas --tenant {slug}
      seed: groups (admin/instructor/student/editor)
      seed: Wagtail site + HomePage
      seed: admin user with temp password
      enqueue("email", "centers.send_welcome")
  → Center is live at /c/{slug}/
```

## Current implementation status

| Phase | Status |
|---|---|
| **Phase 0** — `django-tenants>=3.6` installed, imports verified | ✅ Done |
| **Phase 1** — Models (CenterPlan, CourseCenter, CourseDomain, CenterRegistration) | ✅ Done |
| **Phase 1** — Admin (CourseCenterAdmin, CenterPlanAdmin, CenterRegistrationAdmin) | ✅ Done |
| **Phase 1** — Services (CenterQueryService, ProvisioningService) | ✅ Done |
| **Phase 1** — Path-based middleware (PathCenterMiddleware via `/c/{slug}/`) | ✅ Done |
| **Phase 1** — API endpoints (plans, centers, check-subdomain, register, verify) | ✅ Done |
| **Phase 1** — Signals (auto-provision on approval) | ✅ Done |
| **Phase 1** — `TENANCY_ENABLED` gate, settings wired | ✅ Done |
| **Phase 1** — SQLite migrations applied, `make check` passes | ✅ Done |
| **Phase 2** — SHARED_APPS / TENANT_APPS split | 🔲 Pending |
| **Phase 3** — Tenant-aware auth adapter | 🔲 Pending |
| **Phase 4** — Wagtail CMS seeding per center | 🔲 Pending |
| **Phase 5** — Dramatiq provisioning + lifecycle workflows | 🔲 Pending |
| **Phase 6** — Astro frontend (registration + directory + center pages) | 🔲 Pending |
| **Phase 7** — Infrastructure (Traefik routing, wildcard DNS optional) | 🔲 Pending |
| **Phase 8** — Tests | 🔲 Pending |

## Configuration reference

**`.env.example` additions:**

```bash
# ── Multi-tenancy ──────────────────────────────────────────────────
DB_ENGINE=django_tenants.postgresql_backend    # flip-on for Postgres
TENANT_BASE_URL=https://dev.structa.cloud
```

**Settings reference (`backend/settings.py`):**

```python
TENANCY_ENABLED  # True when DB_ENGINE starts with "django_tenants"
TENANT_MODEL = "tenants.CourseCenter"
TENANT_DOMAIN_MODEL = "tenants.CourseDomain"
PUBLIC_SCHEMA_URLCONF = "configs.urls_public"
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True
```

## Open decisions (confirmed)

1. ✅ **Path-based routing** — `/c/{center}/` URLs (not host-based). No wildcard DNS needed.
2. ✅ **Shared Wagtail admin** — `wagtail.admin` stays in SHARED_APPS (one admin UI),
   page models in TENANT_APPS (each center has its own page tree).
3. ✅ **Auto-approve free/starter** — No manual review for entry-level plans.
4. ✅ **Four roles per center** — admin, instructor, student, editor.
5. 🔲 **Social auth per center** — Should each center bring its own OAuth keys?
6. 🔲 **Pricing/billing** — Deferred to Loop-CRM integration plan.

## Risks

| Risk | Mitigation |
|---|---|
| Schema-per-center overhead at scale | Plan-based schema limits; archive stale centers |
| `migrate_schemas` across many centers is slow | Run via Dramatiq actor; stagger |
| Path-based routing (not native to django-tenants) | `PathCenterMiddleware` replaces `TenantMainMiddleware`; tested |
| Wagtail pages + tenant schemas compatibility | Test early with Wagtail admin under tenant context |
| django-tenants + django-allauth interactions | Tenant-aware adapter (Phase 3) gates signup per center |

## Remarks & Notes

- The Course Center model replaces the earlier generic LMS/CRM split. It is
  a more focused, opinionated direction: every tenant is a teaching org.
- `auto_create_schema` is gated on `TENANCY_ENABLED` — SQLite dev starts
  with no schema creation overhead, identical to today.
- Path-based routing via `PathCenterMiddleware` (not `TenantMainMiddleware`)
  means the `Host` header never matters for tenant resolution. This keeps
  the local dev experience simple (`localhost:8074/c/acme/` works out of
  the box).
- The Formint Cloud reference implementation (`apps/core/models.py`
  `Tenant`/`Domain` pair) was used as the starting pattern and adapted for
  course centers.