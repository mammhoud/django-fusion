"""
Wagtail Hooks for Structa Cloud
"""

from django.utils.translation import gettext_lazy as _

# Import all ViewSets from django-grep
# Manage snippets
from django_rseal.pipelines.snippets.manage.submissions import FormSubmissionViewSet
from plugins.accounts.snippets.manage.peoples import (
    CompanyViewSet,
    PersonViewSet,
    ServiceViewSet,
    # InvitationViewSet,
    # ContactEmailViewSet,
    # ContactPhoneViewSet,
    # BranchViewSet,
    # FooterTextViewSet,
    # DepartmentViewSet,
    # ContactViewSet,
    TeamViewSet,
    WorkspaceViewSet,
)
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

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
