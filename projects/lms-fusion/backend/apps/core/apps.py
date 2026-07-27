import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "apps_core"
    verbose_name = _("Module Common Settings")

    def ready(self):
        with contextlib.suppress(ImportError):
            import apps.core.signals  # noqa: F401

        from django.db.models.signals import post_migrate
        post_migrate.connect(_on_post_migrate, sender=self)


def _on_post_migrate(sender, **kwargs):
    """Call ensure_groups_exist() after migrations run."""
    with contextlib.suppress(Exception):
        from apps.pages.accounts.views.registration import ensure_groups_exist
        ensure_groups_exist()
