from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BuilderAppConfig(AppConfig):
    """App config for the landing builder.

    Add ``django_fusion.builder`` to ``INSTALLED_APPS`` to enable the
    builder's templates (``builder/page.html``, ``builder/sections/*.html``)
    and static assets. The abstract ``BuilderPage`` model produces no
    migrations of its own — concrete subclasses live in consuming products.
    """

    name = "django_fusion.builder"
    label = "fusion_builder"
    verbose_name = _("Landing Builder")
    default_auto_field = "django.db.models.BigAutoField"
