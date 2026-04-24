"""
Registration migration shim.

This app exists solely to own the `accounts_registration` database table
(AuthEmailTemplate, CSVEmailTest, CSVEmailTestBatch).

All business logic (signals, admin, views, forms, tokens, emails) has been
merged into plugins.accounts. This app is kept in MIGRATION_MODULES so
Django can find the existing migrations without running them again.

Do NOT add signals, admin registrations, or ready() logic here.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RegistrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.accounts.registration"
    label = "accounts_registration"
    verbose_name = _("Registration (migrations only)")

    def ready(self):
        # All logic moved to plugins.accounts.apps.AccountsConfig.ready()
        pass
