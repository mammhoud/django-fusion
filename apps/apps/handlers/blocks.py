from django.utils.translation import gettext_lazy as _
from wagtail.snippets.blocks import SnippetChooserBlock
from apps.handlers.models.manage.company import Organization

class OrganizationChooserBlock(SnippetChooserBlock):
    """
    🔗 Chooser block for selecting Organization snippets in StreamFields.
    """
    def __init__(self, **kwargs):
        super().__init__(Organization, **kwargs)

    class Meta:
        icon = "group"
        label = _("Organization")
