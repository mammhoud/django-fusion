"""
Functional-style CRUD operations on Django models.

The bare functions in this module mirror :class:`CRUDService` and
:class:`BatchCRUDService`. New code should prefer the functions because they
compose well and don't require instantiating a service class with model
introspection.

Canonical imports::

    from django_fusion.services.crud import CRUDService
    from django_fusion.services.crud import BatchCRUDService
    from django_fusion.services.crud import (
        bulk_create, bulk_update, bulk_delete, upsert,
        get_or_create, get_by_pk, get_one, update_one, delete_one,
        execute_batch, get_pk_info, PrimaryKeyInfo,
    )
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from django.db import models
from django.db.models import UUIDField

from .base import BaseService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Primary-key introspection (pure)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PrimaryKeyInfo:
    """Resolved primary-key metadata for a model."""

    name: str
    type: str  # 'id' or 'uuid'


def get_pk_info(model: type[models.Model]) -> PrimaryKeyInfo:
    """Inspect a model's primary key without any class-level state."""
    pk = model._meta.pk
    return PrimaryKeyInfo(
        name=pk.name,
        type='uuid' if isinstance(pk, UUIDField) else 'id',
    )


def normalize_pk_kwargs(model: type[models.Model], kwargs: dict[str, Any]) -> dict[str, Any]:
    """Map ``id`` / ``uuid`` aliases to the actual PK field name."""
    info = get_pk_info(model)
    normalized = kwargs.copy()
    if info.name not in normalized:
        if info.type == 'uuid' and 'id' in normalized:
            normalized[info.name] = normalized.pop('id')
        elif info.type == 'id' and 'uuid' in normalized:
            normalized[info.name] = normalized.pop('uuid')
    return normalized


def get_pk_value_from_data(
    model: type[models.Model],
    data: dict[str, Any],
    _pk_info: PrimaryKeyInfo | None = None,
) -> Any | None:
    """Find the PK value inside a data dict, falling back to ``id`` / ``uuid`` aliases.

    ``_pk_info`` is an internal optimisation: pass a pre-resolved
    :class:`PrimaryKeyInfo` to avoid a second ``get_pk_info`` introspection.
    """
    info = _pk_info or get_pk_info(model)
    if info.name in data:
        return data[info.name]
    if info.type == 'uuid' and 'id' in data:
        return data['id']
    if info.type == 'id' and 'uuid' in data:
        return data['uuid']
    return None


# ---------------------------------------------------------------------------
# Functional CRUD operations
# ---------------------------------------------------------------------------


def bulk_create(
    model: type[models.Model],
    objects_data: list[dict[str, Any]],
    batch_size: int = 1000,
) -> tuple[bool, list[models.Model], str]:
    """Bulk-create objects in batches."""
    try:
        created: list[models.Model] = []
        for index in range(0, len(objects_data), batch_size):
            batch = objects_data[index:index + batch_size]
            objs = [model(**data) for data in batch]
            created.extend(model.objects.bulk_create(objs, batch_size))
        return True, created, f"Created {len(created)} objects"
    except Exception as exc:
        logger.error(f"Bulk create failed for {model.__name__}: {exc}")
        return False, [], str(exc)


def bulk_update(
    model: type[models.Model],
    objects: list[models.Model],
    update_fields: list[str],
    batch_size: int = 1000,
) -> tuple[bool, int, str]:
    """Bulk-update existing objects, batching by ``batch_size``."""
    try:
        updated = 0
        for index in range(0, len(objects), batch_size):
            batch = objects[index:index + batch_size]
            model.objects.bulk_update(batch, update_fields, batch_size)
            updated += len(batch)
        return True, updated, f"Updated {updated} objects"
    except Exception as exc:
        logger.error(f"Bulk update failed for {model.__name__}: {exc}")
        return False, 0, str(exc)


def bulk_delete(
    model: type[models.Model],
    identifiers: list[Any],
    field: str | None = None,
) -> tuple[bool, int, str]:
    """Bulk-delete objects whose ``field`` value is in ``identifiers``."""
    try:
        if field in (None, 'id', 'uuid'):
            field = get_pk_info(model).name
        qs = model.objects.filter(**{f"{field}__in": identifiers})
        count = qs.count()
        qs.delete()
        return True, count, f"Deleted {count} objects"
    except Exception as exc:
        logger.error(f"Bulk delete failed for {model.__name__}: {exc}")
        return False, 0, str(exc)


def upsert(
    model: type[models.Model],
    data: dict[str, Any],
    match_fields: list[str] | None = None,
    update_fields: list[str] | None = None,
    _pk_info: PrimaryKeyInfo | None = None,
) -> tuple[bool, models.Model | None, str]:
    """Update if a row matches ``match_fields``, otherwise create.

    ``_pk_info`` is an internal optimisation: callers that have already
    resolved the model's primary key can pass it back to avoid a second
    ``get_pk_info`` introspection call.
    """
    try:
        pk_info = _pk_info or get_pk_info(model)
        if match_fields:
            match_fields = [
                pk_info.name if field_name in ('id', 'uuid') else field_name
                for field_name in match_fields
            ]
        else:
            match_fields = [pk_info.name]

        pk_value = get_pk_value_from_data(model, data, _pk_info=pk_info)
        if pk_value is not None and pk_info.name not in data:
            data[pk_info.name] = pk_value

        match_filter = {
            field_name: data[field_name]
            for field_name in match_fields
            if field_name in data and data[field_name] is not None
        }

        if match_filter:
            try:
                obj = model.objects.get(**match_filter)
                update_fields = update_fields or [
                    field_name for field_name in data if field_name != pk_info.name
                ]
                for field_name in update_fields:
                    if field_name in data:
                        setattr(obj, field_name, data[field_name])
                obj.save()
                return True, obj, "Updated existing object"
            except model.DoesNotExist:
                pass

        obj = model.objects.create(**data)
        return True, obj, "Created new object"
    except Exception as exc:
        logger.error(f"Upsert failed for {model.__name__}: {exc}")
        return False, None, str(exc)


def get_or_create(
    model: type[models.Model],
    defaults: dict[str, Any] | None = None,
    **kwargs,
) -> tuple[models.Model, bool]:
    """``Model.objects.get_or_create`` with PK-aliased kwargs."""
    kwargs = normalize_pk_kwargs(model, kwargs)
    return model.objects.get_or_create(defaults=defaults, **kwargs)


def get_by_pk(model: type[models.Model], value: Any) -> models.Model | None:
    """Return the row whose PK matches ``value`` or ``None``."""
    try:
        return model.objects.get(**{get_pk_info(model).name: value})
    except model.DoesNotExist:
        logger.debug(f"No {model.__name__} found with PK={value}")
        return None
    except Exception as exc:
        logger.error(f"Error getting {model.__name__} by PK: {exc}")
        return None


def get_one(
    model: type[models.Model],
    identifier: Any = None,
    **kwargs,
) -> models.Model | None:
    """Filter with PK-aliased kwargs, returning the first match.

    Prefer :func:`get_first` over this function when you only need the
    ``filter(...).first()`` semantics — :func:`get_one` is kept as alias for
    historical imports.
    """
    return get_first(model, identifier=identifier, **kwargs)


def get_first(
    model: type[models.Model],
    identifier: Any = None,
    **kwargs,
) -> models.Model | None:
    """Filter with PK-aliased kwargs, returning the first match."""
    kwargs = normalize_pk_kwargs(model, kwargs)
    if identifier is not None:
        pk_name = get_pk_info(model).name
        if pk_name not in kwargs:
            kwargs[pk_name] = identifier
    return model.objects.filter(**kwargs).first()


def update_one(
    model: type[models.Model],
    identifier: Any,
    data: dict[str, Any],
    **kwargs,
) -> models.Model | None:
    """Update one row by PK; strip PK aliases from ``data`` before saving."""
    pk_info = get_pk_info(model)
    kwargs = normalize_pk_kwargs(model, kwargs)
    pk_value = identifier if identifier is not None else kwargs.pop(pk_info.name, None)
    if pk_value is None:
        logger.error(f"No identifier provided for update on {model.__name__}")
        return None
    for field_name in (pk_info.name, 'id', 'uuid'):
        data.pop(field_name, None)
    obj = get_by_pk(model, pk_value)
    if obj is None:
        return None
    for field_name, value in data.items():
        setattr(obj, field_name, value)
    obj.save()
    return obj


def delete_one(
    model: type[models.Model],
    identifier: Any,
    **kwargs,
) -> bool:
    """Delete one row by PK. Returns ``True`` on success."""
    pk_info = get_pk_info(model)
    kwargs = normalize_pk_kwargs(model, kwargs)
    pk_value = identifier if identifier is not None else kwargs.pop(pk_info.name, None)
    if pk_value is None:
        logger.error(f"No identifier provided for delete on {model.__name__}")
        return False
    obj = get_by_pk(model, pk_value)
    if obj is None:
        return False
    obj.delete()
    return True


def execute_batch(
    model: type[models.Model],
    operations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run a list of CRUD ``operations`` sequentially and aggregate the result."""
    results = [_execute_single_op(model, op) for op in operations]
    return {
        "total_operations": len(operations),
        "successful": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "results": results,
    }


def _execute_single_op(model: type[models.Model], operation: dict[str, Any]) -> dict[str, Any]:
    """Dispatch one ``create`` / ``update`` / ``delete`` operation."""
    op_type = operation.get("type")
    data = operation.get("data", {})
    try:
        if op_type == "create":
            obj = model.objects.create(**data)
            return {"success": True, "type": op_type, "object": obj}
        if op_type == "update":
            pk_value = get_pk_value_from_data(model, data)
            if pk_value is None:
                return {"success": False, "error": "Missing identifier"}
            pk_info = get_pk_info(model)
            update_data = {
                k: v for k, v in data.items()
                if k not in (pk_info.name, 'id', 'uuid')
            }
            obj = update_one(model, pk_value, update_data)
            return {"success": True, "type": op_type, "object": obj}
        if op_type == "delete":
            pk_value = get_pk_value_from_data(model, data)
            if pk_value is None:
                return {"success": False, "error": "Missing identifier"}
            return {"success": delete_one(model, pk_value), "type": op_type}
        return {"success": False, "error": f"Unknown operation type: {op_type}"}
    except Exception as exc:
        return {"success": False, "error": str(exc), "type": op_type}


# ---------------------------------------------------------------------------
# Service classes — thin facades for backwards compatibility
# ---------------------------------------------------------------------------


class CRUDService(BaseService):
    """
    Backwards-compatible service wrapper around the bare CRUD functions.

    New code should call the module-level functions directly.
    """

    service_name = "crud_service"

    def __init__(self, model_class: type = None):
        super().__init__(model_class)
        self._pk_info: PrimaryKeyInfo | None = None

    def _ensure_pk_info(self) -> PrimaryKeyInfo:
        if self._pk_info is None:
            self._pk_info = get_pk_info(self.model_class)
        return self._pk_info

    @property
    def pk_name(self) -> str:
        return self._ensure_pk_info().name

    @property
    def pk_type(self) -> str:
        return self._ensure_pk_info().type

    def _normalize_pk_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        return normalize_pk_kwargs(self.model_class, kwargs)

    def _get_pk_value_from_data(self, data: dict[str, Any]) -> Any | None:
        return get_pk_value_from_data(self.model_class, data)

    def execute(self, operation: str, **kwargs) -> Any:
        kwargs = normalize_pk_kwargs(self.model_class, kwargs)
        if operation == "bulk_create":
            return self.bulk_create(**kwargs)
        if operation == "bulk_update":
            return self.bulk_update(**kwargs)
        if operation == "bulk_delete":
            return self.bulk_delete(**kwargs)
        if operation == "upsert":
            return self.upsert(**kwargs)
        return super().execute(operation, **kwargs)

    def bulk_create(
        self,
        objects_data: list[dict[str, Any]],
        batch_size: int = 1000,
        **kwargs,
    ) -> tuple[bool, list[models.Model], str]:
        return bulk_create(self.model_class, objects_data, batch_size=batch_size)

    def bulk_update(
        self,
        objects: list[models.Model],
        update_fields: list[str],
        batch_size: int = 1000,
        **kwargs,
    ) -> tuple[bool, int, str]:
        return bulk_update(self.model_class, objects, update_fields, batch_size=batch_size)

    def bulk_delete(
        self,
        identifiers: list[Any],
        field: str = "id",
        **kwargs,
    ) -> tuple[bool, int, str]:
        return bulk_delete(self.model_class, identifiers, field)

    def upsert(
        self,
        data: dict[str, Any],
        match_fields: list[str] = None,
        update_fields: list[str] = None,
        **kwargs,
    ) -> tuple[bool, models.Model | None, str]:
        return upsert(self.model_class, data, match_fields, update_fields)

    def get_or_create(
        self,
        defaults: dict[str, Any] = None,
        **kwargs,
    ) -> tuple[models.Model, bool]:
        return get_or_create(self.model_class, defaults, **kwargs)

    def get_by_pk(self, value: Any) -> models.Model | None:
        return get_by_pk(self.model_class, value)

    def get(self, identifier: Any, **kwargs) -> models.Model | None:
        """Get one row, preserving the legacy ``BaseService.get`` semantics.

        Calls the model's manager ``get_by_field`` first when available
        (matching the pre-refactor behaviour that plugins and subclasses
        could override). Falls back to :func:`get_first` only when the
        manager lacks the custom accessor, so the standard Django usage path
        keeps working even if ``get_by_field`` is not installed.
        """
        kwargs = normalize_pk_kwargs(self.model_class, kwargs)
        manager = self.model_class.objects
        if identifier is not None:
            pk_name = get_pk_info(self.model_class).name
            if pk_name not in kwargs:
                kwargs[pk_name] = identifier
        if hasattr(manager, "get_by_field"):
            return manager.get_by_field(identifier, **kwargs)
        return get_first(self.model_class, identifier=identifier, **kwargs)

    def update(
        self,
        identifier: Any,
        data: dict[str, Any],
        **kwargs,
    ) -> models.Model | None:
        return update_one(self.model_class, identifier, data, **kwargs)

    def delete(self, identifier: Any, **kwargs) -> bool:
        return delete_one(self.model_class, identifier, **kwargs)


class BatchCRUDService(CRUDService):
    """
    Backwards-compatible batch executor wrapper.

    New code should call :func:`execute_batch` directly. The
    ``transaction_required`` flag is honoured at the caller; operations are
    always run sequentially within :func:`execute_batch`.
    """

    service_name = "batch_crud_service"

    def execute_batch(
        self,
        operations: list[dict[str, Any]],
        transaction_required: bool = True,
        **kwargs,
    ) -> dict[str, Any]:
        return execute_batch(self.model_class, operations)

    def _execute_single(self, operation: dict[str, Any]) -> dict[str, Any]:
        return _execute_single_op(self.model_class, operation)
