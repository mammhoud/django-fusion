"""
django_fusion.routes
====================

Declarative, class-based URL routing for Django projects — moved from
``django_fusion.comp.routes`` to ``django_fusion.routes``.

Provides Viewset, BaseViewset, Route, route(), menu_path(), and IndexViewMixin.
Also includes model viewsets, site/application routing, and routable components
with HTMX fragment support.

Import from::

    from django_fusion.routes import (
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
from .pages import (  # noqa: F401
    FusionContentPageView,
    FusionHomePageView,
    FusionPageView,
)
from .detection import (  # noqa: F401
    FragmentDetectionMixin,
    FragmentDetector,
    add_fragment_detection_to_request,
    detect_fragment_strategy,
)
from django_fusion.fragments.forms.mixins import FormMixin, FormTableMixin  # noqa: F401
from django_fusion.fragments.tables.mixins import TableMixin  # noqa: F401
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
from .renderers import (  # noqa: F401
    FusionFragmentPointer,
    FusionFragmentSchema,
    FusionJSONEncoder,
    FusionJSONRenderer,
    fusion_json_response,
)
from .session import (  # noqa: F401
    CODEC_VERSION,
    SESSION_KEY,
    FusionCodec,
    FusionSessionChecker,
    get_session_render_first,
    session_checker,
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
    "FusionPageView",
    "FusionHomePageView",
    "FusionContentPageView",
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
    # Renderers
    "FusionJSONEncoder",
    "FusionJSONRenderer",
    "fusion_json_response",
    "FusionFragmentSchema",
    "FusionFragmentPointer",
    # Session / codec
    "SESSION_KEY",
    "CODEC_VERSION",
    "FusionSessionChecker",
    "session_checker",
    "get_session_render_first",
    "FusionCodec",
]
