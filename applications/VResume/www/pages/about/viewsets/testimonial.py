from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn
from core.snippets import BaseSnippetViewSet
from pages.about.models import Testimonial


class TestimonialViewSet(BaseSnippetViewSet):
    model = Testimonial
    icon = "openquote"
    menu_label = _("Testimonials")
    menu_order = 100
    list_display = ["name", "job_title", BooleanColumn("is_active", label=_("Active")), "order"]
    list_filter = ["is_active"]
    search_fields = ["name", "job_title", "text"]
    ordering = ["order", "name"]
