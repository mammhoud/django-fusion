"""Shim — re-exports from django_osoul.site.routes.base."""


def __getattr__(name: str):
    from django_osoul.site.routes import base as _base
    try:
        val = getattr(_base, name)
    except AttributeError:
        # Also check model.py for BaseModelViewset
        from django_osoul.site.routes import model as _model
        try:
            val = getattr(_model, name)
        except AttributeError:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    globals()[name] = val
    return val
