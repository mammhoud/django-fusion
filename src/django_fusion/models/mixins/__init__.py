"""
django_fusion.models.mixins
==========================

Pure abstract Django model mixins with **no application-layer dependencies**.

These mixins only depend on ``django.db.models`` and the Python standard
library.  They are safe to use in any Django project.

Classes
-------
TimestampedModel
    Adds ``created_at`` / ``updated_at`` auto-fields.
SoftDeleteModel
    Soft-delete via ``is_deleted`` / ``deleted_at`` fields.
UUIDPrimaryKeyModel
    Replaces the default integer PK with a UUID.
SoftDeleteMixin
    Soft-delete behaviour as a mixin (use alongside other base models).
AuditMixin
    Tracks ``created_by`` / ``updated_by`` FK references.
StatusMixin
    Adds an ``is_active`` boolean with ``activate()`` / ``deactivate()`` helpers.
DisplayModeMixin
    Adds ``display_mode`` and ``modal_size`` fields for modal vs detail.
"""

import uuid

from django.db import models
from django.utils import timezone

try:
    from .display_mode import DisplayModeMixin  # noqa: F401
except Exception:
    DisplayModeMixin = None  # type: ignore


class TimestampedModel(models.Model):
    """
    Abstract model that records creation and last-update timestamps.

    Fields
    ------
    created_at : DateTimeField
        Set automatically when the record is first saved.
    updated_at : DateTimeField
        Updated automatically on every save.

    Usage::

        class Article(TimestampedModel):
            title = models.CharField(max_length=255)
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract model that supports soft deletion.

    Instead of removing the database row, ``soft_delete()`` sets
    ``is_deleted=True`` and records the deletion timestamp.

    Fields
    ------
    deleted_at : DateTimeField (nullable)
        Timestamp of soft deletion; ``None`` when the record is active.
    is_deleted : BooleanField
        ``True`` when the record has been soft-deleted.

    Methods
    -------
    soft_delete()
        Mark the record as deleted.
    restore()
        Undo a soft deletion.

    Usage::

        class Order(SoftDeleteModel):
            ...

        order.soft_delete()   # hides the record
        order.restore()       # brings it back
    """

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """Mark this record as deleted without removing it from the database."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self) -> None:
        """Restore a previously soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])


class UUIDPrimaryKeyModel(models.Model):
    """
    Abstract model that uses a UUID as the primary key.

    Useful for distributed systems and when integer PKs should not be
    exposed in URLs.

    Fields
    ------
    id : UUIDField
        Auto-generated UUID primary key.

    Usage::

        class Subscription(UUIDPrimaryKeyModel):
            ...
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    Soft-delete mixin intended to be combined with other base models.

    Identical behaviour to :class:`SoftDeleteModel` but named as a *mixin*
    to make the intent clear when composing multiple abstract bases::

        class Post(TimestampedModel, SoftDeleteMixin):
            ...
    """

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """Mark this record as deleted."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])


class AuditMixin(models.Model):
    """
    Abstract mixin that tracks which user created and last modified a record.

    Fields
    ------
    created_by : ForeignKey → auth.User (nullable)
        The user who created this record.
    updated_by : ForeignKey → auth.User (nullable)
        The user who last modified this record.

    Usage::

        class Invoice(TimestampedModel, AuditMixin):
            ...
    """

    created_by = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated",
    )

    class Meta:
        abstract = True


class StatusMixin(models.Model):
    """
    Abstract mixin that adds an ``is_active`` flag with convenience methods.

    Fields
    ------
    is_active : BooleanField
        ``True`` when the record is active (default).

    Methods
    -------
    activate()
        Set ``is_active = True`` and save.
    deactivate()
        Set ``is_active = False`` and save.

    Usage::

        class Coupon(TimestampedModel, StatusMixin):
            code = models.CharField(max_length=20)

        coupon.deactivate()  # expires the coupon
    """

    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True

    def activate(self) -> None:
        """Activate this record."""
        self.is_active = True
        self.save(update_fields=["is_active"])

    def deactivate(self) -> None:
        """Deactivate this record."""
        self.is_active = False
        self.save(update_fields=["is_active"])
