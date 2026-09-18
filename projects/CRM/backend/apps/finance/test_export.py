"""Tests for the accounting export (invoices, payments, POS revenue)."""
from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.core.models import Workspace
from apps.crm.models import Company
from apps.finance.models import Invoice, Payment
from apps.pos.models import PosSale

User = get_user_model()


class AccountingExportTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Export", slug="export")
        self.other = Workspace.objects.create(name="Other export", slug="other-export")
        self.user = User.objects.create_user(
            username="exporter", email="exporter@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        self.client.force_login(self.user)

        self.company = Company.objects.create(workspace=self.workspace, name="Northline Studio")
        self.invoice = Invoice.objects.create(
            workspace=self.workspace,
            number="INV-EXPORT-1",
            company=self.company,
            status="issued",
            due_on=timezone.localdate(),
            subtotal=Decimal("100.00"),
            tax=Decimal("20.00"),
        )
        self.payment = Payment.objects.create(
            workspace=self.workspace,
            invoice=self.invoice,
            amount=Decimal("120.00"),
            method="card",
        )
        self.pos_sale = PosSale.objects.create(
            workspace=self.workspace,
            external_id="pos-export-1",
            subtotal=Decimal("30.00"),
            total=Decimal("30.00"),
            status="completed",
        )
        # Cross-tenant rows that must never appear.
        other_company = Company.objects.create(workspace=self.other, name="Other Co")
        Invoice.objects.create(
            workspace=self.other,
            number="OTHER-1",
            company=other_company,
            status="paid",
            due_on=timezone.localdate(),
            subtotal=Decimal("9999.00"),
        )

    def test_invoice_csv_export_is_workspace_scoped(self):
        response = self.client.get("/api/v1/finance/export/?kind=invoices&format=csv")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("INV-EXPORT-1", response.content.decode())
        self.assertNotIn("OTHER-1", response.content.decode())

    def test_json_export_returns_rows_and_count(self):
        response = self.client.get("/api/v1/finance/export/?kind=payments&format=json")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["invoice__number"], "INV-EXPORT-1")

    def test_pos_revenue_export_lists_completed_sales(self):
        response = self.client.get("/api/v1/finance/export/?kind=pos_revenue&format=json")
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["external_id"], "pos-export-1")

    def test_export_rejects_unknown_kind_and_bad_format(self):
        self.assertEqual(self.client.get("/api/v1/finance/export/?kind=nope").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/finance/export/?format=xml").status_code, 400)
