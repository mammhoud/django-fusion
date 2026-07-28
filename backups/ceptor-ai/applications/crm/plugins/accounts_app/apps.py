from django.apps import AppConfig


class AccountsAppConfig(AppConfig):
    name = "plugins.accounts_app"
    label = "crm_accounts"
    verbose_name = "CRM Accounts"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import plugins.accounts_app.signals  # noqa: F401
