from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn

from core.snippets import BaseSnippetViewSet
from pages.connect.models import FormSubmission


class FormSubmissionViewSet(BaseSnippetViewSet):
    model = FormSubmission
    icon = "form"
    menu_label = _("Form Submissions")
    menu_name = "form_submissions"
    menu_group = "communications"
    menu_order = 110

    list_display = [
        "form_id",
        "page",
        "get_name",
        "get_email",
        "submitted_at",
        BooleanColumn("email_sent", label=_("Email Sent")),
        BooleanColumn("is_read", label=_("Read")),
    ]
    list_filter = ["form_id", "email_sent", "is_read", "submitted_at"]
    search_fields = ["form_id", "data", "ip_address", "user_agent"]
    ordering = ["-submitted_at"]
    list_export = ["form_id", "submitted_at", "email_sent", "is_read", "ip_address"]
    csv_filename = "form_submissions.csv"
