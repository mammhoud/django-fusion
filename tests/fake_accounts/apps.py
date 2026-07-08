from django.apps import AppConfig


class FakeAccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fake_accounts"
    label = "accounts"
