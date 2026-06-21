"""
CRUD services for database operations.

Canonical imports::
    from django_osoul.core.services import CRUDService
    from django_osoul.core.services import BatchCRUDService
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from django.db import models
from django.db.models import UUIDField

from .base import BaseService

logger = logging.getLogger(__name__)


class CRUDService(BaseService):
    """
    Advanced CRUD service with automatic primary key handling.

    Canonical import: from django_osoul.core.services import CRUDService
    """

    service_name = "crud_service"

    def __init__(self, model_class: type = None):
        super().__init__(model_class)
        self._setup_pk_info()

    def _setup_pk_info(self) -> None:
        """Setup primary key information for the model."""
        if not hasattr(self, '_pk_info'):
            pk = self.model_class._meta.pk
            self._pk_info = {
                'name': pk.name,
                'type': 'uuid' if isinstance(pk, UUIDField) else 'id',
                'field_type': type(pk)
            }
            logger.debug(
                f"PK info for {self.model_class.__name__}: "
                f"name={self._pk_info['name']}, type={self._pk_info['type']}"
            )

    @property
    def pk_name(self) -> str:
        """Get primary key field name."""
        self._setup_pk_info()
        return self._pk_info['name']

    @property
    def pk_type(self) -> str:
        """Get primary key type ('id' or 'uuid')."""
        self._setup_pk_info()
        return self._pk_info['type']

    def _normalize_pk_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize PK kwargs to use actual PK field name.

        Maps 'id' or 'uuid' kwargs to the actual PK field name.
        """
        normalized = kwargs.copy()

        # If PK field name is not in kwargs, check for common aliases
        if self.pk_name not in normalized:
            # Check if 'id' was provided but PK is 'uuid'
            if 'id' in normalized and self.pk_type == 'uuid':
                normalized[self.pk_name] = normalized.pop('id')
                logger.debug(f"Mapped 'id' to PK field '{self.pk_name}'")
            # Check if 'uuid' was provided but PK is 'id'
            elif 'uuid' in normalized and self.pk_type == 'id':
                normalized[self.pk_name] = normalized.pop('uuid')
                logger.debug(f"Mapped 'uuid' to PK field '{self.pk_name}'")

        return normalized

    def _get_pk_value_from_data(self, data: Dict[str, Any]) -> Optional[Any]:
        """Extract PK value from data dictionary."""
        # First try actual PK field
        if self.pk_name in data:
            return data[self.pk_name]

        # Then try common aliases
        if self.pk_type == 'uuid' and 'id' in data:
            return data['id']
        elif self.pk_type == 'id' and 'uuid' in data:
            return data['uuid']

        return None

    def execute(self, operation: str, **kwargs) -> Any:
        """Execute CRUD operation."""
        # Normalize PK kwargs before execution
        kwargs = self._normalize_pk_kwargs(kwargs)

        if operation == "bulk_create":
            return self.bulk_create(**kwargs)
        elif operation == "bulk_update":
            return self.bulk_update(**kwargs)
        elif operation == "bulk_delete":
            return self.bulk_delete(**kwargs)
        elif operation == "upsert":
            return self.upsert(**kwargs)
        else:
            return super().execute(operation, **kwargs)

    def bulk_create(
        self,
        objects_data: List[Dict[str, Any]],
        batch_size: int = 1000,
        **kwargs,
    ) -> Tuple[bool, List[models.Model], str]:
        """
        Bulk create objects.
        """
        try:
            created_objects = []

            for i in range(0, len(objects_data), batch_size):
                batch = objects_data[i:i + batch_size]
                objects = [self.model_class(**data) for data in batch]
                created = self.model_class.objects.bulk_create(objects, batch_size)
                created_objects.extend(created)

            return True, created_objects, f"Created {len(created_objects)} objects"

        except Exception as e:
            logger.error(f"Bulk create failed for {self.model_class.__name__}: {e}")
            return False, [], str(e)

    def bulk_update(
        self,
        objects: List[models.Model],
        update_fields: List[str],
        batch_size: int = 1000,
        **kwargs,
    ) -> Tuple[bool, int, str]:
        """
        Bulk update objects.
        """
        try:
            updated_count = 0

            for i in range(0, len(objects), batch_size):
                batch = objects[i:i + batch_size]
                self.model_class.objects.bulk_update(batch, update_fields, batch_size)
                updated_count += len(batch)

            return True, updated_count, f"Updated {updated_count} objects"

        except Exception as e:
            logger.error(f"Bulk update failed for {self.model_class.__name__}: {e}")
            return False, 0, str(e)

    def bulk_delete(
        self,
        identifiers: List[Any],
        field: str = "id",
        **kwargs,
    ) -> Tuple[bool, int, str]:
        """
        Bulk delete objects.
        """
        try:
            # Normalize field name
            if field in ['id', 'uuid']:
                field = self.pk_name

            # Get objects to delete
            filter_kwargs = {f"{field}__in": identifiers}
            objects = self.manager.filter(**filter_kwargs)
            count = objects.count()

            # Delete
            objects.delete()

            return True, count, f"Deleted {count} objects"

        except Exception as e:
            logger.error(f"Bulk delete failed for {self.model_class.__name__}: {e}")
            return False, 0, str(e)

    def upsert(
        self,
        data: Dict[str, Any],
        match_fields: List[str] = None,
        update_fields: List[str] = None,
        **kwargs,
    ) -> Tuple[bool, Optional[models.Model], str]:
        """
        Upsert operation (update or insert).
        """
        try:
            # Normalize match_fields to use actual PK field name
            if match_fields:
                normalized_match_fields = []
                for field in match_fields:
                    if field in ['id', 'uuid']:
                        normalized_match_fields.append(self.pk_name)
                    else:
                        normalized_match_fields.append(field)
                match_fields = normalized_match_fields
            else:
                # Default to PK field
                match_fields = [self.pk_name]

            # Get PK value from data
            pk_value = self._get_pk_value_from_data(data)
            if pk_value is not None and self.pk_name not in data:
                data[self.pk_name] = pk_value

            # Build match filter
            match_filter = {}
            for field in match_fields:
                if field in data and data[field] is not None:
                    match_filter[field] = data[field]

            if match_filter:
                # Try to get existing object
                try:
                    obj = self.manager.get(**match_filter)

                    # Update if exists
                    update_fields = update_fields or [f for f in data.keys() if f != self.pk_name]
                    for field in update_fields:
                        if field in data:
                            setattr(obj, field, data[field])

                    obj.save()
                    return True, obj, "Updated existing object"

                except self.model_class.DoesNotExist:
                    pass

            # Create new object
            obj = self.model_class.objects.create(**data)
            return True, obj, "Created new object"

        except Exception as e:
            logger.error(f"Upsert failed for {self.model_class.__name__}: {e}")
            return False, None, str(e)

    def get_or_create(
        self,
        defaults: Dict[str, Any] = None,
        **kwargs,
    ) -> Tuple[models.Model, bool]:
        """
        Get or create object.
        """
        try:
            # Normalize PK kwargs
            kwargs = self._normalize_pk_kwargs(kwargs)
            return self.manager.get_or_create(defaults=defaults, **kwargs)
        except Exception as e:
            logger.error(f"Get or create failed for {self.model_class.__name__}: {e}")
            raise

    def get_by_pk(self, value: Any) -> Optional[models.Model]:
        """
        Get object by primary key value.

        Args:
            value: Primary key value (could be ID or UUID)

        Returns:
            Object if found, None otherwise
        """
        try:
            return self.manager.get(**{self.pk_name: value})
        except self.model_class.DoesNotExist:
            logger.debug(f"No {self.model_class.__name__} found with {self.pk_name}={value}")
            return None
        except Exception as e:
            logger.error(f"Error getting {self.model_class.__name__} by {self.pk_name}: {e}")
            return None

    def get(self, identifier: Any, **kwargs) -> Optional[models.Model]:
        """Get object by identifier with PK normalization."""
        # Normalize PK kwargs
        kwargs = self._normalize_pk_kwargs(kwargs)

        # If identifier is provided directly and no PK in kwargs, use it as PK value
        if identifier is not None and self.pk_name not in kwargs:
            kwargs[self.pk_name] = identifier

        return super().get(**kwargs)

    def update(
        self,
        identifier: Any,
        data: Dict[str, Any],
        **kwargs,
    ) -> Optional[models.Model]:
        """Update existing object with PK normalization."""
        # Normalize PK kwargs
        kwargs = self._normalize_pk_kwargs(kwargs)

        # Get PK value from identifier or kwargs
        pk_value = identifier
        if identifier is None and self.pk_name in kwargs:
            pk_value = kwargs.pop(self.pk_name)

        if pk_value is None:
            logger.error(f"No identifier provided for update on {self.model_class.__name__}")
            return None

        # Remove PK from data if present (should not update PK)
        if self.pk_name in data:
            del data[self.pk_name]
        if 'id' in data:
            del data['id']
        if 'uuid' in data:
            del data['uuid']

        # Use our get_by_pk method
        obj = self.get_by_pk(pk_value)
        if obj:
            for field, value in data.items():
                setattr(obj, field, value)
            obj.save()
        return obj

    def delete(self, identifier: Any, **kwargs) -> bool:
        """Delete object with PK normalization."""
        # Normalize PK kwargs
        kwargs = self._normalize_pk_kwargs(kwargs)

        # Get PK value from identifier or kwargs
        pk_value = identifier
        if identifier is None and self.pk_name in kwargs:
            pk_value = kwargs.pop(self.pk_name)

        if pk_value is None:
            logger.error(f"No identifier provided for delete on {self.model_class.__name__}")
            return False

        obj = self.get_by_pk(pk_value)
        if obj:
            obj.delete()
            return True
        return False


class BatchCRUDService(CRUDService):
    """
    Batch CRUD operations service.

    Canonical import: from django_osoul.core.services import BatchCRUDService
    """

    service_name = "batch_crud_service"

    def execute_batch(
        self,
        operations: List[Dict[str, Any]],
        transaction_required: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute batch of CRUD operations.
        """
        results = []

        if transaction_required:
            for op in operations:
                result = self._execute_single(op)
                results.append(result)
        else:
            for op in operations:
                result = self._execute_single(op)
                results.append(result)

        return {
            "total_operations": len(operations),
            "successful": len([r for r in results if r.get("success")]),
            "failed": len([r for r in results if not r.get("success")]),
            "results": results,
        }

    def _execute_single(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single operation."""
        op_type = operation.get("type")
        data = operation.get("data", {})

        try:
            if op_type == "create":
                obj = self.create(data)
                return {"success": True, "type": op_type, "object": obj}
            elif op_type == "update":
                # Extract identifier from data
                pk_value = self._get_pk_value_from_data(data)
                if pk_value:
                    # Remove PK from update data
                    update_data = data.copy()
                    for pk_field in [self.pk_name, 'id', 'uuid']:
                        if pk_field in update_data:
                            del update_data[pk_field]

                    obj = self.update(pk_value, update_data)
                    return {"success": True, "type": op_type, "object": obj}
                else:
                    return {"success": False, "error": "Missing identifier"}
            elif op_type == "delete":
                pk_value = self._get_pk_value_from_data(data)
                if pk_value:
                    success = self.delete(pk_value)
                    return {"success": success, "type": op_type}
                else:
                    return {"success": False, "error": "Missing identifier"}
            else:
                return {"success": False, "error": f"Unknown operation type: {op_type}"}

        except Exception as e:
            return {"success": False, "error": str(e), "type": op_type}
