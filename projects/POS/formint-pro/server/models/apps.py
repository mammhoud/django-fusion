"""
Django AppConfig for POS Full managed models.

Registered in INSTALLED_APPS via dotted path: "models.PosFullConfig"
Covers all managed models with app_label="pos_full".
"""

from django.apps import AppConfig


class PosFullConfig(AppConfig):
    """AppConfig for POS Full managed models (pos_full label)."""

    name = "models"
    label = "pos_full"
    verbose_name = "POS Full — Node Registry, Configuration, Sync & POS Core"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """Register Django signal receivers for the Django-native stack.

        ``signal_handlers`` (webhooks/audit) and ``sync_signals`` (DataToken
        sync flagging) were previously imported by the Robyn ``server.py``
        bootstrap. They now register here so the Django ASGI entry point
        preserves that behavior without importing Robyn.
        """
        import signal_handlers  # noqa: F401
        import sync_signals  # noqa: F401
