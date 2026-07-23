from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreExtAppConfig(AppConfig):
    label = "components"
    name = "django_fusion.comp"
    verbose_name = _("Core Extensions")

    def ready(self):
        from .plugins import pm
        from .configuration.staticfiles import asset_types

        for pre_ready in pm.hook.pre_ready():
            pre_ready()

        pm.hook.register_asset_types(register_type=asset_types.register_type)

        # Register django-fusion built-in component templates.
        _register_builtin_component_paths()

        from .plugins.webpack_compat import _patch_webpack_loader

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
    # directory (`django_fusion/comp/templates/`) and resolve via
    # Django's standard template loader. Sites that need additional
    # components can either add their own paths to
    # ``COMPONENTS_INCLUDE_PATH_ROOTS`` or extend this list in a
    # subclass AppConfig.ready() that runs after this one.
    register_include_paths([
            # ── Single-file components ──
            "components/breadcrumbs.html",
            "components/button.html",
            "components/submit_button.html",
            "components/form/form.html",
            "components/form/form_block.html",
            "components/form/form_field.html",
            "components/form/form_simple.html",
            "components/modal.html",
            "components/modal_trigger.html",
            "components/modal_static.html",
            "components/notification.html",
            "components/notification_small.html",
            "components/pagination.html",
            "components/search.html",
            "components/table.html",
            # ── Multi-file subdirectories ──
            "components/pagination/numbers.html",
            "components/pagination/load_more.html",
            "components/pagination/infinite.html",
            "components/chat/bubble.html",
            "components/cookies/cookie-consent.html",
            "components/cookies/cookie-policy.html",
            "components/cookies/privacy-policy.html",
        ])
