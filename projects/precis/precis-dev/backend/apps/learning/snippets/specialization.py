from django.utils.translation import gettext_lazy as _
from wagtail.snippets.views.snippets import SnippetViewSet

from apps.learning.models import Specialization


class SpecializationSnippetViewSet(SnippetViewSet):
    model = Specialization
    menu_label = _("Specializations")
    menu_icon = "tag"
    list_display = ["title", "order", "is_active", "course_count"]
    list_filter = ["is_active"]
    search_fields = ["title", "description"]
