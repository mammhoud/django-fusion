"""
Wagtail Hooks for Alliance Project
"""

from django.utils.translation import gettext_lazy as _

# Manage snippets
from django_rseal.pipelines.snippets.manage.submissions import FormSubmissionViewSet
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from apps.accounts.snippets.manage.peoples import (
    CompanyViewSet,
    PersonViewSet,
    ServiceViewSet,
    TeamViewSet,
    WorkspaceViewSet,
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
        # PersonViewSet,
        # WorkspaceViewSet,
        # CompanyViewSet,

        # Form Submissions
        FormSubmissionViewSet,
    )


# # =============================================================================
# # This ensures the group's URL namespaces are registered before the URL conf
# # =============================================================================
register_snippet(ManagementsSnippetGroup)
