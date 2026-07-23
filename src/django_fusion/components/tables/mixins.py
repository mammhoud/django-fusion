"""
django_fusion.components.tables.mixins — Enhanced TableMixin.

Provides TableMixin for routable components with:
  - Auto-detection of ORM data (QuerySet, Model, list of dicts)
  - Built-in RowGenerator for ORM-to-row conversion
  - Configurable pagination, column selection, and formatting
  - Backward-compatible with existing override methods
"""

from __future__ import annotations

from typing import Any

from django_fusion.components.tables.row_generator import RowGenerator


class TableMixin:
    """Enhanced mixin for rendering tables in routable components.

    Wraps the original ``TableMixin`` from ``comp.routes.forms_tables``
    with ORM data support via ``RowGenerator``.

    Attributes:
        table_name (str | None): Base name for table template lookup.
        table_columns (list[str] | None): Explicit column names.
        table_exclude (list[str] | None): Fields to skip in auto-generation.
        table_formatters (dict | None): Per-column formatting callables.
        paginate_by (int): Items per page (0 = no pagination).
        row_generator_class (type): RowGenerator class to use.
    """

    table_name: str | None = None
    table_headers: list[dict[str, Any]] | None = None
    table_data: list[Any] | None = None
    table_columns: list[str] | None = None
    table_exclude: list[str] | None = None
    table_formatters: dict[str, Any] | None = None
    paginate_by: int = 50
    row_generator_class: type = RowGenerator

    def get_table_name(self) -> str:
        """Get the table template name for lookup.

        Returns:
            Base name without .html extension.
        """
        if self.table_name:
            return self.table_name
        if hasattr(self, "model") and self.model:
            return f"{self.model._meta.model_name}_table"
        raise ValueError(
            f"{self.__class__.__name__} must define table_name or inherit model"
        )

    def get_table_template_names(self) -> list[str]:
        """Resolve table template names with fallback chain.

        Returns:
            List of template names tried in order.
        """
        table_name = self.get_table_name()
        return [
            f"plugins/tables/{table_name}.html",
            "components/table.html",
        ]

    def get_row_generator(self) -> RowGenerator:
        """Instantiate the RowGenerator with configured options.

        Returns:
            Configured RowGenerator instance.
        """
        return self.row_generator_class(
            data=self.get_table_data(),
            columns=self.table_columns,
            exclude=self.table_exclude,
            formatters=self.table_formatters,
        )

    def get_table_headers(self) -> list[dict[str, Any]]:
        """Get table column headers.

        Delegates to RowGenerator for auto-generation when possible.
        Override for fully custom headers.

        Returns:
            List of header dicts with keys: label, key, sortable, width.
        """
        if self.table_headers:
            return self.table_headers

        # Use RowGenerator for auto-generated headers
        gen = self.get_row_generator()
        return gen.get_columns()

    def get_table_data(self):
        """Get table data rows.

        Returns a QuerySet (lazy), list of Model instances, or list of dicts.
        RowGenerator converts to row dicts regardless of input type.

        Override to fetch or process data with custom filtering.
        This is the single source of truth — pagination uses it too.
        """
        if self.table_data is not None:
            return self.table_data
        if hasattr(self, "get_queryset"):
            return self.get_queryset()
        return []

    def get_table_context_data(self) -> dict[str, Any]:
        """Get full table context for template rendering.

        Returns:
            Dictionary with table_name, table_headers, table_data, pagination.
        """
        gen = self.get_row_generator()
        return {
            "table_name": self.get_table_name(),
            "table_headers": self.get_table_headers(),
            "table_data": gen.get_rows(),
            "pagination": self._get_pagination_context() if self.paginate_by > 0 else None,
        }

    def _get_pagination_context(self) -> dict[str, Any] | None:
        """Build pagination context from the data source.

        Returns None if the data source doesn't support pagination.
        Uses ``get_table_data()`` (not a private method) so subclass
        overrides are respected.
        """
        data = self.get_table_data()

        # QuerySet — use .count() for efficient total
        if hasattr(data, "count") and callable(data.count):
            try:
                total = data.count()
            except Exception:
                total = 0
        # List/tuple — use len()
        elif isinstance(data, (list, tuple)):
            total = len(data)
        else:
            return None

        return {
            "page": 1,
            "per_page": self.paginate_by,
            "total": total,
            "total_pages": max(1, (total + self.paginate_by - 1) // self.paginate_by),
        }
