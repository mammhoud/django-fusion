# type: ignore NOQA
from django.urls import path

from .apps import AccountsConfig

app_name = AccountsConfig.label

urlpatterns = [
    # Auth aliases now live in plugins.urls (plugins:login / plugins:register)
]
