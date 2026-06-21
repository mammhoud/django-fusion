"""
Enums and choices for Django Forge.

Provides enumeration classes for common choices.
"""


from django.db import models


class StatusEnum(models.TextChoices):
    """Status enumeration."""
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    PENDING = "pending", "Pending"
    ARCHIVED = "archived", "Archived"


class RoleEnum(models.TextChoices):
    """Role enumeration."""
    ADMIN = "admin", "Administrator"
    MODERATOR = "moderator", "Moderator"
    USER = "user", "User"
    GUEST = "guest", "Guest"


class PermissionEnum(models.TextChoices):
    """Permission enumeration."""
    READ = "read", "Read"
    WRITE = "write", "Write"
    DELETE = "delete", "Delete"
    ADMIN = "admin", "Administrator"


class VisibilityEnum(models.TextChoices):
    """Visibility enumeration."""
    PRIVATE = "private", "Private"
    SHARED = "shared", "Shared"
    PUBLIC = "public", "Public"


class PriorityEnum(models.TextChoices):
    """Priority enumeration."""
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class MessageTypeEnum(models.TextChoices):
    """Message type enumeration."""
    GENERAL = "general", "General"
    NOTIFICATION = "notification", "Notification"
    ALERT = "alert", "Alert"
    WARNING = "warning", "Warning"
    ERROR = "error", "Error"


class CertificateStatusEnum(models.TextChoices):
    """Certificate status enumeration."""
    VALID = "valid", "Valid"
    EXPIRED = "expired", "Expired"
    REVOKED = "revoked", "Revoked"
    PENDING = "pending", "Pending"


class EnrollmentStatusEnum(models.TextChoices):
    """Enrollment status enumeration."""
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    DROPPED = "dropped", "Dropped"
    SUSPENDED = "suspended", "Suspended"
