from __future__ import annotations

import pytest


@pytest.mark.usefixtures("django_bootstrap")
def test_formint_tables_share_the_base_contract():
    """All resources keep their model-specific metadata on one base class."""
    from formint.components import (
        BaseTableComponent,
        ClientCategoriesTableComponent,
        CustomersTableComponent,
        ProductsTableComponent,
        SalesTableComponent,
        SuppliersTableComponent,
        CategoriesTableComponent,
    )

    components = (
        ProductsTableComponent,
        CategoriesTableComponent,
        CustomersTableComponent,
        ClientCategoriesTableComponent,
        SalesTableComponent,
        SuppliersTableComponent,
    )

    assert all(issubclass(component, BaseTableComponent) for component in components)
    assert all(component.paginate_by == 10 for component in components)
    assert all(component.model is not None for component in components)
    assert all(component.queryset_ordering for component in components)


def test_base_headers_preserve_formint_labels(django_bootstrap):
    from formint.components import (
        ClientCategoriesTableComponent,
        ProductsTableComponent,
        SalesTableComponent,
    )

    assert ProductsTableComponent().get_table_headers()[4]["label"] == "Stock"
    assert ClientCategoriesTableComponent().get_table_headers()[3]["label"] == "Pts/Currency"
    assert SalesTableComponent().get_table_headers()[1]["label"] == "Date"


@pytest.mark.usefixtures("django_bootstrap")
@pytest.mark.usefixtures("django_bootstrap")
def test_base_queryset_preserves_resource_query_contracts():
    from formint.components import (
        CategoriesTableComponent,
        ClientCategoriesTableComponent,
        CustomersTableComponent,
        ProductsTableComponent,
        SalesTableComponent,
        SuppliersTableComponent,
    )

    contracts = {
        ProductsTableComponent: (("name",), ("category",)),
        CategoriesTableComponent: (("display_order", "name"), ()),
        CustomersTableComponent: (("-created_at",), ()),
        ClientCategoriesTableComponent: (("min_points", "name"), ()),
        SalesTableComponent: (("-sale_date",), ("customer",)),
        SuppliersTableComponent: (("name",), ()),
    }
    for component, (ordering, related) in contracts.items():
        assert component.queryset_ordering == ordering
        assert component.select_related_fields == related


def test_related_rows_are_loaded_without_extra_queries(category_factory, product_factory):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    from formint.components import ProductsTableComponent

    category = category_factory(name="Coffee (related)", slug="coffee-related")
    product_factory(name="Cappuccino (related)", category=category)

    with CaptureQueriesContext(connection) as captured:
        products = list(ProductsTableComponent().get_table_data())
        assert str(products[-1].category) == "Coffee (related)"

    assert len(captured) == 1


@pytest.mark.usefixtures("django_bootstrap")
def test_base_context_normalizes_rows_and_reuses_query_source(category_factory, product_factory):
    from formint.components import ProductsTableComponent

    category = category_factory(name="Coffee (context)", slug="coffee-context")
    product_factory(name="Espresso (context)", category=category, price="3.50", stock_quantity=4)

    component = ProductsTableComponent()
    existing_total = ProductsTableComponent().get_table_data().count()
    context = component.get_table_context_data()

    assert context["pagination"] == {
        "page": 1,
        "per_page": 10,
        "total": existing_total,
        "total_pages": 1,
    }
    context_row = next(
        row for row in context["table_data"] if row["name"] == "Espresso (context)"
    )
    assert context_row["category"] == "Coffee (context)"
    assert context_row["price"] == "$3.50"
    assert context_row["is_active"] == "Yes"
    assert context["pagination"]["total"] == existing_total
    assert any(row["name"] == "Espresso (context)" for row in context["table_data"])
    assert component.get_table_data() is component.get_table_data()

    cached_queryset = component.get_table_data()
    component.reset_table_queryset()
    refreshed_queryset = component.get_table_data()
    assert cached_queryset is not refreshed_queryset


def test_render_table_rows_respects_limit(category_factory, product_factory):
    from formint.components import ProductsTableComponent, render_table_rows

    category = category_factory(name="Coffee (limit)", slug="coffee-limit")
    for name in ("Espresso", "Latte", "Mocha"):
        product_factory(name=name, category=category)

    rows = render_table_rows(ProductsTableComponent(), limit=2)

    assert len(rows) == 2
    assert all("name" in row and "price" in row for row in rows)
