from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreExtAppConfig(AppConfig):
    label = "components"
    name = "django_fusion.comp"
    verbose_name = _("Core Extensions")

    def ready(self):
        from .plugins import pm
        from .registry import register_default_partials, register_include_paths
        from .static.staticfiles import asset_types

        for pre_ready in pm.hook.pre_ready():
            pre_ready()

        pm.hook.register_asset_types(register_type=asset_types.register_type)

        # Pre-warm the include-path-to-component registry so the first
        # render of `{% comp "partials/..." %}` does not pay the
        # lazy-load cost. Sites extend this list with the
        # ``COMPONENTS_INCLUDE_PATH_ROOTS`` Django setting.
        register_default_partials()

        # Register django-fusion built-in component templates so they are
        # available to {% comp %} without manual registration.
        register_include_paths([
            "components/table.html",
            "components/pagination.html",
            "components/search.html",
            "components/form.html",
        ])

        from .webpack_compat import _patch_webpack_loader

        _patch_webpack_loader()

        for ready in pm.hook.ready():
            ready()
