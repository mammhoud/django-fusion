"""
Django AppConfig for POS Full managed models.

Registered in INSTALLED_APPS via dotted path: "models.PosFullConfig"
Covers all managed models with app_label="pos_full".

On ``ready()`` the Django signal receivers are imported so the pure-Django
server process (daphne / runserver / runbolt — the replacement for the
removed Robyn ``server.py``) gets the same behaviour ``server.py`` provided:

  * ``sync_signals``      — flag model rows for cloud sync (is_synced)
  * ``signal_handlers``   — audit persistence + outbound webhooks
  * ``ws_sync_signals``   — real-time push of entity CRUD to the cloud WS
"""

from django.apps import AppConfig


class PosFullConfig(AppConfig):
    """AppConfig for POS Full managed models (pos_full label)."""

    name = "models"
    label = "pos_full"
    verbose_name = "POS Full — Node Registry, Configuration, Sync & POS Core"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        # Signal receivers are module-level @receiver registrations — importing
        # them here (registry is ready in AppConfig.ready) activates them.
        # Each import is defensive: a missing optional dependency must not
        # prevent the app from starting.
        for _mod in ("sync_signals", "signal_handlers", "ws_sync_signals"):
            try:
                __import__(_mod)
            except Exception:  # pragma: no cover - startup guard
                import logging
                logging.getLogger(__name__).warning(
                    "Could not import signal receivers from %r — skipping", _mod
                )
