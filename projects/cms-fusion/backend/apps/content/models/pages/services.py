from django.utils.translation import gettext_lazy as _

from apps.handlers.models.manage.service import Service

from .base import BaseIndexPage


class ServicesPage(BaseIndexPage):
    """Displays a list of active Services"""

    template = "base_page.html"
    template_name = "services/main.html"
    fragment_name = "services.index"
    page_title = _("Services Page")

    class Meta:
        verbose_name = _("Services Page")
        verbose_name_plural = _("Services Pages")
        db_table = "content_servicespage"

    def get_listed_items(self):
        return Service.objects.filter(is_active=True).order_by("name")  # noqa: F821
