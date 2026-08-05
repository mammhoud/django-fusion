"""
Formint — django-fusion data components (tables and forms).

These are the server-rendered "data components as tables and forms" for the
merged package.  They are built on the django-fusion fragments libraries:

  * ``django_fusion.fragments.tables`` — ``TableMixin`` / ``RowGenerator`` for
    ORM→table-row conversion (tables).
  * ``django_fusion.fragments.forms`` — ``FormMixin`` / ``FormTagGenerator``
    for ModelForm auto-generation and HTML tag rendering (forms).

Both share the canonical fusion fragment contract: Astro owns the page shell
and skeleton, and these components return lean HTMX fragments that swap only
the target region.

Each component is a small class registered in a ``RESOURCE_MAP`` so that
``/htmx/tables/<resource>/`` and ``/htmx/forms/<resource>/`` resolve to a
component (see ``views.py``).
"""

from __future__ import annotations

from typing import Any

from django.db.models import Model as DjangoModel
from django.forms import ModelForm

from django_fusion.fragments.forms import FormMixin, FormTagGenerator
from django_fusion.fragments.tables import RowGenerator, TableMixin

from formint import models as m

__all__ = [
    "ProductsTableComponent", "CategoriesTableComponent",
    "CustomersTableComponent", "ClientCategoriesTableComponent",
    "SalesTableComponent", "SuppliersTableComponent",
    "ProductFormComponent", "CategoryFormComponent",
    "CustomerFormComponent", "ClientCategoryFormComponent",
    "SupplierFormComponent",
    "TABLE_COMPONENTS", "FORM_COMPONENTS", "RESOURCE_MAP",
]

# Sync-tracking fields are managed by the DataToken/sync layer and are not
# part of the operator-facing form; exclude them from auto-generated forms.
_SYNC_FIELDS = {"is_synced", "synced_at", "sync_status"}


class FusionFormComponent(FormMixin):
    """Base form component: auto-generated ModelForm minus sync fields."""

    def _build_modelform_fields(self, model_class) -> list[str]:
        fields = super()._build_modelform_fields(model_class)
        return [f for f in fields if f not in _SYNC_FIELDS]

    def get_form_class(self):
        if self.form_class:
            return self.form_class
        if hasattr(self, "model") and self.model:
            form_fields = self._build_modelform_fields(self.model)
            meta = type("Meta", (), {"model": self.model, "fields": form_fields})

            # Apply model defaults to form fields so operator forms do not
            # require values the model would default anyway (cost_price=0,
            # tax_rate='standard', stock_quantity=0, ...).
            defaults: dict = {}
            for name in form_fields:
                field = self.model._meta.get_field(name)
                has_default = (
                    field.has_default()
                    and not isinstance(field, DjangoModel)
                    and not getattr(field, "blank", False)
                )
                if has_default and not field.null:
                    default = field.get_default()
                    if default is not None and default != "":
                        defaults[name] = default

            def _patch_form(form_class, _defaults):
                original_init = form_class.__init__

                def __init__(self, *args, **kwargs):
                    data = kwargs.get("data")
                    if data is not None:
                        filled = {
                            k: v for k, v in data.items()
                            if k in _defaults and v in (None, "")
                        }
                        if filled:
                            data = data.copy()
                            data.update(filled)
                            kwargs["data"] = data
                    original_init(self, *args, **kwargs)
                    for name, default in _defaults.items():
                        field_obj = self.fields.get(name)
                        if field_obj is not None:
                            field_obj.required = False
                            if field_obj.initial is None:
                                field_obj.initial = default

                form_class.__init__ = __init__
                return form_class

            return _patch_form(
                type(
                    f"{self.model.__name__}Form",
                    (ModelForm,),
                    {"Meta": meta, "__module__": self.__class__.__module__},
                ),
                defaults,
            )
        raise ValueError(f"{self.__class__.__name__} must define form_class or model")


# ══════════════════════════════════════════════════════════════════════════
# Table components (django-fusion TableMixin + RowGenerator)
# ══════════════════════════════════════════════════════════════════════════


class ProductsTableComponent(TableMixin):
    """Product catalog table fragment."""

    table_name = "formint/tables/products"
    table_columns = ["id", "name", "category", "price", "stock_quantity", "tax_rate", "is_active"]
    table_headers = [
        {"label": "ID", "key": "id"},
        {"label": "Name", "key": "name"},
        {"label": "Category", "key": "category"},
        {"label": "Price", "key": "price"},
        {"label": "Stock", "key": "stock_quantity"},
        {"label": "Tax", "key": "tax_rate"},
        {"label": "Active", "key": "is_active"},
    ]
    paginate_by = 10

    def get_table_data(self):
        return m.Product.objects.select_related("category").order_by("name")


class CategoriesTableComponent(TableMixin):
    """Product category table fragment."""

    table_name = "formint/tables/categories"
    table_columns = ["id", "name", "display_order", "is_active"]
    table_headers = [
        {"label": "ID", "key": "id"},
        {"label": "Name", "key": "name"},
        {"label": "Order", "key": "display_order"},
        {"label": "Active", "key": "is_active"},
    ]
    paginate_by = 10

    def get_table_data(self):
        return m.Category.objects.all().order_by("display_order", "name")


class CustomersTableComponent(TableMixin):
    """Customer list table fragment."""

    table_name = "formint/tables/customers"
    table_columns = ["id", "full_name", "email", "phone", "loyalty_points", "total_spent", "is_active"]
    table_headers = [
        {"label": "ID", "key": "id"},
        {"label": "Name", "key": "full_name"},
        {"label": "Email", "key": "email"},
        {"label": "Phone", "key": "phone"},
        {"label": "Points", "key": "loyalty_points"},
        {"label": "Spent", "key": "total_spent"},
        {"label": "Active", "key": "is_active"},
    ]
    paginate_by = 10

    def get_table_data(self):
        return m.Customer.objects.all().order_by("-created_at")


class ClientCategoriesTableComponent(TableMixin):
    """Loyalty client category table fragment."""

    table_name = "formint/tables/client_categories"
    table_columns = ["id", "name", "min_points", "points_per_currency", "discount_rate", "is_active"]
    table_headers = [
        {"label": "ID", "key": "id"},
        {"label": "Name", "key": "name"},
        {"label": "Min Points", "key": "min_points"},
        {"label": "Pts/Currency", "key": "points_per_currency"},
        {"label": "Discount %", "key": "discount_rate"},
        {"label": "Active", "key": "is_active"},
    ]
    paginate_by = 10

    def get_table_data(self):
        return m.ClientCategory.objects.all().order_by("min_points", "name")


class SalesTableComponent(TableMixin):
    """Recent sales table fragment."""

    table_name = "formint/tables/sales"
    table_columns = ["id", "sale_date", "customer", "payment_method", "status", "total"]
    table_headers = [
        {"label": "ID", "key": "id"},
        {"label": "Date", "key": "sale_date"},
        {"label": "Customer", "key": "customer"},
        {"label": "Payment", "key": "payment_method"},
        {"label": "Status", "key": "status"},
        {"label": "Total", "key": "total"},
    ]
    paginate_by = 10

    def get_table_data(self):
        return m.Sale.objects.select_related("customer").order_by("-sale_date")


class SuppliersTableComponent(TableMixin):
    """Supplier list table fragment."""

    table_name = "formint/tables/suppliers"
    table_columns = ["id", "name", "contact_name", "email", "phone", "is_active"]
    table_headers = [
        {"label": "ID", "key": "id"},
        {"label": "Name", "key": "name"},
        {"label": "Contact", "key": "contact_name"},
        {"label": "Email", "key": "email"},
        {"label": "Phone", "key": "phone"},
        {"label": "Active", "key": "is_active"},
    ]
    paginate_by = 10

    def get_table_data(self):
        return m.Supplier.objects.all().order_by("name")


TABLE_COMPONENTS: dict[str, type[TableMixin]] = {
    "products": ProductsTableComponent,
    "categories": CategoriesTableComponent,
    "customers": CustomersTableComponent,
    "client-categories": ClientCategoriesTableComponent,
    "sales": SalesTableComponent,
    "suppliers": SuppliersTableComponent,
}


# ══════════════════════════════════════════════════════════════════════════
# Form components (django-fusion FormMixin + FormTagGenerator)
# ══════════════════════════════════════════════════════════════════════════


class ProductFormComponent(FusionFormComponent):
    """Product create form fragment (ModelForm auto-generated)."""

    form_name = "formint/forms/product"
    model = m.Product
    form_layout = [
        ["name", "sku"],
        ["category", "price"],
        ["cost_price", "tax_rate"],
        ["barcode", "stock_quantity"],
        ["low_stock_threshold", "is_active"],
        ["description"],
    ]


class CategoryFormComponent(FusionFormComponent):
    """Category create form fragment."""

    form_name = "formint/forms/category"
    model = m.Category
    form_layout = [
        ["name", "slug"],
        ["description"],
        ["display_order", "is_active"],
    ]


class CustomerFormComponent(FusionFormComponent):
    """Customer create form fragment."""

    form_name = "formint/forms/customer"
    model = m.Customer
    form_layout = [
        ["first_name", "last_name"],
        ["email", "phone"],
        ["client_category", "loyalty_points"],
        ["total_spent", "is_active"],
        ["notes"],
    ]


class ClientCategoryFormComponent(FusionFormComponent):
    """Loyalty client category form fragment."""

    form_name = "formint/forms/client_category"
    model = m.ClientCategory
    form_layout = [
        ["name", "description"],
        ["min_points", "points_per_currency"],
        ["points_to_currency", "discount_rate"],
        ["perks", "is_active"],
    ]


class SupplierFormComponent(FusionFormComponent):
    """Supplier form fragment."""

    form_name = "formint/forms/supplier"
    model = m.Supplier
    form_layout = [
        ["name", "contact_name"],
        ["email", "phone"],
        ["address", "tax_id"],
        ["payment_terms", "is_active"],
    ]


FORM_COMPONENTS: dict[str, type[FormMixin]] = {
    "product": ProductFormComponent,
    "category": CategoryFormComponent,
    "customer": CustomerFormComponent,
    "client-category": ClientCategoryFormComponent,
    "supplier": SupplierFormComponent,
}


RESOURCE_MAP: dict[str, Any] = {**TABLE_COMPONENTS, **FORM_COMPONENTS}


def render_table_rows(component: TableMixin, limit: int = 50) -> list[dict]:
    """Render ORM data to table-ready rows via django-fusion RowGenerator."""
    generator = RowGenerator(
        component.get_table_data()[:limit],
        columns=component.table_columns,
    )
    return generator.get_rows()
