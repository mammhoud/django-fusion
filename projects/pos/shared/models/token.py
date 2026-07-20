"""
django-fusion Token System — DeviceToken model for multi-branch authentication.

Provides token-based authentication for POS devices (solo, full, minimal)
connecting to the cloud server. Tokens encode device identity, role,
capabilities, and allowed entity access.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone as django_timezone


# ---------------------------------------------------------------------------
# Role definitions
# ---------------------------------------------------------------------------

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

TOKEN_BYTES = 32  # 256-bit token
TOKEN_PREFIX_LENGTH = 8
DEFAULT_TOKEN_TTL_DAYS = 90


def _now():
    return django_timezone.now()


def generate_raw_token() -> str:
    """Generate a cryptographically secure random token string."""
    return secrets.token_urlsafe(TOKEN_BYTES)


def hash_token(raw_token: str) -> str:
    """Hash a raw token using SHA-256 for storage."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def token_prefix(raw_token: str) -> str:
    """Extract the first N characters of a raw token for display."""
    return raw_token[:TOKEN_PREFIX_LENGTH]


# ---------------------------------------------------------------------------
# DeviceToken model
# ---------------------------------------------------------------------------


class DeviceToken(models.Model):
    """
    Token-based authentication for POS devices across branches.

    Each device (solo, full, minimal) receives a unique token that
    encodes its identity, role, capabilities, and allowed entities.
    Tokens are stored hashed; the raw token is shown only once at creation.

    device_id is NOT unique — multiple tokens per device are allowed
    to support refresh cycles (old token kept for audit, new token issued).
    """

    device_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Device identifier (e.g., NODE-A1B2C3D4). "
                  "Multiple tokens per device allowed for refresh cycles.",
    )
    token_hash = models.CharField(
        max_length=128,
        unique=True,
        help_text="SHA-256 hash of the raw token",
    )
    token_prefix = models.CharField(
        max_length=TOKEN_PREFIX_LENGTH,
        help_text="First 8 characters of raw token (for display/lookup)",
    )

    # Link to Node registry by node_id (CharField to avoid cross-app FK resolution issues)
    node_id_link = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        help_text="Node identifier this token belongs to (matches Node.node_id)",
    )

    # Role & identity
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="viewer",
        db_index=True,
    )
    node_type = models.CharField(
        max_length=20,
        choices=NODE_TYPE_CHOICES,
        default="pos-solo",
        help_text="Type of device this token belongs to",
    )

    # Capability scoping
    capabilities = models.JSONField(
        default=dict,
        blank=True,
        help_text="Device capabilities dict, e.g. {'products': True, 'sync': True}",
    )
    allowed_entities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of allowed entity types, empty = all allowed",
    )

    # Lifecycle
    issued_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this token was issued",
    )
    expires_at = models.DateTimeField(
        help_text="When this token expires",
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this token was used for authentication",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Soft-disable token without deleting it",
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Arbitrary metadata (IP, user-agent, notes, etc.)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "cloud_auth"
        db_table = "cloud_device_tokens"
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["token_hash"]),
            models.Index(fields=["device_id", "is_active"]),
            models.Index(fields=["role"]),
            models.Index(fields=["expires_at"]),
        ]
        verbose_name = "device token"
        verbose_name_plural = "device tokens"

    def __str__(self) -> str:
        return f"[{self.role}] {self.device_id} ({self.token_prefix}...)"

    # -- Token lifecycle methods ----------------------------------------------

    @classmethod
    def issue_token(
        cls,
        device_id: str,
        role: str = "viewer",
        node_type: str = "pos-solo",
        ttl_days: int = DEFAULT_TOKEN_TTL_DAYS,
        capabilities: dict | None = None,
        allowed_entities: list | None = None,
        metadata: dict | None = None,
        node_id_link: str = "",
    ) -> tuple:
        """Issue a new token for a device.

        Returns (DeviceToken instance, raw_token_string).
        The raw token must be communicated to the device securely
        and will NOT be stored in plaintext.
        """
        raw_token = generate_raw_token()
        token_hash_value = hash_token(raw_token)

        obj = cls.objects.create(
            device_id=device_id,
            token_hash=token_hash_value,
            token_prefix=token_prefix(raw_token),
            role=role,
            node_type=node_type,
            node_id_link=node_id_link,
            capabilities=capabilities or {},
            allowed_entities=allowed_entities or [],
            expires_at=_now() + timedelta(days=ttl_days),
            metadata=metadata or {},
        )
        return obj, raw_token

    @classmethod
    def validate_token(cls, raw_token: str):
        """Validate a raw token string.

        Looks up by SHA-256 hash, checks expiry and active status.
        Returns the DeviceToken instance if valid, None otherwise.
        Updates last_used_at on successful validation.
        """
        if not raw_token:
            return None

        token_hash_value = hash_token(raw_token)
        try:
            obj = cls.objects.get(
                token_hash=token_hash_value,
                is_active=True,
                expires_at__gt=_now(),
            )
            # Update last used timestamp (fire-and-forget)
            cls.objects.filter(id=obj.id).update(
                last_used_at=_now(),
                updated_at=_now(),
            )
            return obj
        except cls.DoesNotExist:
            return None

    def revoke(self) -> None:
        """Revoke this token immediately."""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def refresh(
        self,
        ttl_days: int = DEFAULT_TOKEN_TTL_DAYS,
    ) -> tuple:
        """Issue a new token for the same device, revoking the old one.

        Returns (new_token_instance, raw_token_string).
        Old token is kept for audit trails (is_active=False).
        """
        self.revoke()
        return self.__class__.issue_token(
            device_id=self.device_id,
            role=self.role,
            node_type=self.node_type,
            ttl_days=ttl_days,
            capabilities=self.capabilities,
            allowed_entities=self.allowed_entities,
            metadata=self.metadata,
            node_id_link=self.node_id_link,
        )

    def is_expired(self) -> bool:
        """Check if this token has expired."""
        return _now() >= self.expires_at

    def to_dict(self) -> dict:
        """Serialize to dict for API responses (excludes hash)."""
        return {
            "device_id": self.device_id,
            "token_prefix": self.token_prefix,
            "role": self.role,
            "node_type": self.node_type,
            "capabilities": self.capabilities,
            "allowed_entities": self.allowed_entities,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "is_active": self.is_active,
        }

    def has_entity_access(self, entity_type: str) -> bool:
        """Check if this token allows access to a specific entity type."""
        if not self.allowed_entities:
            return True
        return entity_type in self.allowed_entities

    def has_role_at_least(self, minimum_role: str) -> bool:
        """Check if this token's role meets a minimum level.

        Hierarchy: viewer < cashier < manager < admin
        """
        hierarchy = ["viewer", "cashier", "manager", "admin"]
        try:
            return hierarchy.index(self.role) >= hierarchy.index(minimum_role)
        except (ValueError, IndexError):
            return False
