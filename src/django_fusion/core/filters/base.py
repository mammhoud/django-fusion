"""
Base filters for query operations.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db import models
from django.db.models import QuerySet

try:
    import django_filters
except ImportError:
    django_filters = None

if TYPE_CHECKING:
    import django_filters as _django_filters


class BaseFilterMethod:
    """
    Base filter method with field auto-detection.
    """

    def __init__(
        self,
        model_class: Type[models.Model],
        filter_value: Any,
        filter_field: Optional[str] = None,
        filterset_class: Optional[Type] = None,
        filter_data: Optional[Dict[str, Any]] = None,
        base_queryset: Optional[QuerySet] = None,
    ):
        self.model_class = model_class
        self.filter_value = filter_value
        self.filter_field = filter_field or self._detect_field()
        self.filterset_class = filterset_class
        self.filter_data = filter_data or {}
        self.queryset = base_queryset or self.model_class.objects.all()

        # Validate field exists
        self._validate_field_exists(self.filter_field)

    def _detect_field(self) -> str:
        """Auto-detect field based on value type."""
        if isinstance(self.filter_value, uuid.UUID):
            return "uuid"
        elif isinstance(self.filter_value, str):
            # Check for common string fields
            if self._has_field("code"):
                return "code"
            elif self._has_field("slug"):
                return "slug"
            elif self._has_field("email"):
                return "email"
        elif isinstance(self.filter_value, int):
            return "pk"

        raise ValueError("Unable to infer field type. Provide filter_field explicitly.")

    def _has_field(self, field_name: str) -> bool:
        """Check if model has field."""
        try:
            self.model_class._meta.get_field(field_name)
            return True
        except FieldDoesNotExist:
            return False

    def _validate_field_exists(self, field_name: str) -> None:
        """Validate that field exists on model."""
        try:
            self.model_class._meta.get_field(field_name)
        except FieldDoesNotExist:
            raise ValueError(
                f"Field '{field_name}' not found on model '{self.model_class.__name__}'"
            )

    def apply_filterset(self, qs: QuerySet) -> QuerySet:
        """Apply FilterSet if provided."""
        if self.filterset_class and self.filter_data:
            if django_filters is None:
                raise ImportError("django-filters is required to use FilterSet functionality")
            filterset = self.filterset_class(self.filter_data, queryset=qs)
            if filterset.is_valid():
                return filterset.qs
        return qs

    def run(self) -> QuerySet:
        """Execute filter and return queryset."""
        base_qs = self.queryset.filter(**{self.filter_field: self.filter_value})
        return self.apply_filterset(base_qs)

    def get(self) -> Optional[models.Model]:
        """Get single object or None."""
        try:
            return self.run().get()
        except ObjectDoesNotExist:
            return None


class DictFilterMethod(BaseFilterMethod):
    """
    Dictionary-based filtering.
    """

    def __init__(
        self,
        model_class: Type[models.Model],
        filters: Dict[str, Any],
        filterset_class: Optional[Type] = None,
        filter_data: Optional[Dict[str, Any]] = None,
        base_queryset: Optional[QuerySet] = None,
    ):
        self.model_class = model_class
        self.filters = filters
        self.filterset_class = filterset_class
        self.filter_data = filter_data or {}
        self.queryset = base_queryset or self.model_class.objects.all()

        # Validate filters are provided
        if not filters:
            raise ValueError("Filters dictionary cannot be empty")

    def run(self) -> QuerySet:
        """Execute filter with multiple criteria."""
        base_qs = self.queryset.filter(**self.filters)
        return self.apply_filterset(base_qs)


class UniversalFilter:
    """
    Universal filter for dynamic model filtering.
    """

    @staticmethod
    def create_filterset_for_model(
        model_class: Type[models.Model],
        field_config: Optional[Dict[str, Any]] = None,
    ) -> Type:
        """
        Create dynamic FilterSet for model.
        """
        if django_filters is None:
            raise ImportError("django-filters is required to use UniversalFilter")

        if field_config is None:
            # Auto-configure based on field types
            field_config = {}
            for field in model_class._meta.get_fields():
                if field.get_internal_type() in ["CharField", "TextField", "EmailField"]:
                    field_config[field.name] = ["exact", "icontains"]
                elif field.get_internal_type() in ["IntegerField", "FloatField", "DecimalField"]:
                    field_config[field.name] = ["exact", "gt", "gte", "lt", "lte"]
                elif field.get_internal_type() == "BooleanField":
                    field_config[field.name] = ["exact"]
                elif field.get_internal_type() in ["DateTimeField", "DateField"]:
                    field_config[field.name] = ["exact", "gt", "gte", "lt", "lte"]

        class DynamicFilterSet(django_filters.FilterSet):
            class Meta:
                model = model_class
                fields = field_config

        return DynamicFilterSet

    @staticmethod
    def filter_model(
        model_class: Type[models.Model],
        filter_data: Dict[str, Any],
        base_queryset: Optional[QuerySet] = None,
    ) -> QuerySet:
        """
        Filter model using dynamic FilterSet.
        """
        filterset_class = UniversalFilter.create_filterset_for_model(model_class)
        filterset = filterset_class(filter_data, queryset=base_queryset or model_class.objects.all())

        if filterset.is_valid():
            return filterset.qs
        else:
            # Return empty queryset if filters are invalid
            return model_class.objects.none()
