from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoFusionConfig(AppConfig):
    """Default app configuration for django-fusion."""

    name = "django_fusion"
    label = "django_fusion"
    verbose_name = _("django-fusion")
    default_auto_field = "django.db.models.BigAutoField"
