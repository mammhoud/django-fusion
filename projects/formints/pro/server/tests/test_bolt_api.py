"""Tests for the POS Full django-bolt API.

These tests use ``django_bolt.testing.AsyncTestClient``, which routes
requests through the same Rust-backed request handling used in production.
"""

from __future__ import annotations

import os
import sys
import time

import jwt
import pytest

# Ensure a stable API key for the test session before bolt_api is imported.
os.environ.setdefault("POS_FULL_API_KEY", "test-api-key")

# Make the server importable before configuring Django.
_SERVER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SERVER not in sys.path:
    sys.path.insert(0, _SERVER)

# Configure Django as early as possible; bolt_api needs settings at import time.
from django.conf import settings  # noqa: E402

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-bolt-secret-key",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django_bolt",
        ],
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    )
    import django
    django.setup()

from bolt_api import bolt  # noqa: E402

try:
    from django_bolt.testing import AsyncTestClient  # noqa: E402
except ImportError:  # django-bolt < 0.4 removed AsyncTestClient
    AsyncTestClient = None  # type: ignore[assignment]

if AsyncTestClient is None:
    pytest.skip(
        "django-bolt AsyncTestClient not available in installed version "
        "(only sync TestClient) — bolt API tests skipped",
        allow_module_level=True,
    )


def _api_key_headers():
    return {"X-API-Key": "test-api-key"}


@pytest.fixture
def jwt_token():
    token = jwt.encode(
        {
            "sub": "test-device",
            "role": "admin",
            "iat": int(time.time()),
            "exp": int(time.time()) + 300,
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return token


def _jwt_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def bolt_client(bolt_database):
    """Async Django-Bolt test client."""
    async with AsyncTestClient(bolt) as client:
        yield client


@pytest.fixture(scope="session")
def bolt_database(django_bootstrap):
    """Use a shared on-disk test DB so async ORM connections see the tables."""
    import os
    import tempfile
    from django.conf import settings
    from django.db import connection, connections

    fd, path = tempfile.mkstemp(prefix="pos_bolt_test_", suffix=".db")
    os.close(fd)

    settings.DATABASES["default"]["NAME"] = path
    connections.close_all()

    from models.pos import Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee

    # Customer has an FK to ClientCategory (loyalty) — create it first so
    # SQLite FK targets exist when Customer's table is built.
    try:
        from models.loyalty import ClientCategory
        loyalty_models = [ClientCategory]
    except Exception:
        loyalty_models = []

    models_to_create = [
        *loyalty_models,
        Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee,
    ]
    with connection.schema_editor() as schema_editor:
        for model in models_to_create:
            try:
                schema_editor.create_model(model)
            except Exception:
                pass

    yield path

    try:
        os.remove(path)
    except FileNotFoundError:
        pass


@pytest.fixture
def pos_models(bolt_database):
    from models.pos import Category, Product
    from types import SimpleNamespace
    return SimpleNamespace(Category=Category, Product=Product)


@pytest.mark.asyncio
async def test_health_requires_no_auth(bolt_client):
    response = await bolt_client.get("/bolt/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_list_products_requires_auth(bolt_client):
    response = await bolt_client.get("/bolt/products")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_products_with_api_key(bolt_client, pos_models):
    await pos_models.Product.objects.acreate(name="Bolt Test Product", price=12.99, stock_quantity=100)
    response = await bolt_client.get("/bolt/products", headers=_api_key_headers())
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["name"] == "Bolt Test Product" for item in data)


@pytest.mark.asyncio
async def test_list_products_with_jwt(bolt_client, jwt_token, pos_models):
    await pos_models.Product.objects.acreate(name="JWT Product", price=5.00, stock_quantity=10)
    response = await bolt_client.get("/bolt/products", headers=_jwt_headers(jwt_token))
    assert response.status_code == 200
    data = response.json()
    assert any(item["name"] == "JWT Product" for item in data)


@pytest.mark.asyncio
async def test_invalid_api_key_is_rejected(bolt_client, pos_models):
    await pos_models.Product.objects.acreate(name="Secret Product", price=9.99, stock_quantity=10)
    response = await bolt_client.get("/bolt/products", headers={"X-API-Key": "wrong"})
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_expired_jwt_is_rejected(bolt_client, pos_models):
    # django-bolt's Rust JWT validation uses a 60-second leeway, so the token
    # must be expired by more than that to be rejected.
    expired_token = jwt.encode(
        {
            "sub": "test-device",
            "role": "admin",
            "iat": int(time.time()) - 100,
            "exp": int(time.time()) - 70,
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    await pos_models.Product.objects.acreate(name="Expired Product", price=9.99, stock_quantity=10)
    response = await bolt_client.get("/bolt/products", headers=_jwt_headers(expired_token))
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_auth_token_endpoint(bolt_client):
    response = await bolt_client.post(
        "/bolt/auth/token",
        json={"device_id": "test-device", "role": "manager", "ttl": 600},
    )
    print("TOKEN RESPONSE", response.status_code, response.text)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["role"] == "manager"
    assert data["expires_in"] == 600

    # Verify the issued token works against a protected endpoint.
    token = data["token"]
    response = await bolt_client.get("/bolt/products", headers=_jwt_headers(token))
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_and_retrieve_product(bolt_client, pos_models):
    category = await pos_models.Category.objects.acreate(name="Beverages", slug="beverages")
    response = await bolt_client.post(
        "/bolt/products",
        json={
            "name": "Latte",
            "price": 4.50,
            "category_id": category.id,
            "sku": "LAT-001",
            "stock_quantity": 100,
        },
        headers=_api_key_headers(),
    )
    assert response.status_code == 200
    created = response.json()
    assert created["name"] == "Latte"
    assert created["price"] == "4.50"
    assert created["category_id"] == category.id

    response = await bolt_client.get(
        f"/bolt/products/{created['id']}",
        headers=_api_key_headers(),
    )
    assert response.status_code == 200
    retrieved = response.json()
    assert retrieved["name"] == "Latte"


@pytest.mark.asyncio
async def test_update_and_delete_product(bolt_client, pos_models):
    product = await pos_models.Product.objects.acreate(name="Old Name", price=1.00, stock_quantity=10)
    response = await bolt_client.patch(
        f"/bolt/products/{product.id}",
        json={"name": "New Name", "price": 2.00},
        headers=_api_key_headers(),
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "New Name"
    assert updated["price"] == "2.00"

    response = await bolt_client.delete(
        f"/bolt/products/{product.id}",
        headers=_api_key_headers(),
    )
    assert response.status_code == 204

    response = await bolt_client.get(
        f"/bolt/products/{product.id}",
        headers=_api_key_headers(),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_category_and_list(bolt_client):
    response = await bolt_client.post(
        "/bolt/categories",
        json={"name": "Pastries"},
        headers=_api_key_headers(),
    )
    assert response.status_code == 200
    created = response.json()
    assert created["name"] == "Pastries"
    assert created["slug"].startswith("pastries")

    response = await bolt_client.get("/bolt/categories", headers=_api_key_headers())
    assert response.status_code == 200
    data = response.json()
    assert any(item["name"] == "Pastries" for item in data)


@pytest.mark.asyncio
async def test_create_customer_and_employee(bolt_client):
    response = await bolt_client.post(
        "/bolt/customers",
        json={"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com"},
        headers=_api_key_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Alice"
    assert data["email"] == "alice@example.com"

    response = await bolt_client.post(
        "/bolt/employees",
        json={"first_name": "Bob", "last_name": "Jones", "role": "manager"},
        headers=_api_key_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Bob"
    assert data["role"] == "manager"
