import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.handlers"
    label = "handlers"
    verbose_name = _("Module Common Settings")

    def ready(self):
        with contextlib.suppress(ImportError):
            import apps.pages.accounts.signals  # noqa: F401

        from django.db.models.signals import post_migrate

        post_migrate.connect(_on_post_migrate, sender=self)


def _on_post_migrate(sender, **kwargs):
    """Call ensure_groups_exist() after migrations run."""
    from apps.pages.accounts.views.registration import ensure_groups_exist

    ensure_groups_exist()
