"""
Wagtail Blocks: Base classes for Wagtail StreamField blocks.

Canonical import: from apps.domain.blocks.blocks import OrganizationChooserBlockBase

Projects should subclass this and inject their Organization model.
"""

from django.utils.translation import gettext_lazy as _
from wagtail.snippets.blocks import SnippetChooserBlock


class OrganizationChooserBlockBase(SnippetChooserBlock):
    """
    Base class for Organization chooser block in StreamFields.

    Projects should subclass this and set the target_model:

    class OrganizationChooserBlock(OrganizationChooserBlockBase):
        def __init__(self, **kwargs):
            from apps.handlers.models.manage.company import Organization
            super().__init__(Organization, **kwargs)
    """

    class Meta:
        icon = "group"
        label = _("Organization")
