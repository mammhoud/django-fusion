# ⚡ Django Ninja Extra — Alternative Sidecar Plan

> Plan to replace or supplement the Sanic sidecar with Django Ninja Extra for type-safe, auto-documented REST APIs.

---

## Why Django Ninja Extra?

| Feature | Sanic (Current) | Django Ninja Extra (Planned) |
|---------|:---:|:---:|
| **Type safety** | Manual validation | Pydantic models — automatic |
| **API docs** | Manual / none | Auto-generated OpenAPI (Swagger / ReDoc) |
| **Async support** | Native async (Sanic) | Native async (Starlette/ASGI) |
| **ORM integration** | None (raw SQL or SQLAlchemy) | Native Django ORM support |
| **Authentication** | Manual JWT | Built-in auth + permissions |
| **Serialization** | Manual dicts | Pydantic Schema auto-serialize |
| **Learning curve** | Low (minimal framework) | Medium (Django + Pydantic) |
| **Startup speed** | Very fast (<1s) | Fast (~1s with Django) |
| **Bundle size** | Small (~5MB) | Medium (~15MB with Django) |

---

## Architecture Comparison

### Current: Sanic Sidecar

```
Vue → Tauri invoke → Rust → SQLite ← Sanic ← Django ORM (read mirror)
                          ↓
                    Sanic spawns as sidecar
```

### Planned: Django Ninja Extra Sidecar

```
Vue → Tauri invoke → Rust → SQLite ← Django Ninja ← Django ORM
                          ↓              ↓
                    Sidecar spawn   Auto-generated
                                     OpenAPI docs
```

### Alternative: Django Ninja Extra ONLY (No Sanic)

```
Vue → HTTP (not invoke) → Django Ninja Extra → Django ORM → SQLite
                           • Auto OpenAPI docs at /api/docs
                           • Pydantic validation
                           • Django Admin
                           • Async endpoints
```

---

## Implementation Plan

### Phase 1: Add Django Ninja Extra to Solo Edition

```bash
# Install
pip install django-ninja-extra

# Directory structure
pos-solo/sidecar/
├── server.py              # Sanic (keep for backward compat)
├── ninja_api.py           # NEW: Django Ninja Extra API
├── ninja_schemas.py       # NEW: Pydantic schemas
├── ninja_urls.py          # NEW: URL routing for Ninja
├── settings.py            # Updated: add ninja_extra to INSTALLED_APPS
└── urls.py                # Updated: include ninja_urls
```

### Phase 2: Migrate Endpoints

```python
# ninja_schemas.py — Pydantic models for all entities
from ninja_extra import Schema
from typing import Optional
from datetime import datetime

class ProductSchema(Schema):
    id: int
    name: str
    sku: Optional[str]
    price: float
    category_id: int
    is_active: bool = True

class ProductCreateSchema(Schema):
    name: str
    sku: Optional[str] = None
    price: float
    category_id: int

class ProductFilterSchema(Schema):
    category_id: Optional[int] = None
    search: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
```

```python
# ninja_api.py — Type-safe API controllers
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post
from posapp.models import Product
from .ninja_schemas import ProductSchema, ProductCreateSchema, ProductFilterSchema

api = NinjaExtraAPI(
    title="POS API",
    version="1.0.0",
    description="POS Sidecar REST API — auto-documented with OpenAPI",
)

@api_controller("/products", tags=["Products"])
class ProductController:
    @http_get("/", response=list[ProductSchema])
    async def list_products(self, filters: ProductFilterSchema = None):
        """List all products with optional filtering."""
        qs = Product.objects.filter(is_active=True)
        if filters and filters.category_id:
            qs = qs.filter(category_id=filters.category_id)
        if filters and filters.search:
            qs = qs.filter(name__icontains=filters.search)
        return [ProductSchema.from_orm(p) for p in qs]

    @http_get("/{product_id}", response=ProductSchema)
    async def get_product(self, product_id: int):
        """Get a single product by ID."""
        return ProductSchema.from_orm(
            Product.objects.get(id=product_id)
        )

    @http_post("/", response=ProductSchema)
    async def create_product(self, data: ProductCreateSchema):
        """Create a new product."""
        product = Product.objects.create(**data.dict())
        return ProductSchema.from_orm(product)

api.register_controllers(ProductController)
```

### Phase 3: Auto-Generated Docs

Once Django Ninja Extra is running, you get:

- **Swagger UI**: `http://localhost:8765/api/docs`
- **ReDoc**: `http://localhost:8765/api/redoc`
- **OpenAPI JSON**: `http://localhost:8765/api/openapi.json`

```python
# settings.py
INSTALLED_APPS = [
    # ... existing apps ...
    'ninja_extra',
]

# urls.py
from django.urls import path
from ninja_api import api

urlpatterns = [
    path('api/', api.urls),  # ← Auto-mounts /api/docs, /api/redoc, /api/openapi.json
]
```

---

## Migration Strategy: Sanic → Django Ninja Extra

### Step 1: Add Ninja alongside Sanic (Phase 1)

Run both servers temporarily:
- Sanic on port 8765 (existing clients)
- Django Ninja Extra on port 8766 (new clients)

### Step 2: Port endpoints incrementally

```python
# server.py — hybrid mode
import asyncio
from sanic import Sanic
from django.core.wsgi import get_wsgi_application

app = Sanic("POS")

# Mount Django Ninja Extra as a sub-app
@app.listener('before_server_start')
async def setup_ninja(app, loop):
    # Django Ninja runs on the same Sanic server
    from ninja_api import api as ninja_api
    app.blueprint(ninja_api.get_blueprint())  # Mount Ninja routes
```

### Step 3: Deprecate Sanic endpoints

Once all endpoints are ported, remove Sanic server entirely and switch to:

```python
# server.py — Django-only mode
import uvicorn
from django.core.asgi import get_asgi_application

application = get_asgi_application()

if __name__ == "__main__":
    uvicorn.run(application, host="127.0.0.1", port=8765)
```

---

## Edition Impact

| Edition | Current | After Migration |
|---------|---------|-----------------|
| **Minimal** | No sidecar | Django Ninja Extra (optional) |
| **Solo** | Sanic + sync client | Django Ninja Extra + sync client |
| **Full** | Sanic + Django ORM + WebSocket | Django Ninja Extra + Django ORM + WebSocket |

### Minimal Edition with Django Ninja Extra

The Minimal edition can now include a sidecar for the first time:

```bash
# pos-minimal/sidecar/ (NEW)
pip install django django-ninja-extra
python server.py --db restaurant.db --port 8765
```

This gives Minimal edition:
- REST API for external integrations (first time!)
- Auto-generated OpenAPI docs
- Django Admin dashboard
- No Rust ORM needed — Django ORM handles everything

---

## When to Use Which

| Scenario | Use |
|----------|-----|
| **Pure desktop POS, no external integrations** | Rust/Diesel (Minimal, no sidecar) |
| **Need REST API + auto docs** | Django Ninja Extra |
| **Need WebSocket real-time** | Keep Sanic for WS, Ninja for REST |
| **Django expertise > Sanic expertise** | Django Ninja Extra |
| **Minimal bundle size critical** | Sanic (smaller footprint) |
| **Cloud CRM sync needed** | Django Ninja Extra (better ORM integration) |

---

## Related

| Topic | Path |
|-------|------|
| Sidecar overview | [`README.md`](README.md) |
| Django ORM guide | [`django-orm.md`](django-orm.md) |
| Sidecar API (Sanic) | [`sidecar-api.md`](sidecar-api.md) |
| Cloud sync plan | [`../cloud/sync-plan.md`](../cloud/sync-plan.md) |
