"""POS Cloud — Domain Django app config (sync broker, queue, conflict resolver)."""

from django.apps import AppConfig


class DomainConfig(AppConfig):
    name = "apps.domain"
    label = "domain"
    verbose_name = "POS Cloud — Sync Domain Services"
    default_auto_field = "django.db.models.BigAutoField"
