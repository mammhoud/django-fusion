"""
ceptor_ai.pipelines.models - Legacy import shim.
Re-exports from ceptor_ai.content.models for backward compatibility.
"""
from ceptor_ai.content.models import (  # noqa: F401
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
    from ceptor_ai.content.models.users.team import Team  # noqa: F401
except ImportError:
    Team = None  # type: ignore[assignment,misc]

try:
    from ceptor_ai.content.models import Coupon, CouponUsage  # noqa: F401
except ImportError:
    pass
