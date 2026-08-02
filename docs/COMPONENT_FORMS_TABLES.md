# Django-Fusion Forms & Tables — Usage Guide

## Overview

`django_fusion.contrib` provides a unified, dependency-free framework for
form handling and table rendering in routable components. It replaces the
fragmented approach of `comp.routes.forms_tables` with enhanced mixins,
automatic ORM data conversion, and form tag generation.

## Quick Start

### New Canonical Imports

```python
# Tables
from django_fusion.contrib.tables import TableMixin, RowGenerator

# Forms
from django_fusion.contrib.forms import FormMixin, FormTableMixin, FormTagGenerator

# Or all at once
from django_fusion.contrib import TableMixin, RowGenerator, FormMixin, FormTagGenerator
```

### Legacy Imports (still work)

```python
from django_fusion.routes.forms_tables import TableMixin  # → forwarded to contrib
from django_fusion.fragments.forms import FormMixin
```

## Table Usage

### Basic — Auto-generated from Model

```python
from django_fusion.routes.components.routable import RoutableComponent
from django_fusion.contrib.tables import TableMixin

class ProductList(RoutableComponent, TableMixin):
    route_name = "products"
    route_path = "products/"
    title = "Products"
    table_name = "products"
    model = Product

    def get_table_data(self):
        # Returns QuerySet — RowGenerator auto-detects columns from model
        return Product.objects.filter(is_active=True)
```

### With Explicit Columns

```python
class ProductReport(RoutableComponent, TableMixin):
    table_name = "products"
    table_columns = ["name", "price", "stock_quantity", "category__name"]
    table_exclude = ["id", "created_at", "updated_at"]

    def get_table_data(self):
        return Product.objects.select_related("category").all()
```

### Custom Formatters

```python
from decimal import Decimal

class SalesReport(RoutableComponent, TableMixin):
    table_name = "sales"
    table_columns = ["id", "total", "sale_date", "payment_method"]
    table_formatters = {
        "total": lambda v: f"${float(v):,.2f}" if v else "$0.00",
        "sale_date": lambda v: v.strftime("%Y-%m-%d %H:%M") if v else "—",
        "payment_method": lambda v: v.title(),
    }

    def get_table_data(self):
        return Sale.objects.select_related("customer").all()
```

### Using RowGenerator Directly

```python
from django_fusion.contrib.tables import RowGenerator

# From QuerySet (auto-detects columns from model)
gen = RowGenerator(Product.objects.all())
columns = gen.get_columns()  # [{"key": "name", "label": "name", ...}]
rows = gen.get_rows()        # [{"name": "Widget", "price": "$10.00"}]

# From explicit columns
gen = RowGenerator(
    Product.objects.filter(price__gt=100),
    columns=["name", "price", "category__name"],
    exclude=["id"],
    formatters={"price": lambda v: f"€{float(v):,.2f}"},
)
```

## Form Usage

### Basic — Auto-ModelForm from Model

```python
from django_fusion.routes.components.routable import RoutableComponent
from django_fusion.contrib.forms import FormMixin

class ProductCreate(RoutableComponent, FormMixin):
    route_name = "product_create"
    route_path = "products/create/"
    title = "New Product"
    form_name = "product"
    model = Product
    # form_class auto-created from model — no need to define explicitly
```

### With Explicit Form Class

```python
from django.forms import ModelForm

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price", "description"]

class ProductEdit(RoutableComponent, FormMixin):
    form_name = "product"
    form_class = ProductForm
```

### With Layout and Field Customization

```python
class ProductCreate(RoutableComponent, FormMixin):
    form_name = "product"
    model = Product
    form_layout = [
        ["name", "price"],       # Row 1: two fields side by side
        ["category", "sku"],      # Row 2
        ["description"],          # Row 3: full width
    ]
    form_field_kwargs = {
        "price": {"placeholder": "0.00", "css_classes": "w-32"},
        "description": {"help_text": "Optional product description"},
    }
```

### Form + Table Combined

```python
from django_fusion.contrib.forms import FormTableMixin

class ProductSearch(RoutableComponent, FormTableMixin):
    route_name = "search"
    route_path = "products/search/"
    title = "Search Products"
    form_name = "search"
    table_name = "products"
    model = Product
    # FormTableMixin inherits from BOTH FormMixin and TableMixin
    # — provides form rendering AND table rendering in one mixin.
```

## Benefits Over Old Approach

| Feature | Old (`routes/forms_tables`) | New (`comp.contrib`) |
|---------|---------------------------|---------------------|
| ORM data handling | Manual `get_table_data()` returning lists of dicts | Auto-converts QuerySets via `RowGenerator` |
| Column generation | Manual header dicts or basic model field loop | Auto-detects from model `_meta`, supports FK traversal (`category__name`) |
| Form creation | Requires explicit `form_class` | Auto-creates `ModelForm` from `model` attribute |
| Field rendering | Manual template iteration | `FormTagGenerator` provides typed field context with widget detection |
| Layout | None | `form_layout` for field grouping |
| Pagination | Manual | Built-in via `paginate_by` |
| Form + Table combo | Separate `FormTableMixin` with both parents | Cleaner direct inheritance |

## Migration From Old Code

**Before:**
```python
from django_fusion.routes.forms_tables import TableMixin, FormMixin

class MyReport(RoutableComponent, TableMixin):
    table_name = "report"
    def get_table_headers(self):
        return [{"label": "Name", "key": "name", "sortable": True}]
    def get_table_data(self):
        return [{"name": str(p), "price": f"${p.price}"} for p in Product.objects.all()]
```

**After:**
```python
from django_fusion.contrib.tables import TableMixin

class MyReport(RoutableComponent, TableMixin):
    table_name = "report"
    table_columns = ["name", "price"]
    table_formatters = {"price": lambda v: f"${float(v):,.2f}"}
    def get_table_data(self):
        return Product.objects.all()  # RowGenerator handles conversion
```

## Weak Points & Caveats

1. **No template tag files yet** — `{% fusion_table %}` and `{% fusion_form %}` tags are planned but not yet implemented. Current rendering uses the existing `{% comp %}` tag with context data.

2. **No sorting/filtering built-in** — The mixin provides header definitions with `sortable` flags but doesn't process `?sort=column` or `?order=asc` query params automatically.

3. **Pagination is bare-bones** — Returns pagination metadata but doesn't slice the queryset. For full pagination, override `get_table_data()` or use the `paginate_by` attribute with `get_queryset()`.

4. **`RowGenerator` eagerly evaluates** — `get_rows()` materializes all rows into a list. For very large datasets, consider pagination or streaming.
