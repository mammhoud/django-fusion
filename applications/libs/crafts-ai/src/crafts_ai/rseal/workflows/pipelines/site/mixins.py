"""crafts_ai.pipelines.site.mixins — compatibility shim."""
from crafts_ai.content.site.mixins import ProfileContextMixin, ProfileOperationsMixin  # noqa: F401

try:
    from crafts_ai.content.site.mixins import ProfileDashboardMixin  # noqa: F401
except ImportError:
    pass
