"""POS Full — high-performance django-bolt API.

This module provides a BoltAPI instance with core REST endpoints for the
POS Full sidecar (products, categories, customers, sales, inventory,
employees) and dual authentication via JWT and X-API-Key.

Mount it in Django URLs with::

    from bolt_api import bolt
    urlpatterns = [path("bolt/", bolt.urls)]

The API coexists with the existing Robyn sidecar. It is served through
django-bolt's Rust-backed request handling.
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from decimal import Decimal

import jwt
import msgspec
from django.conf import settings
from django.utils.text import slugify

from django_bolt import BoltAPI, Request
from django_bolt.auth import (
    AllowAny,
    IsAuthenticated,
    APIKeyAuthentication,
    JWTAuthentication,
)
from django_bolt.exceptions import BadRequest, NotFound
from django_bolt.openapi import OpenAPIConfig
from msgspec.structs import asdict

from models.pos import (
    Category,
    Customer,
    Employee,
    InventoryTransaction,
    Product,
    Sale,
)

# ---------------------------------------------------------------------------
# Authentication setup
# ---------------------------------------------------------------------------


def _load_api_key() -> str | None:
    """Load the configured API key from the environment."""
    env_key = os.environ.get("POS_FULL_API_KEY", "")
    return env_key or None


_API_KEY = _load_api_key()

_api_key_auth = APIKeyAuthentication(
    api_keys={_API_KEY} if _API_KEY else set(),
    header="X-API-Key",
) if _API_KEY else None

_jwt_auth = JWTAuthentication(secret=settings.SECRET_KEY)

_AUTH_BACKENDS = [backend for backend in [_api_key_auth, _jwt_auth] if backend is not None]

# ---------------------------------------------------------------------------
# Bolt API instance
# ---------------------------------------------------------------------------

bolt = BoltAPI(
    prefix="/bolt",
    namespace="pos-bolt",
    openapi_config=OpenAPIConfig(
        title="POS Full Edition API",
        version="1.0.0",
        path="/bolt/docs",
    ),
)

# ---------------------------------------------------------------------------
# Pydantic request schemas
# ---------------------------------------------------------------------------


class CategoryCreate(msgspec.Struct, kw_only=True):
    name: str
    slug: str | None = None
    description: str = ""
    display_order: int = 0
    is_active: bool = True


class CategoryUpdate(msgspec.Struct, kw_only=True):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    display_order: int | None = None
    is_active: bool | None = None


class ProductCreate(msgspec.Struct, kw_only=True):
    name: str
    price: float
    category_id: int | None = None
    sku: str | None = None
    stock_quantity: int = 0
    is_active: bool = True


class ProductUpdate(msgspec.Struct, kw_only=True):
    name: str | None = None
    price: float | None = None
    category_id: int | None = None
    sku: str | None = None
    stock_quantity: int | None = None
    is_active: bool | None = None


class CustomerCreate(msgspec.Struct, kw_only=True):
    first_name: str
    last_name: str = ""
    email: str | None = None
    phone: str | None = None
    loyalty_points: int = 0
    is_active: bool = True


class CustomerUpdate(msgspec.Struct, kw_only=True):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    loyalty_points: int | None = None
    is_active: bool | None = None


class SaleCreate(msgspec.Struct, kw_only=True):
    customer_id: int | None = None
    subtotal: float
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    total: float
    payment_method: str = "cash"
    status: str = "completed"
    notes: str = ""


class SaleUpdate(msgspec.Struct, kw_only=True):
    customer_id: int | None = None
    subtotal: float | None = None
    tax_amount: float | None = None
    discount_amount: float | None = None
    total: float | None = None
    payment_method: str | None = None
    status: str | None = None
    notes: str | None = None


class InventoryCreate(msgspec.Struct, kw_only=True):
    product_id: int
    transaction_type: str
    quantity: int
    reference: str = ""
    notes: str = ""
    inventory_id: str = "main"


class InventoryUpdate(msgspec.Struct, kw_only=True):
    product_id: int | None = None
    transaction_type: str | None = None
    quantity: int | None = None
    reference: str | None = None
    notes: str | None = None
    inventory_id: str | None = None


class EmployeeCreate(msgspec.Struct, kw_only=True):
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    role: str = "cashier"
    pin_code: str = ""
    is_active: bool = True
    hourly_rate: float = 0.0


class EmployeeUpdate(msgspec.Struct, kw_only=True):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    role: str | None = None
    pin_code: str | None = None
    is_active: bool | None = None
    hourly_rate: float | None = None


# ---------------------------------------------------------------------------
# msgspec response schemas
# ---------------------------------------------------------------------------


class CategoryResponse(msgspec.Struct, kw_only=True):
    id: int
    name: str
    slug: str
    description: str
    display_order: int
    is_active: bool
    created_at: str
    updated_at: str


class ProductResponse(msgspec.Struct, kw_only=True):
    id: int
    name: str
    sku: str | None
    price: str
    stock_quantity: int
    is_active: bool
    category_id: int | None
    created_at: str
    updated_at: str


class CustomerResponse(msgspec.Struct, kw_only=True):
    id: int
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    loyalty_points: int
    total_spent: str
    is_active: bool
    created_at: str
    updated_at: str


class SaleResponse(msgspec.Struct, kw_only=True):
    id: int
    customer_id: int | None
    sale_date: str
    subtotal: str
    tax_amount: str
    discount_amount: str
    total: str
    payment_method: str
    status: str
    notes: str
    created_at: str
    updated_at: str


class InventoryResponse(msgspec.Struct, kw_only=True):
    id: int
    product_id: int
    transaction_type: str
    quantity: int
    reference: str
    notes: str
    inventory_id: str
    created_at: str


class EmployeeResponse(msgspec.Struct, kw_only=True):
    id: int
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    role: str
    pin_code: str
    is_active: bool
    hourly_rate: str
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------


def _format_dt(value: datetime | None) -> str:
    return value.isoformat() if value else ""


def _to_str(value: Decimal | float | None) -> str:
    if value is None:
        return ""
    return f"{value:.2f}"


def _struct_updates(body: msgspec.Struct) -> dict[str, Any]:
    """Convert a request struct to a dict, skipping unset (None) values."""
    return {k: v for k, v in asdict(body).items() if v is not None}


async def _resolve_category(category_id: int | None) -> Category | None:
    if category_id is None:
        return None
    try:
        return await Category.objects.aget(id=category_id)
    except Category.DoesNotExist as exc:
        raise BadRequest(f"Category {category_id} not found") from exc


async def _resolve_customer(customer_id: int | None) -> Customer | None:
    if customer_id is None:
        return None
    try:
        return await Customer.objects.aget(id=customer_id)
    except Customer.DoesNotExist as exc:
        raise BadRequest(f"Customer {customer_id} not found") from exc


async def _resolve_product(product_id: int) -> Product:
    try:
        return await Product.objects.aget(id=product_id)
    except Product.DoesNotExist as exc:
        raise BadRequest(f"Product {product_id} not found") from exc


# ---------------------------------------------------------------------------
# Public health endpoint
# ---------------------------------------------------------------------------

@bolt.get("/health", guards=[AllowAny()], auth=[])
async def health(request: Request) -> dict:
    """Public health check."""
    return {"status": "ok", "service": "pos-full-bolt"}


class TokenCreate(msgspec.Struct, kw_only=True):
    device_id: str
    role: str = "viewer"
    ttl: int = 3600


@bolt.post("/auth/token", guards=[AllowAny()], auth=[])
async def create_token(request: Request, body: TokenCreate) -> dict:
    """Issue a JWT for use with bolt endpoints."""
    now = int(time.time())
    token = jwt.encode(
        {
            "sub": body.device_id,
            "role": body.role,
            "iat": now,
            "exp": now + body.ttl,
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return {"token": token, "role": body.role, "expires_in": body.ttl}


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@bolt.get("/categories", response_model=list[CategoryResponse], guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def list_categories(request: Request) -> list[CategoryResponse]:
    return [
        _category_response(category)
        async for category in Category.objects.filter(is_active=True).order_by("display_order", "name")
    ]


@bolt.get("/categories/{category_id}", response_model=CategoryResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def get_category(request: Request, category_id: int) -> CategoryResponse:
    try:
        category = await Category.objects.aget(id=category_id)
    except Category.DoesNotExist:
        raise NotFound(f"Category {category_id} not found")
    return _category_response(category)


@bolt.post("/categories", response_model=CategoryResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def create_category(request: Request, body: CategoryCreate) -> CategoryResponse:
    slug = body.slug or slugify(body.name)
    category = await Category.objects.acreate(
        name=body.name,
        slug=slug,
        description=body.description,
        display_order=body.display_order,
        is_active=body.is_active,
    )
    return _category_response(category)


@bolt.patch("/categories/{category_id}", response_model=CategoryResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def update_category(request: Request, category_id: int, body: CategoryUpdate) -> CategoryResponse:
    try:
        category = await Category.objects.aget(id=category_id)
    except Category.DoesNotExist:
        raise NotFound(f"Category {category_id} not found")
    updates = _struct_updates(body)
    updates.pop("id", None)
    if "slug" in updates and not updates["slug"]:
        updates["slug"] = slugify(updates.get("name", category.name))
    for key, value in updates.items():
        if value is not None:
            setattr(category, key, value)
    await category.asave()
    return _category_response(category)


@bolt.delete("/categories/{category_id}", status_code=204, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def delete_category(request: Request, category_id: int) -> None:
    try:
        category = await Category.objects.aget(id=category_id)
    except Category.DoesNotExist:
        raise NotFound(f"Category {category_id} not found")
    await category.adelete()


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@bolt.get("/products", response_model=list[ProductResponse], guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def list_products(request: Request) -> list[ProductResponse]:
    return [
        _product_response(product)
        async for product in Product.objects.filter(is_active=True).select_related("category").order_by("name")
    ]


@bolt.get("/products/{product_id}", response_model=ProductResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def get_product(request: Request, product_id: int) -> ProductResponse:
    try:
        product = await Product.objects.aget(id=product_id)
    except Product.DoesNotExist:
        raise NotFound(f"Product {product_id} not found")
    return _product_response(product)


@bolt.post("/products", response_model=ProductResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def create_product(request: Request, body: ProductCreate) -> ProductResponse:
    category = await _resolve_category(body.category_id)
    product = await Product.objects.acreate(
        name=body.name,
        price=body.price,
        category=category,
        sku=body.sku,
        stock_quantity=body.stock_quantity,
        is_active=body.is_active,
    )
    return _product_response(product)


@bolt.patch("/products/{product_id}", response_model=ProductResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def update_product(request: Request, product_id: int, body: ProductUpdate) -> ProductResponse:
    try:
        product = await Product.objects.aget(id=product_id)
    except Product.DoesNotExist:
        raise NotFound(f"Product {product_id} not found")
    updates = _struct_updates(body)
    updates.pop("id", None)
    if "category_id" in updates:
        category_id = updates.pop("category_id")
        product.category = await _resolve_category(category_id)
    for key, value in updates.items():
        if value is not None:
            setattr(product, key, value)
    await product.asave()
    return _product_response(product)


@bolt.delete("/products/{product_id}", status_code=204, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def delete_product(request: Request, product_id: int) -> None:
    try:
        product = await Product.objects.aget(id=product_id)
    except Product.DoesNotExist:
        raise NotFound(f"Product {product_id} not found")
    await product.adelete()


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

@bolt.get("/customers", response_model=list[CustomerResponse], guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def list_customers(request: Request) -> list[CustomerResponse]:
    return [
        _customer_response(customer)
        async for customer in Customer.objects.filter(is_active=True).order_by("-created_at")
    ]


@bolt.get("/customers/{customer_id}", response_model=CustomerResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def get_customer(request: Request, customer_id: int) -> CustomerResponse:
    try:
        customer = await Customer.objects.aget(id=customer_id)
    except Customer.DoesNotExist:
        raise NotFound(f"Customer {customer_id} not found")
    return _customer_response(customer)


@bolt.post("/customers", response_model=CustomerResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def create_customer(request: Request, body: CustomerCreate) -> CustomerResponse:
    customer = await Customer.objects.acreate(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone or "",
        loyalty_points=body.loyalty_points,
        is_active=body.is_active,
    )
    return _customer_response(customer)


@bolt.patch("/customers/{customer_id}", response_model=CustomerResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def update_customer(request: Request, customer_id: int, body: CustomerUpdate) -> CustomerResponse:
    try:
        customer = await Customer.objects.aget(id=customer_id)
    except Customer.DoesNotExist:
        raise NotFound(f"Customer {customer_id} not found")
    updates = _struct_updates(body)
    updates.pop("id", None)
    for key, value in updates.items():
        if value is not None:
            setattr(customer, key, value)
    await customer.asave()
    return _customer_response(customer)


@bolt.delete("/customers/{customer_id}", status_code=204, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def delete_customer(request: Request, customer_id: int) -> None:
    try:
        customer = await Customer.objects.aget(id=customer_id)
    except Customer.DoesNotExist:
        raise NotFound(f"Customer {customer_id} not found")
    await customer.adelete()


# ---------------------------------------------------------------------------
# Sales
# ---------------------------------------------------------------------------

@bolt.get("/sales", response_model=list[SaleResponse], guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def list_sales(request: Request) -> list[SaleResponse]:
    return [
        _sale_response(sale)
        async for sale in Sale.objects.order_by("-sale_date")
    ]


@bolt.get("/sales/{sale_id}", response_model=SaleResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def get_sale(request: Request, sale_id: int) -> SaleResponse:
    try:
        sale = await Sale.objects.aget(id=sale_id)
    except Sale.DoesNotExist:
        raise NotFound(f"Sale {sale_id} not found")
    return _sale_response(sale)


@bolt.post("/sales", response_model=SaleResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def create_sale(request: Request, body: SaleCreate) -> SaleResponse:
    customer = await _resolve_customer(body.customer_id)
    sale = await Sale.objects.acreate(
        customer=customer,
        subtotal=body.subtotal,
        tax_amount=body.tax_amount,
        discount_amount=body.discount_amount,
        total=body.total,
        payment_method=body.payment_method,
        status=body.status,
        notes=body.notes,
    )
    return _sale_response(sale)


@bolt.patch("/sales/{sale_id}", response_model=SaleResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def update_sale(request: Request, sale_id: int, body: SaleUpdate) -> SaleResponse:
    try:
        sale = await Sale.objects.aget(id=sale_id)
    except Sale.DoesNotExist:
        raise NotFound(f"Sale {sale_id} not found")
    updates = _struct_updates(body)
    updates.pop("id", None)
    if "customer_id" in updates:
        customer_id = updates.pop("customer_id")
        sale.customer = await _resolve_customer(customer_id)
    for key, value in updates.items():
        if value is not None:
            setattr(sale, key, value)
    await sale.asave()
    return _sale_response(sale)


@bolt.delete("/sales/{sale_id}", status_code=204, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def delete_sale(request: Request, sale_id: int) -> None:
    try:
        sale = await Sale.objects.aget(id=sale_id)
    except Sale.DoesNotExist:
        raise NotFound(f"Sale {sale_id} not found")
    await sale.adelete()


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

@bolt.get("/inventory", response_model=list[InventoryResponse], guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def list_inventory(request: Request) -> list[InventoryResponse]:
    return [
        _inventory_response(tx)
        async for tx in InventoryTransaction.objects.order_by("-created_at")
    ]


@bolt.get("/inventory/{transaction_id}", response_model=InventoryResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def get_inventory_transaction(request: Request, transaction_id: int) -> InventoryResponse:
    try:
        tx = await InventoryTransaction.objects.aget(id=transaction_id)
    except InventoryTransaction.DoesNotExist:
        raise NotFound(f"Inventory transaction {transaction_id} not found")
    return _inventory_response(tx)


@bolt.post("/inventory", response_model=InventoryResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def create_inventory_transaction(request: Request, body: InventoryCreate) -> InventoryResponse:
    product = await _resolve_product(body.product_id)
    tx = await InventoryTransaction.objects.acreate(
        product=product,
        transaction_type=body.transaction_type,
        quantity=body.quantity,
        reference=body.reference,
        notes=body.notes,
        inventory_id=body.inventory_id,
    )
    return _inventory_response(tx)


@bolt.patch("/inventory/{transaction_id}", response_model=InventoryResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def update_inventory_transaction(request: Request, transaction_id: int, body: InventoryUpdate) -> InventoryResponse:
    try:
        tx = await InventoryTransaction.objects.aget(id=transaction_id)
    except InventoryTransaction.DoesNotExist:
        raise NotFound(f"Inventory transaction {transaction_id} not found")
    updates = _struct_updates(body)
    updates.pop("id", None)
    if "product_id" in updates:
        product_id = updates.pop("product_id")
        tx.product = await _resolve_product(product_id)
    for key, value in updates.items():
        if value is not None:
            setattr(tx, key, value)
    await tx.asave()
    return _inventory_response(tx)


@bolt.delete("/inventory/{transaction_id}", status_code=204, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def delete_inventory_transaction(request: Request, transaction_id: int) -> None:
    try:
        tx = await InventoryTransaction.objects.aget(id=transaction_id)
    except InventoryTransaction.DoesNotExist:
        raise NotFound(f"Inventory transaction {transaction_id} not found")
    await tx.adelete()


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------

@bolt.get("/employees", response_model=list[EmployeeResponse], guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def list_employees(request: Request) -> list[EmployeeResponse]:
    return [
        _employee_response(employee)
        async for employee in Employee.objects.filter(is_active=True).order_by("last_name", "first_name")
    ]


@bolt.get("/employees/{employee_id}", response_model=EmployeeResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def get_employee(request: Request, employee_id: int) -> EmployeeResponse:
    try:
        employee = await Employee.objects.aget(id=employee_id)
    except Employee.DoesNotExist:
        raise NotFound(f"Employee {employee_id} not found")
    return _employee_response(employee)


@bolt.post("/employees", response_model=EmployeeResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def create_employee(request: Request, body: EmployeeCreate) -> EmployeeResponse:
    employee = await Employee.objects.acreate(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone or "",
        role=body.role,
        pin_code=body.pin_code or "",
        is_active=body.is_active,
        hourly_rate=body.hourly_rate,
    )
    return _employee_response(employee)


@bolt.patch("/employees/{employee_id}", response_model=EmployeeResponse, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def update_employee(request: Request, employee_id: int, body: EmployeeUpdate) -> EmployeeResponse:
    try:
        employee = await Employee.objects.aget(id=employee_id)
    except Employee.DoesNotExist:
        raise NotFound(f"Employee {employee_id} not found")
    updates = _struct_updates(body)
    updates.pop("id", None)
    for key, value in updates.items():
        if value is not None:
            setattr(employee, key, value)
    await employee.asave()
    return _employee_response(employee)


@bolt.delete("/employees/{employee_id}", status_code=204, guards=[IsAuthenticated()], auth=_AUTH_BACKENDS)
async def delete_employee(request: Request, employee_id: int) -> None:
    try:
        employee = await Employee.objects.aget(id=employee_id)
    except Employee.DoesNotExist:
        raise NotFound(f"Employee {employee_id} not found")
    await employee.adelete()


# ---------------------------------------------------------------------------
# Response helpers (kept at the bottom to avoid forward references)
# ---------------------------------------------------------------------------


def _category_response(category: Category) -> CategoryResponse:
    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        display_order=category.display_order,
        is_active=category.is_active,
        created_at=_format_dt(category.created_at),
        updated_at=_format_dt(category.updated_at),
    )


def _product_response(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        name=product.name,
        sku=product.sku,
        price=_to_str(product.price),
        stock_quantity=product.stock_quantity,
        is_active=product.is_active,
        category_id=product.category_id,
        created_at=_format_dt(product.created_at),
        updated_at=_format_dt(product.updated_at),
    )


def _customer_response(customer: Customer) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        phone=customer.phone,
        loyalty_points=customer.loyalty_points,
        total_spent=_to_str(customer.total_spent),
        is_active=customer.is_active,
        created_at=_format_dt(customer.created_at),
        updated_at=_format_dt(customer.updated_at),
    )


def _sale_response(sale: Sale) -> SaleResponse:
    return SaleResponse(
        id=sale.id,
        customer_id=sale.customer_id,
        sale_date=_format_dt(sale.sale_date),
        subtotal=_to_str(sale.subtotal),
        tax_amount=_to_str(sale.tax_amount),
        discount_amount=_to_str(sale.discount_amount),
        total=_to_str(sale.total),
        payment_method=sale.payment_method,
        status=sale.status,
        notes=sale.notes,
        created_at=_format_dt(sale.created_at),
        updated_at=_format_dt(sale.updated_at),
    )


def _inventory_response(tx: InventoryTransaction) -> InventoryResponse:
    return InventoryResponse(
        id=tx.id,
        product_id=tx.product_id,
        transaction_type=tx.transaction_type,
        quantity=tx.quantity,
        reference=tx.reference,
        notes=tx.notes,
        inventory_id=tx.inventory_id,
        created_at=_format_dt(tx.created_at),
    )


def _employee_response(employee: Employee) -> EmployeeResponse:
    return EmployeeResponse(
        id=employee.id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        phone=employee.phone,
        role=employee.role,
        pin_code=employee.pin_code,
        is_active=employee.is_active,
        hourly_rate=_to_str(employee.hourly_rate),
        created_at=_format_dt(employee.created_at),
        updated_at=_format_dt(employee.updated_at),
    )
