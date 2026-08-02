from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreExtAppConfig(AppConfig):
    label = "components"
    name = "django_fusion.comp"
    verbose_name = _("Core Extensions")

    def ready(self):
        from django_fusion.plugins import pm
        from django_fusion.config.staticfiles import asset_types

        for pre_ready in pm.hook.pre_ready():
            pre_ready()

        pm.hook.register_asset_types(register_type=asset_types.register_type)

        # Register django-fusion built-in component templates.
        _register_builtin_component_paths()

        from django_fusion.plugins.webpack.webpack_compat import _patch_webpack_loader

        _patch_webpack_loader()

        for ready in pm.hook.ready():
            ready()


def _register_builtin_component_paths():
    """Register default partials and built-in component templates.

    Extracted so tests can re-populate the registry without calling
    ``AppConfig.ready()`` again.
    """
    from .registry import register_default_partials, register_include_paths

    # Pre-warm the include-path-to-component registry so the first
    # render of `{% comp "partials/..." %}` does not pay the
    # lazy-load cost. Sites extend this list with the
    # ``COMPONENTS_INCLUDE_PATH_ROOTS`` Django setting.
    register_default_partials()

    # Register django-fusion built-in component templates so they are
    # available to {% comp %} without manual registration.
    #
    # All paths are relative to the django-fusion app's templates
    # directory and resolve via Django's standard template loader.
    # Sites that need additional components can either add their own
    # paths to ``COMPONENTS_INCLUDE_PATH_ROOTS`` or extend this list in
    # a subclass AppConfig.ready() that runs after this one.
    built_in = [
        # ── Single-file components ──
        "fusion/components/breadcrumbs.html",
        "fusion/components/button.html",
        "fusion/components/submit_button.html",
        "fusion/components/modal/modal.html",
        "fusion/components/modal/modal_trigger.html",
        "fusion/components/modal/modal_static.html",
        "fusion/components/notification/notification.html",
        "fusion/components/notification/notification_small.html",
        "fusion/components/pagination/pagination.html",
        "fusion/components/search.html",
        "fusion/components/table.html",
        # ── Multi-file subdirectories ──
        "fusion/components/pagination/numbers.html",
        "fusion/components/pagination/load_more.html",
        "fusion/components/pagination/infinite.html",
        "fusion/components/chat/bubble.html",
        "fusion/components/cookies/cookie-consent.html",
        "fusion/components/cookies/cookie-policy.html",
        "fusion/components/cookies/privacy-policy.html",
    ]
    # Form components use the package-wide canonical components/ namespace.
    for _name in ("form", "form_block", "form_field", "form_simple"):
        built_in.append(f"components/form/{_name}.html")
    register_include_paths(built_in)
