"""AppConfig for the CI (Core Integration) app within django_fusion."""

from django.apps import AppConfig


class CIIntegrationConfig(AppConfig):
    """Site interface app — hosts DataToken, Call, Notification, Integration models.

    These models use ``app_label = "CI"`` in their Meta so they are
    migration-managed under this app rather than ``django_fusion``.
    """

    name = "django_fusion.site.interface"
    label = "CI"
    verbose_name = "Core Integration"
    default_auto_field = "django.db.models.BigAutoField"
