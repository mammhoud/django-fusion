"""
django_fusion models — base models and mixins for Django applications.
"""
from .auth import Role, UserRole  # noqa: F401
from .base import BaseModel, TimeStampedModel, UUIDModel  # noqa: F401
from .datatoken import (  # noqa: F401
    AbstractDataToken,
    BaseDeviceToken,
    DataToken,
    DataTokenManager,
    DataTokenMixin,
    DataTokenQuerySet,
    sync_log_success_handler,
    untag_by_entity,
)
from .email import EmailLog, EmailTemplate, UserGroup  # noqa: F401
from .integrations import Integration
try:
    from .default import ContentBase  # noqa: F401
except ImportError:
    ContentBase = None  # type: ignore
try:
    from .model_cache import ModelCacheMixin  # noqa: F401
except ImportError:
    ModelCacheMixin = None  # type: ignore
try:
    from .cache_storage import CachingStorage  # noqa: F401
except ImportError:
    CachingStorage = None  # type: ignore
try:
    from .tags import BaseTag, BaseTagCategory, PersonTag, Tag  # noqa: F401
except ImportError:
    BaseTag = None  # type: ignore
    BaseTagCategory = None  # type: ignore
    PersonTag = None  # type: ignore
    Tag = None  # type: ignore
try:
    from .tasks import BackgroundTaskLog  # noqa: F401
except ImportError:
    BackgroundTaskLog = None  # type: ignore
try:
    from .interaction.call import Call
    from .interaction.notification import Notification
except Exception:
    Call = None  # type: ignore
    Notification = None  # type: ignore
from .managers import SoftDeleteManager, SoftDeleteQuerySet  # noqa: F401
try:
    from .mixins import (  # noqa: F401
        AuditMixin,
        DisplayModeMixin,
        SoftDeleteMixin,
        SoftDeleteModel,
        StatusMixin,
        TimestampedModel,
        UUIDPrimaryKeyModel,
    )
except Exception:
    from .mixins import (  # noqa: F401
        AuditMixin,
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
    # DataToken sync-tagging system
    "AbstractDataToken",
    "BaseDeviceToken",
    "DataToken",
    "DataTokenManager",
    "DataTokenMixin",
    "DataTokenQuerySet",
    "sync_log_success_handler",
    "untag_by_entity",
    # Migrated from shared/models/ (framework-level)
    "ContentBase",
    "ModelCacheMixin",
    "CachingStorage",
    "BaseTag",
    "BaseTagCategory",
    "PersonTag",
    "Tag",
    "BackgroundTaskLog",
]
