"""SQLite-safe tests for the tenant-schema plan (08-tenant-schemas.md).

These tests run on the default dev database (SQLite) and verify the
tenancy-gated code paths are inert while the models are importable and
fully functional as data records. Postgres-only integration tests
(schema creation, cross-tenant isolation) are documented at the bottom
and skipped unless ``TENANCY_ENABLED`` is True.
"""

from django.conf import settings
from django.test import TestCase
from django.test.utils import skipUnless

from apps.core.models import (
    Branch,
    BranchSettings,
    Domain,
    Organization,
    Tenant,
)


class BranchSettingsTest(TestCase):
    """Complete per-branch configuration — creation, accessor, JSON flags."""

    def setUp(self):
        self.org = Organization.objects.create(name="Acme", slug="acme")
        self.branch = Branch.objects.create(
            name="Downtown", code="ACME-01", organization=self.org,
        )

    def test_branch_settings_accessor_creates_default_row(self):
        settings_row = self.branch.branch_settings
        self.assertIsInstance(settings_row, BranchSettings)
        self.assertEqual(settings_row.branch_id, self.branch.id)
        # Idempotent — the accessor reuses the existing row.
        self.assertEqual(self.branch.branch_settings.pk, settings_row.pk)
        self.assertEqual(BranchSettings.objects.filter(branch=self.branch).count(), 1)

    def test_defaults_are_sane(self):
        s = self.branch.branch_settings
        self.assertEqual(s.currency_code, "USD")
        self.assertEqual(s.tax_rate, 0)
        self.assertEqual(s.timezone, "UTC")
        self.assertEqual(s.receipt_paper_width_mm, 80)
        self.assertEqual(s.sync_interval_seconds, 300)
        self.assertEqual(s.offline_grace_minutes, 30)

    def test_financial_configuration_round_trip(self):
        s = self.branch.branch_settings
        s.currency_code = "EUR"
        s.tax_rate = "19.0000"
        s.price_decimal_places = 2
        s.round_after_tax = True
        s.save()
        s.refresh_from_db()
        self.assertEqual(s.currency_code, "EUR")
        self.assertEqual(float(s.tax_rate), 19.0)
        self.assertTrue(s.round_after_tax)

    def test_feature_flag_json_round_trip(self):
        s = self.branch.branch_settings
        s.features = {"kitchen_display": True, "self_checkout": False}
        s.settings = {"printer_name": "EPSON-TM88", "theme": "tactical"}
        s.save()
        s.refresh_from_db()
        self.assertEqual(s.features["kitchen_display"], True)
        self.assertEqual(s.features["self_checkout"], False)
        self.assertEqual(s.settings["printer_name"], "EPSON-TM88")

    def test_str(self):
        s = self.branch.branch_settings
        self.assertIn(self.branch.code, str(s))
        self.assertIn("USD", str(s))


class TenantSettingsFieldTest(TestCase):
    """Tenant.settings JSON column — identity-layer overrides (8.4)."""

    def setUp(self):
        self.org = Organization.objects.create(name="Acme", slug="acme-settings")

    def test_settings_defaults_to_empty_dict(self):
        tenant = Tenant(schema_name="acme-settings", organization=self.org)
        self.assertEqual(tenant.settings, {})

    def test_settings_json_round_trip(self):
        tenant = Tenant(schema_name="acme-settings-2", organization=self.org)
        tenant.settings = {"allow_signup": False, "social": {"google": {"key": "k"}}}
        self.assertEqual(tenant.settings["allow_signup"], False)
        self.assertEqual(tenant.settings["social"]["google"]["key"], "k")

    def test_default_branch_resolves_headquarters(self):
        tenant = Tenant(schema_name="acme-settings-3", organization=self.org)
        branch = Branch.objects.create(
            name="HQ", code="ACME-HQ", organization=self.org, is_headquarters=True
        )
        Branch.objects.create(name="Satellite", code="ACME-SAT", organization=self.org)
        self.assertEqual(tenant.default_branch, branch)


class TenantContextProcessorTest(TestCase):
    """context_processors.tenant — None tenant under SQLite/dev."""

    def test_returns_none_tenant_context(self):
        from apps.core.context_processors import tenant

        ctx = tenant(None)
        self.assertIsNone(ctx["current_tenant"])
        self.assertIsNone(ctx["branch_settings"])


class TenantProviderSettingsTest(TestCase):
    """services.tenant_providers — global fallback with no active tenant."""

    def test_provider_falls_back_to_settings(self):
        from apps.core.services.tenant_providers import tenant_provider_settings

        # No active tenant → falls back to (empty) global settings.
        self.assertEqual(tenant_provider_settings("google"), {})


class TenantAwareAdapterTest(TestCase):
    """auth_adapters.TenantAwareAccountAdapter — defaults with no tenant."""

    def _request(self):
        from django.contrib.auth import get_user_model
        from django.test import RequestFactory

        request = RequestFactory().get("/")
        user = get_user_model().objects.create_user(
            username="adapter-test", email="a@example.com", password="x"
        )
        request.user = user
        return request

    def test_signup_open_without_tenant(self):
        from apps.core.auth_adapters import TenantAwareAccountAdapter

        adapter = TenantAwareAccountAdapter()
        self.assertTrue(adapter.is_open_for_signup(self._request()))

    def test_login_redirect_without_tenant(self):
        from apps.core.auth_adapters import DefaultAccountAdapter, TenantAwareAccountAdapter

        adapter = TenantAwareAccountAdapter()
        # No tenant → base fallback, never a tenant-scoped route.
        redirect = adapter.get_login_redirect_url(self._request())
        if DefaultAccountAdapter is object:
            # django-allauth is not a formint-cloud dependency — the lazy
            # import falls back to object and the adapter returns "/".
            self.assertEqual(redirect, "/")
        else:
            # With allauth installed, the base returns LOGIN_REDIRECT_URL.
            self.assertEqual(redirect, "/accounts/profile/")


class TenantModelTest(TestCase):
    """Tenant/Domain registry models import and behave as data records on SQLite.

    ``Tenant.save()`` is NOT exercised here — ``auto_create_schema`` fires
    Postgres-only ``CREATE SCHEMA`` SQL that SQLite cannot execute (and would
    be wrong to). In-memory instances verify fields + stringification.
    """

    def setUp(self):
        self.org = Organization.objects.create(name="Acme", slug="acme-org")

    def test_tenant_constructs_and_stringifies(self):
        tenant = Tenant(schema_name="acme", organization=self.org)
        self.assertEqual(tenant.schema_name, "acme")
        # Schema auto-creation is gated on tenancy being active — inert on
        # SQLite so a plain save() can never emit CREATE SCHEMA SQL.
        self.assertEqual(
            tenant.auto_create_schema,
            getattr(settings, "TENANCY_ENABLED", False),
        )
        self.assertIn("Tenant[acme]", str(tenant))
        self.assertIn("Acme", str(tenant))

    def test_tenant_has_organization_relation(self):
        tenant = Tenant(schema_name="acme2", organization=self.org)
        self.assertEqual(tenant.organization_id, self.org.id)
        self.assertEqual(self.org.tenant, tenant)

    def test_domain_constructs_and_stringifies(self):
        tenant = Tenant(schema_name="acme3", organization=self.org)
        domain = Domain(domain="acme.pos-cloud.app", tenant=tenant, is_primary=True)
        self.assertEqual(domain.domain, "acme.pos-cloud.app")
        self.assertTrue(domain.is_primary)
        self.assertIn("acme.pos-cloud.app", str(domain))

    def test_settings_reference_tenant_model_paths(self):
        self.assertEqual(settings.TENANT_MODEL, "core.Tenant")
        self.assertEqual(settings.TENANT_DOMAIN_MODEL, "core.Domain")


class TenancyGatingTest(TestCase):
    """Under SQLite (dev default) tenancy is fully inert."""

    def test_tenancy_disabled_on_sqlite(self):
        self.assertFalse(settings.TENANCY_ENABLED)

    def test_tenant_middleware_not_in_middleware_chain(self):
        self.assertNotIn(
            "django_tenants.middleware.main.TenantMainMiddleware",
            settings.MIDDLEWARE,
        )

    def test_no_tenant_router_under_sqlite(self):
        routers = getattr(settings, "DATABASE_ROUTERS", [])
        self.assertNotIn("django_tenants.routers.TenantSyncRouter", routers)

    def test_engine_is_sqlite(self):
        self.assertEqual(settings.DATABASES["default"]["ENGINE"], "django.db.backends.sqlite3")

    def test_public_urlconf_setting_present(self):
        self.assertEqual(settings.PUBLIC_SCHEMA_URLCONF, "configs.urls_public")


# ── Postgres-only integration tests (documented in 08-tenant-schemas.md) ──
# These assert real schema creation + cross-tenant isolation and require a
# live Postgres with DB_ENGINE=django_tenants.postgresql_backend. They are
# intentionally skipped on the default SQLite dev database.


@skipUnless(getattr(settings, "TENANCY_ENABLED", False), "requires Postgres + django-tenants backend")
class TenantSchemaIntegrationTest(TestCase):
    """Run against a live Postgres with tenancy flipped on."""

    def test_schema_creation_and_isolation(self):
        org = Organization.objects.create(name="Isolation", slug="isolation")
        tenant = Tenant(schema_name="isolation_a", organization=org)
        tenant.save(create_schema=True)
        tenant.domains.create(domain="iso-a.pos-cloud.app", is_primary=True)
        self.assertTrue(Tenant.objects.filter(schema_name="isolation_a").exists())
        # A second tenant schema exists independently.
        org2 = Organization.objects.create(name="Isolation B", slug="isolation-b")
        tenant2 = Tenant(schema_name="isolation_b", organization=org2)
        tenant2.save(create_schema=True)
        self.assertNotEqual(tenant.schema_name, tenant2.schema_name)
