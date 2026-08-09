# Standard Edition — Design, Architecture & Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the Standard tier (gated inside `formint/sidecar/`) by shipping multi-currency, tax profiles, custom roles & permissions enforcement, and CSV/JSON data export, with design, architecture, and data model documented as an extension of Community.

**Architecture:** Standard shares the Pro codebase (`formint/`) and is gated by configuration. It is a full Django setup (Ninja + ninja-extra controllers, django-fusion, Unfold admin) over the 48-model `pos_full` schema. This plan adds two models (`Currency`, `TaxProfile`), a permission helper, and export views — all following the existing model-discovery, controller-registration, and URL-wiring conventions.

**Tech Stack:** Python (Django 5.2, ninja-extra, django-fusion), pytest. No new third-party dependencies (stdlib `csv` only).

## Global Constraints

- All changes live under `projects/formints/formint/sidecar/` only.
- **No new third-party dependencies.** Django stdlib (`csv`, `json`) and existing packages only.
- Model conventions (copy verbatim): `app_label = "pos_full"`, `db_table = "full_<name>"`, sync fields `is_synced` / `synced_at` / `sync_status` (choices `pending|synced|failed`), audit fields `created_at` / `updated_at`.
- New models are discovered via `models/models.py` imports and exposed via the `ALL_CONTROLLERS` list in `formint/controllers.py`.
- Migrations: `python manage.py makemigrations pos_full` then `make migrate` (from `formint/sidecar/`).
- Test command: `cd projects/formints/formint/sidecar && make test` (runs `pytest tests/ -q -k "not rust_db"`).
- Ports unchanged: backend 8767, bolt 8766, frontend 4321. No Robyn.
- **Feature inheritance (hard):** Standard MUST include every Community feature (`01-community.md`) PLUS its own additions. The parity sweep in Task B8 verifies inheritance and fixes any gap.

---

## Design

**Audience:** a branch with several terminals that must price, tax, and role-govern sales differently from the base Community tier.

**Multi-currency.** A `Currency` catalogue (ISO-4217 code, name, symbol, cross-rate to the default currency). Exactly one currency is `is_default` at any time. Sales can record their currency; the sale screen picks from active currencies.

**Tax profiles.** Named tax rates (`Standard` 15%, `Reduced` 7%, `Zero-rated` 0%). Products and sales may carry a `tax_profile`; the `compute_tax(subtotal, rate)` helper rounds to cents with `ROUND_HALF_UP`. This replaces the fixed `tax_rate` charfield semantics with a first-class, admin-manageable profile.

**Custom roles & permissions.** The `Role` model already exists with a JSON `permissions` dict; the gap is **enforcement**. This plan adds `resolve_permissions(user, role)` (superusers get all keys; otherwise truthy JSON flags) and a `require_permission("key")` decorator, applied to the new `CurrencyController` writes as the reference enforcement point. Admin already manages roles.

**Data export.** Four GET endpoints (`/export/products.csv`, `/export/sales.csv`, `/export/customers.csv`, `/export/inventory.csv`) return streaming CSV; `?format=json` returns `{count, items}`. Exports are read-only, ordered, and stable.

**Copy register:** admin-facing labels stay concrete ("Standard", "Reduced"); endpoints are plain resource names.

## Architecture

```
Django (formint/sidecar, pos_full app)
├── models/money.py          # Currency, TaxProfile (new)
├── models/pos.py            # Product.tax_profile, Sale.tax_profile FK (new)
├── models/models.py         # discovery imports (new)
├── formint/controllers.py   # CurrencyController, TaxProfileController + ALL_CONTROLLERS
├── formint/tax.py           # compute_tax helper (new)
├── formint/permissions.py   # resolve_permissions + require_permission (new)
├── formint/export.py        # export_* views (new)
├── configs/urls.py          # /export/* routes (new)
└── admin.py                 # Currency, TaxProfile registration
```

Data flow: React/Astro frontend → `/api/v1/currencies` (Ninja controller, permission-gated writes) · sale totals via `compute_tax` · export via plain Django views streaming CSV.

## Data model (extension of Community)

Community contributes the domain concepts (sales, products, customers) in Diesel. Standard re-expresses them as Django `full_*` tables and **extends** with sync + money + tax:

| New entity | Table | Extends concept | Key columns |
|-----------|-------|-----------------|-------------|
| `Currency` | `full_currencies` | multi-currency pricing | `code` (unique), `name`, `symbol`, `exchange_rate`, `is_default`, `is_active` |
| `TaxProfile` | `full_tax_profiles` | product tax semantics | `name` (unique), `rate` (fraction), `is_default`, `is_active` |
| `Product.tax_profile` | FK on `full_products` | product tax linkage | `tax_profile_id` → `TaxProfile` |
| `Sale.tax_profile` | FK on `full_sales` | sale-level tax linkage | `tax_profile_id` → `TaxProfile` |

Existing entities this tier relies on: `Role` (`full_roles`, JSON `permissions`), `Sale` (`full_sales`, `tax_amount`), `Product` (`full_products`).

**Extension delta over Community:** +2 tables, +2 FKs, no changes to existing tables' columns (nullable FKs only).

---

## Task B1: Multi-currency support

**Files:**
- Create: `formint/sidecar/models/money.py`
- Modify: `formint/sidecar/models/models.py`, `formint/sidecar/formint/controllers.py`, `formint/sidecar/admin.py`
- Modify: `formint/sidecar/models/management/commands/seed_demo.py`
- Test: `formint/sidecar/tests/test_currency.py`

**Interfaces:**
- Produces: `Currency` model + `CurrencyController` at `/api/v1/currencies`. Consumed by Task B2 (tax per currency) and the frontend currency picker.

- [ ] **Step 1: Write the failing test**

Create `formint/sidecar/tests/test_currency.py`:

```python
from django.test import TestCase

from models.money import Currency


class CurrencyModelTest(TestCase):
    def test_create_currency(self):
        c = Currency.objects.create(
            code="EUR", name="Euro", symbol="€", exchange_rate="0.92",
        )
        assert str(c) == "EUR (€)"
        assert c.is_active is True

    def test_only_one_default_currency(self):
        Currency.objects.create(code="USD", name="US Dollar", is_default=True)
        c2 = Currency.objects.create(code="EUR", name="Euro")
        c2.is_default = True
        c2.save()
        assert Currency.objects.filter(is_default=True).count() == 1
        assert Currency.objects.get(code="USD").is_default is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_currency.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'models.money'`

- [ ] **Step 3: Write the model**

Create `formint/sidecar/models/money.py`:

```python
"""Money models — multi-currency support (Standard tier)."""

from django.db import models


class Currency(models.Model):
    """ISO-4217 currency with an optional cross-rate to the default currency."""

    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=64)
    symbol = models.CharField(max_length=8, blank=True, default="")
    exchange_rate = models.DecimalField(
        max_digits=12, decimal_places=6, default=1,
        help_text="Rate relative to the default currency (1.0 = base).",
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking (copy existing convention)
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20, default="pending",
        choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")],
    )

    class Meta:
        app_label = "pos_full"
        db_table = "full_currencies"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} ({self.symbol})"

    def save(self, *args, **kwargs):
        # Enforce a single default currency.
        if self.is_default:
            Currency.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
```

- [ ] **Step 4: Register the model**

In `formint/sidecar/models/models.py`, add after the `crm` import:

```python
from models.money import Currency  # noqa: F401 — discovered by Django
```

In `formint/sidecar/formint/controllers.py`: add `Currency` to the `from formint.models import (...)` list; after the `ALL_CONTROLLERS = [` opening (≈line 314) append (mirroring an existing simple controller such as `CategoryController`):

```python
@api_controller("/currencies", tags=["currencies"])
class CurrencyController(ModelControllerBase):
    model_config = ModelConfig(
        model=Currency,
        allowed_routes=["list", "create", "retrieve", "update", "partial_update", "delete"],
    )
```

Then add `CurrencyController,` to `ALL_CONTROLLERS`.

In `formint/sidecar/admin.py`, register `Currency` the same way other models are registered (if explicit; skip if auto-discovered — verify with `make check`).

- [ ] **Step 5: Generate and apply the migration**

Run:
```bash
cd projects/formints/formint/sidecar
python manage.py makemigrations pos_full
make migrate
```
Expected: `models/migrations/0002_currency.py` created and applied.

- [ ] **Step 6: Seed defaults**

In `formint/sidecar/models/management/commands/seed_demo.py`:

```python
from models.money import Currency

if not Currency.objects.exists():
    Currency.objects.create(code="USD", name="US Dollar", symbol="$", is_default=True)
    Currency.objects.create(code="EUR", name="Euro", symbol="€", exchange_rate="0.92")
    Currency.objects.create(code="GBP", name="British Pound", symbol="£", exchange_rate="0.79")
    Currency.objects.create(code="MAD", name="Moroccan Dirham", symbol="DH", exchange_rate="9.90")
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_currency.py -q && make test`
Expected: PASS — new tests green, full suite green

- [ ] **Step 8: Commit**

```bash
git add projects/formints/formint/sidecar/models/money.py projects/formints/formint/sidecar/models/models.py projects/formints/formint/sidecar/formint/controllers.py projects/formints/formint/sidecar/admin.py projects/formints/formint/sidecar/models/migrations/ projects/formints/formint/sidecar/models/management/commands/seed_demo.py projects/formints/formint/sidecar/tests/test_currency.py
git commit -m "feat(sidecar): multi-currency support with single-default enforcement"
```

---

## Task B2: Tax profiles

**Files:**
- Modify: `formint/sidecar/models/money.py`, `formint/sidecar/models/pos.py`, `formint/sidecar/models/models.py`, `formint/sidecar/formint/controllers.py`, `formint/sidecar/admin.py`
- Create: `formint/sidecar/formint/tax.py`
- Test: `formint/sidecar/tests/test_tax_profile.py`

**Interfaces:**
- Produces: `TaxProfile` model + `compute_tax(subtotal: Decimal, rate: Decimal) -> Decimal` in `formint/tax.py`. Consumed by Task B4 (export of tax rates) and the sale flow.

- [ ] **Step 1: Write the failing test**

Create `formint/sidecar/tests/test_tax_profile.py`:

```python
from decimal import Decimal

from django.test import TestCase

from models.money import TaxProfile
from models.pos import Product
from formint.tax import compute_tax


class TaxProfileTest(TestCase):
    def test_compute_tax(self):
        assert compute_tax(Decimal("100.00"), Decimal("0.15")) == Decimal("15.00")
        assert compute_tax(Decimal("99.99"), Decimal("0.00")) == Decimal("0.00")

    def test_default_profile(self):
        TaxProfile.objects.create(name="Standard", rate="0.15", is_default=True)
        TaxProfile.objects.create(name="Reduced", rate="0.07")
        reduced = TaxProfile.objects.get(name="Reduced")
        reduced.is_default = True
        reduced.save()
        assert TaxProfile.objects.filter(is_default=True).count() == 1

    def test_product_can_carry_tax_profile(self):
        profile = TaxProfile.objects.create(name="Standard", rate="0.15", is_default=True)
        product = Product.objects.create(name="Latte", price="4.50", tax_profile=profile)
        assert product.tax_profile.rate == Decimal("0.15")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_tax_profile.py -q`
Expected: FAIL — import errors for `TaxProfile`, `formint.tax`

- [ ] **Step 3: Write the model + helper**

Append to `formint/sidecar/models/money.py`:

```python
class TaxProfile(models.Model):
    """Named tax rate applied to sales (Standard tier). Rate is a fraction."""

    name = models.CharField(max_length=100, unique=True)
    rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0,
        help_text="Tax rate as a fraction, e.g. 0.15 = 15%",
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20, default="pending",
        choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")],
    )

    class Meta:
        app_label = "pos_full"
        db_table = "full_tax_profiles"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({float(self.rate) * 100:.2f}%)"

    def save(self, *args, **kwargs):
        if self.is_default:
            TaxProfile.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
```

Create `formint/sidecar/formint/tax.py`:

```python
"""Tax helpers (Standard tier)."""

from decimal import Decimal, ROUND_HALF_UP


def compute_tax(subtotal: Decimal, rate: Decimal) -> Decimal:
    """Return the tax amount for a subtotal at the given fractional rate."""
    if rate <= 0:
        return Decimal("0.00")
    return (subtotal * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

- [ ] **Step 4: Wire the FK + registrations**

In `formint/sidecar/models/pos.py`:
- `Product` (≈line 38): `tax_profile = models.ForeignKey("pos_full.TaxProfile", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")`
- `Sale` (after `tax_amount`): `tax_profile = models.ForeignKey("pos_full.TaxProfile", on_delete=models.SET_NULL, null=True, blank=True, related_name="sales")`

In `models/models.py`: `from models.money import Currency, TaxProfile  # noqa: F401`

In `formint/controllers.py`: import `TaxProfile`; add `TaxProfileController` mirroring `CurrencyController` (route `/tax-profiles`); append to `ALL_CONTROLLERS`.

In `admin.py`: register `TaxProfile` like `Currency` (Task B1 Step 4).

- [ ] **Step 5: Migrate**

Run:
```bash
cd projects/formints/formint/sidecar
python manage.py makemigrations pos_full
make migrate
```

- [ ] **Step 6: Seed defaults**

In `seed_demo.py`, next to the currency seed:

```python
from models.money import TaxProfile

if not TaxProfile.objects.exists():
    TaxProfile.objects.create(name="Standard", rate="0.15", is_default=True)
    TaxProfile.objects.create(name="Reduced", rate="0.07")
    TaxProfile.objects.create(name="Zero-rated", rate="0")
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_tax_profile.py tests/test_currency.py -q && make test`
Expected: PASS — new tests green, full suite green

- [ ] **Step 8: Commit**

```bash
git add projects/formints/formint/sidecar/models/money.py projects/formints/formint/sidecar/models/pos.py projects/formints/formint/sidecar/models/models.py projects/formints/formint/sidecar/formint/tax.py projects/formints/formint/sidecar/formint/controllers.py projects/formints/formint/sidecar/admin.py projects/formints/formint/sidecar/models/migrations/ projects/formints/formint/sidecar/models/management/commands/seed_demo.py projects/formints/formint/sidecar/tests/test_tax_profile.py
git commit -m "feat(sidecar): tax profiles with product/sale linkage and compute_tax helper"
```

---

## Task B3: Custom roles & permissions enforcement

**Files:**
- Create: `formint/sidecar/formint/permissions.py`
- Modify: `formint/sidecar/formint/controllers.py`
- Test: `formint/sidecar/tests/test_permissions.py`

**Interfaces:**
- Consumes: `models.extra.Role` (exists, JSON `permissions`).
- Produces: `resolve_permissions(user, role=None) -> set[str]` and `require_permission(perm: str)` decorator. Consumed by `CurrencyController` writes (Task B1).

- [ ] **Step 1: Write the failing test**

Create `formint/sidecar/tests/test_permissions.py`:

```python
from django.contrib.auth.models import User
from django.test import TestCase

from models.extra import Role
from formint.permissions import resolve_permissions


class PermissionHelperTest(TestCase):
    def test_superuser_has_all_permissions(self):
        user = User.objects.create_superuser("boss", "boss@example.com", "pw")
        assert "can_manage_products" in resolve_permissions(user)

    def test_role_permissions_are_resolved(self):
        role = Role.objects.create(
            name="Cashier",
            permissions={"can_manage_products": False, "can_issue_refunds": True},
        )
        user = User.objects.create_user("cashier", "cashier@example.com", "pw")
        perms = resolve_permissions(user, role=role)
        assert "can_issue_refunds" in perms
        assert "can_manage_products" not in perms

    def test_plain_user_gets_empty_permissions(self):
        user = User.objects.create_user("guest", "guest@example.com", "pw")
        assert resolve_permissions(user) == set()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_permissions.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'formint.permissions'`

- [ ] **Step 3: Write the helper**

Create `formint/sidecar/formint/permissions.py`:

```python
"""Permission resolution for the Standard tier (custom roles & permissions)."""

from __future__ import annotations

from functools import wraps
from typing import Optional

from ninja_extra import HttpError

from models.extra import Role

# Canonical permission keys (keep in sync with Role.permissions JSON usage).
ALL_PERMISSIONS = {"can_manage_products", "can_issue_refunds", "can_manage_inventory"}


def resolve_permissions(user, role: Optional[Role] = None) -> set[str]:
    """Return the effective permission keys for a user.

    Superusers bypass role checks. A role's JSON ``permissions`` dict lists
    flags; keys whose value is truthy are granted.
    """
    if user.is_superuser:
        return set(ALL_PERMISSIONS)
    if role is None:
        return set()
    return {key for key, granted in (role.permissions or {}).items() if granted}


def require_permission(permission: str):
    """Controller decorator that 403s when the request user lacks a permission."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            perms = resolve_permissions(request.user, role=getattr(request, "role", None))
            if permission not in perms:
                raise HttpError(403, f"Missing permission: {permission}")
            return func(self, request, *args, **kwargs)

        return wrapper

    return decorator
```

- [ ] **Step 4: Gate a write route**

In `formint/sidecar/formint/controllers.py`:

```python
from formint.permissions import require_permission

@api_controller("/currencies", tags=["currencies"])
class CurrencyController(ModelControllerBase):
    model_config = ModelConfig(
        model=Currency,
        allowed_routes=["list", "create", "retrieve", "update", "partial_update", "delete"],
    )

    @require_permission("can_manage_inventory")
    def create(self, request, payload):
        return super().create(request, payload)

    @require_permission("can_manage_inventory")
    def update(self, request, id, payload):
        return super().update(request, id, payload)
```

> Confirm the exact create/update signatures of `ModelControllerBase` (ninja-extra) in this codebase by checking an existing overridden controller method — if the base signatures differ, adapt the wrapper (the decorator contract stays the same).

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_permissions.py -q && make test`
Expected: PASS — helper tests green, full suite green

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formint/sidecar/formint/permissions.py projects/formints/formint/sidecar/formint/controllers.py projects/formints/formint/sidecar/tests/test_permissions.py
git commit -m "feat(sidecar): permission helper and enforcement on currency writes"
```

---

## Task B4: CSV/JSON data export

**Files:**
- Create: `formint/sidecar/formint/export.py`
- Modify: `formint/sidecar/configs/urls.py`
- Test: `formint/sidecar/tests/test_export.py`

**Interfaces:**
- Consumes: `models.pos.{Product, Sale, Customer}`, `models.inventory.InventoryTransaction`.
- Produces: views `export_products`, `export_sales`, `export_customers`, `export_inventory` at `/export/<name>.csv` (+ `?format=json`).

- [ ] **Step 1: Write the failing test**

Create `formint/sidecar/tests/test_export.py`:

```python
import json

from django.test import TestCase
from django.urls import reverse

from models.pos import Product


class ExportTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Product.objects.create(name="Latte", price="4.50", tax_rate="standard")

    def test_products_csv(self):
        resp = self.client.get(reverse("export-products"))
        assert resp.status_code == 200
        assert resp["Content-Type"].startswith("text/csv")
        body = resp.content.decode()
        assert "id,name,price" in body
        assert "Latte" in body

    def test_products_json(self):
        resp = self.client.get(reverse("export-products") + "?format=json")
        assert resp.status_code == 200
        payload = json.loads(resp.content)
        assert payload["count"] == 1
        assert payload["items"][0]["name"] == "Latte"

    def test_sales_csv(self):
        resp = self.client.get(reverse("export-sales"))
        assert resp.status_code == 200
        assert resp["Content-Type"].startswith("text/csv")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_export.py -q`
Expected: FAIL — `django.urls.exceptions.NoReverseMatch` (routes not wired)

- [ ] **Step 3: Write the export views**

Create `formint/sidecar/formint/export.py`:

```python
"""CSV/JSON data export endpoints (Standard capability)."""

from __future__ import annotations

import csv

from django.http import HttpResponse, JsonResponse

from models.pos import Customer, Product, Sale
from models.inventory import InventoryTransaction


def _csv_response(filename: str, header: list[str], rows: list[list]) -> HttpResponse:
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(header)
    writer.writerows(rows)
    return response


def _json_response(items: list[dict]) -> JsonResponse:
    return JsonResponse({"count": len(items), "items": items})


def export_products(request):
    rows = [
        [p.id, p.name, str(p.price), p.tax_rate]
        for p in Product.objects.all().order_by("id")
    ]
    if request.GET.get("format") == "json":
        return _json_response(
            [{"id": r[0], "name": r[1], "price": r[2], "tax_rate": r[3]} for r in rows]
        )
    return _csv_response("products.csv", ["id", "name", "price", "tax_rate"], rows)


def export_sales(request):
    rows = [
        [s.id, s.sale_date.isoformat(), str(s.subtotal), str(s.tax_amount), str(s.total), s.status]
        for s in Sale.objects.all().order_by("-sale_date")
    ]
    if request.GET.get("format") == "json":
        return _json_response(
            [{"id": r[0], "sale_date": r[1], "subtotal": r[2], "tax_amount": r[3], "total": r[4], "status": r[5]} for r in rows]
        )
    return _csv_response("sales.csv", ["id", "sale_date", "subtotal", "tax_amount", "total", "status"], rows)


def export_customers(request):
    rows = [
        [c.id, c.name, c.phone or "", c.email or ""]
        for c in Customer.objects.all().order_by("id")
    ]
    if request.GET.get("format") == "json":
        return _json_response(
            [{"id": r[0], "name": r[1], "phone": r[2], "email": r[3]} for r in rows]
        )
    return _csv_response("customers.csv", ["id", "name", "phone", "email"], rows)


def export_inventory(request):
    rows = [
        [t.id, t.product_id, str(t.quantity), t.transaction_type, t.created_at.isoformat()]
        for t in InventoryTransaction.objects.all().order_by("-created_at")
    ]
    if request.GET.get("format") == "json":
        return _json_response(
            [{"id": r[0], "product_id": r[1], "quantity": r[2], "transaction_type": r[3], "created_at": r[4]} for r in rows]
        )
    return _csv_response("inventory.csv", ["id", "product_id", "quantity", "transaction_type", "created_at"], rows)
```

> Verify the actual field names of `Customer` (`phone`, `email`) and `InventoryTransaction` (`quantity`, `transaction_type`) in `models/pos.py` / `models/inventory.py` and adjust the tuples if they differ — the endpoint contract (route names, formats) stays the same.

- [ ] **Step 4: Wire the routes**

In `formint/sidecar/configs/urls.py`, add to the `urlpatterns` block that already contains the `htmx/*` paths (and import at the top):

```python
from formint.export import (
    export_customers,
    export_inventory,
    export_products,
    export_sales,
)

urlpatterns += [
    path("export/products.csv", export_products, name="export-products"),
    path("export/sales.csv", export_sales, name="export-sales"),
    path("export/customers.csv", export_customers, name="export-customers"),
    path("export/inventory.csv", export_inventory, name="export-inventory"),
]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_export.py -q && make test`
Expected: PASS — export tests green, full suite green

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formint/sidecar/formint/export.py projects/formints/formint/sidecar/configs/urls.py projects/formints/formint/sidecar/tests/test_export.py
git commit -m "feat(sidecar): CSV/JSON export endpoints for products, sales, customers, inventory"
```

---

# Cross-cutting enhancements (Standard)

## Task B6: django-fusion fragments for Currency + TaxProfile

**Files:**
- Modify: `formint/sidecar/formint/components.py` (add components + register in `TABLE_COMPONENTS` / `FORM_COMPONENTS`)
- Modify: `formint/sidecar/htmx_views.py` (add `htmx_currencies`, `htmx_tax_profiles` views mirroring `htmx_products`)
- Modify: `formint/sidecar/configs/urls.py` (add `/htmx/currencies/`, `/htmx/tax-profiles/` routes next to `/htmx/products/`)
- Test: `formint/sidecar/tests/test_fusion_fragments.py`

**Interfaces:**
- Consumes: `Currency`/`TaxProfile` models (Task B1/B2), `BaseTableComponent` + `TABLE_COMPONENTS` + `FusionFormComponent` + `FORM_COMPONENTS` from `formint/components.py`.
- Produces: table components `CurrenciesTableComponent` / `TaxProfilesTableComponent` and form component `CurrencyFormComponent`, rendered at `/htmx/currencies/` and `/htmx/tax-profiles/`.

- [ ] **Step 1: Write the failing test**

Create `formint/sidecar/tests/test_fusion_fragments.py`:

```python
from django.test import TestCase
from django.urls import reverse

from models.money import Currency, TaxProfile


class FusionFragmentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Currency.objects.create(code="USD", name="US Dollar", symbol="$", is_default=True)
        TaxProfile.objects.create(name="Standard", rate="0.15", is_default=True)

    def test_currencies_fragment_renders_rows(self):
        resp = self.client.get(reverse("htmx-currencies"))
        assert resp.status_code == 200
        assert "USD" in resp.content.decode()

    def test_tax_profiles_fragment_renders_rows(self):
        resp = self.client.get(reverse("htmx-tax-profiles"))
        assert resp.status_code == 200
        assert "Standard" in resp.content.decode()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_fusion_fragments.py -q`
Expected: FAIL — `NoReverseMatch` for `htmx-currencies` / `htmx-tax-profiles`

- [ ] **Step 3: Add the table components**

In `formint/sidecar/formint/components.py`, after the existing `BaseTableComponent` and beside the other resource components (mirror `SalesTableComponent`'s declaration style), add:

```python
class CurrenciesTableComponent(BaseTableComponent):
    """Currency table fragment (Standard tier)."""

    model = Currency
    queryset_ordering = ("code",)
    header_labels = {
        "code": "Code",
        "name": "Name",
        "symbol": "Symbol",
        "exchange_rate": "Rate",
        "is_default": "Default",
        "is_active": "Active",
    }


class TaxProfilesTableComponent(BaseTableComponent):
    """Tax profile table fragment (Standard tier)."""

    model = TaxProfile
    queryset_ordering = ("name",)
    header_labels = {
        "name": "Name",
        "rate": "Rate",
        "is_default": "Default",
        "is_active": "Active",
    }
```

Register them in `TABLE_COMPONENTS`:

```python
TABLE_COMPONENTS: dict[str, type[TableMixin]] = {
    # ... existing entries ...
    "currencies": CurrenciesTableComponent,
    "tax-profiles": TaxProfilesTableComponent,
}
```

Add a form component for currency creation next to the existing form components:

```python
class CurrencyFormComponent(FusionFormComponent):
    """Currency create form fragment (Standard tier)."""

    form_name = "formint/forms/currency"
    model = Currency
```

and register it in `FORM_COMPONENTS` as `"currency": CurrencyFormComponent`.

- [ ] **Step 4: Add the htmx views + routes**

In `formint/sidecar/htmx_views.py`, add two views mirroring the existing `htmx_products` view (same rendering call, component name swapped):

```python
def htmx_currencies(request):
    # Mirror htmx_products: resolve TABLE_COMPONENTS["currencies"] and render it.
    ...


def htmx_tax_profiles(request):
    # Mirror htmx_products: resolve TABLE_COMPONENTS["tax-profiles"] and render it.
    ...
```

In `formint/sidecar/configs/urls.py`, next to the existing `/htmx/products/` path, add:

```python
path("htmx/currencies/", htmx_currencies, name="htmx-currencies"),
path("htmx/tax-profiles/", htmx_tax_profiles, name="htmx-tax-profiles"),
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_fusion_fragments.py -q && make test`
Expected: PASS — fragments green, full suite green

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formint/sidecar/formint/components.py projects/formints/formint/sidecar/htmx_views.py projects/formints/formint/sidecar/configs/urls.py projects/formints/formint/sidecar/tests/test_fusion_fragments.py
git commit -m "feat(sidecar): django-fusion table/form fragments for currencies and tax profiles"
```

## Task B7: Consume the modular TS client in the Astro frontend

**Files:**
- Modify: `formint/frontend/package.json` (add `@formints/client` workspace dep)
- Modify: `formint/frontend/src/lib/currencies.ts` (create — typed wrapper over the SDK)
- Test: `formint/frontend/src/lib/currencies.test.ts`

**Interfaces:**
- Consumes: `createClient`, `listCurrencies`, `createCurrency`, `listTaxProfiles` from `@formints/client` (06-js-sdk.md, Task S2).
- Produces: `currenciesApi(baseUrl)` returning `{ list, create, listTaxProfiles }` used by the currency admin page.

- [ ] **Step 1: Write the failing test**

Create `formint/frontend/src/lib/currencies.test.ts` (Vitest, mirror the contract tests in `formint/frontend/tests/`):

```ts
import { describe, it, expect, vi, afterEach } from 'vitest';
import { currenciesApi } from './currencies';

const fetchMock = vi.fn();
vi.stubGlobal('fetch', fetchMock);

const api = currenciesApi('http://127.0.0.1:8767');

afterEach(() => vi.restoreAllMocks());

describe('currenciesApi', () => {
  it('lists currencies', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ count: 1, items: [{ code: 'USD' }] }), { status: 200 }));
    const { items } = await api.list();
    expect(items[0]?.code).toBe('USD');
    expect(fetchMock).toHaveBeenCalledWith('http://127.0.0.1:8767/api/v1/currencies', expect.any(Object));
  });

  it('creates a currency', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ code: 'EUR' }), { status: 201 }));
    const created = await api.create({ code: 'EUR', name: 'Euro', symbol: '€' });
    expect(created.code).toBe('EUR');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formint/frontend && pnpm vitest run src/lib/currencies.test.ts`
Expected: FAIL — cannot find module `./currencies`

- [ ] **Step 3: Write the wrapper**

Create `formint/frontend/src/lib/currencies.ts`:

```ts
import { createClient, listCurrencies, createCurrency, listTaxProfiles } from '@formints/client';

export function currenciesApi(baseUrl: string) {
  const client = createClient(baseUrl);
  return {
    list: () => listCurrencies(client),
    create: (input: Parameters<typeof createCurrency>[1]) => createCurrency(client, input),
    listTaxProfiles: () => listTaxProfiles(client),
  };
}
```

Wire `@formints/client` as a workspace dependency in `formint/frontend/package.json` (add to `dependencies`: `"@formints/client": "workspace:*"` — or a file: reference if the repo does not use pnpm workspaces for this package; see `06-js-sdk.md` for the package path).

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd projects/formints/formint/frontend && pnpm vitest run src/lib/currencies.test.ts && pnpm check`
Expected: PASS — tests green, Astro check green

- [ ] **Step 5: Commit**

```bash
git add projects/formints/formint/frontend/package.json projects/formints/formint/frontend/src/lib/currencies.ts projects/formints/formint/frontend/src/lib/currencies.test.ts
git commit -m "feat(formint-frontend): consume @formints/client for currencies and tax profiles"
```

## Task B8: Playwright e2e for the Standard surface + inheritance parity sweep

**Files:**
- Create: `formint/frontend/playwright.config.ts`
- Create: `formint/frontend/e2e/currencies.spec.ts`
- Modify: `projects/formints/docs/architecture/editions.md` (parity note)

**Interfaces:**
- Consumes: the seeded backend (`make seed` in `formint/sidecar/`) and the Astro frontend (`:4321`).
- Produces: a standalone Standard e2e suite + the feature-inheritance parity check.

- [ ] **Step 1: Write the config + spec**

Create `formint/frontend/playwright.config.ts` (mirror `formintA/playwright.config.ts`, baseURL `http://127.0.0.1:4321`):

```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: { baseURL: 'http://127.0.0.1:4321' },
  webServer: undefined, // started manually via `make env` (backend :8767 + frontend :4321)
});
```

Create `formint/frontend/e2e/currencies.spec.ts`:

```ts
import { test, expect } from '@playwright/test';

test('currency admin table lists the seeded currencies', async ({ page }) => {
  await page.goto('/admin/currencies');
  await expect(page.getByText('USD')).toBeVisible();
  await expect(page.getByText('MAD')).toBeVisible();
});

test('tax profiles admin table lists the seeded profiles', async ({ page }) => {
  await page.goto('/admin/tax-profiles');
  await expect(page.getByText('Standard')).toBeVisible();
});
```

> If the frontend does not yet have `/admin/currencies` / `/admin/tax-profiles` routes, add thin Astro pages that render the B6 fragments (or the B7 `currenciesApi`), then point the spec at those routes. The assertions (seeded USD/MAD/Standard visible) are the contract.

- [ ] **Step 2: Run the e2e suite**

Run (backend + frontend up via `make env`):
```bash
cd projects/formints/formint/sidecar && make seed
cd projects/formints/formint/frontend && pnpm exec playwright test
```
Expected: PASS — both specs green.

- [ ] **Step 3: Feature-inheritance parity sweep**

Verify every Community capability (see `01-community.md`: sale, products, customers, inventory, KDS, i18n, RBAC, theme system, refunds/returns, offline mode) is reachable in the Standard surface. For each: open the page and confirm it renders. Fix any missing page by wiring the existing controller/fragment, and add a row to the spec asserting it.

- [ ] **Step 4: Commit**

```bash
git add formint/frontend/playwright.config.ts formint/frontend/e2e/ projects/formints/docs/architecture/editions.md
git commit -m "test(formint-frontend): Standard e2e suite + Community feature-inheritance sweep"
```

---

## Self-Review

1. **Spec coverage:** all four Standard capability markers (multi-currency, tax profiles, custom roles & permissions, data export) map to tasks B1-B4.
2. **Placeholder scan:** two conditional instructions, both actionable with named files (B3: confirm ninja-extra signatures; B4: verify `Customer`/`InventoryTransaction` field names). No TBDs.
3. **Type consistency:** `Currency`/`TaxProfile` defined in B1/B2 referenced identically in `models/models.py`, `controllers.py`, tests. `compute_tax(Decimal, Decimal) -> Decimal` matches its test. `require_permission` produced in B3 is applied in B3 itself (same task, self-consistent). Export view names match the `reverse()` names in tests.

## Execution Handoff

**Plan complete and saved to `projects/formints/docs/superpowers/plans/2026-08-09-editions/02-standard.md`.** Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
