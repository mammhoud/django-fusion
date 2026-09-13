# M1 — Multi-domain, multi-tenant CRM schemas

> **Status:** Proposed — awaiting review · **Owner:** Mahmoud · **Validator:** Moustafa
> **Owning product:** `projects/loop-crm/` · **Depends on:** —
> **Tags:** `#multi-tenant` `#django-tenants` `#schemas` `#domains` `#methodology`

<!-- AI-generated: review needed -->

## Goal

One domain resolves to exactly one **schema + workspace**, with a **methodology**
(the product mix that tenant runs) attached to the domain — so one deployment
serves a CRM domain, an LMS domain, and a research domain without branching code.

## Decisions

- **Extend Loop-CRM.** `projects/loop-crm/` already has `Workspace`,
  `apps/core/tenancy.py`, a Stripe-shaped `apps/billing/`, and Wagtail under
  `apps/pages/`. This plan adds schemas to it; it does not create a second CRM.
- **Reuse the sibling pattern, don't reinvent it.** `precis-dev` (django-tenants
  ≥ 3.6, `PathCenterMiddleware`) and `edition 08` / `formint-cloud`
  (`Tenant`/`Domain`, `DB_ENGINE` flip-on) are the reference implementations.
- **Methodology is data, not branches.** `METHODOLOGY_PROFILES` selects the app
  allowlist, navigation source, and seed actor. It never gates authorisation —
  that stays in `apps/core/permissions.py`.
- **SQLite dev is untouched.** With the default dev engine nothing changes; no
  `auto_create_schema`, no tenant setup, `make check` stays green.

| Methodology | Apps | Example domain |
|---|---|---|
| `crm` | crm, marketing, attribution, tasks | `crm.structa.cloud` |
| `learning` | pages, content, tasks + LMS bridge | an LMS tenant |
| `research` | pages, content, attribution | a CTC-style tenant |
| `commerce` | pos, finance, crm | a POS-backed tenant |

## Schema design

```text
db_loop_crm
├── public   Workspace · WorkspaceDomain · Plan · BillingAccount · Seat
│            Registration · methodology profiles · job tables
└── {tenant} crm · marketing · attribution · pos · finance · tasks · pages · content
```

Billing and domain→schema resolution must be readable **before** a schema is
known, so they live in `public`. Everything else is tenant-scoped. `wagtail.admin`
stays shared; page/content **models** are tenant, so each tenant keeps its own
page tree. `SHARED_APPS`/`TENANT_APPS` map 1:1 onto that table.

## Tasks

| # | Task | Done when | Effectful |
|---|---|---|---|
| M1.1 | Dependency + settings gate | `django-tenants` pinned to the `precis-dev` version; `TENANT_MODEL`, `TENANT_DOMAIN_MODEL`, `PUBLIC_SCHEMA_URLCONF`, `TENANCY_ENABLED` set with the same names; `.env.example` names only | no |
| M1.2 | Tenant + domain + methodology models | `apps/tenants/` with `WorkspaceDomain`, plan link, `METHODOLOGY_PROFILES`; `Workspace` gains `schema_name` + `methodology`; FK direction is `WorkspaceDomain → Workspace` | migration (dev DB) |
| M1.3 | `SHARED_APPS`/`TENANT_APPS` audit + split | Every model classified in a table; `tenancy.py` callers migrated before any `workspace_id` column is dropped | column drops |
| M1.4 | Domain → schema resolution | Host-based in production, path-based in dev/CI; unknown host renders a public "no such workspace" page and never leaks a tenant list | no |
| M1.5 | Provisioning actor | Create workspace → verify → `CREATE SCHEMA` → `migrate_schemas --tenant` → seed groups → methodology seed → Wagtail site; serialised per schema name | **yes** |
| M1.6 | Methodology wiring | Sidebar and default page types follow the tenant's methodology | no |
| M1.7 | Tests | Cross-tenant read/write fails; resolution is table-driven over host + path; each methodology seeds and navigates differently | test DB |
| M1.8 | Runbook | `projects/loop-crm/docs/SETUP_AND_BUILD.md` covers Postgres, `migrate_schemas`, adding a tenant, restoring one schema, SQLite dev | no |

## Gates

- `make check` (SQLite path) stays green at every step.
- A query in tenant A cannot return tenant B rows.
- Billing stays permissive with no Stripe keys — local dev and tests must not
  require them.
- `Workspace.id` is the **only** tenant identity. M2's session and M3's checkout
  carry it; no plan mints a second one.

## Effectful — confirm first

- `CREATE SCHEMA` and `migrate_schemas` run against a **dev database only**;
  anything else needs explicit operator approval.
- Dropping `workspace_id` columns touches many call sites — audit first, drop per
  app in its own slice.

## Links

- → [`README.md`](README.md) — Program index
- → [`../repository/precis-dev-multitenant.md`](../repository/precis-dev-multitenant.md) — Reference pattern
- → [`../editions/08-tenant-schemas.md`](../editions/08-tenant-schemas.md) — Tenant/Domain pair
