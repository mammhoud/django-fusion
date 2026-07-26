from django.utils.translation import gettext_lazy as _
from wagtail.snippets.views.snippets import SnippetViewSet

from plugins.lms.models import Enrollment


class EnrollmentViewSet(SnippetViewSet):
    """
    Admin management for student enrollments.
    """
    model = Enrollment
    menu_label = _("Enrollments")
    icon = "user"  # Choose an appropriate icon
    menu_order = 500
    list_display = ["student", "course", "status", "payment_status", "amount_paid", "enrolled_at"]
    list_filter = ["status", "payment_status", "course"]
    search_fields = ["student__username", "student__email", "course__title", "payment_reference"]

    # Optional: Customize templates if needed, but default is usually fine for snippets.
