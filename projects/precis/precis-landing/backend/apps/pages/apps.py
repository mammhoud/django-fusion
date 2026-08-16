from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PagesConfig(AppConfig):
    """Wagtail page models for the landing site (Home / About / Services / Products / Features / Projects / Blog / Pricing / Contact / FAQ / Privacy)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"
    label = "pages"
    verbose_name = _("Landing pages")

    def ready(self):
        # Pre-register the shared content-region partial as an include-path
        # component so `{% comp "pages/partials/page_content.html" /%}` gets a
        # stable identity (and the slash path never leaks into data-block-*
        # attributes if COMPONENTS_ENABLE_BLOCK_ATTRS is later enabled).
        from django_fusion.comp.registry import register_include_paths

        register_include_paths(["pages/partials/page_content.html"])
