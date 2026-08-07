from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import Certificate, CourseSnippetViewSet, Enrollment, Review, Wishlist


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
    list_display = ["course", "user", "rating", "is_published", "created_at"]
    list_filter = ["is_published", "rating"]
    search_fields = ["course__title", "user__email", "body"]


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
        EnrollmentSnippetViewSet,
        CertificateSnippetViewSet,
        ReviewSnippetViewSet,
        WishlistSnippetViewSet,
    )


# CourseSnippetViewSet is defined with the model in models.py to keep the
# course's Wagtail panels beside its content schema. The remaining operational
# snippets live in this grouped hook module.
register_snippet(LearningAdminGroup)
