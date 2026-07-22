import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "www.contrib"
    # Label kept as "www_apps" for migration continuity — do NOT rename.
    # The directory was renamed apps → contrib, but Django's migration tracker
    # uses this label in the django_migrations table. Changing it would orphan
    # all existing migrations and require `--fake-initial` or manual repair.
    label = "www_apps"
    verbose_name = _("Module Common Settings")

    def ready(self):
        with contextlib.suppress(ImportError):
            import www.contrib.signals  # noqa: F401

        from django.db.models.signals import post_migrate
        post_migrate.connect(_on_post_migrate, sender=self)


def _on_post_migrate(sender, **kwargs):
    """Call ensure_groups_exist() after migrations run."""
    with contextlib.suppress(Exception):
        from plugins.accounts.views.registration import ensure_groups_exist
        ensure_groups_exist()
