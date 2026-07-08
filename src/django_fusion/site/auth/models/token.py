import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _  # type: ignore

from django_fusion.core.managers import TokenCachedManager

logger = logging.getLogger(__name__)

class Token(models.Model):
    """Token model for authentication tokens."""

    ACCESS = "access"
    REFRESH = "refresh"
    SLIDING = "sliding"
    TOKEN_TYPE_CHOICES = [
        (ACCESS, "Access"),
        (REFRESH, "Refresh"),
        (SLIDING, "Sliding"),
    ]

    # Primary key
    id = models.AutoField(primary_key=True, editable=False)

    # JWT ID for token tracking
    jti = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name="JWT ID",
        help_text="Unique identifier for JWT token",
    )

    # Token fields
    token = models.TextField(
        null=True,
        blank=True,
        help_text="Token value for authentication",
    )
    token_type = models.CharField(
        max_length=10,
        choices=TOKEN_TYPE_CHOICES,
        help_text="Type of token",
    )

    # Relationships
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tokens",
        help_text="The user this token was issued for.",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        help_text="Parent token (refresh token for access tokens)",
    )

    # Security fields
    secret = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="Secure secret for token validation",
    )
    is_revoked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    # Usage metadata
    usage = models.CharField(
        max_length=20,
        choices=[("api", "API"), ("web", "Web"), ("mobile", "Mobile")],
        default="api",
        help_text="Usage context for the token",
    )
    session_token = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        help_text="Session ID associated with the token",
    )
    preferences = models.JSONField(
        default=list,
        blank=True,
        help_text="Token preferences and metadata",
    )

    # Timestamps
    iat = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Issued At",
        help_text="When the token was issued",
    )
    exp = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expires At",
        help_text="When the token expires",
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the token was used",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager
    objects = TokenCachedManager()

    class Meta:
        verbose_name = _("Bearer Token")
        verbose_name_plural = _("Bearer Tokens")
        app_label = "django_fusion"
        db_table = "tokens"
        indexes = [
            models.Index(fields=["user", "token_type", "is_revoked"]),
            models.Index(fields=["jti"]),
            models.Index(fields=["session_token"]),
            models.Index(fields=["exp"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.token_type} ({self.id})"

    # ==================== INSTANCE METHODS ====================

    def is_valid(self) -> bool:
        """Check if token is valid."""
        return (
            not self.is_revoked and not self.is_deleted and (self.exp is None or self.exp > now())
        )

    def revoke(self) -> None:
        """Revoke this token and its children."""
        self.is_revoked = True
        self.save()

        # Revoke child tokens
        if self.token_type == self.REFRESH:
            self.children.filter(is_revoked=False).update(is_revoked=True)

    def delete(self, *args, **kwargs):
        """Soft delete token."""
        self.is_deleted = True
        self.is_revoked = True
        self.save()

    def update_last_used(self) -> None:
        """Update last used timestamp."""
        self.last_used = now()
        self.save(update_fields=["last_used"])

    def to_dict(self) -> dict:
        """Convert token to dictionary."""
        return {
            "id": self.id,
            "jti": str(self.jti),
            "token_type": self.token_type,
            "user_id": self.user_id,
            "is_revoked": self.is_revoked,
            "expires_at": self.exp.isoformat() if self.exp else None,
            "issued_at": self.iat.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "usage": self.usage,
            "session_token": self.session_token,
        }

    # ==================== SAVE OVERRIDE ====================

    def save(self, *args, **kwargs):
        """Override save to set defaults."""
        if not self.exp:
            if self.token_type == self.REFRESH:
                self.exp = now() + timedelta(days=7)
            else:
                self.exp = now() + timedelta(minutes=15)

        if not self.secret:
            self.secret = get_random_string(64)

        if not self.jti:
            self.jti = uuid.uuid4()

        super().save(*args, **kwargs)
