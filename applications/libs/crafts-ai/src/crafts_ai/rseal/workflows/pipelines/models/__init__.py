"""
crafts_ai.pipelines.models - Legacy import shim.
Re-exports from crafts_ai.content.models for backward compatibility.
"""
from crafts_ai.content.models import (  # noqa: F401
    BaseTag,
    BaseTagCategory,
    CachingStorage,
    ContentBase,
    DefaultBase,
    EmailSettings,
    GlobalSettings,
    ModelCacheMixin,
    Newsletter,
    Person,
    PersonTag,
    PersonTagCategory,
    TemplateRenderMixin,
    TemplateVariable,
)

try:
    from crafts_ai.content.models.users.team import Team  # noqa: F401
except ImportError:
    Team = None  # type: ignore[assignment,misc]

try:
    from crafts_ai.content.models import Coupon, CouponUsage  # noqa: F401
except ImportError:
    pass
