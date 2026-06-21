"""django_rseal.pipelines.site.mixins — compatibility shim."""
from django_rseal.content.site.mixins import ProfileContextMixin, ProfileOperationsMixin  # noqa: F401

try:
    from django_rseal.content.site.mixins import ProfileDashboardMixin  # noqa: F401
except ImportError:
    pass
