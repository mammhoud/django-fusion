"""POS Cloud — Handlers Django app config (consumers, dashboard, fragments, sync API)."""

from django.apps import AppConfig


class HandlersConfig(AppConfig):
    name = "apps.handlers"
    label = "handlers"
    verbose_name = "POS Cloud — Request Handlers"
    default_auto_field = "django.db.models.BigAutoField"
