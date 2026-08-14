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

from shop.models import Order, Product

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
