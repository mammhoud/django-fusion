"""
AppConfig for the accounts registration sub-app (ctc-research.com).
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsRegistrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.accounts.registration"
    label = "accounts_registration"
    verbose_name = _("Accounts Registration")

    def ready(self):
        pass  # signals registered in parent accounts app
