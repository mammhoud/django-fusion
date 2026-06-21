from django.utils.translation import gettext_lazy as _
from crafts_ai.rseal.handlers.models.manage_company import Organization
from wagtail.snippets.blocks import SnippetChooserBlock


class OrganizationChooserBlock(SnippetChooserBlock):
    """
    🔗 Chooser block for selecting Organization snippets in StreamFields.
    """
    def __init__(self, **kwargs):
        super().__init__(Organization, **kwargs)

    class Meta:
        icon = "group"
        label = _("Organization")
