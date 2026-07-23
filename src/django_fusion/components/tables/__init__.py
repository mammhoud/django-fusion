"""
django_fusion.components.tables — Table integration with RowGenerator.

Provides:
  - TableMixin: Enhanced mixin for table rendering with ORM data support
  - RowGenerator: Converts ORM objects/queries into table-ready row dicts

Usage::

    from django_fusion.components.tables import TableMixin, RowGenerator

    class ProductReport(RoutableComponent, TableMixin):
        table_name = "products"
        table_columns = ["name", "price", "stock_quantity"]

        def get_table_data(self):
            return Product.objects.filter(is_active=True)
"""

from django_fusion.components.tables.mixins import TableMixin
from django_fusion.components.tables.row_generator import RowGenerator

__all__ = ["TableMixin", "RowGenerator"]
