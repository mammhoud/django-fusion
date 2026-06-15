from django.utils.translation import gettext_lazy as _

from plugins.accounts.snippets import BaseSnippetViewSet

from ..models import Course, Module


class CourseSnippet(BaseSnippetViewSet):
    """
    Snippet admin configuration for managing courses in Wagtail CMS.
    """

    model = Course
    icon = "media"
    menu_label = _("Courses")
    menu_order = 100
    list_display = ["title", "language", "is_published", "is_featured", "publication_date"]
    list_filter = ["is_published", "is_featured", "language"]
    search_fields = ["title", "slug", "overview"]
    inspect_view_enabled = True

    panels = Course.panels

class ModuleSnippet(BaseSnippetViewSet):
    """
    Snippet admin configuration for managing course modules.
    """

    model = Module
    icon = "list-ul"
    menu_label = _("Modules")
    menu_order = 110
    list_display = ["title", "course", "order", "has_quiz", "has_assignment"]
    list_filter = ["course", "has_quiz", "has_assignment"]
    search_fields = ["title", "course__title"]
    inspect_view_enabled = True

    panels = Module.panels

# class TrackSnippet(BaseSnippetViewSet):
#     """
#     Snippet admin configuration for managing tracks (course groups).
#     """

#     model = Track
#     icon = "folder-open-inverse"
#     menu_label = _("Tracks")
#     menu_order = 120
#     list_display = ["title", "specialization"]
#     search_fields = ["title", "description"]
#     inspect_view_enabled = True

#     panels = Track.panels
