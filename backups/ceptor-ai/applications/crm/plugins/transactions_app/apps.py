from django.apps import AppConfig


class TransactionsAppConfig(AppConfig):
    name = "plugins.transactions_app"
    label = "crm_transactions"
    verbose_name = "CRM Transactions"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        pass
