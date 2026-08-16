"""
POS Full — ApiKey model with scoped permissions for external integrations.

Each API key maps to a set of resource scopes (e.g., ``products:read``,
``sales:*``, ``*:*``) and can be revoked, rotated, or time-limited.

Usage::

    from models.apikey import ApiKey

    key = ApiKey.objects.create_key(
        name="Mobile App",
        scopes=["products:read", "customers:read", "sales:*"],
        expires_days=365,
    )
    print(key.prefix, key.plaintext)  # Save plaintext only at creation time
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import ClassVar

from django.db import models
from django.utils import timezone


class ApiKey(models.Model):
    """Scoped API key for programmatic access to the /api/v1/ contract.

    The raw key is never stored — only a SHA-256 hash.  The plaintext is
    returned exactly once at creation time via ``create_key()``.
    """

    # ── Identity ──
    name = models.CharField(max_length=200, help_text="Human-readable label (e.g. 'Mobile App v2')")
    prefix = models.CharField(max_length=12, unique=True, db_index=True,
                              help_text="First 8 chars of the key for identification")
    key_hash = models.CharField(max_length=128, unique=True,
                                help_text="SHA-256 hash of the full key")

    # ── Scopes ──
    # Stored as a JSON list of scope strings: ["products:read", "sales:*", "*:*"]
    scopes = models.JSONField(default=list, help_text="List of resource:action scopes")

    # ── Lifecycle ──
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True,
                                       help_text="Key expires after this date (null = never)")
    last_used_at = models.DateTimeField(null=True, blank=True)
    use_count = models.PositiveIntegerField(default=0)

    # ── Rate limiting ──
    # Maximum requests per minute across all endpoints. ``None`` means
    # unlimited. Enforced by ApiKeyRateLimitMiddleware on /api/v1/ and
    # /api-keys/ (sliding window, in-memory for single-node; Redis-ready).
    rate_limit_per_minute = models.PositiveIntegerField(
        null=True, blank=True, default=None,
        help_text="Max requests per minute (null = unlimited)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    # ── Metadata ──
    created_by = models.CharField(max_length=200, blank=True, default="",
                                   help_text="Who or what created this key")
    description = models.TextField(blank=True, default="")
    allowed_ips = models.JSONField(default=list, blank=True,
                                    help_text="Optional IP allowlist (empty = any IP)")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_api_keys"
        ordering = ["-created_at"]
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    # ── Constants ──
    KEY_PREFIX_LENGTH: ClassVar[int] = 8
    KEY_LENGTH: ClassVar[int] = 48
    HASH_ALGORITHM: ClassVar[str] = "sha256"

    # ── Wildcard scope ──
    WILDCARD_SCOPE: ClassVar[str] = "*:*"

    def __str__(self) -> str:
        status = "active" if self.is_active else "revoked"
        expired = " (expired)" if self.expires_at and self.expires_at < timezone.now() else ""
        return f"{self.name} [{self.prefix}...] — {status}{expired}"

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return self.expires_at < timezone.now()

    @property
    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired

    @classmethod
    def create_key(
        cls,
        name: str,
        scopes: list[str] | None = None,
        expires_days: int | None = None,
        description: str = "",
        created_by: str = "",
        metadata: dict | None = None,
        rate_limit_per_minute: int | None = None,
    ) -> "ApiKey":
        """Generate a new API key and return the model instance.

        The plaintext key is available on the returned instance as
        ``instance._plaintext`` — save it immediately; it is **not**
        stored in the database.

        Returns the unsaved instance with ``_plaintext`` set.
        Call ``.save()`` to persist.
        """
        raw = secrets.token_urlsafe(cls.KEY_LENGTH)[:cls.KEY_LENGTH]
        prefix = raw[:cls.KEY_PREFIX_LENGTH]
        key_hash = hashlib.new(cls.HASH_ALGORITHM, raw.encode()).hexdigest()

        instance = cls(
            name=name,
            prefix=prefix,
            key_hash=key_hash,
            scopes=scopes or [cls.WILDCARD_SCOPE],
            description=description,
            created_by=created_by,
            metadata=metadata or {},
            rate_limit_per_minute=rate_limit_per_minute,
        )
        if expires_days:
            instance.expires_at = timezone.now() + timedelta(days=expires_days)

        # Attach plaintext to the instance (caller must save + capture)
        instance._plaintext = raw  # type: ignore[attr-defined]
        return instance

    def verify(self, raw_key: str) -> bool:
        """Check whether *raw_key* matches this key's hash."""
        computed = hashlib.new(self.HASH_ALGORITHM, raw_key.encode()).hexdigest()
        return computed == self.key_hash

    def has_scope(self, resource: str, action: str) -> bool:
        """Check if this key grants *action* on *resource*.

        Supports wildcard matching:
        - ``*:*`` — full access
        - ``products:*`` — all actions on products
        - ``products:read`` — exact match
        """
        for scope in self.scopes:
            if scope == self.WILDCARD_SCOPE:
                return True
            if ":" not in scope:
                continue
            scope_resource, scope_action = scope.split(":", 1)
            if scope_resource == resource and (scope_action == "*" or scope_action == action):
                return True
        return False

    def record_usage(self) -> None:
        """Bump last_used_at and use_count (caller should save)."""
        self.last_used_at = timezone.now()
        self.use_count += 1

    def revoke(self) -> None:
        """Revoke this key (caller should save)."""
        self.is_active = False
        self.revoked_at = timezone.now()

    @classmethod
    def lookup_key(cls, raw_key: str) -> "ApiKey | None":
        """Look up an API key by its raw value.

        Returns ``None`` if the key is not found, revoked, or expired.
        """
        if not raw_key or len(raw_key) < cls.KEY_PREFIX_LENGTH:
            return None
        prefix = raw_key[:cls.KEY_PREFIX_LENGTH]
        try:
            key_obj = cls.objects.get(prefix=prefix)
        except cls.DoesNotExist:
            return None
        if not key_obj.is_valid:
            return None
        if not key_obj.verify(raw_key):
            return None
        return key_obj


# ── Known scope resources ──
# Used by the API key creation UI and validation middleware.
KNOWN_SCOPES: list[tuple[str, str, list[str]]] = [
    # (resource, label, [actions])
    ("products", "Products", ["read", "write", "delete"]),
    ("categories", "Categories", ["read", "write", "delete"]),
    ("customers", "Customers", ["read", "write", "delete"]),
    ("sales", "Sales", ["read", "write", "delete"]),
    ("inventory", "Inventory", ["read", "write", "delete"]),
    ("employees", "Employees", ["read", "write", "delete"]),
    ("suppliers", "Suppliers", ["read", "write", "delete"]),
    ("nodes", "Nodes", ["read", "write"]),
    ("sync", "Sync", ["read", "write"]),
    ("config", "Configuration", ["read", "write"]),
    ("crm", "CRM", ["read", "write", "delete"]),
    ("kitchen", "Kitchen", ["read", "write"]),
    ("reports", "Reports", ["read"]),
    ("health", "Health & Stats", ["read"]),
    ("api-keys", "API Keys", ["read", "write", "delete"]),
]


def scope_is_valid(scope: str) -> bool:
    """Check if a scope string matches a known resource + valid action."""
    if scope == "*:*":
        return True
    if ":" not in scope:
        return False
    resource, action = scope.split(":", 1)
    for r, _, actions in KNOWN_SCOPES:
        if r == resource:
            return action == "*" or action in actions
    return False
