"""
django_fusion models — base models and mixins for Django applications.
"""
from .auth import Role, UserRole  # noqa: F401
from .base import BaseModel, TimeStampedModel, UUIDModel  # noqa: F401
from .email import EmailLog, EmailTemplate, UserGroup  # noqa: F401
from .integrations import Integration
from .interaction.call import Call
from .interaction.notification import Notification
from .managers import SoftDeleteManager, SoftDeleteQuerySet  # noqa: F401
from .mixins import (  # noqa: F401
    AuditMixin,
    DisplayModeMixin,
    SoftDeleteMixin,
    SoftDeleteModel,
    StatusMixin,
    TimestampedModel,
    UUIDPrimaryKeyModel,
)

# Alias for backward compatibility
DefaultBase = BaseModel

__all__ = [
    "BaseModel",
    "DefaultBase",
    "TimeStampedModel",
    "UUIDModel",
    "SoftDeleteMixin",
    "SoftDeleteModel",
    "AuditMixin",
    "DisplayModeMixin",
    "StatusMixin",
    "TimestampedModel",
    "UUIDPrimaryKeyModel",
    "SoftDeleteQuerySet",
    "SoftDeleteManager",
    "Call",
    "Notification",
    "Integration",
    # Email models
    "EmailLog",
    "EmailTemplate",
    "UserGroup",
    # Auth models
    "UserRole",
    "Role",
]
