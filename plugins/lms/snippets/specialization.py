from django.utils.translation import gettext_lazy as _
from django_filters import CharFilter
from wagtail.admin.filters import WagtailFilterSet

from plugins.accounts.filters.revision import RevisionFilterSetMixin
from plugins.accounts.snippets import BaseSnippetViewSet

from ..models import Specialization


class SpecializationFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    """
    Filtering for Specialization model.
    """
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Specialization name contains')
    )
    description = CharFilter(
        field_name='description',
        lookup_expr='icontains',
        label=_('Description contains')
    )

    class Meta:
        model = Specialization
        fields = {}


class SpecializationViewSet(BaseSnippetViewSet):
    """
    Admin interface for managing Course Specializations.
    Organizes courses into categories and topics.
    """
    model = Specialization
    menu_label = _("Specializations")
    icon = "tag"
    menu_order = 130
    add_to_settings_menu = False
    exclude_from_explorer = False

    list_display = [
        "name",
        "description",
        "courses_count",
        "is_active"
    ]

    list_filter = {
        "is_active": ["exact"],
    }

    search_fields = ["name", "description"]
    ordering = ["name"]

    filterset_class = SpecializationFilterSet

    # Custom columns
    @staticmethod
    def courses_count(specialization):
        return specialization.courses.count()

    courses_count.short_description = _("Courses")

    # Custom actions
    list_actions = ["update_courses_count_action"]

    def update_courses_count_action(self, request, queryset):
        """
        Update cached courses count for specializations.
        """
        from django.contrib import messages
        from django.utils.translation import ngettext

        updated_count = 0
        for specialization in queryset:
            # This would trigger any cached count updates
            specialization.save()
            updated_count += 1

        message = ngettext(
            "Updated courses count for %(count)d specialization",
            "Updated courses count for %(count)d specializations",
            updated_count
        ) % {"count": updated_count}
        messages.success(request, message)

    update_courses_count_action.label = _("Update counts")
    update_courses_count_action.icon = "refresh"

