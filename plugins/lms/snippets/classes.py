from django.utils.translation import gettext_lazy as _

from www.apps.accounts.snippets import BaseSnippetViewSet

from ..models import Classes, Schedule

class ScheduleSnippet(BaseSnippetViewSet):
    """
    Snippet admin configuration for managing schedules.
    """

    model = Schedule
    icon = "date"
    menu_label = _("Schedules")
    menu_order = 140
    list_display = ["title", "schedule_type", "start_date", "start_time", "end_time", "is_active"]
    list_filter = [
        "is_active",
        "schedule_type",
    ]
    search_fields = ["title"]
    inspect_view_enabled = True

    panels = Schedule.panels

class ClassesSnippet(BaseSnippetViewSet):
    """
    Snippet admin configuration for managing individual course classes.
    """

    model = Classes
    icon = "user"
    menu_label = _("Classes")
    menu_order = 130
    list_display = ["course", "module"]
    search_fields = ["course__title", "module__title"]
    inspect_view_enabled = True

    panels = Classes.panels

