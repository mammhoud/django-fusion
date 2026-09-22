from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContentConfig(AppConfig):
    """StreamField blocks for the landing sections (hero, stats, features, pricing, faq, cta, contact)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.content"
    label = "content"
    verbose_name = _("Landing content blocks")
