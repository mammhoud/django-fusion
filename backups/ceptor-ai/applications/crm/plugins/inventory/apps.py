from django.apps import AppConfig


class InventoryConfig(AppConfig):
    name = "plugins.inventory"
    label = "crm_inventory"
    verbose_name = "CRM Inventory"

    def ready(self):
        pass
