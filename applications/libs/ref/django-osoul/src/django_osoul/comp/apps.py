from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreExtAppConfig(AppConfig):
    label = "components"
    name = "django_osoul.comp"
    verbose_name = _("Core Extensions")

    def ready(self):
        from .plugins import pm
        from .static.staticfiles import asset_types

        for pre_ready in pm.hook.pre_ready():
            pre_ready()

        pm.hook.register_asset_types(register_type=asset_types.register_type)

        for ready in pm.hook.ready():
            ready()
