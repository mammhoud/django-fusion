from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import (
    Certificate,
    CourseSnippetViewSet,
    CourseTranslation,
    Enrollment,
    Review,
    Wishlist,
)
from .snippets import CourseTagSnippetViewSet, SpecializationSnippetViewSet


class CourseTranslationSnippetViewSet(SnippetViewSet):
    model = CourseTranslation
    menu_label = _("Course translations")
    icon = "doc-full-inverse"
    list_display = ["course", "language", "title", "updated_at"]
    list_filter = ["language"]
    search_fields = ["course__title", "title"]


class EnrollmentSnippetViewSet(SnippetViewSet):
    model = Enrollment
    menu_label = _("Enrollments")
    icon = "group"
    list_display = ["user", "course", "status", "progress", "enrolled_at"]
    list_filter = ["status"]
    search_fields = ["user__email", "course__title"]


class CertificateSnippetViewSet(SnippetViewSet):
    model = Certificate
    menu_label = _("Certificates")
    icon = "doc-full"
    list_display = ["certificate_id", "user", "course", "issued_at"]
    search_fields = ["certificate_id", "user__email", "course__title"]


class ReviewSnippetViewSet(SnippetViewSet):
    model = Review
    menu_label = _("Reviews")
    icon = "comment"
    list_display = [
        "course",
        "user",
        "rating_display",
        "body_display",
        "is_published_display",
        "created_at",
    ]
    list_filter = ["is_published", "rating", "course"]
    search_fields = ["course__title", "user__email", "body"]
    list_export = ["course", "user", "rating", "body", "is_published", "created_at"]
    csv_filename = "reviews.csv"

    @staticmethod
    def rating_display(obj):
        """Show rating visually as stars."""
        return f"{obj.stars} ({obj.rating}/5)"

    rating_display.short_description = _("Rating")

    @staticmethod
    def body_display(obj):
        """Shortened comment preview."""
        return obj.short_body

    body_display.short_description = _("Comment")

    @staticmethod
    def is_published_display(obj):
        """Visibility status badge."""
        return "🟢" if obj.is_published else "🔴"

    is_published_display.short_description = _("Published")


class WishlistSnippetViewSet(SnippetViewSet):
    model = Wishlist
    menu_label = _("Wishlists")
    icon = "pick"
    list_display = ["user", "course", "created_at"]
    search_fields = ["user__email", "course__title"]


class LearningAdminGroup(SnippetViewSetGroup):
    menu_label = _("Learning")
    menu_icon = "book"
    menu_order = 120
    items = (
        CourseSnippetViewSet,
        CourseTranslationSnippetViewSet,
        SpecializationSnippetViewSet,
        CourseTagSnippetViewSet,
        EnrollmentSnippetViewSet,
        CertificateSnippetViewSet,
        ReviewSnippetViewSet,
        WishlistSnippetViewSet,
    )


# CourseSnippetViewSet is defined with the model in models.py to keep the
# course's Wagtail panels beside its content schema. The remaining operational
# snippets live in this grouped hook module.
register_snippet(LearningAdminGroup)
