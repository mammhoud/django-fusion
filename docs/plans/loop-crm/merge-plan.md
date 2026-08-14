# Loop-CRM — Merge & Architecture Plan

> **Status:** Foundation integrated; django-bolt API migration, token auth, navigation, workflow execution, finance ledger, and browser coverage shipped. Provider OAuth adapters remain credential-gated.
> **Source projects:** [twentyhq/twenty](https://github.com/twentyhq/twenty) (CRM) · [gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app) (social scheduling)
> **Canonical path:** [`projects/loop-crm/`](../../../projects/loop-crm/)
> **License:** AGPL-3.0
> **Last reviewed:** 2026-08-13

Loop-CRM merges Twenty's CRM (custom objects, pipelines, workflows) with
Postiz's social scheduling (30+ platforms, AI post generation) into one
django-fusion modular monolith. The value proposition is **"from social
impression to closed deal — one platform, one source of truth"**: every social
interaction is attributable to a deal, workflows span the whole customer
journey, and RevOps sees marketing ROI in real time.

---

## 1. Why django-fusion (not django-cotton)

| Aspect | Benefit |
|---|---|
| Single transaction | Create a social post AND link it to a deal atomically |
| Unified auth | One login for sales reps AND social managers |
| Zero network overhead | Django ORM hits one PostgreSQL database — sub-50ms dashboards |
| Simplified DevOps | One Compose file: Django, Postgres, Redis, Dramatiq |
| Shared components | `{% comp %}` + fragments replace django-cotton's component layer |

django-fusion (`libs/django-fusion`) provides the `{% comp %}` component tag,
fragment serving, the dual render-first / data-API pipeline, and the
`FUSION_RENDER_FIRST` switch. Loop-CRM consumes those directly — it does **not**
use django-cotton.

---

## 2. Architecture

```text
User browser
  → Astro frontend (:4321)
      ├── Static pages (marketing site, docs)
      ├── SSR pages (dashboard, deals, post calendar)
      └── React islands (RevOps board, attribution, analytics)
      ├── Redux (RTK) — data-API road source of truth
      ├── Alpine.js — modal toggles, dropdowns, form validation
      └── HTMX — list pagination, form submission, inline editing
  → Django backend (:8000)
      ├── django-bolt API — /bolt/companies|deals|posts|dashboard (canonical)
      ├── Django fallback — /api/v1/* (compatibility when Bolt is absent)
      ├── Django views   — HTMX responses (/dashboard/, /deals/, /posts/)
      ├── Django ORM     — core | crm | marketing | attribution
      └── Django admin   — internal management
  → Dramatiq task queue (publishing, OAuth refresh, analytics, attribution)
  → PostgreSQL (unified DB) + Redis (cache/queue)
```

**Substitutions from the sources:** Dramatiq replaces both Temporal (Twenty)
and BullMQ (Postiz); django-fusion replaces django-cotton; a single Django
project replaces the NestJS/Twenty and NextJS/Postiz service split.

---

## 3. Module organization

```text
projects/loop-crm/
├── backend/
│   ├── settings.py          # SQLite (dev) / PostgreSQL (prod via USE_POSTGRES)
│   ├── urls.py              # admin + browser + /bolt/ + /api/v1/* mounts
│   └── apps/
│       ├── core/            # Workspace (tenancy), User (RBAC), AuditLog, permissions
│       ├── crm/             # Company, Contact, Pipeline, PipelineStage, Deal, Activity
│       ├── marketing/       # Campaign, SocialChannel, Post, Media, PostAnalytics
│       ├── attribution/     # AttributionModel, AttributionTouchpoint + engines/
│       ├── finance/         # Invoice, Payment, RevenueEvent + HTMX screens
│       └── tasks/           # Dramatiq actors (publish, refresh, aggregate, attribute)
├── frontend/                # Astro 5 + Tailwind 4 + HTMX + Alpine + Redux + GSAP
├── docker-compose.yml       # Django + Postgres + Redis + Dramatiq worker
└── Makefile                 # dev | build | check | backend-*
```

---

## 4. Unified data model

- **core** — `Workspace` (multi-tenant root), `User` (AbstractUser + 7 RBAC
  roles), `AuditLog` (append-only trail).
- **crm** — `Company`, `Contact`, `Pipeline`, `PipelineStage` (probability,
  color, order), `Deal` (with `campaign` FK → marketing), `Activity`.
- **marketing** — `SocialChannel` (12 platforms + WhatsApp), `Campaign`,
  `Media`, `Post` (draft/pending approval/approved/scheduled/publishing/published/failed),
  `PostAnalytics` (impressions/clicks/engagement/spend).
- **attribution** — `AttributionModel` (first/last/linear/time-decay/
  position-based) and `AttributionTouchpoint` (fractional weight 0..1 per deal).
- **finance** — `Invoice`, `Payment`, and `RevenueEvent` are workspace-scoped
  records linked to CRM companies/deals and marketing campaigns. A closed-won
  workflow can idempotently create the invoice and recognized revenue event;
  payments update invoice status without allowing overpayment.

The attribution glue is `crm.Deal.campaign` — a closed deal rolls revenue back
to the campaign (and posts) that influenced it. Companies, contacts, and deals
also expose tenant-scoped `custom_attributes`; the custom-object catalog makes
those Twenty-style fields discoverable without hard-coding workspace schemas.

---

## 5. RBAC matrix (summary)

| Role | Sales | Marketing | Attribution |
|---|---|---|---|
| Super Admin | full | full | full |
| Sales Manager | manage | view | view |
| Sales Rep | own deals | — | — |
| Marketing Manager | view | manage | view |
| Marketing Specialist | — | own posts | — |
| RevOps Manager | manage | manage | manage |
| Viewer | view | view | view |

Helpers live in `apps/core/permissions.py`; django-bolt's JWT/API-key
backends and `IsAuthenticated` guards protect the canonical API road. The
Django compatibility road remains intentionally usable for local development.

---

## 6. Delivery status and roadmap

- **Phase 0 (done) — scaffold:** domain models, admin, django-fusion wiring,
  Dramatiq actors, Astro frontend, Compose + Makefile, Redux store.
- **Phase 1 (foundation done) — API + navigation:** the Loop-CRM
  `Application` owns browser routes; `apps/core/navigation.py` is the module
  registry for Django templates and Astro; responsive side navigation exposes
  every module and subpage; `/api/v1/` exposes dashboard, CRM, marketing,
  attribution, workflow, and integration catalog endpoints.
- **Phase 1b (implemented) — Bolt API migration:** `apps/core/bolt_api.py`
  registers the full resource/catalog surface on django-bolt, mounts
  `/bolt/` through Django URLs, and exposes `/bolt/auth/token`. The reusable
  `django_fusion.plugins.apis` bridge supplies model schema generation, CRUD
  mounting, dual-mode responses, JWT bearer tokens, and optional API keys.
  `/api/v1/` remains a compatibility road when the optional Bolt runtime is
  not installed; the repository's django-bolt placeholder is detected as
  unavailable rather than treated as a working server. Token responses include
  rotating access/refresh pairs at `/auth/token` and `/auth/refresh`.
- **Phase 1c (implemented) — interaction verticals:** `WorkflowDefinition` and
  `WorkflowRun` are persisted in the core database and seeded with the four
  product workflow templates. The workflow editor and content calendar use
  validated Django forms, HTMX partial responses, CSRF headers, and explicit
  empty/error/loading states. `Post.transition_to()` prevents lifecycle skips,
  while Dramatiq task discovery now registers actors once through
  `apps/tasks/tasks.py`.
- **Phase 2 (contract done) — connectors:** the Postiz-style 12-platform
  capability catalog and `SocialConnector`/`PublishResult` contract are in
  `apps/marketing/connectors.py`. The Dramatiq actor now moves posts through
  `publishing → failed|published` and never claims success without a provider
  adapter. OAuth/token storage and concrete provider adapters are credential-
  gated follow-up work.
- **Phase 3 (implemented) — workflows + attribution + finance:** the cross-module
  workflow catalog covers lead capture, content approval, publish-and-attribute,
  and deal-won revenue closure. Dramatiq now executes concrete CRM activity,
  attribution, revenue-event, and invoice actions with idempotent records;
  unconfigured external notifications/publishers are explicitly deferred rather
  than reported as successful. `Deal.transition_to_stage()` queues the deal-won
  workflow when a pipeline lead becomes closed-won.
- **Phase 3b (implemented) — finance surface:** `/finance/`, invoices, payments,
  and recognized-revenue pages use real ModelForms, tenant-safe relationships,
  HTMX reset/list fragments, Bolt resources, and explicit empty/loading/error
  states.
- **Phase 4 — AI hub:** lead scoring, sales emails, and social post generation
  behind provider adapters, with explicit workspace consent and audit logging.
- **Phase 5 — domain screens:** replace the navigation-ready module surfaces
  with paginated HTMX/JSON screens for companies, deals, calendar, analytics,
  approvals, and reports.

### Navigation contract

Every active web road consumes the same hierarchy: **module → subpage →
current breadcrumb**. Django uses `apps/core/navigation.py` plus a top-level
`LoopCrmSite` containing the `LoopCrmApplication`; django-fusion owns the root
URL composition and `menu_path` metadata. Astro keeps a typed compile-time
route contract, but its initial navigator is loaded from the backend HTMX
fragment, cached in session storage, and refreshed after page navigation by
changing only active classes/ARIA state. The JSON `/api/v1/navigation/`
contract carries the same tree with private cache headers for data-road clients.

### Integration boundary

The repository can validate route shape, capabilities, workflow definitions,
queue state transitions, and attribution contracts locally. It cannot complete
external OAuth handshakes or publish to third-party networks without workspace
credentials, redirect URLs, encryption policy, and provider approval. Those
adapters must be added behind `SocialConnector`, never in templates or views.

---

## 7. Verification

```bash
cd projects/loop-crm/backend
make check        # Django system checks
make migrate      # makemigrations + migrate (SQLite by default)
make test         # Django tests

cd ../frontend
npm run check     # astro check
npm run build     # Astro build
```

For the optional API runtime, install `django-fusion[bolt]`, set
`FUSION_BOLT_JWT_SECRET`, and validate `/bolt/health`, `/bolt/auth/token`, and
one protected resource with either a bearer token or `X-API-Key`. No provider
credentials are needed for these local contract checks.

Reference clones (for the connector/API phases, kept outside the tree):
`twentyhq/twenty` and `gitroomhq/postiz-app`.

### Browser verification

The scoped Playwright suite covers complete navigation state across CRM
subpages, workflow creation → activation → queued run, and content draft →
approval → scheduled transitions. The deterministic `seed_playwright` command
creates only the records needed by those browser flows; it never fabricates
production data.

---

## 8. Data tables, extensible fields, and account security plan

### Package analysis

| Capability | Existing package/convention | Decision |
|---|---|---|
| Server-rendered tables | `django-tables2` is already a workspace dependency and django-fusion exposes `TableView`/table mixins | Use `django-tables2` for interactive members/roles and future domain tables; keep querysets tenant-scoped and allowlisted. Do not add a second table library. |
| Authentication pages | `django-allauth` is already a workspace dependency and is used by Landing-Fusion | Add allauth account URLs, middleware, branded Loop-CRM templates, and the existing `auth.User` + `UserProfile` role boundary. Keep social providers opt-in. |
| Dynamic fields | Existing `custom_attributes` JSON is provider-neutral and already used by Company, Contact, and Deal | Add persisted `CustomFieldDefinition` metadata with field type, validation, choices, and object key. Validate values at the service/form boundary, then store values in the existing JSON column. |
| Polymorphic records | No polymorphism package is installed for this product | Do not introduce `django-polymorphic` or model inheritance for custom fields. A definition catalog plus JSON values avoids multi-table joins, preserves tenant isolation, and maps cleanly to Bolt/OpenAPI. Use `ContentType` only for a future audited cross-model relation, never for unvalidated field keys. |
| API identity | django-fusion Bolt helpers already issue/verify JWTs and API keys | Add user-bound verification that resolves `sub` to an active Django user and checks role/workspace claims. Token routes must never mint an identity from an unauthenticated arbitrary subject. |

### Delivery slices

1. **Tables** — ship the members/roles table first using `django-tables2`, with explicit columns, search, role filtering, and no secret/token fields. Reuse the table contract for companies, deals, posts, and audit rows as those screens become real.
2. **Fields** — persist field definitions per workspace/object type; support text, number, boolean, date, URL, email, select, and multi-select with JSON-safe validation. Keep field definitions versionable and archive rather than hard-delete fields.
3. **Accounts** — expose `/accounts/login/`, `/accounts/signup/`, logout, password reset, and `/account/profile/`; display the current role, workspace, permission groups, and token status without rendering raw tokens.
4. **Token security** — verify signature, issuer/audience, expiry, token type, active user, and optional role/workspace claims. Use short-lived access tokens, rotated refresh tokens, HTTPS-only production cookies, CSRF for browser mutations, and API keys only for explicitly configured machine access.
5. **Testing** — cover anonymous token rejection, inactive-user rejection, role/workspace mismatch, allauth page rendering, table column safety, custom-field validation, and Bolt auth round-trips. Browser-level tests should exercise login → profile → protected route once a browser dependency is available.

## Related

- [`../../../projects/loop-crm/README.md`](../../../projects/loop-crm/README.md)
- [`../README.md`](../README.md)
- [`../../../libs/django-fusion/README.md`](../../../libs/django-fusion/README.md)
