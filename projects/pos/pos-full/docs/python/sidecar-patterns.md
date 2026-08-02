# POS Full — Sidecar Patterns

> **Directory:** `docs/python/`
> **Language:** Python 3.11+
> **Framework:** Robyn + Django ORM
> **Port:** 8765 (POS Full) / 8766 (POS Solo)

---

## Route Handler Pattern

```python
# sidecar/routes/products.py
from robyn import Robyn, Request, jsonify
from django_fusion.comp.routes import RoutableComponent
from sidecar.models.pos import Product
from django.core.paginator import Paginator

app = Robyn(__file__)

@app.get("/api/products/")
async def list_products(request: Request):
    """GET /api/products/?page=1&per_page=20&search=espresso"""
    page = int(request.query_params.get("page", 1))
    per_page = int(request.query_params.get("per_page", 20))
    search = request.query_params.get("search", "")

    qs = Product.objects.filter(is_active=True)
    if search:
        qs = qs.filter(name__icontains=search)

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page)

    return jsonify({
        "data": [p.to_dict() for p in page_obj],
        "total": paginator.count,
        "page": page,
        "pages": paginator.num_pages,
    })
```

## Fusion Response Pattern

```python
from django_fusion.routes.rendering.renderers import fusion_json_response

@app.get("/api/products/<int:product_id>/")
async def get_product(request: Request, product_id: int):
    product = Product.objects.get(id=product_id)

    return fusion_json_response(
        data=product.to_dict(),
        status=200,
        message="Success",
    )
```

## Django ORM Model Pattern

```python
# sidecar/models/pos.py
from django.db import models
from django_fusion.core.models import BaseModel

class Product(BaseModel):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    border_color = models.CharField(max_length=7, blank=True, default="")

    class Meta:
        db_table = "products"
        ordering = ["name"]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "price": float(self.price),
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "is_active": self.is_active,
            "border_color": self.border_color or "",
        }
```

## RobynFusionChecker Pattern

```python
# sidecar/middleware/fusion.py
from django_fusion.cache.session import FusionSessionChecker
from sidecar.services.device_tokens import get_token_info

class RobynFusionChecker(FusionSessionChecker):
    def __init__(self, check_fn=None):
        super().__init__(check_fn=check_fn or self._role_check)

    @staticmethod
    def _role_check(request):
        """Admin/manager roles get fragment-first rendering."""
        token_info = get_token_info(request)
        role = token_info.get("role", "")
        return role in ("admin", "manager")
```

## Testing Pattern

```python
# sidecar/tests/test_products.py
import pytest
from sidecar.models.pos import Product, Category

@pytest.mark.django_db
class TestProductAPI:
    def test_list_products(self, client):
        response = client.get("/api/products/")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_filter_by_search(self, client):
        Product.objects.create(name="Espresso", price=3.50)
        Product.objects.create(name="Latte", price=4.50)

        response = client.get("/api/products/?search=espresso")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_create_product(self, client):
        response = client.post("/api/products/", json={
            "name": "Cappuccino",
            "price": 5.00,
            "unit": "item",
        })
        assert response.status_code == 201
        assert Product.objects.filter(name="Cappuccino").exists()
```

## Database Connection Pattern

```python
# sidecar/config/database.py
import django
from django.conf import settings

def init_django(db_path: str):
    """Initialize Django ORM with SQLite database."""
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': db_path,
            }
        },
        INSTALLED_APPS=['sidecar.models'],
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )
    django.setup()
```
