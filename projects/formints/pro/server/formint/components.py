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

from collections.abc import Mapping
from typing import Any, ClassVar

from django.db.models import Model as DjangoModel
from django.forms import ModelForm

from django_fusion.fragments.forms import FormMixin, FormTagGenerator
from django_fusion.fragments.tables import RowGenerator, TableMixin

from formint import models as m

__all__ = [
    "BaseTableComponent", "ProductsTableComponent", "CategoriesTableComponent",
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


class BaseTableComponent(TableMixin):
    """Shared Formint table contract.

    Resource components only declare their model, columns, labels, related
    objects, and ordering.  QuerySet construction, header normalization, and
    the shared page size stay in one place.  ``TableMixin`` continues to own
    row generation and pagination metadata so this base remains compatible
    with every django-fusion table consumer.
    """

    model: ClassVar[type[DjangoModel] | None] = None
    paginate_by: ClassVar[int] = 10
    queryset_ordering: ClassVar[tuple[str, ...]] = ()
    select_related_fields: ClassVar[tuple[str, ...]] = ()
    header_labels: ClassVar[Mapping[str, str]] = {}
    _table_queryset: Any = None

    def reset_table_queryset(self) -> None:
        """Clear the request-scoped QuerySet cache after a data mutation."""
        self._table_queryset = None

    def get_table_data(self):
        """Return the resource QuerySet with eager-loading and ordering.

        Components are request-scoped, so retaining the lazy QuerySet avoids
        rebuilding the same query when ``TableMixin`` asks for rows and then
        pagination totals.  Evaluation remains lazy and Django's QuerySet
        result cache is preserved for repeated consumers in one response.
        """
        if self.model is None:
            return super().get_table_data()

        # Components are normally request-scoped.  Keep the lazy QuerySet
        # stable within that request so rows, pagination, and helper methods
        # share one configured source; callers that mutate data can explicitly
        # call ``reset_table_queryset()`` before rendering again.
        if self._table_queryset is not None:
            return self._table_queryset

        queryset = self.model.objects.all()
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        if self.queryset_ordering:
            queryset = queryset.order_by(*self.queryset_ordering)
        self._table_queryset = queryset
        return queryset

    def get_table_headers(self) -> list[dict[str, Any]]:
        """Build stable headers from the declared columns and labels."""
        if self.table_headers:
            return super().get_table_headers()

        return [
            {
                "key": column,
                "label": self.header_labels.get(
                    column, column.replace("_", " ").title()
                ),
                "sortable": True,
            }
            for column in (self.table_columns or [])
            if column not in (self.table_exclude or [])
        ]


class ProductsTableComponent(BaseTableComponent):
    """Product catalog table fragment."""

    model = m.Product
    table_name = "formint/tables/products"
    table_columns = ["id", "name", "category", "price", "stock_quantity", "tax_rate", "is_active"]
    header_labels = {
        "id": "ID", "name": "Name", "category": "Category", "price": "Price",
        "stock_quantity": "Stock", "tax_rate": "Tax", "is_active": "Active",
    }
    queryset_ordering = ("name",)
    select_related_fields = ("category",)


class CategoriesTableComponent(BaseTableComponent):
    """Product category table fragment."""

    model = m.Category
    table_name = "formint/tables/categories"
    table_columns = ["id", "name", "display_order", "is_active"]
    header_labels = {
        "id": "ID", "name": "Name", "display_order": "Order", "is_active": "Active",
    }
    queryset_ordering = ("display_order", "name")


class CustomersTableComponent(BaseTableComponent):
    """Customer list table fragment."""

    model = m.Customer
    table_name = "formint/tables/customers"
    table_columns = ["id", "full_name", "email", "phone", "loyalty_points", "total_spent", "is_active"]
    header_labels = {
        "id": "ID", "full_name": "Name", "email": "Email", "phone": "Phone",
        "loyalty_points": "Points", "total_spent": "Spent", "is_active": "Active",
    }
    queryset_ordering = ("-created_at",)


class ClientCategoriesTableComponent(BaseTableComponent):
    """Loyalty client category table fragment."""

    model = m.ClientCategory
    table_name = "formint/tables/client_categories"
    table_columns = ["id", "name", "min_points", "points_per_currency", "discount_rate", "is_active"]
    header_labels = {
        "id": "ID", "name": "Name", "min_points": "Min Points",
        "points_per_currency": "Pts/Currency", "discount_rate": "Discount %",
        "is_active": "Active",
    }
    queryset_ordering = ("min_points", "name")


class SalesTableComponent(BaseTableComponent):
    """Recent sales table fragment."""

    model = m.Sale
    table_name = "formint/tables/sales"
    table_columns = ["id", "sale_date", "customer", "payment_method", "status", "total"]
    header_labels = {
        "id": "ID", "sale_date": "Date", "customer": "Customer",
        "payment_method": "Payment", "status": "Status", "total": "Total",
    }
    queryset_ordering = ("-sale_date",)
    select_related_fields = ("customer",)


class SuppliersTableComponent(BaseTableComponent):
    """Supplier list table fragment."""

    model = m.Supplier
    table_name = "formint/tables/suppliers"
    table_columns = ["id", "name", "contact_name", "email", "phone", "is_active"]
    header_labels = {
        "id": "ID", "name": "Name", "contact_name": "Contact", "email": "Email",
        "phone": "Phone", "is_active": "Active",
    }
    queryset_ordering = ("name",)


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


def render_table_rows(component: BaseTableComponent, limit: int = 50) -> list[dict]:
    """Render ORM data to table-ready rows via django-fusion RowGenerator."""
    generator = RowGenerator(
        component.get_table_data()[:limit],
        columns=component.table_columns,
    )
    return generator.get_rows()
