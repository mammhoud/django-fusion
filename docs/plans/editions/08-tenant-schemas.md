# Tenant Schemas — Multi-Tenancy Plan (django-tenants) for Every Edition

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the Cloud edition from **row-level** multi-tenancy (an `Organization` FK on every table) to **PostgreSQL schema-per-tenant** isolation using **`django-tenants`** — the actively maintained fork of the (deprecated) `django-tenant-schemas` — and document what tenancy means for every other edition in the extension chain.

**Library decision (why django-tenants, not django-tenant-schemas):**

| | `django-tenant-schemas` | `django-tenants` ✅ |
|---|---|---|
| Maintenance | Deprecated / unmaintained for years | Actively maintained |
| Django support | ≤ 3.x only | 4.2 LTS, 5.0, 5.1, 5.2+ |
| PostgreSQL | required | required |
| Model | `TenantMixin` / `DomainMixin` schema-per-tenant | Same, drop-in continuation |
| Install | `pip install django-tenant-schemas` (stale) | `pip install django-tenants` |

**Database constraint:** schema-per-tenant is **PostgreSQL-only**. This plan wires the full `django-tenants` stack in formint-cloud (models, settings split, middleware, routers, tenant URLs) so it is **ready to flip on**; the active dev DB remains SQLite (`DB_ENGINE` default) until the operator points `DB_ENGINE=django_tenants.postgresql_backend` + `DB_HOST` at a Postgres server. All tenancy-gated code paths are conditional on `TENANCY_ENABLED` so nothing breaks under SQLite.

## Current State (formint-cloud)

- **15 model classes** in `apps/core/models.py`; **6** carry an explicit `organization = ForeignKey(Organization)` (Branch, Lead, Contact, Deal, InventoryReport, BranchReport).
- Sync/tenant concepts are spread by **row** (`organization_id` column) — no schema isolation, no cross-tenant hard guarantees.
- DB defaults to SQLite; `DB_ENGINE` / `DB_HOST` env overrides exist; `psycopg2-binary` is already a dependency.
- A local PostgreSQL 14 server is available (port 5433); the repo ships a `docker-compose` Postgres (port 5432, user `admin`, db `app_db`).

## Architecture — schema-per-tenant

```
┌──────────────────────────────────────────────────────────────┐
│                         PostgreSQL                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────┐ │
│  │  public    │  │ tenant_a   │  │ tenant_b   │  │  ...    │ │
│  │ (registry) │  │ (schema)   │  │ (schema)   │  │ (schema)│ │
│  │ Tenant     │  │ branches   │  │ branches   │  │         │ │
│  │ Domain     │  │ products   │  │ products   │  │         │ │
│  │ auth/users │  │ sales      │  │ sales      │  │         │ │
│  └────────────┘  └────────────┘  └────────────┘  └─────────┘ │
└──────────────────────────────────────────────────────────────┘
        ▲                                ▲
  TenantMainMiddleware            TenantSyncRouter
  (resolves tenant per host)      (routes shared vs tenant tables)
```

- **`public` schema** = shared registry: `Tenant`, `Domain`, Django auth/users, admin, `django_tenants` itself.
- **One schema per tenant** (one per `Organization`): every tenant-scoped table lives there.
- **Branch settings** become tenant-relative: each tenant owns its branches and each branch owns a rich `BranchSettings` row (currency, tax, timezone, receipt, sync, features — see below).

## Edition Matrix — what tenancy means per edition

| Edition | Tenancy model | Action in this plan |
|---|---|---|
| **Cloud** (`formint-cloud`, Django) | Schema-per-tenant (`django-tenants`) | **Full implementation** (this plan) |
| **Pro** (`formint-pro`, Rust/Tauri + optional sidecar) | Local SQLite per install; syncs to Cloud | Document: Cloud schema is the master; sidecar keeps row-level `branch`/`store` refs |
| **Standard** (`formint-standard`, Rust/Diesel) | Local SQLite per install; syncs to Cloud | Document: same — local-first, Cloud tenant owns the canonical schema |
| **Community** (`formint-community`, Astro/React) | Offline-first local store | Document: no server tenancy; when bridged to Cloud it becomes a tenant's branch |
| **POS client** (`05-pos-client.md`) | Device auth (`DeviceToken`) against a tenant | Document: `node_id` scopes to a tenant's branch |
| **JS SDK** (`06-js-sdk.md`) | `@formints/client` per base URL | Document: `createClient(tenantUrl)` → tenant-scoped API |

**Key principle:** tenancy is a **Cloud-side** concept. Every other edition stays local-first and treats the Cloud schema as the sync master; no local edition needs `django-tenants`.

## Cloud Implementation Plan (formint-cloud)

### Tenant 1 — Dependency & settings split

**Files:**
- Modify: `formint-cloud/backend/pyproject.toml` (add `django-tenants`)
- Modify: `formint-cloud/backend/configs/__init__.py` (settings)

- [x] **Step 1: Add the dependency** (pyproject.toml — pinned `django-tenants>=3.6,<3.14` so the resolver stays on Django 5.0; 3.14+ requires Django 6)

- [x] **Step 2: Split apps into shared / tenant + wire the router** (configs/__init__.py — `SHARED_APPS`/`TENANT_APPS`, `TENANT_MODEL`, `DATABASE_ROUTERS` gated on `TENANCY_ENABLED`)

```python
# ── Tenancy (django-tenants) ────────────────────────────────────
TENANCY_ENABLED = os.environ.get("DB_ENGINE", "").startswith("django_tenants")

SHARED_APPS = [
    "daphne",
    "unfold", "unfold.contrib.filters", "unfold.contrib.forms", "unfold.contrib.inlines",
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "wagtail", "wagtail.admin",
    "channels", "django_fusion", "rest_framework", "django_filters", "django_bolt",
    "django_tenants",
    "apps.core.apps.CoreConfig",   # Tenant/Domain models live in core
    "apps.domain.apps.DomainConfig",
    "apps.handlers.apps.HandlersConfig",
    "apps.tasks",
]

TENANT_APPS = [
    "daphne",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels", "django_fusion", "rest_framework", "django_filters", "django_bolt",
    "apps.core.apps.CoreConfig",
    "apps.domain.apps.DomainConfig",
    "apps.handlers.apps.HandlersConfig",
    "apps.tasks",
]

INSTALLED_APPS = list(SHARED_APPS) + [a for a in TENANT_APPS if a not in SHARED_APPS]

TENANT_MODEL = "core.Tenant"
TENANT_DOMAIN_MODEL = "core.Domain"
PUBLIC_SCHEMA_URLCONF = "configs.urls_public"

if TENANCY_ENABLED:
    DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)
```

- [x] **Step 3: Gate the tenant middleware + Postgres engine** (configs/__init__.py — `TenantMainMiddleware` inserted only when enabled; engine falls back to `django_tenants.postgresql_backend` under tenancy)

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # ... existing middleware ...
]
if TENANCY_ENABLED:
    MIDDLEWARE.insert(1, "django_tenants.middleware.main.TenantMainMiddleware")

DATABASES = {
    "default": {
        "ENGINE": os.environ.get(
            "DB_ENGINE",
            "django.db.backends.sqlite3"
            if not TENANCY_ENABLED
            else "django_tenants.postgresql_backend",
        ),
        "NAME": os.environ.get("DB_NAME", str(BASE_DIR / "formint_cloud.db")),
    }
}
```

> Under SQLite (`TENANCY_ENABLED=False`) everything imports and runs as today; the router, tenant middleware, and Postgres engine activate only when `DB_ENGINE` is flipped.

### Tenant 2 — Tenant + Domain models

**Files:**
- Modify: `formint-cloud/backend/apps/core/models.py`
- New: `formint-cloud/backend/apps/core/migrations/0008_tenant_domain_branchsettings.py`

- [x] **Step 1: `Tenant` (TenantMixin) mapped 1:1 to `Organization`** (apps/core/models.py + migration 0008)

```python
from django_tenants.models import TenantMixin, DomainMixin

class Tenant(TenantMixin):
    """One PostgreSQL schema per Cloud organization."""

    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name="tenant"
    )
    auto_create_schema = True

    def __str__(self):
        return f"Tenant[{self.schema_name}] {self.organization.name}"
```

- [x] **Step 2: `Domain` (DomainMixin)** (apps/core/models.py + migration 0008)

```python
class Domain(DomainMixin):
    """Host → tenant mapping (e.g. acme.pos-cloud.app)."""

    def __str__(self):
        return f"{self.domain} → {self.tenant}"
```

- [x] **Step 3: Migration + schema creation flow** (0008 applied on SQLite; `migrate_schemas --shared/--tenant` is the Postgres flip-on flow)

```
manage.py migrate_schemas --shared
# create public Tenant + localhost Domain, then per organization:
tenant = Tenant(schema_name="acme", organization=org); tenant.save(create_schema=True)
tenant.domains.create(domain="acme.pos-cloud.app", is_primary=True)
manage.py migrate_schemas --tenant
```

### Tenant 3 — Branch settings (complete per-branch configuration)

**Files:**
- Modify: `formint-cloud/backend/apps/core/models.py`

- [x] **Step 1: `BranchSettings` model — one rich settings row per branch** (apps/core/models.py + migration 0008)

```python
class BranchSettings(models.Model):
    """Complete per-branch configuration (tenant-relative)."""

    branch = models.OneToOneField(
        Branch, on_delete=models.CASCADE, related_name="settings_row"
    )

    # Financial
    currency_code = models.CharField(max_length=3, default="USD")
    tax_profile_id = models.CharField(max_length=50, blank=True)   # maps to Standard tax_profiles
    tax_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    price_decimal_places = models.PositiveSmallIntegerField(default=2)
    round_after_tax = models.BooleanField(default=False)

    # Time / locale
    timezone = models.CharField(max_length=64, default="UTC")
    locale = models.CharField(max_length=10, default="en")
    week_starts_on = models.PositiveSmallIntegerField(default=1)   # 0=Sun .. 6=Sat

    # Receipt / printing
    receipt_footer = models.TextField(blank=True)
    receipt_logo_url = models.URLField(blank=True)
    receipt_paper_width_mm = models.PositiveSmallIntegerField(default=80)
    auto_print_receipt = models.BooleanField(default=True)

    # Sync / operations
    sync_interval_seconds = models.PositiveIntegerField(default=300)
    offline_grace_minutes = models.PositiveIntegerField(default=30)
    low_stock_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=10)

    # Feature flags
    features = models.JSONField(default=dict, blank=True)   # {"kitchen_display": true, ...}
    settings = models.JSONField(default=dict, blank=True)   # free-form extras

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "branch settings"
        verbose_name_plural = "branch settings"

    def __str__(self):
        return f"Settings[{self.branch.code}] {self.currency_code}"
```

- [x] **Step 2: Convenience accessor on `Branch`** (`branch.branch_settings` lazy get-or-create)

```python
@property
def branch_settings(self) -> "BranchSettings":
    settings, _ = BranchSettings.objects.get_or_create(branch=self)
    return settings
```

### Tenant 4 — Admin + URL routing

**Files:**
- Modify: `formint-cloud/backend/apps/core/admin.py`
- New: `formint-cloud/backend/configs/urls_public.py`

- [x] **Step 1: Register `Tenant`, `Domain`, `BranchSettings` in Unfold admin** (apps/core/admin.py — `BranchSettingsInline` on `BranchAdmin`; `TenantAdmin` uses `TenantAdminMixin` when available).
- [x] **Step 2: `configs/urls_public.py`** — public-schema URLconf (admin + tenant registry) referenced by `PUBLIC_SCHEMA_URLCONF`.
- [x] **Step 3: Gate** — tenant-aware routing is handled by `TenantMainMiddleware`; `configs/urls.py` remains the tenant URLconf.

### Tenant 5 — Tests (SQLite-safe)

**Files:**
- New: `formint-cloud/backend/apps/test_tenancy.py`

- [x] **Step 1: Unit tests that run on SQLite** (apps/test_tenancy.py — 14 passing: `BranchSettings` defaults/accessor/JSON round-trip, `Tenant`/`Domain` construction + stringify, `TENANCY_ENABLED` gating).
- [x] **Step 2: Document Postgres-only integration tests** (apps/test_tenancy.py — `TenantSchemaIntegrationTest` gated `skipUnless(TENANCY_ENABLED)`, skipped on SQLite).

### Tenant 6 — Migration path (row-level → schema-per-tenant)

1. Keep `Organization` as the row-level registry **and** become the 1:1 anchor for `Tenant`.
2. One-time backfill: for each `Organization` create `Tenant(schema_name=slug, organization=org)` + a primary `Domain`.
3. `manage.py migrate_schemas --tenant` builds tenant schemas from `TENANT_APPS`.
4. Ship rows per tenant (backfill script: per tenant, copy its `organization_id` rows into the tenant schema).
5. Deprecate `organization` FKs over time — queries become schema-local (no `organization_id` filter needed inside a tenant schema).
6. Keep the legacy FK columns for rollback; drop in a later release after data verification.

> **Registry-table note:** `apps.core` appears in both `SHARED_APPS` and `TENANT_APPS`, so `core_tenant` / `core_domain` tables are also created inside every tenant schema when `migrate_schemas --tenant` runs. Harmless (schemas are independent and the registry is only used in `public`), but a future release may move `Tenant`/`Domain` into a dedicated SHARED-only app (`apps.tenants`) to avoid the duplication.

### Tenant 7 — Operations & rollback

- **Flip-on checklist:** set `DB_ENGINE=django_tenants.postgresql_backend`, `DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT`; run `migrate_schemas --shared` then `--tenant`; seed `public` Tenant + `localhost` Domain; restart daphne.
- **Rollback:** unset `DB_ENGINE` → SQLite row-level mode (all gated code off). No destructive commands run by this plan.
- **Backups:** `pg_dump` per schema (`pg_dump -n tenant_a`), complementing the Cloud `BackupRun` monitoring from `04-cloud.md`.

## Tenant 8 — Auth adapters, allauth-per-tenant and database-adapter-per-branch

> The core tenancy plan (Tenant 1–7) covers **data isolation**. This section
> covers the **identity** layer: how authentication adapters, django-allauth
> and branch-scoped database adapters behave once schemas are live.

### 8.1 Auth adapters per tenant

**Principle:** the *adapter* (login strategy, signup rules, redirects) is
**tenant-aware**, not per-schema. There is one shared `public` auth registry
(Django auth tables live in `public`), so user records are global — but every
adapter decision (allowed signup methods, email verification, session policy)
reads the **current tenant** from the request to return tenant-specific
behaviour.

```python
# formint-cloud/backend/apps/core/auth_adapters.py
from django.conf import settings
from django.utils.functional import cached_property
from allauth.account.adapter import DefaultAccountAdapter

class TenantAwareAccountAdapter(DefaultAccountAdapter):
    """One adapter, tenant-aware behaviour via the active schema."""

    @cached_property
    def tenant(self):
        # django-tenants sets ``connection.tenant`` in TenantMainMiddleware.
        from django.db import connection
        return getattr(connection, "tenant", None)

    def is_open_for_signup(self, request):
        # Per-tenant signup gate: allow per-branch setting.
        if self.tenant is None:
            return True  # public schema → admin/backoffice signup
        return bool(self.tenant.settings.get("allow_signup", True))

    def get_login_redirect_url(self, request):
        # Branch-specific landing after login (POS desk vs backoffice).
        if self.tenant is not None:
            branch = self.tenant.default_branch
            if branch is not None:
                return branch.settings.get("login_redirect", "/dashboard/")
        return super().get_login_redirect_url(request)
```

Wire in settings (allauth reads `ACCOUNT_ADAPTER`):

```python
ACCOUNT_ADAPTER = "apps.core.auth_adapters.TenantAwareAccountAdapter"
```

### 8.2 allauth-per-tenant

**Decision: single allauth install, schema-scoped sessions.** Do **not** run
one allauth app instance per schema. Because auth tables live in `public`
(the shared schema), allauth runs once there; what changes per tenant is the
**session scope** and the **tenant context processors**:

1. `TenantMainMiddleware` (already in the plan) resolves the tenant from the
   host **before** allauth's session middleware runs, so
   `request.session` is already tenant-scoped.
2. Add a tenant context processor so every template/API view can read
   `current_tenant` and its `BranchSettings` without a second lookup:

```python
# formint-cloud/backend/apps/core/context_processors.py
def tenant(request):
    from django.db import connection
    tenant = getattr(connection, "tenant", None)
    return {
        "current_tenant": tenant,
        "branch_settings": tenant.branch_settings if tenant else None,
    }
```

3. allauth templates/social providers stay shared; provider keys
   (OAuth client id/secret) may be **per-tenant** via `Tenant.settings`
   JSON, with the `public` value as fallback — see `8.4`.

### 8.3 Database adapter per branch

**Requirement:** each branch may point at a different Postgres target
(regional replication, separate read replica, or a dedicated reporting DB).
The **tenant schema** stays the source of truth; the per-branch adapter is an
**optional read/export target**, never a second write path.

```python
# formint-cloud/backend/configs/databases.py
from django.conf import settings

def branch_database_aliases() -> dict[str, dict]:
    """Extra DATABASES entries per branch, from BranchSettings.settings JSON.

    BranchSettings.settings = {
        "database_alias": "branch_downtown",  # key into DATABASES
        ...
    }
    """
    aliases = {}
    for branch in Branch.objects.all():
        alias = branch.branch_settings.settings.get("database_alias")
        if alias and alias in settings.DATABASES:
            aliases[branch.code] = alias
    return aliases
```

```python
# settings snippet — branch adapters are declared, then mapped by code
DATABASES = {
    "default": { ... django_tenants.postgresql_backend ... },
    "branch_downtown": {"ENGINE": "django.db.backends.postgresql", "NAME": "reports_downtown", ...},
}
```

Usage is **explicit and read-mostly** — a service uses `.using(alias)` for
reporting/export jobs only:

```python
# example: nightly export to a branch's reporting DB
rows = SalesRecord.objects.using("branch_downtown").filter(day=...)
```

### 8.4 Per-tenant provider settings (allauth + adapters)

Extend `Tenant` with a JSON `settings` column (already used for feature flags
on `BranchSettings`; mirror at tenant level):

```python
class Tenant(TenantMixin):
    # ... existing fields ...
    settings = models.JSONField(default=dict, blank=True)
    # e.g. {"allow_signup": True, "social": {"google": {"key": ..., "secret": ...}}}
```

A small helper resolves per-tenant overrides with `public` fallback:

```python
def tenant_provider_settings(provider_id: str) -> dict:
    tenant = getattr(connection, "tenant", None)
    if tenant is not None:
        overrides = tenant.settings.get("social", {}).get(provider_id, {})
        if overrides:
            return overrides
    return getattr(settings, "SOCIALACCOUNT_PROVIDERS", {}).get(provider_id, {})
```

### 8.5 Checklist for this tenant step

- [x] Add `apps/core/auth_adapters.py` (`TenantAwareAccountAdapter`)
- [x] Set `ACCOUNT_ADAPTER = "apps.core.auth_adapters.TenantAwareAccountAdapter"`
- [x] Add `apps/core/context_processors.py` (tenant + branch_settings) and register in `TEMPLATES`
- [x] Add `Tenant.settings` JSON column + migration
- [x] Add `apps/core/services/tenant_providers.py` (per-tenant provider overrides)
- [x] Document `DATABASES` branch aliases + `.using(alias)` read-only convention
- [x] Tests (SQLite-safe): adapter falls back to defaults with no tenant; context processor returns `None` tenant; provider helper falls back to settings

**Verification (SQLite, `TENANCY_ENABLED=False`):** all four pieces import,
run and fall back gracefully — `connection.tenant` is `None`, the context
processor returns empty tenant context, the provider helper returns global
settings, and `BranchSettings.settings` round-trips JSON.

## Self-Review

1. **Library:** `django-tenants` is the maintained successor of the deprecated `django-tenant-schemas`; this plan uses it everywhere. No use of the stale package.
2. **Edition coverage:** matrix covers Cloud, Pro, Standard, Community, POS client, and JS SDK — tenancy is a Cloud-side concern only.
3. **SQLite safety:** every tenancy code path (router, middleware, Postgres engine, tenant URLs) is gated on `TENANCY_ENABLED`; the active dev DB stays SQLite until flipped.
4. **Branch settings:** complete financial/time/locale/receipt/sync/feature configuration per branch, tenant-relative.
5. **No destructive ops:** migration path keeps legacy columns for rollback; nothing is dropped.

## Execution Handoff

1. Implement **Tenant 1–5** in `formint-cloud/backend/` (steps below in the checklist).
2. Run `manage.py check` + `pytest apps/test_tenancy.py` + related suites (SQLite mode).
3. When a Postgres target is available: flip `DB_ENGINE`, run `migrate_schemas`, seed a tenant, run the Postgres integration tests, and mark **Tenant 6–7** executed.
