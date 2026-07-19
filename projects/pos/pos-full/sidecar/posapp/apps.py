from django.apps import AppConfig


class PosAppConfig(AppConfig):
    name = "posapp"
    label = "posapp"
    verbose_name = "POS"

    def ready(self):
        """Register POS models on app ready.

        CRM and sync models have moved to pos-full/cloud/ —
        they run as a standalone cloud server alongside the sidecar.
        """
        pass
