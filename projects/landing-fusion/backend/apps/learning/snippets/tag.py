from django.utils.translation import gettext_lazy as _

from wagtail.snippets.views.snippets import SnippetViewSet

from apps.learning.models import CourseTag


class CourseTagSnippetViewSet(SnippetViewSet):
    model = CourseTag
    menu_label = _("Course tags")
    menu_icon = "tag"
    list_display = ["name", "slug"]
    search_fields = ["name"]
