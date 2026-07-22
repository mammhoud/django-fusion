"""
DataToken — Sync-tagging model for database rows.

A **DataToken** acts as a lightweight tag/marker on any database row that
needs to be synchronised to an upstream master (e.g. pos-cloud).  It supports:

*   **Generic foreign-key tagging** — tag *any* model instance via
    ``content_type`` / ``object_id`` (supports both integer and UUID PKs).
*   **Parent/child tree ordering** — link related rows (invoice → invoice items)
    so they are synced in dependency order.
*   **Node-scoped batching** — group rows by ``node_id`` for per-device sync
    windows.
*   **Progress tracking** — ``sync_status``, ``retry_count``, ``error_message``,
    ``synced_at``.
*   **Auto-untag on sync** — a ``post_save`` signal on the project's
    ``SyncLog`` model (or explicit ``mark_synced()`` call) marks the tag
    as synced once the upstream confirms receipt, preserving the audit trail.

Primary lookup field
--------------------
The ``token`` field is the **first lookup key**.  It is a unique,
human-readable identifier (e.g. ``"inv_42_node_abc"``) that ties a
batch of related rows together.

Usage (tagging a row)::

    from django_fusion.core.models import DataToken

    DataToken.objects.tag_row(
        model_instance=invoice,
        token="inv_42_node_abc",
        node_id="pos-solo-001",
        sync_order=1,
    )
    # Tag each line item as a child of the invoice token
    for item in invoice.items.all():
        DataToken.objects.tag_row(
            model_instance=item,
            token="inv_42_node_abc__item_%s" % item.id,
            node_id="pos-solo-001",
            sync_order=2,
            parent_token=DataToken.objects.get(token="inv_42_node_abc"),
        )

Usage (getting a sync batch)::

    batch = DataToken.objects.sync_batch(node_id="pos-solo-001", limit=100)
    for token in batch:
        push(token.content_object)
        token.mark_synced()

Signals (optional)
------------------
If your project has a ``SyncLog`` model whose ``status`` flips to
``"success"`` after a confirmed push, connect the built-in handler::

    # In your AppConfig.ready():
    from django_fusion.core.models import sync_log_success_handler
    from django.db.models.signals import post_save
    post_save.connect(sync_log_success_handler, sender=SyncLog)
"""

from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, ClassVar

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

logger = logging.getLogger("django_fusion.datatoken")


# ===========================================================================
# Manager
# ===========================================================================


class DataTokenQuerySet(models.QuerySet):
    """QuerySet with sync-aware chainable methods."""

    def unsynced(self) -> DataTokenQuerySet:
        """Return tokens that still need syncing."""
        return self.filter(sync_status=DataToken.Status.PENDING)

    def for_node(self, node_id: str) -> DataTokenQuerySet:
        """Filter tokens belonging to a specific node/device."""
        return self.filter(node_id=node_id)

    def ordered(self) -> DataTokenQuerySet:
        """Order by sync_order then creation date (deterministic)."""
        return self.order_by("sync_order", "created_at")

    def roots(self) -> DataTokenQuerySet:
        """Return only root tokens (no parent — top-level sync rows)."""
        return self.filter(parent__isnull=True)

    def children_of(self, parent_token) -> DataTokenQuerySet:
        """Return direct children of a parent token."""
        return self.filter(parent=parent_token).ordered()


class DataTokenManager(models.Manager.from_queryset(DataTokenQuerySet)):
    """Manager with convenience batch helpers."""

    def sync_batch(self, node_id: str, limit: int = 100) -> DataTokenQuerySet:
        """Return the next ordered batch of unsynced root tokens for a node.

        Only root tokens are returned to preserve parent→child ordering.
        The caller should iterate children after pushing the root.
        """
        return (
            self.get_queryset()
            .unsynced()
            .for_node(node_id)
            .roots()
            .ordered()[:limit]
        )

    def tag_row(
        self,
        model_instance,
        token: str,
        node_id: str,
        sync_order: int = 0,
        parent_token=None,
        metadata: dict | None = None,
    ) -> DataToken:
        """Tag *model_instance* with a DataToken for sync tracking.

        Args:
            model_instance: Any Django model instance.
            token: Unique human-readable sync-token (primary lookup).
            node_id: Identifier of the node/device that owns this row.
            sync_order: Order within the sync batch (lower = first).
            parent_token: Optional parent DataToken (for tree linking).
            metadata: Arbitrary JSON-serialisable extra data.
        """
        ct = ContentType.objects.get_for_model(model_instance)
        return self.create(
            token=token,
            node_id=node_id,
            content_type=ct,
            object_id=str(model_instance.pk),
            parent=parent_token,
            sync_order=sync_order,
            metadata=metadata or {},
        )

    def mark_batch_synced(self, token_ids: list[int]) -> int:
        """Mark a batch of tokens as synced in a single UPDATE query.

        Returns the number of rows updated.
        """
        return (
            self.get_queryset()
            .filter(pk__in=token_ids)
            .update(
                sync_status=DataToken.Status.SYNCED,
                synced_at=timezone.now(),
            )
        )


# ===========================================================================
# Model
# ===========================================================================


class DataToken(models.Model):
    """Lightweight sync tag attached to any database row.

    The ``token`` field is the **first lookup key** — query by token to find
    the tagged row instantly.  Parent/child links enable ordered sync of
    related entities (e.g. invoice → invoice items).
    """

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending Sync")
        SYNCING = "syncing", _("Syncing")
        SYNCED = "synced", _("Synced")
        FAILED = "failed", _("Failed")

    # ── Primary lookup ──
    token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text=_("Unique human-readable sync-token (primary lookup key)."),
    )

    # ── Node scoping ──
    node_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text=_("Node/device identifier that owns this row."),
    )

    # ── Generic foreign key — tag ANY model ──
    # Uses CharField for object_id so UUID and string PKs are supported.
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text=_("Model type of the tagged row."),
    )
    object_id = models.CharField(
        max_length=255,
        help_text=_("Primary key of the tagged row (supports int, UUID, slug)."),
    )
    content_object: ClassVar = GenericForeignKey("content_type", "object_id")

    # ── Tree structure (parent → child ordering) ──
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text=_("Parent token for tree-structured sync (invoice → items)."),
    )

    # ── Ordering ──
    sync_order = models.IntegerField(
        default=0,
        db_index=True,
        help_text=_("Order within a sync batch. Lower = synced first."),
    )

    # ── Progress tracking ──
    sync_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text=_("Current sync state of this row."),
    )
    retry_count = models.IntegerField(
        default=0,
        help_text=_("Number of times this row has been retried."),
    )
    error_message = models.TextField(
        blank=True,
        default="",
        help_text=_("Last error message if sync failed."),
    )
    synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the row was confirmed synced upstream."),
    )

    # ── Metadata ──
    metadata = models.JSONField(
        blank=True,
        default=dict,
        help_text=_("Arbitrary extra data (e.g. invoice total, customer name)."),
    )

    # ── Timestamps ──
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ── Manager ──
    objects: ClassVar = DataTokenManager.from_queryset(DataTokenQuerySet)()

    class Meta:
        app_label = "CI"
        verbose_name = _("Data Token")
        verbose_name_plural = _("Data Tokens")
        ordering = ["sync_order", "created_at"]
        indexes = [
            models.Index(fields=["node_id", "sync_status", "sync_order"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["sync_status", "created_at"]),
        ]

    def __str__(self) -> str:
        ct_name = self.content_type.model if self.content_type_id else "?"
        return f"DataToken({self.token!r} → {ct_name}#{self.object_id})"

    # ── Instance methods ──────────────────────────────────────────

    def mark_synced(self) -> None:
        """Mark this token and all its descendants as synced."""
        now = timezone.now()
        with transaction.atomic():
            # Update self
            self.sync_status = self.Status.SYNCED
            self.synced_at = now
            self.save(update_fields=["sync_status", "synced_at", "updated_at"])
            # Cascade to children (bulk update — no signal overhead)
            type(self).objects.filter(parent=self).update(
                sync_status=self.Status.SYNCED,
                synced_at=now,
                updated_at=now,
            )

    def mark_failed(self, error: str = "") -> None:
        """Record a failed sync attempt and increment retry count."""
        self.sync_status = self.Status.FAILED
        self.error_message = error
        self.retry_count = int(self.retry_count) + 1
        self.save(
            update_fields=[
                "sync_status",
                "error_message",
                "retry_count",
                "updated_at",
            ]
        )

    def mark_retrying(self) -> None:
        """Reset to pending for a retry attempt."""
        self.sync_status = self.Status.PENDING
        self.error_message = ""
        self.save(update_fields=["sync_status", "error_message", "updated_at"])

    @property
    def is_synced(self) -> bool:
        return self.sync_status == self.Status.SYNCED

    @property
    def is_root(self) -> bool:
        return self.parent_id is None

    @cached_property
    def has_children(self) -> bool:
        """Whether this token has child tokens (cached after first access)."""
        return self.children.exists()  # type: ignore[attr-defined]

    def get_sync_tree(self) -> list[DataToken]:
        """Return [self] + all descendants in sync_order (depth-first)."""
        result = [self]
        for child in self.children.ordered():  # type: ignore[attr-defined]
            result.extend(child.get_sync_tree())
        return result


# ===========================================================================
# Mixin — for models that want to be taggable
# ===========================================================================


class DataTokenMixin:
    """Mixin for models whose instances can be tagged with DataTokens.

    Adds convenience properties and methods::

        class Invoice(DataTokenMixin, models.Model):
            ...

        invoice = Invoice.objects.first()
        invoice.tag_for_sync(token="inv_42", node_id="solo-001", sync_order=5)
        print(invoice.sync_token)        # → DataToken instance or None
        print(invoice.is_tagged_for_sync)  # → bool
        invoice.mark_synced()            # preserve audit trail
        invoice.untag_for_sync()         # hard delete tokens
    """

    # ContentType is cached per model class to avoid repeated DB lookups.
    _content_type_cache: ClassVar[dict] = {}

    def _get_content_type(self) -> ContentType:
        cache_key = f"{type(self).__module__}.{type(self).__qualname__}"
        if cache_key not in self._content_type_cache:
            self._content_type_cache[cache_key] = ContentType.objects.get_for_model(
                type(self)
            )
        return self._content_type_cache[cache_key]

    @property
    def sync_token(self) -> DataToken | None:
        """Return the DataToken attached to this instance, if any."""
        return DataToken.objects.filter(
            content_type=self._get_content_type(),
            object_id=str(self.pk),
        ).first()

    @property
    def is_tagged_for_sync(self) -> bool:
        return self.sync_token is not None

    def tag_for_sync(
        self,
        token: str,
        node_id: str,
        sync_order: int = 0,
        parent_token=None,
        metadata: dict | None = None,
    ) -> DataToken:
        """Attach a DataToken to this instance."""
        return DataToken.objects.tag_row(
            model_instance=self,
            token=token,
            node_id=node_id,
            sync_order=sync_order,
            parent_token=parent_token,
            metadata=metadata,
        )

    def mark_synced(self) -> int:
        """Mark all pending DataTokens on this instance as synced.

        Returns the number of tokens updated.  Preserves the audit trail.
        """
        return DataToken.objects.filter(
            content_type=self._get_content_type(),
            object_id=str(self.pk),
            sync_status__in=[DataToken.Status.PENDING, DataToken.Status.SYNCING],
        ).update(
            sync_status=DataToken.Status.SYNCED,
            synced_at=timezone.now(),
        )

    def untag_for_sync(self, force_delete: bool = False) -> int:
        """Remove DataTokens from this instance.

        By default, tokens are marked as *synced* (preserving the audit
        trail).  Pass ``force_delete=True`` to hard-delete them instead.

        Returns the number of tokens affected.
        """
        if force_delete:
            deleted, _ = DataToken.objects.filter(
                content_type=self._get_content_type(),
                object_id=str(self.pk),
            ).delete()
            return deleted
        return self.mark_synced()


# ===========================================================================
# Signal handler — auto-untag on SyncLog success
# ===========================================================================
# This is a PLAIN FUNCTION — NOT decorated with @receiver.
# Connect it manually to YOUR project's SyncLog model in AppConfig.ready():
#
#   from django_fusion.core.models import sync_log_success_handler
#   from django.db.models.signals import post_save
#   post_save.connect(sync_log_success_handler, sender=SyncLog)
#


def untag_by_entity(node_id: str, entity_type: str, entity_id: str) -> int:
    """Find and mark tokens matching *node_id* + *entity_type* + *entity_id*.

    Uses metadata.entity_id as the primary lookup strategy, with a
    scoped token-ending fallback.

    Returns the number of tokens updated.
    """
    _status_filter = dict(
        sync_status__in=[DataToken.Status.PENDING, DataToken.Status.SYNCING],
    )

    # Strategy 1: metadata.entity_id (most precise)
    updated = DataToken.objects.filter(
        node_id=node_id,
        metadata__entity_id=str(entity_id),
        **_status_filter,
    ).update(sync_status=DataToken.Status.SYNCED, synced_at=timezone.now())

    if updated:
        return updated

    # Strategy 2: token ends with the entity_id prefixed by separator
    # e.g. "inv_42" matches token "node-abc_inv_42" but NOT "inv_420"
    updated = DataToken.objects.filter(
        node_id=node_id,
        token__regex=rf"[_:]{entity_id}$",
        **_status_filter,
    ).update(sync_status=DataToken.Status.SYNCED, synced_at=timezone.now())

    return updated


def sync_log_success_handler(sender, instance, created, **kwargs) -> None:
    """Auto-untag DataTokens when a SyncLog flips to success.

    Connect this to YOUR project's SyncLog model in AppConfig.ready()::

        from django_fusion.core.models import sync_log_success_handler
        from django.db.models.signals import post_save
        post_save.connect(sync_log_success_handler, sender=SyncLog)

    This is a **plain function** — it is NOT decorated with @receiver
    and therefore does NOT fire on every model save globally.
    """
    # Guard: only handle models with the expected fields
    if not hasattr(instance, "status") or not hasattr(instance, "node_id"):
        return

    if instance.status != "success":
        return

    entity_type = getattr(instance, "entity_type", "")
    entity_id = getattr(instance, "entity_id", "")

    count = untag_by_entity(
        node_id=instance.node_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    if count:
        logger.debug(
            "Auto-untagged %d DataToken(s) for node=%s entity=%s/%s",
            count,
            instance.node_id,
            entity_type,
            entity_id,
        )
