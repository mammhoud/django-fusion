"""Tests for the demo dataset: seed_demo command, --user option, and the
Start free signup signal that provisions a fresh account's workspace."""
from __future__ import annotations

from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from apps.core.models import Workspace
from apps.crm.models import Deal, Pipeline, PipelineStage
from apps.finance.models import Invoice, Payment, RevenueEvent
from apps.marketing.models import Campaign, Post, SocialChannel

User = get_user_model()


class SeedDemoCommandTests(TestCase):
    def test_command_builds_the_full_demo_trail(self):
        call_command("seed_demo")

        workspace = Workspace.objects.get(slug="demo-workspace")
        self.assertEqual(Pipeline.objects.filter(workspace=workspace).count(), 1)
        self.assertEqual(PipelineStage.objects.filter(pipeline__workspace=workspace).count(), 5)
        self.assertEqual(Campaign.objects.filter(workspace=workspace).count(), 1)
        self.assertEqual(SocialChannel.objects.filter(workspace=workspace).count(), 2)
        self.assertEqual(Deal.objects.filter(workspace=workspace).count(), 8)
        self.assertEqual(Post.objects.filter(workspace=workspace).count(), 7)

        # Won-deal → invoice → payment → recognized revenue trail.
        invoice = Invoice.objects.get(workspace=workspace, number="INV-2026-014")
        self.assertEqual(invoice.deal.name, "Enterprise rollout")
        self.assertTrue(Payment.objects.filter(workspace=workspace, invoice=invoice).exists())
        self.assertEqual(RevenueEvent.objects.get(workspace=workspace, deal=invoice.deal).amount, invoice.subtotal)

    def test_command_is_idempotent(self):
        call_command("seed_demo")
        counts = {m: m.objects.count() for m in [Pipeline, Deal, Post, Invoice, Payment, RevenueEvent]}
        call_command("seed_demo")
        for model, count in counts.items():
            self.assertEqual(model.objects.count(), count)

    def test_command_user_option_seeds_existing_users_workspace(self):
        user = User.objects.create_user(username="alice", email="alice@example.com", password="Strong-pass-123")
        call_command("seed_demo", "--user", "alice")

        user.profile.refresh_from_db()
        workspace = user.profile.workspace
        self.assertIsNotNone(workspace)
        self.assertEqual(Deal.objects.filter(workspace=workspace).count(), 8)
        self.assertEqual(Invoice.objects.filter(workspace=workspace).count(), 1)
        # The user owns the seeded records.
        self.assertEqual(Deal.objects.filter(workspace=workspace, owner=user).count(), 8)

    def test_command_user_option_requires_a_real_user(self):
        from django.core.management.base import CommandError

        with self.assertRaises(CommandError):
            call_command("seed_demo", "--user", "nobody")


class StartFreeSignupSignalTests(TestCase):
    def _signup(self, username):
        user = User.objects.create_user(username=username, email=f"{username}@example.com", password="Strong-pass-123")
        user_signed_up.send(sender=None, request=None, user=user)
        return user

    def test_signup_provisions_a_seeded_personal_workspace(self):
        user = self._signup("founder")

        user.profile.refresh_from_db()
        workspace = user.profile.workspace
        self.assertIsNotNone(workspace)
        self.assertEqual(workspace.slug, f"demo-{user.pk}")
        self.assertEqual(user.profile.role, "super_admin")
        self.assertEqual(Deal.objects.filter(workspace=workspace).count(), 8)
        self.assertEqual(Post.objects.filter(workspace=workspace).count(), 7)
        self.assertTrue(RevenueEvent.objects.filter(workspace=workspace).exists())

    def test_signup_with_existing_workspace_is_left_alone(self):
        user = User.objects.create_user(username="existing", email="existing@example.com", password="Strong-pass-123")
        original = Workspace.objects.create(name="Existing workspace", slug="existing-workspace")
        user.profile.workspace = original
        user.profile.save()

        user_signed_up.send(sender=None, request=None, user=user)
        user.profile.refresh_from_db()

        self.assertEqual(user.profile.workspace, original)
        self.assertFalse(Deal.objects.filter(workspace=original).exists())

    def test_signup_is_idempotent_for_repeated_signal_fires(self):
        user = self._signup("repeat")
        user.profile.refresh_from_db()
        first = user.profile.workspace
        user_signed_up.send(sender=None, request=None, user=user)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.workspace, first)


class DashboardScopingTests(TestCase):
    """The /api/v1/dashboard counts must be workspace-scoped so each account
    sees only its own numbers (the RevOps KPI cards and funnel)."""

    def setUp(self):
        self.user = User.objects.create_user(username="revops2", email="revops2@example.com", password="Strong-pass-123")
        self.workspace = Workspace.objects.create(name="Mine", slug="mine")
        self.user.profile.workspace = self.workspace
        self.user.profile.save()

        self.other_workspace = Workspace.objects.create(name="Theirs", slug="theirs")
        self.client.force_login(self.user)

    def test_counts_reflect_only_the_callers_workspace(self):
        # The caller's workspace owns two deals; the other workspace owns nine.
        from apps.crm.models import Company, Contact

        mine_pipeline = Pipeline.objects.create(workspace=self.workspace, name="Mine pipeline", is_default=True)
        mine_company = Company.objects.create(workspace=self.workspace, name="Mine Co")
        mine_contact = Contact.objects.create(
            workspace=self.workspace, company=mine_company, first_name="Mine", last_name="User", email="mine@example.com"
        )
        for i in range(2):
            Deal.objects.create(
                workspace=self.workspace,
                company=mine_company,
                contact=mine_contact,
                pipeline=mine_pipeline,
                name=f"Mine deal {i}",
                value="10000.00",
                expected_close_date="2026-12-31",
            )

        theirs_pipeline = Pipeline.objects.create(workspace=self.other_workspace, name="Theirs pipeline", is_default=True)
        theirs_company = Company.objects.create(workspace=self.other_workspace, name="Theirs Co")
        theirs_contact = Contact.objects.create(
            workspace=self.other_workspace,
            company=theirs_company,
            first_name="Theirs",
            last_name="User",
            email="theirs@example.com",
        )
        for i in range(9):
            Deal.objects.create(
                workspace=self.other_workspace,
                company=theirs_company,
                contact=theirs_contact,
                pipeline=theirs_pipeline,
                name=f"Theirs deal {i}",
                value="5000.00",
                expected_close_date="2026-12-31",
            )

        response = self.client.get("/api/v1/dashboard/")
        self.assertEqual(response.status_code, 200)
        counts = response.json()["data"]["counts"]

        self.assertEqual(counts["deals"], 2)
        self.assertEqual(counts["companies"], 1)
        self.assertEqual(counts["contacts"], 1)
        self.assertEqual(counts["pipelines"], 1)

    def test_anonymous_requests_stay_unscoped(self):
        self.client.logout()
        response = self.client.get("/api/v1/dashboard/")
        self.assertEqual(response.status_code, 200)
        # Anonymous has no workspace to scope to, so the endpoint still answers.
        self.assertIn("counts", response.json()["data"])
