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
