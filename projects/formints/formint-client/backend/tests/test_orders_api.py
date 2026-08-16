"""Order JSON API — GET /api/orders/ (list), POST /api/orders/ (create),
and GET /api/orders/<pk>/ (detail).

The Vue POS client consumes these endpoints: the list drives the Orders and
Dashboard views, the detail backs the expandable cards and the printable
receipt, and the register submits the ticket via POST. These tests pin the
decimal-safe serialization contract (amounts serialized as strings, not
floats), the 404 behaviour for unknown ids, and the creation/validation
rules for the register submission.
"""

from datetime import datetime
from decimal import Decimal

import pytest

from shop.models import Cart, Order, Product, PromoCode

pytestmark = pytest.mark.django_db


@pytest.fixture
def products():
    """A couple of available catalog products with known prices."""
    from shop.models import Category

    category = Category.objects.create(name="Coffee", slug="coffee")
    espresso = Product.objects.create(
        category=category, name="Espresso", price=Decimal("3.50"), slug="espresso"
    )
    knot = Product.objects.create(
        category=category, name="Cinnamon Knot", price=Decimal("5.50"), slug="cinnamon-knot"
    )
    return {"espresso": espresso, "knot": knot}


@pytest.fixture
def order():
    """A completed dine-in order with two line items."""
    order = Order.objects.create(
        customer_name="Ada Lovelace",
        customer_email="ada@example.com",
        customer_phone="+1 555 0142",
        order_type=Order.OrderType.DINE_IN,
        status=Order.Status.COMPLETED,
        notes="Extra napkins, please",
        subtotal=Decimal("12.50"),
        tax=Decimal("1.00"),
        total=Decimal("13.50"),
    )
    order.items.create(
        product_name="Espresso", unit_price=Decimal("3.50"), quantity=2
    )
    order.items.create(
        product_name="Cinnamon Knot", unit_price=Decimal("5.50"), quantity=1
    )
    return order


class TestOrderListApi:
    def test_list_is_200_json(self, client, order):
        response = client.get("/api/orders/")
        assert response.status_code == 200
        assert response["Content-Type"].startswith("application/json")

    def test_list_payload_shape(self, client, order):
        payload = client.get("/api/orders/").json()["orders"][0]
        assert payload["id"] == order.pk
        assert payload["reference"] == order.reference
        assert payload["customer_name"] == "Ada Lovelace"
        assert payload["status"] == "completed"
        assert payload["order_type"] == "dine_in"
        # Decimal-safe: amounts are strings, never floats.
        assert payload["total_amount"] == "13.50"
        assert payload["currency"] == "$"
        # created_at is a parseable ISO-8601 timestamp.
        datetime.fromisoformat(payload["created_at"])

    def test_list_items_shape(self, client, order):
        items = client.get("/api/orders/").json()["orders"][0]["items"]
        assert [i["product_name"] for i in items] == [
            "Espresso",
            "Cinnamon Knot",
        ]
        espresso = items[0]
        assert espresso["quantity"] == 2
        assert espresso["unit_price"] == "3.50"
        assert espresso["subtotal"] == "7.00"  # 2 × 3.50, as a string
        knot = items[1]
        assert knot["unit_price"] == "5.50"
        assert knot["subtotal"] == "5.50"

    def test_list_sorts_newest_first(self, client, order):
        newer = Order.objects.create(customer_name="Newer", total=Decimal("9.99"))
        refs = [o["reference"] for o in client.get("/api/orders/").json()["orders"]]
        assert refs[0] == newer.reference
        assert refs[1] == order.reference

    def test_list_caps_at_50(self, client):
        for i in range(55):
            Order.objects.create(customer_name=f"Customer {i}", total=Decimal("5.00"))
        response = client.get("/api/orders/")
        assert response.status_code == 200
        assert len(response.json()["orders"]) == 50



class TestOrderCreateApi:
    def test_create_returns_201_with_payload(self, client, products):
        response = client.post(
            "/api/orders/",
            data={
                "items": [
                    {"product_id": products["espresso"].pk, "quantity": 2},
                    {"product_id": products["knot"].pk, "quantity": 1},
                ],
                "order_type": "dine_in",
                "customer_name": "Ada Lovelace",
                "notes": "Window seat",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        payload = response.json()
        assert payload["customer_name"] == "Ada Lovelace"
        assert payload["order_type"] == "dine_in"
        assert payload["notes"] == "Window seat"
        assert payload["status"] == "pending"
        # Totals recomputed server-side: 2 × 3.50 + 1 × 5.50 = 12.50,
        # 10% tax = 1.25, total = 13.75 — all decimal-safe strings.
        assert payload["subtotal"] == "12.50"
        assert payload["tax"] == "1.25"
        assert payload["total_amount"] == "13.75"
        # The order actually persisted with line items.
        order = Order.objects.get(pk=payload["id"])
        assert order.item_count == 3
        assert list(order.items.values_list("product_name", flat=True)) == [
            "Espresso",
            "Cinnamon Knot",
        ]

    def test_create_defaults_guest_takeaway(self, client, products):
        response = client.post(
            "/api/orders/",
            data={"items": [{"product_id": products["espresso"].pk, "quantity": 1}]},
            content_type="application/json",
        )
        assert response.status_code == 201
        payload = response.json()
        assert payload["customer_name"] == "Guest"
        assert payload["order_type"] == "takeaway"
        assert payload["total_amount"] == "3.85"  # 3.50 + 10%

    def test_create_rejects_empty_items(self, client):
        response = client.post(
            "/api/orders/",
            data={"items": []},
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "items" in response.json()["error"]

    def test_create_rejects_unknown_product(self, client):
        response = client.post(
            "/api/orders/",
            data={"items": [{"product_id": 999999, "quantity": 1}]},
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "999999" in response.json()["error"]

    def test_create_rejects_zero_quantity(self, client, products):
        response = client.post(
            "/api/orders/",
            data={"items": [{"product_id": products["espresso"].pk, "quantity": 0}]},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_rejects_bad_json(self, client):
        response = client.post(
            "/api/orders/",
            data="not json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_ignores_unavailable_product(self, client, products):
        products["espresso"].is_available = False
        products["espresso"].save(update_fields=["is_available"])
        response = client.post(
            "/api/orders/",
            data={"items": [{"product_id": products["espresso"].pk, "quantity": 1}]},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_put_is_not_allowed(self, client):
        assert client.put("/api/orders/").status_code == 405


class TestOrderDetailApi:
    def test_detail_extends_list_payload(self, client, order):
        payload = client.get(f"/api/orders/{order.pk}/").json()
        # List fields present…
        assert payload["id"] == order.pk
        assert payload["reference"] == order.reference
        assert payload["customer_name"] == "Ada Lovelace"
        assert payload["status"] == "completed"
        assert payload["order_type"] == "dine_in"
        assert payload["total_amount"] == "13.50"
        assert payload["currency"] == "$"
        # …plus the detail-only fields.
        assert payload["customer_email"] == "ada@example.com"
        assert payload["customer_phone"] == "+1 555 0142"
        assert payload["notes"] == "Extra napkins, please"
        assert payload["subtotal"] == "12.50"
        assert payload["tax"] == "1.00"
        assert len(payload["items"]) == 2

    def test_detail_totals_reconcile(self, client, order):
        payload = client.get(f"/api/orders/{order.pk}/").json()
        assert Decimal(payload["subtotal"]) + Decimal(payload["tax"]) == Decimal(
            payload["total_amount"]
        )

    def test_detail_matches_list(self, client, order):
        listed = client.get("/api/orders/").json()["orders"][0]
        detail = client.get(f"/api/orders/{order.pk}/").json()
        for key in (
            "id",
            "reference",
            "customer_name",
            "status",
            "order_type",
            "total_amount",
            "currency",
        ):
            assert detail[key] == listed[key]
        assert detail["items"] == listed["items"]

    def test_unknown_order_returns_404(self, client):
        assert client.get("/api/orders/999999/").status_code == 404

    def test_post_is_not_allowed(self, client, order):
        assert client.post(f"/api/orders/{order.pk}/").status_code == 405


class TestOrderFulfilmentFields:
    """The checkout extras — ready time, delivery address, table number,
    payment method and promo codes — persisted via the POS JSON API."""

    def _post(self, client, products, **extra):
        body = {
            "items": [{"product_id": products["espresso"].pk, "quantity": 2}],
            "order_type": "delivery",
            "customer_name": "Ada Lovelace",
        }
        body.update(extra)
        return client.post("/api/orders/", data=body, content_type="application/json")

    def test_delivery_fields_persisted(self, client, products):
        response = self._post(
            client,
            products,
            delivery_address="123 Roastery Lane, Apt 4",
            delivery_city="Chicago",
            delivery_zip="60601",
            payment_method="card",
        )
        assert response.status_code == 201
        payload = response.json()
        assert payload["delivery_address"] == "123 Roastery Lane, Apt 4"
        assert payload["delivery_city"] == "Chicago"
        assert payload["delivery_zip"] == "60601"
        assert payload["payment_method"] == "card"
        order = Order.objects.get(pk=payload["id"])
        assert order.delivery_address == "123 Roastery Lane, Apt 4"
        assert order.payment_method == "card"

    def test_dine_in_table_persisted(self, client, products):
        payload = self._post(
            client, products, order_type="dine_in", table_number="12"
        ).json()
        assert payload["table_number"] == "12"

    def test_ready_at_persisted(self, client, products):
        payload = self._post(
            client,
            products,
            ready_at="2026-08-14T18:30:00Z",
        ).json()
        assert payload["ready_at"] is not None
        order = Order.objects.get(pk=payload["id"])
        assert order.ready_at is not None
        assert order.ready_at.hour == 18

    def test_invalid_payment_defaults_to_cash(self, client, products):
        payload = self._post(client, products, payment_method="crypto").json()
        assert payload["payment_method"] == "cash"

    def test_item_notes_persisted(self, client, products):
        response = client.post(
            "/api/orders/",
            data={
                "items": [
                    {
                        "product_id": products["espresso"].pk,
                        "quantity": 2,
                        "note": "No sugar",
                    }
                ],
                "order_type": "takeaway",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        item = Order.objects.get(pk=response.json()["id"]).items.first()
        assert item.note == "No sugar"


class TestPromoCodes:
    @pytest.fixture(autouse=True)
    def promo(self):
        return PromoCode.objects.create(
            code="WELCOME10",
            discount_type=PromoCode.DiscountType.PERCENT,
            value=Decimal("10.00"),
            is_active=True,
        )

    def test_percent_promo_applied(self, client, products, promo):
        # 2 × 3.50 = 7.00; 10% off → 6.30; tax 0.63; total 6.93.
        response = client.post(
            "/api/orders/",
            data={
                "items": [{"product_id": products["espresso"].pk, "quantity": 2}],
                "promo_code": "welcome10",  # case-insensitive
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        payload = response.json()
        assert payload["promo_code"] == "WELCOME10"
        assert payload["discount"] == "0.70"
        assert payload["subtotal"] == "7.00"
        assert payload["tax"] == "0.63"
        assert payload["total_amount"] == "6.93"
        promo.refresh_from_db()
        assert promo.used_count == 1

    def test_fixed_promo_capped_at_subtotal(self, client, products):
        PromoCode.objects.create(
            code="FLAT50",
            discount_type=PromoCode.DiscountType.FIXED,
            value=Decimal("50.00"),
            is_active=True,
        )
        payload = client.post(
            "/api/orders/",
            data={
                "items": [{"product_id": products["espresso"].pk, "quantity": 1}],
                "promo_code": "FLAT50",
            },
            content_type="application/json",
        ).json()
        # Discount never exceeds the subtotal (3.50) — order total is free.
        assert payload["discount"] == "3.50"
        assert payload["total_amount"] == "0.00"

    def test_unknown_promo_ignored(self, client, products):
        payload = client.post(
            "/api/orders/",
            data={
                "items": [{"product_id": products["espresso"].pk, "quantity": 1}],
                "promo_code": "NOPE123",
            },
            content_type="application/json",
        ).json()
        assert payload["discount"] == "0.00"
        assert payload["promo_code"] == ""
        assert payload["total_amount"] == "3.85"

    def test_inactive_promo_ignored(self, client, products, promo):
        promo.is_active = False
        promo.save(update_fields=["is_active"])
        payload = client.post(
            "/api/orders/",
            data={
                "items": [{"product_id": products["espresso"].pk, "quantity": 1}],
                "promo_code": "WELCOME10",
            },
            content_type="application/json",
        ).json()
        assert payload["discount"] == "0.00"
        assert payload["promo_code"] == ""

    def test_exhausted_promo_ignored(self, client, products, promo):
        promo.max_uses = 1
        promo.used_count = 1
        promo.save(update_fields=["max_uses", "used_count"])
        payload = client.post(
            "/api/orders/",
            data={
                "items": [{"product_id": products["espresso"].pk, "quantity": 1}],
                "promo_code": "WELCOME10",
            },
            content_type="application/json",
        ).json()
        assert payload["discount"] == "0.00"
        assert payload["promo_code"] == ""


class TestCheckoutPage:
    """The server-rendered checkout — anonymous render, promo apply and the
    form-value preservation across the promo round-trip."""

    @pytest.fixture(autouse=True)
    def cart_in_session(self, client, products):
        cart = Cart.objects.create(session_key="checkout-test-session")
        cart.items.create(
            product=products["espresso"], quantity=1, unit_price=products["espresso"].price
        )
        from shop.services import CART_SESSION_KEY

        session = client.session
        session[CART_SESSION_KEY] = cart.pk
        session.save()
        return cart

    def test_anonymous_checkout_renders(self, client):
        response = client.get("/checkout/")
        assert response.status_code == 200
        assert b"Promo code" in response.content
        assert b"Ready by" in response.content

    def test_apply_promo_preserves_form_values(self, client):
        PromoCode.objects.create(
            code="WELCOME10",
            discount_type=PromoCode.DiscountType.PERCENT,
            value=Decimal("10.00"),
            is_active=True,
        )
        response = client.post(
            "/checkout/",
            {
                "apply_promo": "1",
                "promo_code": "WELCOME10",
                "customer_name": "Grace Hopper",
                "order_type": "takeaway",
                "notes": "Window seat",
            },
        )
        assert response.status_code == 302
        rendered = client.get("/checkout/")
        assert rendered.status_code == 200
        html = rendered.content.decode()
        # The form survived the promo round-trip (no field loss).
        assert 'value="Grace Hopper"' in html
        assert "Window seat" in html
        assert "WELCOME10 applied" in html
        # Discount shown and math correct: 3.50 − 0.35, tax on 3.15.
        assert "0.35" in html

    def test_invalid_promo_shows_error_but_keeps_values(self, client):
        response = client.post(
            "/checkout/",
            {
                "apply_promo": "1",
                "promo_code": "NOPE",
                "customer_name": "Ada Lovelace",
                "order_type": "delivery",
                "delivery_address": "1 Test St",
            },
        )
        assert response.status_code == 302
        rendered = client.get("/checkout/")
        html = rendered.content.decode()
        assert "isn&#x27;t valid" in html or "isn't valid" in html
        assert 'value="Ada Lovelace"' in html
        assert 'value="1 Test St"' in html


class TestOrderStatusApi:
    """POST /api/orders/<pk>/status/ — the kitchen advance flow."""

    @pytest.fixture
    def pending_order(self):
        return Order.objects.create(
            customer_name="Kitchen Test",
            status=Order.Status.PENDING,
            subtotal=Decimal("4.00"),
            tax=Decimal("0.40"),
            total=Decimal("4.40"),
        )

    def _advance(self, client, pk, status):
        return client.post(
            f"/api/orders/{pk}/status/",
            data={"status": status},
            content_type="application/json",
        )

    def test_pending_to_preparing(self, client, pending_order):
        response = self._advance(client, pending_order.pk, "preparing")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "preparing"
        pending_order.refresh_from_db()
        assert pending_order.status == Order.Status.PREPARING

    def test_preparing_to_ready(self, client, pending_order):
        self._advance(client, pending_order.pk, "preparing")
        response = self._advance(client, pending_order.pk, "ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"

    def test_ready_to_completed(self, client, pending_order):
        for step in ("preparing", "ready", "completed"):
            response = self._advance(client, pending_order.pk, step)
            assert response.status_code == 200, response.content
        pending_order.refresh_from_db()
        assert pending_order.status == Order.Status.COMPLETED

    def test_forward_skip_is_allowed(self, client, pending_order):
        # The POS flow is pending → preparing → ready; confirmed is skipped
        # entirely, so any forward move (not just +1) is legal.
        response = self._advance(client, pending_order.pk, "ready")
        assert response.status_code == 200
        pending_order.refresh_from_db()
        assert pending_order.status == Order.Status.READY

    def test_backward_move_is_rejected(self, client, pending_order):
        for step in ("preparing", "ready"):
            self._advance(client, pending_order.pk, step)
        response = self._advance(client, pending_order.pk, "pending")
        assert response.status_code == 409
        pending_order.refresh_from_db()
        assert pending_order.status == Order.Status.READY

    def test_terminal_completed_cannot_move(self, client, pending_order):
        for step in ("preparing", "ready", "completed"):
            self._advance(client, pending_order.pk, step)
        response = self._advance(client, pending_order.pk, "cancelled")
        assert response.status_code == 409
        pending_order.refresh_from_db()
        assert pending_order.status == Order.Status.COMPLETED

    def test_open_order_can_be_cancelled(self, client, pending_order):
        response = self._advance(client, pending_order.pk, "cancelled")
        assert response.status_code == 200
        pending_order.refresh_from_db()
        assert pending_order.status == Order.Status.CANCELLED

    def test_invalid_status_is_rejected(self, client, pending_order):
        response = self._advance(client, pending_order.pk, "shipped")
        assert response.status_code == 400

    def test_unknown_order_returns_404(self, client):
        response = self._advance(client, 999999, "preparing")
        assert response.status_code == 404

    def test_get_is_not_allowed(self, client, pending_order):
        response = client.get(f"/api/orders/{pending_order.pk}/status/")
        assert response.status_code == 405


class TestFusionEditorialApi:
    """GET /fusion/editorial/ — the storefront's editorial content payload.

    Pins the settings-driven contract: craft panels + testimonials served
    from SHOP_EDITORIAL so the Astro page never hardcodes placeholder
    imagery (picsum was removed from the storefront in favour of this
    endpoint).
    """

    def test_serves_craft_and_voices(self, client):
        response = client.get("/fusion/editorial/")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload["craft"]) == 3
        assert len(payload["voices"]) == 3
        for panel in payload["craft"]:
            assert panel["img"].startswith("https://")
            assert panel["alt"]
        for voice in payload["voices"]:
            assert voice["img"].startswith("https://")
            assert voice["name"]

    def test_no_placeholder_imagery(self, client):
        """The payload must never carry picsum/placeholder image URLs."""
        response = client.get("/fusion/editorial/")
        payload = response.json()
        all_urls = [p["img"] for p in payload["craft"]] + [v["img"] for v in payload["voices"]]
        assert all("picsum" not in u for u in all_urls)

    def test_craft_titles(self, client):
        response = client.get("/fusion/editorial/")
        titles = [p["title"] for p in response.json()["craft"]]
        assert titles == ["The roast", "The kitchen", "The pickup"]

    def test_db_settings_override_settings_payload(self, client):
        """Edits in the Wagtail EditorialSettings replace the settings seed."""
        from cms.models import EditorialSettings
        from wagtail.models import Site

        site = Site.objects.get(is_default_site=True)
        EditorialSettings.objects.filter(site=site).delete()
        EditorialSettings.objects.create(
            site=site,
            craft=[
                {
                    "type": "panel",
                    "value": {
                        "title": "The espresso bar",
                        "caption": "Since 2019",
                        "body": "A two-group La Marzocco and a lot of patience.",
                        "img": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=80",
                        "alt": "Espresso machine pouring a shot",
                    },
                    "id": "panel-1",
                }
            ],
            voices=[
                {
                    "type": "voice",
                    "value": {
                        "name": "Noor Al-Rashid",
                        "role": "Opening shift",
                        "quote": "The first pull of the day is always the best one.",
                        "img": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
                    },
                    "id": "voice-1",
                }
            ],
        )
        response = client.get("/fusion/editorial/")
        payload = response.json()
        assert [p["title"] for p in payload["craft"]] == ["The espresso bar"]
        assert payload["voices"][0]["name"] == "Noor Al-Rashid"

    def test_empty_db_falls_back_to_settings(self, client):
        """Cleared streams fall back to the SHOP_EDITORIAL settings seed."""
        from cms.models import EditorialSettings
        from wagtail.models import Site

        EditorialSettings.objects.filter(site=Site.objects.get(is_default_site=True)).update(
            craft=[], voices=[]
        )
        response = client.get("/fusion/editorial/")
        payload = response.json()
        assert len(payload["craft"]) == 3
        assert len(payload["voices"]) == 3
