"""Tests for the machine-to-machine POS ingest road.

Covers API-key auth, workspace resolution by ``external_ref``, idempotent
upsert, refund reconciliation, and the POS revenue bridge into the finance
trend (tenant-scoped).
"""
from __future__ import annotations

import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from apps.core.models import AuditLog, Workspace
from apps.crm.models import Contact
from apps.finance.models import RevenueEvent
from apps.pos.models import PosPayment, PosSale, PosSaleItem

INGEST_URL = "/api/v1/ingest/pos/sales/"
INGEST_KEY = "test-ingest-key"


def _sale_payload(external_ref: str, external_id: str = "sale-1", **overrides) -> dict:
    sale = {
        "external_id": external_id,
        "sale_date": "2026-08-14T10:00:00Z",
        "subtotal": "100.00",
        "tax_amount": "8.00",
        "discount_amount": "0.00",
        "cashback_amount": "0.00",
        "total": "108.00",
        "payment_method": "card",
        "status": "completed",
        "customer": {
            "external_id": "cust-1",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "phone": "555-0100",
        },
        "items": [
            {"product_name": "Latte", "quantity": 2, "unit_price": "4.50", "line_total": "9.00"},
        ],
        "payments": [{"amount": "108.00", "method": "card", "reference": "pay-1"}],
    }
    sale.update(overrides)
    return {"external_ref": external_ref, "sales": [sale]}


@override_settings(POS_INGEST_API_KEY=INGEST_KEY)
class PosIngestApiTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(
            name="POS org", slug="pos-org", external_ref="pos-org-a"
        )
        self.other = Workspace.objects.create(
            name="Other org", slug="other-org", external_ref="pos-org-b"
        )

    def _post(self, payload, key=INGEST_KEY):
        return self.client.post(
            INGEST_URL,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_API_KEY=key,
        )

    def test_requires_api_key(self):
        response = self.client.post(
            INGEST_URL,
            data=json.dumps(_sale_payload("pos-org-a")),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        response = self._post(_sale_payload("pos-org-a"), key="wrong-key")
        self.assertEqual(response.status_code, 401)

    def test_unknown_workspace_returns_404(self):
        response = self._post(_sale_payload("missing-org"))
        self.assertEqual(response.status_code, 404)

    def test_ingest_creates_sale_items_payments_revenue_and_audit(self):
        response = self._post(_sale_payload("pos-org-a"))
        self.assertEqual(response.status_code, 200)
        result = response.json()["results"][0]
        self.assertEqual(result["status"], "created")

        sale = PosSale.objects.get(external_id="sale-1", workspace=self.workspace)
        self.assertEqual(sale.total, Decimal("108.00"))
        self.assertEqual(sale.status, "completed")
        self.assertEqual(sale.items.count(), 1)
        self.assertEqual(sale.payments.count(), 1)

        contact = Contact.objects.get(email="jane@example.com", workspace=self.workspace)
        self.assertEqual(contact.company.name, "Walk-in customers")
        self.assertEqual(sale.contact_id, contact.pk)

        event = RevenueEvent.objects.get(external_ref="pos:sale-1", workspace=self.workspace)
        self.assertEqual(event.kind, "pos_sale")
        self.assertEqual(event.amount, Decimal("108.00"))
        self.assertIsNone(event.deal_id)

        self.assertTrue(
            AuditLog.objects.filter(
                workspace=self.workspace, model_name="pos.PosSale", object_id="sale-1"
            ).exists()
        )

    def test_reingest_is_idempotent(self):
        self._post(_sale_payload("pos-org-a"))
        response = self._post(_sale_payload("pos-org-a"))
        self.assertEqual(response.json()["results"][0]["status"], "updated")
        self.assertEqual(PosSale.objects.filter(external_id="sale-1").count(), 1)
        self.assertEqual(PosSaleItem.objects.count(), 1)
        self.assertEqual(PosPayment.objects.count(), 1)
        self.assertEqual(Contact.objects.filter(email="jane@example.com").count(), 1)
        self.assertEqual(RevenueEvent.objects.filter(external_ref="pos:sale-1").count(), 1)

    def test_refund_removes_recognized_revenue(self):
        self._post(_sale_payload("pos-org-a"))
        response = self._post(_sale_payload("pos-org-a", status="refunded"))
        self.assertEqual(response.status_code, 200)

        sale = PosSale.objects.get(external_id="sale-1")
        self.assertEqual(sale.status, "refunded")
        self.assertFalse(RevenueEvent.objects.filter(external_ref="pos:sale-1").exists())

    def test_pos_revenue_lands_in_trend(self):
        self._post(_sale_payload("pos-org-a"))
        user = User.objects.create_user(
            username="revops", email="revops@example.com", password="Strong-pass-123"
        )
        user.profile.workspace = self.workspace
        user.profile.save()
        self.client.force_login(user)

        response = self.client.get("/api/v1/revenue/trend/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["grand_total"], "108.00")

    def test_pos_revenue_is_workspace_scoped(self):
        self._post(_sale_payload("pos-org-a"))
        user_b = User.objects.create_user(
            username="revops-b", email="revopsb@example.com", password="Strong-pass-123"
        )
        user_b.profile.workspace = self.other
        user_b.profile.save()
        self.client.force_login(user_b)

        response = self.client.get("/api/v1/revenue/trend/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["grand_total"], "0.00")
