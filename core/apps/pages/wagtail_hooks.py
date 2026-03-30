"""
Wagtail Hooks for Alliance Project
"""

from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

# Import all ViewSets from django-grep

# Manage snippets
from django_grep.pipelines.snippets.manage.submissions import FormSubmissionViewSet
from apps.handlers.snippets.manage.peoples import (
    PersonViewSet,
    WorkspaceViewSet,
    CompanyViewSet,
    # DepartmentViewSet,
    # ContactViewSet,
    TeamViewSet,
    ServiceViewSet,
    # InvitationViewSet,
    # ContactEmailViewSet,
    # ContactPhoneViewSet,
    # BranchViewSet,
    # FooterTextViewSet,
)


# =============================================================================
# SNIPPET GROUP: Manage
# =============================================================================

class ManagementsSnippetGroup(SnippetViewSetGroup):
    """
    Management snippets for people, contacts, and form submissions.
    """
    menu_label = _("Manage")
    menu_icon = "briefcase"
    menu_order = 200
    items = (
        # People & Organizations
        PersonViewSet,
        WorkspaceViewSet,
        CompanyViewSet,
        # DepartmentViewSet,

        # Teams & Services
        TeamViewSet,
        ServiceViewSet,

        # Form Submissions
        FormSubmissionViewSet,

        # Contacts & Others (Commented out)
        # ContactViewSet,
        # ContactEmailViewSet,
        # ContactPhoneViewSet,
        # BranchViewSet,
        # InvitationViewSet,
        # FooterTextViewSet,
    )


# =============================================================================
# REGISTER SNIPPET GROUPS
# =============================================================================

register_snippet(ManagementsSnippetGroup)
