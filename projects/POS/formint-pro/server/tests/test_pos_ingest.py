"""Loop-CRM POS ingest push (Formint Pro side) — unit tests.

Covers ``services.pos_ingest``: sale/item/customer serialization into
Loop-CRM's ingest shape, pending-row collection (completed/refunded only,
unsynced only), the idempotent push + per-row ``sync_status`` reconciliation,
and the unconfigured/offline no-op paths. Uses ``httpx.MockTransport`` so no
real Loop-CRM server is required.
"""

from __future__ import annotations

import json

import pytest
from services import pos_ingest


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    from models.pos import Customer, Product, Sale, SaleItem

    SaleItem.objects.all().delete()
    Sale.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()
    yield


def _client(handler, **kwargs):
    """Build a PosIngestClient wired to an httpx MockTransport handler."""
    import httpx

    transport = httpx.MockTransport(handler)
    defaults = dict(
        base_url="https://crm.example.com",
        api_key="secret-key",
        workspace_ref="ws-ref-1",
        transport=transport,
    )
    defaults.update(kwargs)
    return pos_ingest.PosIngestClient(**defaults)


class TestSerializeSale:
    def test_serialize_returns_loop_crm_shape(self, sale_factory, sale_item_factory):
        sale = sale_factory(
            subtotal=10.00, tax_amount=1.00, discount_amount=0.50,
            cashback_amount=0.25, total=10.25, payment_method="card",
            status="completed", notes="table 3",
        )
        item = sale_item_factory(sale=sale, product_name="Espresso", quantity=2,
                                 unit_price=4.00, line_total=8.00)

        payload = pos_ingest.serialize_sale(sale)

        assert payload["external_id"] == f"formint-pro:{sale.pk}"
        assert payload["status"] == "completed"
        assert payload["payment_method"] == "card"
        assert payload["subtotal"] == 10.0
        assert payload["tax_amount"] == 1.0
        assert payload["discount_amount"] == 0.5
        assert payload["cashback_amount"] == 0.25
        assert payload["total"] == 10.25
        assert payload["source"] == "formint-pro"
        assert payload["sale_date"] == sale.sale_date.isoformat()

        assert len(payload["items"]) == 1
        line = payload["items"][0]
        assert line["product_name"] == "Espresso"
        assert line["quantity"] == 2
        assert line["unit_price"] == 4.0
        assert line["line_total"] == 8.0
        assert line["external_id"] == f"formint-pro:{sale.pk}:{item.pk}"

        customer = payload["customer"]
        assert customer["email"] == sale.customer.email
        assert customer["external_id"] == f"formint-pro:{sale.customer.pk}"

    def test_serialize_anonymous_sale_has_no_customer(self, sale_factory):
        sale = sale_factory(customer=None, total=5.00)
        payload = pos_ingest.serialize_sale(sale)
        assert payload["customer"] is None


class TestCollectPending:
    def test_collects_completed_and_refunded_unsynced_only(self, sale_factory):
        from models.pos import Sale

        completed = sale_factory(status="completed")
        refunded = sale_factory(status="refunded")
        pending = sale_factory(status="pending")
        cancelled = sale_factory(status="cancelled")
        # The flag_for_sync signal resets rows on create, so acknowledge via
        # .update() (the same path the real reconcile uses).
        already = sale_factory(status="completed")
        Sale.objects.filter(pk=already.pk).update(sync_status="synced", is_synced=True)

        client = pos_ingest.PosIngestClient()
        collected = client.collect_pending()

        pks = {s.pk for s in collected}
        assert completed.pk in pks
        assert refunded.pk in pks
        assert pending.pk not in pks
        assert cancelled.pk not in pks
        assert already.pk not in pks

    def test_failed_rows_are_retried(self, sale_factory):
        from models.pos import Sale

        sale = sale_factory(status="completed")
        Sale.objects.filter(pk=sale.pk).update(sync_status="failed")
        client = pos_ingest.PosIngestClient()
        assert len(client.collect_pending()) == 1


class TestPush:
    def test_push_posts_payload_and_marks_synced(self, sale_factory):
        sale = sale_factory(status="completed", total=12.34)
        captured = {}

        def handler(request):
            captured["url"] = str(request.url)
            captured["api_key"] = request.headers.get("X-API-Key")
            captured["body"] = json.loads(request.content)
            import httpx
            return httpx.Response(
                200, json={
                    "results": [
                        {"external_id": f"formint-pro:{sale.pk}", "status": "created",
                         "pos_sale_id": 99},
                    ],
                    "count": 1,
                },
            )

        client = _client(handler)
        result = client.push([sale])

        assert result["status"] == "ok"
        assert result["count"] == 1
        assert captured["url"] == "https://crm.example.com/api/v1/ingest/pos/sales/"
        assert captured["api_key"] == "secret-key"
        assert captured["body"]["external_ref"] == "ws-ref-1"
        assert len(captured["body"]["sales"]) == 1
        assert captured["body"]["sales"][0]["total"] == 12.34

        sale.refresh_from_db()
        assert sale.sync_status == "synced"
        assert sale.is_synced is True
        assert sale.synced_at is not None

    def test_push_marks_error_rows_failed(self, sale_factory):
        ok = sale_factory(status="completed")
        bad = sale_factory(status="completed")
        import httpx

        def handler(request):
            return httpx.Response(200, json={
                "results": [
                    {"external_id": f"formint-pro:{ok.pk}", "status": "updated"},
                    {"external_id": f"formint-pro:{bad.pk}", "status": "error",
                     "error": "bad total"},
                ],
                "count": 2,
            })

        client = _client(handler)
        client.push([ok, bad])

        ok.refresh_from_db()
        bad.refresh_from_db()
        assert ok.sync_status == "synced"
        assert bad.sync_status == "failed"
        assert bad.is_synced is False

    def test_push_http_failure_marks_all_failed(self, sale_factory):
        sale = sale_factory(status="completed")
        import httpx

        def handler(request):
            return httpx.Response(500, text="boom")

        client = _client(handler)
        result = client.push([sale])

        assert result["status"] == "failed"
        sale.refresh_from_db()
        assert sale.sync_status == "failed"
        assert sale.is_synced is False


class TestConfigAndEntryPoint:
    def test_unconfigured_client_is_skipped(self):
        client = pos_ingest.PosIngestClient(base_url="", api_key="", workspace_ref="")
        assert client.is_configured is False
        assert client.push([]) == {"status": "skipped", "reason": "unconfigured", "count": 0}

    def test_push_pending_sales_skips_when_unconfigured(self, monkeypatch, sale_factory):
        sale_factory(status="completed")
        monkeypatch.delenv("LOOP_CRM_URL", raising=False)
        monkeypatch.delenv("LOOP_CRM_INGEST_API_KEY", raising=False)
        monkeypatch.delenv("LOOP_CRM_WORKSPACE_REF", raising=False)

        result = pos_ingest.push_pending_sales()
        assert result["status"] == "skipped"
        assert result["reason"] == "unconfigured"

    def test_is_configured_requires_all_three(self):
        assert pos_ingest.PosIngestClient(
            base_url="https://crm", api_key="k", workspace_ref="r",
        ).is_configured is True
        assert pos_ingest.PosIngestClient(
            base_url="https://crm", api_key="", workspace_ref="r",
        ).is_configured is False
