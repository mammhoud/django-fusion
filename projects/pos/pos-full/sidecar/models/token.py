"""
django-fusion Token System — DeviceToken model (Full Edition).

Provides token-based authentication for POS devices connecting to the cloud server.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone as django_timezone


ROLE_CHOICES = [
    ("admin", "Administrator — full access to all resources"),
    ("manager", "Manager — read/write on POS data, approvals, config"),
    ("cashier", "Cashier — read/write on sales, read on products/customers"),
    ("viewer", "Viewer — read-only access"),
]

NODE_TYPE_CHOICES = [
    ("pos-solo", "POS Solo — standalone node"),
    ("pos-full", "POS Full — cloud master"),
    ("pos-minimal", "POS Minimal — lightweight node"),
    ("cloud-server", "Cloud Server — central auth hub"),
    ("external", "External — third-party integration"),
]

TOKEN_BYTES = 32
TOKEN_PREFIX_LENGTH = 8
DEFAULT_TOKEN_TTL_DAYS = 90


def _now():
    return django_timezone.now()


def generate_raw_token() -> str:
    return secrets.token_urlsafe(TOKEN_BYTES)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def token_prefix(raw_token: str) -> str:
    return raw_token[:TOKEN_PREFIX_LENGTH]


class DeviceToken(models.Model):
    """Token-based authentication for POS devices across branches.

    Linked to django-fusion's DataToken sync-tagging system for tracking
    which rows have been synced and when.
    """

    # ── App type flag (used for DataToken scoping) ──
    class AppType(models.TextChoices):
        POS_SOLO = "pos-solo", "POS Solo"
        POS_FULL = "pos-full", "POS Full"
        POS_MINI = "pos-mini", "POS Mini"
        CLOUD = "cloud", "Cloud Server"

    device_id = models.CharField(
        max_length=100, db_index=True,
        help_text="Device identifier. Multiple tokens per device allowed for refresh cycles.",
    )
    token_hash = models.CharField(max_length=128, unique=True, help_text="SHA-256 hash of the raw token")
    token_prefix = models.CharField(max_length=TOKEN_PREFIX_LENGTH, help_text="First 8 characters of raw token")
    node_id_link = models.CharField(
        max_length=100, blank=True, default="", db_index=True,
        help_text="Node identifier this token belongs to (matches Node.node_id)",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer", db_index=True)
    node_type = models.CharField(max_length=20, choices=NODE_TYPE_CHOICES, default="pos-solo")
    app_type = models.CharField(max_length=20, choices=AppType.choices, default=AppType.POS_SOLO, db_index=True,
                                help_text="Application type flag for DataToken sync scoping")
    capabilities = models.JSONField(default=dict, blank=True)
    allowed_entities = models.JSONField(default=list, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When this token expires")
    last_used_at = models.DateTimeField(null=True, blank=True)
    # ── DataToken sync tracking ──
    last_synced_at = models.DateTimeField(null=True, blank=True,
                                           help_text="When data tagged with this token was last confirmed synced")
    sync_status = models.CharField(max_length=20, default="pending",
                                    choices=[("pending", "Pending"), ("syncing", "Syncing"),
                                             ("synced", "Synced"), ("failed", "Failed")],
                                    db_index=True, help_text="Sync status of data tagged with this token")
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_full"
        db_table = "cloud_device_tokens"
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["token_hash"]),
            models.Index(fields=["device_id", "is_active"]),
            models.Index(fields=["role"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["sync_status"]),
            models.Index(fields=["app_type", "sync_status"]),
        ]
        verbose_name = "device token"
        verbose_name_plural = "device tokens"

    def __str__(self) -> str:
        return f"[{self.role}] {self.device_id} ({self.token_prefix}...)"

    @classmethod
    def issue_token(cls, device_id, role="viewer", node_type="pos-solo", ttl_days=DEFAULT_TOKEN_TTL_DAYS,
                    capabilities=None, allowed_entities=None, metadata=None, node_id_link=""):
        raw_token = generate_raw_token()
        token_hash_value = hash_token(raw_token)
        obj = cls.objects.create(
            device_id=device_id, token_hash=token_hash_value,
            token_prefix=token_prefix(raw_token), role=role, node_type=node_type,
            node_id_link=node_id_link, capabilities=capabilities or {},
            allowed_entities=allowed_entities or [],
            expires_at=_now() + timedelta(days=ttl_days), metadata=metadata or {},
        )
        return obj, raw_token

    @classmethod
    def validate_token(cls, raw_token):
        if not raw_token:
            return None
        token_hash_value = hash_token(raw_token)
        try:
            obj = cls.objects.get(token_hash=token_hash_value, is_active=True, expires_at__gt=_now())
            cls.objects.filter(id=obj.id).update(last_used_at=_now(), updated_at=_now())
            return obj
        except cls.DoesNotExist:
            return None

    def revoke(self):
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def refresh(self, ttl_days=DEFAULT_TOKEN_TTL_DAYS):
        self.revoke()
        return self.__class__.issue_token(
            device_id=self.device_id, role=self.role, node_type=self.node_type,
            ttl_days=ttl_days, capabilities=self.capabilities,
            allowed_entities=self.allowed_entities, metadata=self.metadata,
            node_id_link=self.node_id_link,
        )

    def is_expired(self):
        return _now() >= self.expires_at

    def to_dict(self):
        return {
            "device_id": self.device_id, "token_prefix": self.token_prefix,
            "role": self.role, "node_type": self.node_type, "app_type": self.app_type,
            "capabilities": self.capabilities, "allowed_entities": self.allowed_entities,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
            "sync_status": self.sync_status,
            "is_active": self.is_active,
        }

    def mark_data_synced(self):
        """Mark this token's associated data as synced and update last_synced_at.

        Also cascades to linked DataTokens matching this device's node_id_link."""
        self.sync_status = "synced"
        self.last_synced_at = _now()
        self.save(update_fields=["sync_status", "last_synced_at", "updated_at"])
        # ── Cascade to linked DataTokens ──
        if self.node_id_link:
            try:
                from django_fusion.core.models import DataToken
                DataToken.objects.filter(
                    node_id=self.node_id_link,
                    sync_status__in=["pending", "syncing"],
                ).update(sync_status="synced", synced_at=_now())
            except ImportError:
                pass

    def mark_data_sync_failed(self):
        """Mark this token's sync as failed."""
        self.sync_status = "failed"
        self.save(update_fields=["sync_status", "updated_at"])

    def has_entity_access(self, entity_type):
        if not self.allowed_entities:
            return True
        return entity_type in self.allowed_entities

    def has_role_at_least(self, minimum_role):
        hierarchy = ["viewer", "cashier", "manager", "admin"]
        try:
            return hierarchy.index(self.role) >= hierarchy.index(minimum_role)
        except (ValueError, IndexError):
            return False
