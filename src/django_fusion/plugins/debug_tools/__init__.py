"""Development + introspection tooling for django-fusion projects.

The introspection views expose the plugin map, component usage and render
tracker to any Django/Wagtail project::

    from django_fusion.plugins.debug_tools.introspection import (
        fusion_introspection_urls,
    )

    urlpatterns += fusion_introspection_urls()
"""

from .introspection import (
    FusionIntrospectionApiView,
    FusionIntrospectionDashboardView,
    fusion_introspection_urls,
)

__all__ = [
    "FusionIntrospectionApiView",
    "FusionIntrospectionDashboardView",
    "fusion_introspection_urls",
]
