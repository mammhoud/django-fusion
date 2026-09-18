"""
Non-authentication views for domain.

Canonical imports::
    from apps.domain.site.views import NotificationView
    from apps.domain.site.views import PaymentsView
    from apps.domain.site.views import SearchView
    from apps.domain.site.views import TagsView
    from django_fusion.health.views import HealthCheckView
"""

from django_fusion.routes.views.notifications import NotificationView
from .payments import PaymentsView  # noqa: F401
from .search import SearchView  # noqa: F401
from django_fusion.routes.views.tags import EnhancedTagsView as TagsView

__all__ = [
    "NotificationView",
    "PaymentsView",
    "SearchView",
    "TagsView",
]
