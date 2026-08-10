from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoFusionConfig(AppConfig):
    """Default app configuration for django-fusion."""

    name = "django_fusion"
    label = "django_fusion"
    verbose_name = _("django-fusion")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Wire django-fusion subsystems on startup."""
        # ── Auto-configure task backend from FUSION_TASKS settings ──
        try:
            from django_fusion.tasks import _configure_from_settings
            _configure_from_settings()
        except Exception:
            pass

        # ── Auto-discover per-app task modules ────────────────
        try:
            from django_fusion.tasks.registry import task_registry
            task_registry.autodiscover()
        except Exception:
            pass
