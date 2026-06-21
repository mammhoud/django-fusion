"""
Compatibility shims for crafts_ai.rseal blocks and models.

Resolves the old 'crafts_ai.rseal.content.*' API paths to the correct
locations in the installed version of crafts_ai.rseal.

Block locations (installed version):
  ContactCardBlock  → crafts_ai.rseal.blocks.contact.contact_card
  PageLinkBlock     → crafts_ai.rseal.blocks.partials.button
  ContactMethodBlock → crafts_ai.rseal.blocks.contact.contact_methods
  FAQSectionBlock   → crafts_ai.rseal.blocks.partials.faq
  MediaGalleryBlock → crafts_ai.rseal.blocks.media.gallery

Model locations:
  DefaultBase       → crafts_ai.rseal.models.default
  Organization      → crafts_ai.rseal.handlers.models.manage_company
  Contact / Corporate → crafts_ai.rseal.contrib.core.models
  Team              → crafts_ai.rseal.models.users.team
  Person            → crafts_ai.rseal.models.users.users
"""

# ---------------------------------------------------------------------------
# Blocks — import directly from the correct installed paths
# ---------------------------------------------------------------------------
from crafts_ai.rseal.blocks.contact.contact_card import ContactCardBlock
from crafts_ai.rseal.blocks.contact.contact_methods import ContactMethodBlock
from crafts_ai.rseal.blocks.media.gallery import MediaGalleryBlock
from crafts_ai.rseal.blocks.partials.button import PageLinkBlock
from crafts_ai.rseal.blocks.partials.faq import FAQSectionBlock

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
# Import DefaultBase directly from the submodule to avoid triggering
# crafts_ai.rseal.models.__init__ which tries to register EmailSettings
# (a Wagtail GenericSetting) before crafts_ai.rseal is in INSTALLED_APPS.
from crafts_ai.rseal.models.default import DefaultBase
from crafts_ai.rseal.handlers.models.manage_company import Organization

__all__ = [
    "ContactCardBlock",
    "ContactMethodBlock",
    "MediaGalleryBlock",
    "PageLinkBlock",
    "FAQSectionBlock",
    "DefaultBase",
    "Organization",
]
