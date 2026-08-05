"""
Schema generation for the django-fusion ``apis`` plugin.

Builds ``ModelSchema`` subclasses from Django models automatically so an
API surface can be declared from the model layer without hand-writing a
schema class per resource.

Design
------
* :func:`generate_schema` introspects a Django model's fields and creates a
  ``ModelSchema`` subclass (from ``django_fusion.routes.schemas.model_schema``
  so all django-fusion enhancements — ``create``/``update``/``save`` helpers,
  Pydantic v2 semantics — apply).
* Field set is derived from ``model._meta.fields`` by default; foreign keys
  are exposed as their ``_id`` column (``fk_id``) and choices/read-only
  columns are preserved.
* :class:`SchemaRegistry` caches generated classes per model so repeated
  calls are cheap and stable.

The generated schemas are *output* schemas (read). For write operations
use ``fields`` + ``exclude`` kwargs, or subclass and add ``optional``
fields — mirroring the hand-written ``formint/schemas.py`` pattern.
"""

from __future__ import annotations

import logging
from typing import Any

from django.apps import apps as django_apps
from django.db.models import Model

from django_fusion.routes.schemas.model_schema import ModelSchema

logger = logging.getLogger(__name__)

__all__ = [
    "SchemaRegistry",
    "generate_schema",
    "generate_schemas_for_app",
    "get_schema",
]


def _default_field_names(model: type[Model]) -> list[str]:
    """Return the canonical field list for *model*.

    Uses concrete model fields (the columns), exposing foreign keys as
    ``fk_id`` columns and skipping the reverse-relation synthetic fields.
    """
    names: list[str] = []
    for field in model._meta.concrete_fields:  # type: ignore[attr-defined]
        names.append(field.attname)
    return names


class SchemaRegistry:
    """Registry that caches generated schemas per model class."""

    def __init__(self) -> None:
        self._schemas: dict[type[Model], type[ModelSchema]] = {}

    def get(self, model: type[Model]) -> type[ModelSchema]:
        """Return the cached schema for *model*, generating it if needed."""
        schema = self._schemas.get(model)
        if schema is None:
            schema = generate_schema(model, registry=self)
        return schema

    def register(self, model: type[Model], schema: type[ModelSchema]) -> None:
        """Store *schema* for *model* (overwrites any prior entry)."""
        self._schemas[model] = schema

    def all(self) -> list[tuple[type[Model], type[ModelSchema]]]:
        """Return ``(model, schema)`` pairs in registration order."""
        return list(self._schemas.items())


#: Module-level registry shared by convenience helpers.
_default_registry = SchemaRegistry()


def generate_schema(
    model: type[Model],
    *,
    name: str | None = None,
    fields: list[str] | None = None,
    exclude: list[str] | None = None,
    registry: SchemaRegistry | None = None,
) -> type[ModelSchema]:
    """Generate (and cache) a ``ModelSchema`` subclass for *model*.

    Arguments:
        model: The Django model class to introspect.
        name: Optional schema class name (default ``f"{model.__name__}Schema"``).
        fields: Optional explicit field list (default: all concrete fields).
        exclude: Optional field names to drop from the generated schema.
        registry: Optional registry to cache into (defaults to the module one).

    Returns:
        A new ``ModelSchema`` subclass bound to *model*.
    """
    if fields is None:
        field_names = _default_field_names(model)
    else:
        field_names = list(fields)

    if exclude:
        field_names = [f for f in field_names if f not in exclude]

    schema_name = name or f"{model.__name__}Schema"

    config_attrs: dict[str, Any] = {"model": model, "fields": field_names}
    config = type("Config", (), config_attrs)

    # Pydantic's model metaclass treats classes whose ``__qualname__`` starts
    # with the parent namespace's ``__qualname__`` as nested types and skips
    # the "non-annotated attribute" check. Hand-written ``class Config:``
    # gets this for free; replicate it for dynamic classes so the generated
    # schema passes Pydantic v2 validation.
    config.__module__ = __name__
    config.__qualname__ = f"{schema_name}.Config"

    # ``__module__``/``__qualname__`` are required by Pydantic's model
    # construction (private-attribute scoping + nested-type detection). Point
    # them at this module so dynamic schemas behave like hand-written ones.
    schema = type(
        schema_name,
        (ModelSchema,),
        {
            "Config": config,
            "__module__": __name__,
            "__qualname__": schema_name,
        },
    )

    reg = registry or _default_registry
    reg.register(model, schema)
    return schema


def generate_schemas_for_app(
    app_label: str,
    *,
    registry: SchemaRegistry | None = None,
) -> dict[str, type[ModelSchema]]:
    """Generate schemas for every model of a Django app config.

    Returns a ``{model_name: schema}`` mapping for all models registered
    under ``app_label``.
    """
    config = django_apps.get_app_config(app_label)
    result: dict[str, type[ModelSchema]] = {}
    for model in config.get_models():
        try:
            result[model.__name__] = generate_schema(model, registry=registry)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("apis: failed to generate schema for %s: %s", model, exc)
    return result


def get_schema(model: type[Model]) -> type[ModelSchema]:
    """Convenience: return the cached/generated schema for *model*."""
    return _default_registry.get(model)
