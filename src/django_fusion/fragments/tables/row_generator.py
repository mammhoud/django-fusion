"""
django_fusion.fragments.tables.row_generator — ORM data → table rows.

Converts Django QuerySets, model instances, and lists of dicts/objects
into table-ready row dictionaries with auto-generated column headers.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Callable

from django.db.models import Model, QuerySet
from django.db.models.fields.related import ForeignKey


class RowGenerator:
    """Convert ORM data into table rows with auto-column detection.

    Accepts Django QuerySets, model lists, or plain dicts. Auto-generates
    column definitions from model ``_meta`` or from explicit ``columns``.

    Usage::

        gen = RowGenerator(Product.objects.all(), columns=["name", "price"])
        headers = gen.get_columns()  # [{"key": "name", "label": "Name", ...}]
        rows = gen.get_rows()        # [{"name": "Widget", "price": "$10.00"}]
    """

    def __init__(
        self,
        data: QuerySet | list[Model] | list[dict] | list,
        columns: list[str] | None = None,
        exclude: list[str] | None = None,
        formatters: dict[str, Callable[[Any], Any]] | None = None,
    ) -> None:
        self._data = data
        self._columns = columns
        self._exclude = exclude or []
        self._formatters = formatters or {}
        self._model = self._detect_model()

    def _detect_model(self) -> type[Model] | None:
        """Detect the Django model class from the data source."""
        if isinstance(self._data, QuerySet):
            return self._data.model
        if isinstance(self._data, (list, tuple)) and len(self._data) > 0:
            first = self._data[0]
            if isinstance(first, Model):
                return type(first)
        return None

    def get_columns(self) -> list[dict[str, Any]]:
        """Generate column definitions with labels, keys, and sortability.

        Returns:
            List of column dicts: ``{"key": str, "label": str, "sortable": bool}``
        """
        if self._columns:
            return [
                {
                    "key": col,
                    "label": self._column_label(col),
                    "sortable": True,
                }
                for col in self._columns
                if col not in self._exclude
            ]

        # Auto-generate from model
        columns = []
        if self._model:
            for field in self._model._meta.get_fields():
                if field.name in self._exclude:
                    continue
                # Skip auto-generated, many-to-one, and one-to-many fields
                if field.auto_created or field.many_to_one or field.one_to_many:
                    continue
                columns.append({
                    "key": field.name,
                    "label": self._field_label(field),
                    "sortable": getattr(field, "db_index", False) or field.primary_key,
                })

        # If no model, infer from first row
        if not columns and isinstance(self._data, (list, tuple)) and len(self._data) > 0:
            first = self._data[0]
            if isinstance(first, dict):
                columns = [
                    {"key": k, "label": k.replace("_", " ").title(), "sortable": True}
                    for k in first.keys()
                    if k not in self._exclude
                ]

        return columns

    def get_rows(self) -> list[dict[str, Any]]:
        """Generate row dictionaries from the data source.

        Returns:
            List of row dicts keyed by column name, with values formatted.
        """
        # Resolve columns once (not per-row)
        columns = self.get_columns()
        rows = []
        data_iter = self._data if hasattr(self._data, "__iter__") else [self._data]

        for obj in data_iter:
            row = {}
            for col in columns:
                key = col["key"]
                value = self._extract_value(obj, key)

                # Apply column formatter if defined
                if key in self._formatters:
                    value = self._formatters[key](value)
                else:
                    value = self._default_format(value)

                row[key] = value
            rows.append(row)

        return rows

    # ── Internal helpers ──

    def _extract_value(self, obj, key: str) -> Any:
        """Extract a value from an object by key, supporting dotted paths."""
        if isinstance(obj, dict):
            return obj.get(key, "")

        # Support dotted keys for FK traversal (e.g., "category__name")
        if "__" in key:
            parts = key.split("__")
            value = obj
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part, "")
                else:
                    return ""
            return value if not callable(value) else value()

        return getattr(obj, key, "") if hasattr(obj, key) else ""

    def _field_label(self, field) -> str:
        """Human-readable label from a Django model field.

        Uses Django's verbose_name as-is (already human-readable).
        Avoids title-casing which mangles pre-formatted labels like "SKU".
        """
        if hasattr(field, "verbose_name"):
            return str(field.verbose_name).replace("_", " ")
        return field.name.replace("_", " ")

    def _column_label(self, col_name: str) -> str:
        """Human-readable label for a column name."""
        if self._model:
            try:
                field = self._model._meta.get_field(col_name)
                return str(field.verbose_name).replace("_", " ")
            except Exception:
                pass
        return col_name.replace("_", " ")

    @staticmethod
    def _default_format(value: Any) -> str:
        """Default value formatting for table display."""
        if value is None:
            return "—"
        if isinstance(value, Decimal):
            return f"${float(value):,.2f}"
        if isinstance(value, bool):
            return "Yes" if value else "No"
        if isinstance(value, Model):
            return str(value)
        return str(value)
