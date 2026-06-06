from django.utils.translation import gettext_lazy as _
from plugins.accounts.models.manage.service import Service

from .base import BaseIndexPage


class ServicesPage(BaseIndexPage):
    """Displays a list of active Services"""

    fragment_name = "services.index"
    template = "base_page.html"
    page_title = _("Services Page")

    class Meta:
        verbose_name = _("Services Page")
        verbose_name_plural = _("Services Pages")
        db_table = "content_servicespage"

    def get_listed_items(self):
        return Service.objects.filter(is_active=True).order_by("name")  # noqa: F821
