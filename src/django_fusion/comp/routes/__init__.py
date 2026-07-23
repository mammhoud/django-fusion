"""
django_fusion.comp.routes
========================

Declarative, class-based URL routing for Django projects — moved from
``django_fusion.site.routes`` to ``django_fusion.comp.routes``.

Provides Viewset, BaseViewset, Route, route(), menu_path(), and IndexViewMixin.
Also includes model viewsets, site/application routing, and routable components
with HTMX fragment support.

Import from::

    from django_fusion.comp.routes import (
        Viewset, BaseViewset, Route, route, menu_path, viewprop,
        Application, Site, AppMenuMixin,
        RoutableComponent, FragmentComponent,
        ModelViewset, ReadonlyModelViewset,
    )
"""
from .base import (
    BaseViewset,
    IndexViewMixin,
    Route,
    Viewset,
    ViewsetMeta,
    menu_path,
    route,
    viewprop,
)
from .components import RoutableComponent  # noqa: F401
from .detection import (  # noqa: F401
    FragmentDetectionMixin,
    FragmentDetector,
    add_fragment_detection_to_request,
    detect_fragment_strategy,
)
from django_fusion.comp.contrib.forms import FormMixin, FormTableMixin  # noqa: F401
from django_fusion.comp.contrib.tables import TableMixin  # noqa: F401
from .fragments import FragmentComponent  # noqa: F401
from .template_resolver import TemplateResolverMixin  # noqa: F401
from .model import BaseModelViewset  # noqa: F401
from .other import (  # noqa: F401
    CreateViewMixin,
    DeleteViewMixin,
    DetailViewMixin,
    ListBulkActionsMixin,
    ModelViewset,
    ReadonlyModelViewset,
    UpdateViewMixin,
)
from .sites import Application, AppMenuMixin, Site  # noqa: F401

__all__ = [
    # Base routing
    "Viewset",
    "BaseViewset",
    "ViewsetMeta",
    "Route",
    "route",
    "menu_path",
    "IndexViewMixin",
    # Descriptor utility
    "viewprop",
    # Model viewsets
    "BaseModelViewset",
    "ListBulkActionsMixin",
    "CreateViewMixin",
    "UpdateViewMixin",
    "DeleteViewMixin",
    "DetailViewMixin",
    "ModelViewset",
    "ReadonlyModelViewset",
    # Site/Application
    "Application",
    "AppMenuMixin",
    "Site",
    # Routable components
    "RoutableComponent",
    "FragmentComponent",
    # Fragment detection
    "FragmentDetector",
    "FragmentDetectionMixin",
    "detect_fragment_strategy",
    "add_fragment_detection_to_request",
    # Forms and Tables integration
    "FormMixin",
    "TableMixin",
    "FormTableMixin",
    # Template resolution
    "TemplateResolverMixin",
]
