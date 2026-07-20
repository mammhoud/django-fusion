"""
Django AppConfig for POS Solo managed models.

Registered in INSTALLED_APPS via dotted path: "models.PosSoloConfig"
Covers all managed models with app_label="pos_unified".
"""

from django.apps import AppConfig


class PosSoloConfig(AppConfig):
    """AppConfig for POS Solo managed models (pos_unified label)."""

    name = "models"
    label = "pos_unified"
    verbose_name = "POS Solo — POS Core, Menu, Node Registry & Sync"
    default_auto_field = "django.db.models.BigAutoField"
