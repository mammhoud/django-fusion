"""
Compatibility shims for django_rseal blocks and models.

Resolves the old 'django_rseal.content.*' API paths to the correct
locations in the installed version of django_rseal.

Block locations (installed version):
  ContactCardBlock  → django_rseal.blocks.contact.contact_card
  PageLinkBlock     → django_rseal.blocks.partials.button
  ContactMethodBlock → django_rseal.blocks.contact.contact_methods
  FAQSectionBlock   → django_rseal.blocks.partials.faq
  MediaGalleryBlock → django_rseal.blocks.media.gallery

Model locations:
  DefaultBase       → django_rseal.models.default
  Organization      → django_rseal.handlers.models.manage_company
  Contact / Corporate → django_rseal.contrib.core.models
  Team              → django_rseal.models.users.team
  Person            → django_rseal.models.users.users
"""

# ---------------------------------------------------------------------------
# Blocks — import directly from the correct installed paths
# ---------------------------------------------------------------------------
from django_rseal.blocks.contact.contact_card import ContactCardBlock
from django_rseal.blocks.contact.contact_methods import ContactMethodBlock
from django_rseal.blocks.media.gallery import MediaGalleryBlock
from django_rseal.blocks.partials.button import PageLinkBlock
from django_rseal.blocks.partials.faq import FAQSectionBlock

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
# Import DefaultBase directly from the submodule to avoid triggering
# django_rseal.models.__init__ which tries to register EmailSettings
# (a Wagtail GenericSetting) before django_rseal is in INSTALLED_APPS.
from django_rseal.models.default import DefaultBase
from django_rseal.handlers.models.manage_company import Organization

__all__ = [
    "ContactCardBlock",
    "ContactMethodBlock",
    "MediaGalleryBlock",
    "PageLinkBlock",
    "FAQSectionBlock",
    "DefaultBase",
    "Organization",
]
