from django.utils.translation import gettext_lazy as _
from wagtail.snippets.views.snippets import SnippetViewSet

from ceptor_ai.content.models.contacts.submission import FormSubmission


class FormSubmissionViewSet(SnippetViewSet):
    """
    Admin view for form submissions.
    """
    model = FormSubmission
    icon = "form"
    menu_label = _("Form Submissions")
    menu_name = "form_submissions"
    menu_order = 400
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ["id", "form_name", "page_title", "submitted_at", "summary"]
    list_filter = ["form_name", "submitted_at", "page"]
    search_fields = ["form_data", "ip_address", "user_agent"]

    def page_title(self, obj):
        return obj.page_title

    def summary(self, obj):
        return obj.summary

    def get_template_names(self, request):
        if self.action == "detail":
            return ["wagtailadmin/snippets/formsubmission/detail.html"]

