"""
DataToken — Sync-tagging model for database rows (v2 — Abstract Base).

Architecture
------------
*   **AbstractDataToken** — abstract base providing shared sync-tracking fields
    (``sync_status``, ``app_type``, ``metadata``, timestamps) that both
    ``DataToken`` (sync-tagging) and ``DeviceToken`` (auth) inherit from.
*   **DataToken** — concrete sync-tag model with GenericForeignKey, parent/child
    tree ordering, node-scoped batching, and progress tracking.
*   **DataTokenManager / DataTokenQuerySet** — sync-aware queryset with chained
    filtering (unsynced, for_node, roots, ordered) and batch operations
    (sync_batch, tag_row, mark_batch_synced).
*   **DataTokenMixin** — drop-in mixin for any Django model that needs sync
    tracking.  Adds ``tag_for_sync()``, ``mark_synced()``, ``untag_for_sync()``
    with cached ContentType lookups.
*   **Signal handler** — ``sync_log_success_handler`` auto-untags tokens when a
    SyncLog confirms receipt upstream.  Connect manually in AppConfig.ready().

State Machine
-------------
Every token follows the same lifecycle::

    PENDING  ──→  SYNCING  ──→  SYNCED
       │                          ↑
       └────  FAILED  ───────────┘
              (retry_count++)

DeviceToken ↔ DataToken Cascade
-------------------------------
When ``DeviceToken.mark_data_synced()`` is called, it cascades to all linked
``DataToken`` rows matching ``node_id_link`` — marking them as synced in a
single bulk UPDATE.  This ensures per-device sync confirmation propagates
to all tagged rows without row-by-row iteration.

Usage (tagging a row)::

    from django_fusion.core.models import DataToken, AbstractDataToken

    DataToken.objects.tag_row(
        model_instance=invoice,
        token="inv_42_node_abc",
        node_id="pos-solo-001",
        sync_order=1,
        app_type=AbstractDataToken.AppType.POS_SOLO,
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
        token.mark_synced()  # cascades to children

Usage (DeviceToken inheriting the abstract base)::

    from django_fusion.core.models import AbstractDataToken

    class DeviceToken(AbstractDataToken):
        device_id = models.CharField(...)
        token_hash = models.CharField(...)
        # sync_status, app_type, metadata inherited from AbstractDataToken

Database Tables
---------------
*   ``ci_datatoken`` — DataToken (GenericFK tagging, app_label="CI")
*   ``cloud_device_tokens`` — DeviceToken (pos-full, pos-solo, pos-cloud)

Indexes
-------
*   ``(node_id, sync_status, sync_order)`` — primary sync_batch query path
*   ``(content_type, object_id)`` — untag_by_entity lookups
*   ``(sync_status, created_at)`` — global unsynced scans
*   ``(app_type, sync_status)`` — per-edition sync scoping (v2)
"""

from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import timedelta
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
# Abstract base — shared sync-tracking fields
# ===========================================================================


class AbstractDataToken(models.Model):
    """Abstract base for token models that track sync state.

    Provides shared fields and helpers used by both:

    *   ``DataToken`` — sync-tagging model (tags any DB row for cloud sync).
        Lives in the ``CI`` app (``ci_datatoken`` table).
    *   ``DeviceToken`` — device authentication model used by pos-full,
        pos-solo, and pos-cloud sidecars (``cloud_device_tokens`` table).

    Concrete subclasses add their own domain-specific fields:

    *   DataToken adds GenericFK (``content_type`` / ``object_id``), parent
        tree, sync_order, retry_count, error_message, synced_at.
    *   DeviceToken adds device_id, token_hash, role, node_type,
        capabilities, allowed_entities, lifecycle fields.

    State Machine
    -------------
    Every token transitions through::

        PENDING → SYNCING → SYNCED   (success path)
        PENDING → FAILED             (error, retry_count incremented)
        FAILED  → PENDING            (mark_retrying)

    Base helpers (``base_mark_*``) provide minimal implementations.
    Subclasses override for domain-specific cascading (e.g. DataToken
    cascades to children, DeviceToken cascades to linked DataTokens).
    """

    class Status(models.TextChoices):
        """Sync lifecycle shared by DataToken and DeviceToken.

        Both models use the same status values, ensuring consistent
        filtering regardless of whether you query DataToken or
        DeviceToken tables.
        """
        PENDING = "pending", _("Pending Sync")
        SYNCING = "syncing", _("Syncing")
        SYNCED = "synced", _("Synced")
        FAILED = "failed", _("Failed")

    class AppType(models.TextChoices):
        """POS edition scope for DataToken sync filtering.

        Used to partition sync batches by application type so that
        pos-solo devices don't pick up pos-full tokens and vice-versa.
        """
        POS_SOLO = "pos-solo", _("POS Solo")
        POS_FULL = "pos-full", _("POS Full")
        POS_MINI = "pos-mini", _("POS Mini")
        CLOUD = "cloud", _("Cloud Server")

    # ── Sync tracking ──
    sync_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text=_("Current sync state of this row/token."),
    )

    # ── App type (DataToken ↔ DeviceToken scoping) ──
    app_type = models.CharField(
        max_length=20,
        choices=AppType.choices,
        default=AppType.POS_SOLO,
        db_index=True,
        help_text=_("Application type flag for DataToken sync scoping."),
    )

    # ── Arbitrary extra data ──
    metadata = models.JSONField(
        blank=True,
        default=dict,
        help_text=_("Arbitrary extra data (e.g. invoice total, customer name)."),
    )

    # ── Timestamps ──
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    # ── Base helpers ──────────────────────────────────────────────
    # These provide minimal implementations.  Subclasses override
    # for domain-specific cascading:
    #   DataToken.mark_synced()  → cascades to children (tree)
    #   DeviceToken.mark_data_synced() → cascades to linked DataTokens
    # ────────────────────────────────────────────────────────────────

    def _mark_sync_status(self, status: str, **extra_fields) -> None:
        """Update sync_status and optional extra fields in a single save.

        Uses ``update_fields`` for performance — only touches the
        columns that actually change, avoiding full-row writes.

        Args:
            status: One of Status.{PENDING, SYNCING, SYNCED, FAILED}.
            **extra_fields: Additional model fields to update (e.g.
                ``synced_at``, ``error_message``).  Must exist on
                the concrete subclass or save will fail.
        """
        update_fields = ["sync_status", "updated_at"]
        self.sync_status = status
        for field, value in extra_fields.items():
            setattr(self, field, value)
            update_fields.append(field)
        self.save(update_fields=update_fields)

    def base_mark_synced(self) -> None:
        """Mark this token as synced (no cascading — override for that).

        Note: only works on models that have a ``synced_at`` field
        (e.g. DataToken).  DeviceToken should use its own
        ``mark_data_synced()`` which sets ``last_synced_at``.
        """
        if hasattr(self, "synced_at"):
            self._mark_sync_status(self.Status.SYNCED, synced_at=timezone.now())
        else:
            self._mark_sync_status(self.Status.SYNCED)

    def base_mark_failed(self, error: str = "") -> None:
        """Record a failed sync attempt (only on models with error_message field)."""
        kwargs = {}
        if hasattr(self, "error_message"):
            kwargs["error_message"] = error
        self._mark_sync_status(self.Status.FAILED, **kwargs)

    def base_mark_retrying(self) -> None:
        """Reset to pending for a retry attempt (only on models with error_message field)."""
        kwargs = {}
        if hasattr(self, "error_message"):
            kwargs["error_message"] = ""
        self._mark_sync_status(self.Status.PENDING, **kwargs)

    @property
    def is_synced(self) -> bool:
        return self.sync_status == self.Status.SYNCED  # type: ignore[attr-defined]


# ===========================================================================
# BaseDeviceToken — shared auth fields for sidecar DeviceToken models
# ===========================================================================

# Shared constants (available as BaseDeviceToken.ROLE_CHOICES, etc.)
_ROLE_CHOICES = [
    ("admin", "Administrator — full access to all resources"),
    ("manager", "Manager — read/write on POS data, approvals, config"),
    ("cashier", "Cashier — read/write on sales, read on products/customers"),
    ("viewer", "Viewer — read-only access"),
]

_NODE_TYPE_CHOICES = [
    ("pos-solo", "POS Solo — standalone node"),
    ("pos-full", "POS Full — cloud master"),
    ("pos-minimal", "POS Minimal — lightweight node"),
    ("cloud-server", "Cloud Server — central auth hub"),
    ("external", "External — third-party integration"),
]

_TOKEN_BYTES = 32
_TOKEN_PREFIX_LENGTH = 8
_DEFAULT_TOKEN_TTL_DAYS = 90


# Module-level helpers (used internally; also exposed as staticmethods on BaseDeviceToken)
def _generate_raw_token() -> str:
    """Generate a cryptographically secure random token (256-bit entropy)."""
    return secrets.token_urlsafe(_TOKEN_BYTES)


def _hash_token(raw_token: str) -> str:
    """Hash a raw token with SHA-256 for database storage."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _token_prefix(raw_token: str) -> str:
    """Extract the first 8 characters of a raw token for UI display."""
    return raw_token[:_TOKEN_PREFIX_LENGTH]


class BaseDeviceToken(AbstractDataToken):
    """Abstract base for POS device authentication tokens.

    Inherits ``sync_status``, ``app_type``, ``metadata``, ``created_at``,
    and ``updated_at`` from :class:`AbstractDataToken`.

    Provides ALL shared fields and methods needed by sidecar DeviceToken
    implementations (pos-full, pos-solo).  Concrete subclasses only need
    to define their ``Meta`` class (``app_label``, ``db_table``, indexes).

    **Token Lifecycle**: Issue → Validate → Cascade Sync → Revoke

    **Security**: Raw tokens are ``secrets.token_urlsafe(32)`` (256-bit
    entropy).  Only SHA-256 hashes are stored.  Tokens auto-expire after
    ``DEFAULT_TOKEN_TTL_DAYS`` (90 days).

    Usage::

        from django_fusion.core.models import BaseDeviceToken

        class DeviceToken(BaseDeviceToken):
            # POS Full edition device token
            class Meta(BaseDeviceToken.Meta):
                abstract = False
                app_label = "pos_full"
                db_table = "cloud_device_tokens"
    """

    # ── Class-level constants (accessible as cls.ROLE_CHOICES, etc.) ──
    ROLE_CHOICES = _ROLE_CHOICES
    NODE_TYPE_CHOICES = _NODE_TYPE_CHOICES
    TOKEN_BYTES = _TOKEN_BYTES
    TOKEN_PREFIX_LENGTH = _TOKEN_PREFIX_LENGTH
    DEFAULT_TOKEN_TTL_DAYS = _DEFAULT_TOKEN_TTL_DAYS

    # ── Fields ──────────────────────────────────────────────────

    # Core identity
    device_id = models.CharField(
        max_length=100, db_index=True,
        help_text="Device identifier. Multiple tokens per device allowed for refresh cycles.",
    )
    token_hash = models.CharField(
        max_length=128, unique=True,
        help_text="SHA-256 hash of the raw token",
    )
    token_prefix = models.CharField(
        max_length=_TOKEN_PREFIX_LENGTH,
        help_text="First 8 characters of raw token",
    )

    # Node linkage
    node_id_link = models.CharField(
        max_length=100, blank=True, default="", db_index=True,
        help_text="Node identifier this token belongs to (matches Node.node_id)",
    )

    # Role & type (app_type inherited from AbstractDataToken)
    role = models.CharField(
        max_length=20, choices=_ROLE_CHOICES, default="viewer", db_index=True,
    )
    node_type = models.CharField(
        max_length=20, choices=_NODE_TYPE_CHOICES, default="pos-solo",
    )

    # Capabilities
    capabilities = models.JSONField(default=dict, blank=True)
    allowed_entities = models.JSONField(default=list, blank=True)

    # Lifecycle
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When this token expires")
    last_used_at = models.DateTimeField(null=True, blank=True)

    # Device-level sync tracking
    last_synced_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When data tagged with this token was last confirmed synced",
    )

    # State
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["-issued_at"]
        verbose_name = "device token"
        verbose_name_plural = "device tokens"

    # ── Representation ──────────────────────────────────────────

    def __str__(self) -> str:
        return f"[{self.role}] {self.device_id} ({self.token_prefix}...)"

    # ── Static helpers (exposed on the class for convenience) ───

    @staticmethod
    def generate_raw_token() -> str:
        """Generate a cryptographically secure random token."""
        return _generate_raw_token()

    @staticmethod
    def hash_token(raw_token: str) -> str:
        """Hash a raw token with SHA-256 for database storage."""
        return _hash_token(raw_token)

    @staticmethod
    def extract_token_prefix(raw_token: str) -> str:
        """Extract the first 8 characters of a raw token for UI display.

        Named ``extract_token_prefix`` to avoid shadowing the Django
        model field ``token_prefix``.
        """
        return _token_prefix(raw_token)

    # ── Class methods ───────────────────────────────────────────

    @classmethod
    def issue_token(
        cls, device_id, role="viewer", node_type="pos-solo",
        ttl_days=_DEFAULT_TOKEN_TTL_DAYS, capabilities=None,
        allowed_entities=None, metadata=None, node_id_link="",
        app_type="pos-solo",
    ):
        """Issue a new device token.

        Generates a cryptographically secure random token, hashes it,
        and persists only the hash.  Returns BOTH the model instance
        AND the raw token — the caller MUST store the raw token on
        the device side (it cannot be recovered from the hash).

        Args:
            device_id: Unique device identifier (e.g. "pos-register-01").
            role: One of admin/manager/cashier/viewer.
            node_type: pos-solo/pos-full/pos-minimal/cloud-server/external.
            ttl_days: Days until expiry (default 90).
            capabilities: JSON dict of allowed operations.
            allowed_entities: JSON list of accessible entity types.
            metadata: Arbitrary extra data stored on the token.
            node_id_link: Matched to Node.node_id for DataToken cascade.
            app_type: POS edition scope (pos-solo/pos-full/pos-mini/cloud).

        Returns:
            Tuple of (DeviceToken instance, raw_token_string).
        """
        raw_token = cls.generate_raw_token()
        token_hash_value = cls.hash_token(raw_token)
        obj = cls.objects.create(
            device_id=device_id,
            token_hash=token_hash_value,
            token_prefix=cls.extract_token_prefix(raw_token),
            role=role,
            node_type=node_type,
            node_id_link=node_id_link,
            capabilities=capabilities or {},
            allowed_entities=allowed_entities or [],
            app_type=app_type,
            expires_at=timezone.now() + timedelta(days=ttl_days),
            metadata=metadata or {},
        )
        return obj, raw_token

    @classmethod
    def validate_token(cls, raw_token):
        """Validate a raw token string and return the DeviceToken if valid.

        Checks: hash match, is_active=True, not expired.
        Updates ``last_used_at`` on successful validation (side-effect
        via bulk update to avoid triggering save signals).

        Returns:
            DeviceToken instance if valid, None otherwise.
        """
        if not raw_token:
            return None
        token_hash_value = cls.hash_token(raw_token)
        try:
            obj = cls.objects.get(
                token_hash=token_hash_value, is_active=True,
                expires_at__gt=timezone.now(),
            )
            # Bulk-update last_used_at — avoids save() signal overhead
            cls.objects.filter(id=obj.id).update(
                last_used_at=timezone.now(), updated_at=timezone.now(),
            )
            return obj
        except cls.DoesNotExist:
            return None

    # ── Instance methods ────────────────────────────────────────

    def revoke(self):
        """Disable this token.  Use ``refresh()`` to issue a replacement."""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def refresh(self, ttl_days=_DEFAULT_TOKEN_TTL_DAYS):
        """Revoke this token and issue a new one with the same parameters.

        Returns:
            Tuple of (new DeviceToken, new raw_token).
        """
        self.revoke()
        return self.__class__.issue_token(
            device_id=self.device_id, role=self.role, node_type=self.node_type,
            ttl_days=ttl_days, capabilities=self.capabilities,
            allowed_entities=self.allowed_entities, metadata=self.metadata,
            node_id_link=self.node_id_link, app_type=self.app_type,
        )

    def is_expired(self) -> bool:
        """Check if this token has passed its expiry date."""
        return timezone.now() >= self.expires_at

    def to_dict(self) -> dict:
        """Serialize all public fields to a JSON-compatible dict."""
        return {
            "device_id": self.device_id,
            "token_prefix": self.token_prefix,
            "role": self.role,
            "node_type": self.node_type,
            "app_type": self.app_type,
            "capabilities": self.capabilities,
            "allowed_entities": self.allowed_entities,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
            "sync_status": self.sync_status,
            "is_active": self.is_active,
        }

    def mark_data_synced(self):
        """Mark this token's data as synced and cascade to linked DataTokens.

        Two-phase update:
        1. Sets ``sync_status=SYNCED`` + ``last_synced_at=now`` on self.
        2. Bulk-updates ALL pending ``DataToken`` rows matching
           ``node_id_link`` — one query for any number of rows.

        The cascade is wrapped in try/except ImportError so this module
        works even when django-fusion is not installed (e.g. offline
        POS devices that don't use cloud sync).
        """
        self.sync_status = self.Status.SYNCED
        self.last_synced_at = timezone.now()
        self.save(update_fields=["sync_status", "last_synced_at", "updated_at"])
        # Cascade to linked DataTokens — single bulk UPDATE.
        # NOTE: DataToken is defined ~200 lines later in this same module.
        # The lazy import resolves correctly and is guarded by ImportError
        # so this works even without django-fusion on the import path.
        if self.node_id_link:
            try:
                from django_fusion.core.models import DataToken

                DataToken.objects.filter(
                    node_id=self.node_id_link,
                    sync_status__in=[self.Status.PENDING, self.Status.SYNCING],
                ).update(sync_status=self.Status.SYNCED, synced_at=timezone.now())
            except ImportError:
                pass

    def mark_data_sync_failed(self):
        """Mark this token's sync as failed."""
        self.sync_status = self.Status.FAILED
        self.save(update_fields=["sync_status", "updated_at"])

    def has_entity_access(self, entity_type: str) -> bool:
        """Check if this token can access a given entity type.

        Returns True if ``allowed_entities`` is empty (unrestricted)
        or if *entity_type* is in the allowed list.
        """
        if not self.allowed_entities:
            return True
        return entity_type in self.allowed_entities

    def has_role_at_least(self, minimum_role: str) -> bool:
        """Check if this token's role is at least *minimum_role*.

        The role hierarchy is: viewer < cashier < manager < admin.
        """
        hierarchy = ["viewer", "cashier", "manager", "admin"]
        try:
            return hierarchy.index(self.role) >= hierarchy.index(minimum_role)
        except (ValueError, IndexError):
            return False


# ===========================================================================
# Manager & QuerySet — concrete DataToken
# ===========================================================================


class DataTokenQuerySet(models.QuerySet):
    """QuerySet with sync-aware chainable filtering methods.

    All methods return ``DataTokenQuerySet`` so they can be chained::

        DataToken.objects.unsynced().for_node("solo-001").ordered()
    """

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
    """Manager with convenience batch operations for sync workflows.

    Key methods:

    *   ``sync_batch(node_id, limit)`` — next ordered batch of unsynced roots
    *   ``tag_row(instance, token, node_id, ...)`` — tag any model instance
    *   ``mark_batch_synced(token_ids)`` — bulk UPDATE for confirmed syncs
    """

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
        app_type: str = "",
    ) -> DataToken:
        """Tag *model_instance* with a DataToken for sync tracking.

        Creates a ``DataToken`` row linked to *model_instance* via
        GenericForeignKey.  The ``token`` field is the primary lookup
        key — query by token to find the tagged row instantly.

        Args:
            model_instance: Any Django model instance (must have a PK).
            token: Unique human-readable sync-token.  Convention:
                ``"{entity}_{pk}_{node_id}"``, e.g. ``"inv_42_solo-001"``.
            node_id: Device/node identifier (e.g. ``"pos-solo-001"``).
            sync_order: Batch ordering priority (lower = first).
            parent_token: Optional parent DataToken for tree linking
                (invoice → line items).
            metadata: Arbitrary JSON-serialisable extra data stored
                on the token (e.g. ``{"total": 99.99}``).
            app_type: POS edition scope.  Defaults to
                ``AbstractDataToken.AppType.POS_SOLO`` when empty.

        Returns:
            The newly created DataToken instance.
        """
        ct = ContentType.objects.get_for_model(model_instance)
        return self.create(
            token=token,
            node_id=node_id,
            content_type=ct,
            object_id=str(model_instance.pk),
            parent=parent_token,
            sync_order=sync_order,
            app_type=app_type or AbstractDataToken.AppType.POS_SOLO,
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
# Concrete DataToken — sync-tagging model
# ===========================================================================


class DataToken(AbstractDataToken):
    """Lightweight sync tag attached to any database row.

    Inherits ``sync_status``, ``app_type``, ``metadata``, and timestamps
    from :class:`AbstractDataToken`.

    The ``token`` field is the **primary lookup key** — query by token to
    find the tagged row instantly (``DataToken.objects.get(token=...)``).

    Parent/child links (``parent`` FK) enable ordered sync of related
    entities — parents are synced before children, ensuring referential
    integrity at the destination.

    Every token tracks:

    *   **sync_status** — inherited from AbstractDataToken (PENDING → SYNCED)
    *   **app_type** — inherited, scopes sync by POS edition
    *   **retry_count** — incremented on each failed push attempt
    *   **error_message** — last upstream error (cleared on retry)
    *   **synced_at** — timestamp of confirmed upstream receipt
    """

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
    # Uses CharField for object_id so UUID and string PKs are supported
    # alongside standard integer PKs.  This avoids hard-coding a PK type.
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

    # ── Per-row progress tracking ──
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
            models.Index(fields=["app_type", "sync_status"]),
        ]

    def __str__(self) -> str:
        ct_name = self.content_type.model if self.content_type_id else "?"
        return f"DataToken({self.token!r} → {ct_name}#{self.object_id})"

    # ── Instance methods (override base with tree-cascading) ──────────

    def mark_synced(self) -> None:
        """Mark this token and all its descendants as synced.

        Uses a database transaction to ensure atomicity — the root token
        and ALL child tokens are updated together or not at all.

        Child tokens are updated via a single bulk ``UPDATE`` query
        (no per-row signal overhead), making this efficient for deep
        trees (e.g. invoices with 50+ line items).
        """
        now = timezone.now()
        with transaction.atomic():
            self.sync_status = self.Status.SYNCED
            self.synced_at = now
            self.save(update_fields=["sync_status", "synced_at", "updated_at"])
            # Bulk-update children — one query for all descendants
            type(self).objects.filter(parent=self).update(
                sync_status=self.Status.SYNCED,
                synced_at=now,
                updated_at=now,
            )

    def mark_failed(self, error: str = "") -> None:
        """Record a failed sync attempt and increment retry count.

        Unlike ``mark_synced()``, this does NOT cascade to children —
        each child token must be individually retried.  The caller
        should inspect ``retry_count`` to implement backoff or max-retry
        logic.
        """
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
    def is_root(self) -> bool:
        return self.parent_id is None

    @cached_property
    def has_children(self) -> bool:
        """Whether this token has child tokens (cached after first access)."""
        return self.children.exists()  # type: ignore[attr-defined]

    def get_sync_tree(self) -> list[DataToken]:
        """Return [self] + all descendants in sync_order (depth-first traversal).

        Useful for pushing an entire invoice tree in one batch::

            for node in token.get_sync_tree():
                await push(node.content_object)
            token.mark_synced()  # cascades to whole tree
        """
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

        from django_fusion.core.models import DataTokenMixin

        class Invoice(DataTokenMixin, models.Model):
            customer = models.CharField(max_length=100)
            total = models.DecimalField(max_digits=10, decimal_places=2)

        invoice = Invoice.objects.first()

        # Tag for sync
        invoice.tag_for_sync(
            token="inv_42", node_id="solo-001",
            sync_order=5, app_type="pos-solo",
        )
        print(invoice.sync_token)        # → DataToken instance or None
        print(invoice.is_tagged_for_sync)  # → bool

        # Mark synced (preserves audit trail)
        invoice.mark_synced()

        # Hard-delete tokens
        invoice.untag_for_sync(force_delete=True)

    Performance note: ``_get_content_type()`` uses a class-level cache
    keyed by ``module.qualname`` to avoid repeated DB lookups.
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
        app_type: str = "",
    ) -> DataToken:
        """Attach a DataToken to this instance."""
        return DataToken.objects.tag_row(
            model_instance=self,
            token=token,
            node_id=node_id,
            sync_order=sync_order,
            parent_token=parent_token,
            metadata=metadata,
            app_type=app_type or AbstractDataToken.AppType.POS_SOLO,
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

        # In your_custom_app/apps.py:
        from django.apps import AppConfig

        class MyAppConfig(AppConfig):
            def ready(self):
                from django_fusion.core.models import sync_log_success_handler
                from django.db.models.signals import post_save
                from your_app.models import SyncLog
                post_save.connect(sync_log_success_handler, sender=SyncLog)

    **Design decision**: This is a PLAIN FUNCTION — NOT decorated with
    ``@receiver``.  Using ``@receiver`` would cause Django to eagerly
    import this module for EVERY project that has django_fusion installed,
    even those that don't use SyncLog.  Manual connection keeps the
    dependency graph clean.

    **Guard logic**: Only processes instances that have both ``status``
    and ``node_id`` attributes, and only when ``status == "success"``.
    This prevents accidental firing on unrelated models.
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
