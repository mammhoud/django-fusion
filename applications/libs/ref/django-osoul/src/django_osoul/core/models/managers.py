"""
Custom QuerySet and Manager classes for Django Forge.

Provides specialized managers for common patterns like soft delete.
"""

from django.db import models


class SoftDeleteQuerySet(models.QuerySet):
    """
    QuerySet for models using soft delete.

    Provides methods to filter active/deleted records.
    """

    def active(self):
        """Get only non-deleted records."""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Get only deleted records."""
        return self.filter(is_deleted=True)

    def all_with_deleted(self):
        """Get all records including deleted."""
        return self.all()

    def soft_delete(self):
        """Soft delete all records in queryset."""
        return self.update(is_deleted=True, deleted_at=models.F('updated_at'))


class SoftDeleteManager(models.Manager):
    """
    Manager for models using soft delete.

    By default, returns only non-deleted records.
    """

    def get_queryset(self):
        """Override to filter out deleted records by default."""
        return SoftDeleteQuerySet(self.model, using=self._db).active()

    def active(self):
        """Get only non-deleted records."""
        return self.get_queryset()

    def deleted(self):
        """Get only deleted records."""
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()

    def all_with_deleted(self):
        """Get all records including deleted."""
        return SoftDeleteQuerySet(self.model, using=self._db).all()
