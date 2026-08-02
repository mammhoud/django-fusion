from django.utils.translation import gettext_lazy as _

from apps.domain.contrib.snippets.base import BaseSnippetViewSet
from apps.pages.lms.models import Review


class ReviewViewSet(BaseSnippetViewSet):
    """Admin interface for managing Course Reviews."""

    model = Review
    menu_label = _("Reviews")
    icon = "folder-open-inverse"
    menu_order = 190
    search_fields = ["profile__user__username", "course__title", "comment"]
    ordering = ["-created_at"]

    list_display = [
        "course",
        "profile",
        "rating",
        "comment",
        "is_displayed",
    ]
    list_filter = ["rating", "is_displayed", "course"]
    list_export = ["course", "profile", "rating", "comment", "is_displayed"]
    csv_filename = "reviews.csv"

    # ======================
    # DISPLAY HELPERS
    # ======================

    @staticmethod
    def course_display(obj):
        """Show the related course title."""
        return f"🎓 {obj.course.title}" if obj.course else "—"
    course_display.short_description = _("Course")

    @staticmethod
    def student_display(obj):
        """Show the student name."""
        if hasattr(obj.profile.user, "get_full_name"):
            return f"👤 {obj.profile.user.get_full_name()}"
        return str(obj.profile)
    student_display.short_description = _("Student")

    @staticmethod
    def rating_display(obj):
        """Show rating visually as stars."""
        return f"{obj.stars} ({obj.rating}/5)"
    rating_display.short_description = _("Rating")

    @staticmethod
    def comment_display(obj):
        """Show a shortened version of the comment."""
        return obj.short_comment
    comment_display.short_description = _("Comment")

    @staticmethod
    def is_displayed_display(obj):
        """Show visibility status."""
        return "🟢" if obj.is_displayed else "🔴"
    is_displayed_display.short_description = _("Visible")
