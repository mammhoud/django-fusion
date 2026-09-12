# M1 — Multi-Domain, Multi-Tenant CRM Schemas

> **Status:** Proposed — awaiting review
> **Milestone:** M1 of [Workspace CRM Program](README.md)
> **Tags:** `#multi-tenant` `#django-tenants` `#schemas` `#domains` `#methodology` `#loop-crm`
> **Owning product:** `projects/loop-crm/`

<!-- AI-generated: review needed -->

## 1. Goal

Make one domain resolve to exactly one **schema + workspace**, with a
**methodology** (the product mix a tenant runs) attached to the domain, so the
same deployment serves `crm.structa.cloud` (CRM methodology), an LMS domain
(learning methodology), and a research domain (research methodology) without
branching code paths.

## 2. Verified starting point

| Piece | Where it lives now | Gap |
|---|---|---|
| Workspace boundary | `projects/loop-crm/backend/apps/core/models.py` L15 `Workspace`; `UserProfile.workspace`; `apps/core/tenancy.py` `current_workspace_id(request)` | Row-scoped only — one database, one schema |
| App surface | `apps/{crm,marketing,attribution,pos,finance,tasks,pages,content,core,billing}` | No `SHARED_APPS`/`TENANT_APPS` split |
| Billing/plan | `apps/billing/models.py` `Plan`, `BillingAccount`, `Seat`; `gates.py` | Plan not attached to a domain/tenant row |
| Tenant pattern | `precis-dev` `django-tenants>=3.6` (Phase 1 done), `PathCenterMiddleware`; `editions/08-tenant-schemas.md`; `formint-cloud` `Tenant`/`Domain` | Pattern exists in siblings; not applied to the CRM |

**Decision (from review):** the CRM is Loop-CRM. This plan adds schemas to it;
it does not create a new product.

## 3. Methodology model — "multi-domain methodologies"

A **methodology** is the named configuration of a domain: which app group is
authoritative, which seed set runs, and which navigation/workflow starters load.
It is data, not code branches.

| Methodology | Authoritative apps | Seed set | Example domain |
|---|---|---|---|
| `crm` | `crm`, `marketing`, `attribution`, `tasks` | pipelines, deals, channels | `crm.structa.cloud` |
| `learning` | `pages`, `content`, `tasks` + LMS bridge | course-center tree, instructors | an LMS tenant |
| `research` | `pages`, `content`, `attribution` | research programs, publications | a CTC-style tenant |
| `commerce` | `pos`, `finance`, `crm` | catalog, ledger, customers | a POS-backed tenant |

```python
# apps/tenants/models.py  (new)
class DomainMethodology(models.TextChoices):
    CRM = "crm"
    LEARNING = "learning"
    RESEARCH = "research"
    COMMERCE = "commerce"

class WorkspaceDomain(DomainMixin):        # django-tenants
    methodology = models.CharField(choices=DomainMethodology.choices, default=DomainMethodology.CRM)
```

**Invariant:** `methodology` never gates authorisation directly — it selects a
`METHODOLOGY_PROFILES` config (app allowlist, navigation source, seed actor) that
the tenant provisioning service consumes. Authorisation stays in
`apps/core/permissions.py`.

## 4. Schema design

```text
PostgreSQL  db_loop_crm
├── public   Workspace · WorkspaceDomain · Plan · BillingAccount · Seat
│            Registration · DomainMethodology profiles · Dramatiq tables
└── {tenant} crm · marketing · attribution · pos · finance · tasks · pages · content
             + per-tenant groups (owner, admin, member, viewer)
```

| Layer | Contents | Why there |
|---|---|---|
| `public` | `Workspace`, `WorkspaceDomain`, billing (`Plan`/`BillingAccount`/`Seat`), registration | Billing and domain→tenant resolution must be readable **before** a schema is known |
| tenant | All product data (`crm`, `marketing`, `attribution`, `pos`, `finance`, `tasks`, `pages`, `content`) | Isolation by construction; a broken query cannot cross tenants |
| shared | `pages`/`content` **models**, `wagtail.admin` | One admin UI; each tenant keeps its own page tree (mirrors precis-dev decision #2) |

`SHARED_APPS` / `TENANT_APPS` map 1:1 onto that table. `apps/core` splits:
`Workspace`/`UserProfile`/`AuditLog` → shared; workflow/webhook/email models →
tenant.

## 5. Milestones (tasks)

### M1.1 — Dependency + settings gate

- Add `django-tenants>=3.6` to `projects/loop-crm/backend/requirements.txt` (align the pin with `precis-dev`; do not invent a second version).
- Settings (`backend/configs/default/__init__.py`): `TENANT_MODEL`, `TENANT_DOMAIN_MODEL`, `PUBLIC_SCHEMA_URLCONF`, `SHOW_PUBLIC_IF_NO_TENANT_FOUND`, `TENANCY_ENABLED` gate derived from `DB_ENGINE` — same names as `precis-dev`.
- `.env.example`: `DB_ENGINE=django_tenants.postgresql_backend`, `TENANT_BASE_URL`.
- **Gate:** with SQLite (default dev) nothing changes — no `auto_create_schema`, `make check` still green.

### M1.2 — Tenant + domain + methodology models

- New `apps/tenants/` (`models.py`, `services.py`, `admin.py`, `migrations/`) with `WorkspaceDomain`, `TenantPlan` link, and `METHODOLOGY_PROFILES`.
- `Workspace` gains `schema_name` (unique, slug-validated) and `methodology`; existing rows backfill to `crm`.
- Attention: `Workspace` is currently **shared**; the FK direction must be `WorkspaceDomain → Workspace` so the public schema owns resolution.

### M1.3 — SHARED_APPS / TENANT_APPS split

- Audit every model in `apps/{crm,marketing,attribution,pos,finance,tasks,pages,content,core}` and record the split in a table inside this plan (the precis-dev Phase 2 task).
- Any model with a `workspace` FK that lands in a **tenant** app drops the column in favour of the schema boundary — but only after `apps/core/tenancy.py` callers are migrated (it currently reads `profile.workspace_id`).
- `tenancy.py` becomes: schema is authoritative in tenant context; `current_workspace_id()` remains for the public schema and for shared-app reads.

### M1.4 — Domain → schema resolution middleware

- Production: host-based via `TenantMainMiddleware` (wildcard `*.structa.cloud` cert).
- Dev/CI: **path-based** (`/{workspace}/…`) reusing the `PathCenterMiddleware` shape from precis-dev, so `localhost` needs no DNS.
- Resolution order is explicit and logged once per request: `Host` → `WorkspaceDomain` → schema; fallback `Host` → path prefix → schema; final fallback `SHOW_PUBLIC_IF_NO_TENANT_FOUND`.
- Unknown host must render the public "no such workspace" page — never leak a tenant list.

### M1.5 — Provisioning (Dramatiq)

```text
Workspace created (paid or seeded)
  → Registration(status=pending, verification_token)
  → verify email → auto-approve free/starter
  → actor "system.workspaces.provision":
       WorkspaceDomain + TenantPlan (public)
       CREATE SCHEMA {schema_name}            # PostgreSQL only
       migrate_schemas --tenant {schema_name}
       seed groups (owner, admin, member, viewer)
       seed per METHODOLOGY_PROFILES[methodology]
       Wagtail site + HomePage for the tenant
       admin user + temp password → email actor
  → workspace reachable on its domain
```

- Reuse `precis-dev`'s `ProvisioningService` shape; if generalising it, put the shared piece in one place and import it from both products (no copy-paste).
- Staggering/retry: schema creation is queue-serialised per schema name to avoid concurrent `CREATE SCHEMA`.

### M1.6 — Per-domain methodology wiring

- `METHODOLOGY_PROFILES` drives: `INSTALLED_APPS` extras (if any static), navigation source, seed actor, and default Wagtail page types.
- `apps/core/navigation.py` reads the methodology so the tenant's sidebar matches its product mix.

### M1.7 — Tests

- `test_tenancy.py` (exists) extended: cross-tenant read/write attempts fail; domain→schema resolution table-driven over host + path forms; unknown host renders public page.
- New `test_provisioning.py`: provisioning actor creates schema + groups + seed in one pass (SQLite skips `CREATE SCHEMA` and asserts records).
- New `test_methodology.py`: each methodology's seed set + navigation differ as declared.

### M1.8 — Runbook

- Document (in `projects/loop-crm/docs/SETUP_AND_BUILD.md`): Postgres requirement, `migrate_schemas --shared` / `--tenant`, adding a tenant manually, restoring one schema, and the SQLite dev story.

## 6. Verification

```bash
cd projects/loop-crm/backend
make check                       # SQLite path unchanged
python manage.py test apps.core.test_tenancy apps.core.test_provisioning apps.core.test_methodology

# Postgres flip-on (dev database only — effectful)
DB_ENGINE=django_tenants.postgresql_backend python manage.py migrate_schemas --shared
DB_ENGINE=django_tenants.postgresql_backend python manage.py migrate_schemas --tenant acme
```

Pass criteria: one domain row resolves to exactly one schema; a query issued in
tenant A cannot return tenant B rows; the SQLite dev path needs no tenant setup.

## 7. Risks

| Risk | Mitigation |
|---|---|
| Dropping `workspace_id` columns touches many call sites | Split into M1.3 (audit + plan table) and a follow-up slice per app, behind the schema boundary already being enforced |
| `migrate_schemas` N tenants is slow | Dramatiq actor, serialise per schema, stagger; measure at 20 tenants before scaling |
| Wagtail admin under tenant context | Test early (precis-dev lists the same risk); keep `wagtail.admin` shared, page models tenant |
| Path-based routing deviates from django-tenants default | Reuse the tested `PathCenterMiddleware` pattern; keep host-based as the production path |
| Billing must stay in `public` while `Plan` is referenced by tenant code | Tenant code reads plan limits through a service that queries the public schema explicitly |

## 8. Remarks & Notes

- The **subscription key** introduced here (`Workspace.id` + `DomainMethodology`)
  is the single identity M2's session and M3's checkout carry; no plan may mint
  a second one.
- `apps/billing/gates.py` stays permissive without Stripe keys — M1 must not
  make billing mandatory for local dev or tests.
- Nothing in M1 provisions against a shared/production database. Schema
  creation and `migrate_schemas` are effectful: dev database first, operator
  approval for anything else.
