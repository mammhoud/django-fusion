from django.apps import AppConfig


class DomainConfig(AppConfig):
    name = "apps.core.domain"
    label = "shared"
    verbose_name = "Domain Models"
    default_auto_field = "django.db.models.BigAutoField"
