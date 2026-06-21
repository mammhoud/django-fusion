"""
django_osoul.routes — shim re-exporting from django_osoul.site.routes.

Backward-compat module. All routing code lives in django_osoul.site.routes.
Uses lazy __getattr__ to avoid circular imports at module load time.
"""


def __getattr__(name: str):
    from django_osoul.site import routes as _routes
    try:
        val = getattr(_routes, name)
    except AttributeError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    globals()[name] = val
    return val


# Eagerly expose the most-used names so IDEs and type checkers see them.
from django_osoul.site.routes import (  # noqa: E402, F401
    Application,
    AppMenuMixin,
    BaseModelViewset,
    BaseViewset,
    FragmentComponent,
    IndexViewMixin,
    ModelViewset,
    RoutableComponent,
    Route,
    Site,
    Viewset,
    ViewsetMeta,
    menu_path,
    route,
    viewprop,
)
