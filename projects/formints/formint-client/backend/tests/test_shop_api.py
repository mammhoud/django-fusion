"""Shop API + fragment contract tests — catalog JSON, auth status, cart
count fragment, and the My Orders HTMX fragment (D1 + D5 in 05-pos-client.md).

These lock the storefront-facing contracts with the Django test client so the
Astro frontend never regresses: the catalog always returns available products,
auth status reports the session, and the fragments honour the HTMX-only rule
(non-HTMX requests get a 406 rather than HTML).
"""

from decimal import Decimal

import pytest

from shop.models import Cart, Category, Order, Product

pytestmark = pytest.mark.django_db


@pytest.fixture
def category():
    return Category.objects.create(name="Coffee", slug="coffee")


@pytest.fixture
def product(category):
    return Product.objects.create(
        category=category,
        name="Latte",
        slug="latte",
        price=Decimal("4.50"),
        description="Espresso + steamed milk",
    )


class TestCatalogApi:
    def test_catalog_api_returns_products(self, client, product):
        resp = client.get("/api/catalog/")
        assert resp.status_code == 200
        assert resp["Content-Type"].startswith("application/json")
        payload = resp.json()
        names = [p["name"] for p in payload["products"]]
        assert "Latte" in names

    def test_catalog_api_shape(self, client, product, category):
        payload = client.get("/api/catalog/").json()
        assert payload["shop"]["name"]
        cats = [c["slug"] for c in payload["categories"]]
        assert "coffee" in cats
        item = next(p for p in payload["products"] if p["name"] == "Latte")
        assert item["price"] == "4.50"  # decimal-safe string
        assert item["category"] == "coffee"

    def test_catalog_api_excludes_unavailable(self, client, product):
        product.is_available = False
        product.save(update_fields=["is_available"])
        names = [p["name"] for p in client.get("/api/catalog/").json()["products"]]
        assert "Latte" not in names

    def test_catalog_api_empty_shop(self, client):
        resp = client.get("/api/catalog/")
        assert resp.status_code == 200
        assert resp.json()["products"] == []


class TestAuthStatusApi:
    def test_auth_status_anonymous(self, client):
        resp = client.get("/apis/auth/status/")
        assert resp.status_code == 200
        assert resp.json() == {"authenticated": False, "user": None}


class TestCartCountFragment:
    def test_cart_count_requires_htmx(self, client):
        # A plain (non-HTMX) GET must not serve the fragment as a full page.
        resp = client.get("/shop/fragments/cart/count/")
        assert resp.status_code == 406

    def test_cart_count_fragment_renders(self, client, product):
        cart = Cart.objects.create(session_key="cart-count-test")
        cart.items.create(product=product, quantity=2, unit_price=product.price)
        from shop.services import CART_SESSION_KEY

        session = client.session
        session[CART_SESSION_KEY] = cart.pk
        session.save()
        resp = client.get(
            "/shop/fragments/cart/count/",
            HTTP_HX_REQUEST="true",
        )
        assert resp.status_code == 200
        assert b"2" in resp.content


class TestMyOrdersFragment:
    def test_my_orders_fragment_requires_htmx(self, client):
        resp = client.get("/shop/fragments/my-orders/")
        assert resp.status_code == 406

    def test_my_orders_fragment_anonymous_renders_empty(self, client):
        resp = client.get(
            "/shop/fragments/my-orders/",
            HTTP_HX_REQUEST="true",
        )
        assert resp.status_code == 200
        assert b"appear here" in resp.content
