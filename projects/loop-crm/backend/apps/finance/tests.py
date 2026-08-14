"""Tests for the finance revenue-trend API used by the RevOps dashboard card."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.core.models import Workspace
from apps.crm.models import Company, Contact, Deal, Pipeline, PipelineStage
from apps.finance.models import RevenueEvent
from apps.finance.services import revenue_trend_results

User = get_user_model()


class RevenueTrendApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="revops", email="revops@example.com", password="Strong-pass-123")
        self.workspace = Workspace.objects.create(name="Trend workspace", slug="trend-workspace")
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        self.client.force_login(self.user)

        self.other_workspace = Workspace.objects.create(name="Other workspace", slug="other-workspace")
        self.company = Company.objects.create(workspace=self.workspace, name="Trend Co")
        self.contact = Contact.objects.create(
            workspace=self.workspace,
            company=self.company,
            first_name="Ada",
            last_name="Lovelace",
            email="ada@trend.example",
        )
        self.pipeline = Pipeline.objects.create(workspace=self.workspace, name="Sales pipeline", is_default=True)
        self.stage = PipelineStage.objects.create(
            pipeline=self.pipeline,
            name="Won",
            stage_type="closed_won",
            order=5,
            probability=100,
        )

    def _event(self, workspace, amount, recognized_on: date) -> RevenueEvent:
        deal = Deal.objects.create(
            workspace=workspace,
            company=self.company,
            contact=self.contact,
            stage=self.stage,
            pipeline=self.pipeline,
            name=f"Deal {amount}",
            value=amount,
            expected_close_date=recognized_on,
        )
        return RevenueEvent.objects.create(
            workspace=workspace,
            deal=deal,
            amount=amount,
            recognized_on=recognized_on,
        )

    def test_trend_returns_six_zero_filled_months(self):
        response = self.client.get("/api/v1/revenue/trend/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 6)
        self.assertEqual(len(payload["results"]), 6)
        # Every trailing month appears, even without revenue.
        self.assertEqual(payload["grand_total"], "0.00")
        self.assertEqual({row["total"] for row in payload["results"]}, {"0.00"})

    def test_trend_buckets_revenue_by_month_and_sums(self):
        today = timezone.localdate()
        this_month = date(today.year, today.month, 1)
        self._event(self.workspace, "12000.00", this_month)
        self._event(self.workspace, "4500.00", this_month)

        response = self.client.get("/api/v1/revenue/trend/")
        payload = response.json()

        current = payload["results"][-1]
        self.assertEqual(current["month"], this_month.strftime("%Y-%m"))
        self.assertEqual(current["total"], "16500.00")
        self.assertEqual(current["events"], 2)
        self.assertEqual(payload["grand_total"], "16500.00")

    def test_trend_is_workspace_scoped(self):
        today = timezone.localdate()
        this_month = date(today.year, today.month, 1)
        self._event(self.workspace, "1000.00", this_month)
        self._event(self.other_workspace, "99999.00", this_month)

        response = self.client.get("/api/v1/revenue/trend/")
        payload = response.json()
        self.assertEqual(payload["grand_total"], "1000.00")

    def test_trend_rejects_non_get(self):
        response = self.client.post("/api/v1/revenue/trend/", {})
        self.assertEqual(response.status_code, 405)

    def test_trend_service_shapes_rows_for_any_road(self):
        # The same pure helper backs the Django and django-bolt roads, so the
        # canonical road is covered even though the bolt runtime is optional.
        today = timezone.localdate()
        current = date(today.year, today.month, 1)
        payload = revenue_trend_results(
            [{"month": current, "total": Decimal("12000.00"), "events": 3}],
            today=today,
        )
        self.assertEqual(payload["count"], 6)
        self.assertEqual(payload["grand_total"], "12000.00")
        last = payload["results"][-1]
        self.assertEqual(last["month"], current.strftime("%Y-%m"))
        self.assertEqual(last["total"], "12000.00")
        self.assertEqual(last["events"], 3)
        self.assertTrue(all(row["total"] == "0.00" for row in payload["results"][:-1]))
