"""Tests for the SaaS billing app — catalog, gates, checkout gating, webhook."""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from apps.billing.gates import account_for_workspace, feature_enabled, seat_count_ok
from apps.billing.models import BillingAccount, Plan, Seat
from apps.billing.services import _apply_invoice_paid, handle_webhook, plan_catalog
from apps.core.models import Workspace
from apps.finance.models import RevenueEvent


def make_plan(slug: str = "growth", **overrides) -> Plan:
    defaults = {
        "name": "Growth",
        "price_cents": 14900,
        "period": "monthly",
        "seat_limit": 25,
        "feature_flags": {"attribution": True, "finance_ledger": True},
    }
    defaults.update(overrides)
    plan, _ = Plan.objects.get_or_create(slug=slug, defaults=defaults)
    return plan


class BillingCatalogTests(TestCase):
    def test_plans_api_exposes_public_catalog(self):
        make_plan()
        response = self.client.get("/apis/billing/plans/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["configured"])
        self.assertEqual([p["slug"] for p in payload["plans"]], ["growth"])

    def test_plan_catalog_includes_checkout_href(self):
        make_plan()
        plan = plan_catalog()[0]
        self.assertEqual(plan["checkout"], "/billing/checkout/?plan=growth&period=monthly")
        self.assertEqual(plan["price"], "149.00")


class BillingAccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="biller", email="biller@example.com", password="Strong-pass-123")
        self.workspace = Workspace.objects.create(name="Billing workspace", slug="billing-workspace")

    def test_account_api_requires_login(self):
        response = self.client.get("/apis/billing/account/")
        self.assertEqual(response.status_code, 302)

    def test_account_api_returns_none_when_workspace_missing(self):
        self.client.force_login(self.user)
        response = self.client.get("/apis/billing/account/")
        self.assertEqual(response.status_code, 404)

    def test_account_api_returns_trial_state(self):
        plan = make_plan()
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        BillingAccount.objects.create(workspace=self.workspace, plan=plan, status="trial")
        Seat.objects.create(workspace=self.workspace, user=self.user)
        self.client.force_login(self.user)
        payload = self.client.get("/apis/billing/account/").json()
        self.assertEqual(payload["status"], "trial")
        self.assertEqual(payload["plan"]["slug"], "growth")
        self.assertEqual(payload["seats"], 1)

    def test_checkout_disabled_without_stripe_keys(self):
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        self.client.force_login(self.user)
        response = self.client.post(
            "/billing/checkout/",
            data='{"plan": "growth", "period": "monthly"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)

    @override_settings(STRIPE_SECRET_KEY="sk_test_123")
    def test_checkout_requires_plan_slug(self):
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        self.client.force_login(self.user)
        response = self.client.post("/billing/checkout/", data="{}", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_portal_disabled_without_stripe_keys(self):
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        self.client.force_login(self.user)
        response = self.client.get("/billing/portal/")
        self.assertEqual(response.status_code, 503)


class BillingGateTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Gate workspace", slug="gate-workspace")

    def test_feature_gate_is_permissive_without_account(self):
        self.assertTrue(feature_enabled(self.workspace.pk, "attribution"))

    def test_feature_gate_honors_plan_flags(self):
        plan = make_plan(feature_flags={"attribution": False, "finance_ledger": True})
        BillingAccount.objects.create(workspace=self.workspace, plan=plan, status="active")
        self.assertFalse(feature_enabled(self.workspace.pk, "attribution"))
        self.assertTrue(feature_enabled(self.workspace.pk, "finance_ledger"))

    def test_feature_gate_denies_when_not_entitled(self):
        plan = make_plan(feature_flags={"attribution": True})
        BillingAccount.objects.create(workspace=self.workspace, plan=plan, status="canceled")
        self.assertFalse(feature_enabled(self.workspace.pk, "attribution"))

    def test_seat_limit(self):
        plan = make_plan(seat_limit=2)
        BillingAccount.objects.create(workspace=self.workspace, plan=plan, status="active")
        self.assertTrue(seat_count_ok(self.workspace.pk, 2))
        self.assertFalse(seat_count_ok(self.workspace.pk, 3))


class BillingWebhookTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Stripe workspace", slug="stripe-workspace")

    @override_settings(STRIPE_SECRET_KEY="", STRIPE_WEBHOOK_SECRET="whsec_test")
    def test_webhook_rejected_when_unconfigured(self):
        ok, error = handle_webhook(b"{}", "sig")
        self.assertFalse(ok)
        self.assertIn("not configured", error)

    @override_settings(STRIPE_SECRET_KEY="sk_test_123", STRIPE_WEBHOOK_SECRET="")
    def test_webhook_rejected_without_webhook_secret(self):
        ok, error = handle_webhook(b"{}", "sig")
        self.assertFalse(ok)
        self.assertIn("STRIPE_WEBHOOK_SECRET", error)

    def test_invoice_paid_writes_idempotent_revenue_event(self):
        make_plan()
        account = BillingAccount.objects.create(
            workspace=self.workspace,
            plan=Plan.objects.get(slug="growth"),
            status="trial",
            stripe_subscription_id="sub_123",
        )
        invoice = {"id": "in_1", "amount_paid": 14900, "subscription": "sub_123", "metadata": {}}
        _apply_invoice_paid(invoice)
        _apply_invoice_paid(invoice)  # idempotent: no duplicate
        account.refresh_from_db()
        self.assertEqual(account.status, "active")
        events = RevenueEvent.objects.filter(workspace=self.workspace, external_ref="stripe:in_1")
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.get().amount, Decimal("149.00"))
        self.assertEqual(events.get().kind, "subscription")
