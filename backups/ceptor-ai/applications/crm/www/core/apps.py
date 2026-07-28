"""Core Django app config for the CRM site."""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "www.core"
    label = "crm_core"
    verbose_name = "CRM Core"
