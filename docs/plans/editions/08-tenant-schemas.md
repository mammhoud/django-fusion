# Tenant Schemas — Multi-Tenancy Plan (django-tenants) for Every Edition

> Tags: `#formints` `#pos` `#cloud` `#tenancy` `#django-tenants` `#postgres` — status 🟡 Postgres flip-on pending (21 Aug 2026).

> **Status:** Row-level model work complete and verified on SQLite — `Tenant`
> + `Domain` (migration 0008), `BranchSettings` (+ `Branch.branch_settings`
> accessor), Unfold admin + public-schema URLconf, 14 SQLite unit tests, and
> the tenant-aware allauth/auth/database adapters (`TenantAwareAccountAdapter`,
> context processor, per-tenant provider overrides). The remaining work is the
> **PostgreSQL flip-on** (Tenant 6–7 below).

## Remaining work — Postgres schema-per-tenant flip-on (Tenant 6–7)

### Tenant 6 — Migration path (row-level → schema-per-tenant)

1. Keep `Organization` as the row-level registry **and** become the 1:1 anchor for `Tenant`.
2. One-time backfill: for each `Organization` create `Tenant(schema_name=slug, organization=org)` + a primary `Domain`.
3. `manage.py migrate_schemas --tenant` builds tenant schemas from `TENANT_APPS`.
4. Ship rows per tenant (backfill script: per tenant, copy its `organization_id` rows into the tenant schema).
5. Deprecate `organization` FKs over time — queries become schema-local (no `organization_id` filter needed inside a tenant schema).
6. Keep the legacy FK columns for rollback; drop in a later release after data verification.

> **Registry-table note:** `apps.core` appears in both `SHARED_APPS` and
> `TENANT_APPS`, so `core_tenant` / `core_domain` tables are also created inside
> every tenant schema when `migrate_schemas --tenant` runs. Harmless (schemas
> are independent and the registry is only used in `public`), but a future
> release may move `Tenant`/`Domain` into a dedicated SHARED-only app
> (`apps.tenants`) to avoid the duplication.

### Tenant 7 — Operations & rollback

- **Flip-on checklist:** set `DB_ENGINE=django_tenants.postgresql_backend`,
  `DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT`; run `migrate_schemas --shared`
  then `--tenant`; seed `public` Tenant + `localhost` Domain; restart daphne.
- **Rollback:** unset `DB_ENGINE` → SQLite row-level mode (all gated code off).
  No destructive commands run by this plan.
- **Backups:** `pg_dump` per schema (`pg_dump -n tenant_a`), complementing the
  Cloud `BackupRun` monitoring from `04-cloud.md`.

## Execution Handoff

When a Postgres target is available: flip `DB_ENGINE`, run `migrate_schemas`,
seed a tenant, run the Postgres integration tests (`TenantSchemaIntegrationTest`,
gated `skipUnless(TENANCY_ENABLED)`), and mark Tenant 6–7 executed.
