"""POS Cloud — Core Django app config (domain models + fusion fragments)."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"
    verbose_name = "POS Cloud — Branches, Orgs, Leads & Reports"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Register django-fusion fragments at startup.

        Sync broker handler registration lives in HandlersConfig.ready()
        (it imports apps.domain + apps.handlers, so it belongs to the
        handlers app).
        """
        from apps.handlers.fragments import tables, modals, reports, layouts, skeletons  # noqa: F401
        _patch_unfold_context_flatten()


def _patch_unfold_context_flatten():
    """Work around unfold 0.90 + Django 5.0 ``context.flatten()`` crash.

    unfold's ``RenderComponentNode`` flattens the template context via
    ``Context.flatten()`` on Django >= 5.0, which raises
    ``ValueError: dictionary update sequence element ...`` when a nested
    ``Context``/``RequestContext`` sits in the dict stack (every admin
    ``*/add/`` page).  Replace it with unfold's own safe implementation
    (the one it uses for Django < 5) on all supported versions.
    """
    import unfold.templatetags.unfold as unfold_tags

    def _safe_flatten(context):
        keys = set()
        for d in context.dicts:
            if hasattr(d, "keys"):
                keys.update(d.keys())
        return {k: context[k] for k in keys}

    unfold_tags._flatten_context = _safe_flatten
