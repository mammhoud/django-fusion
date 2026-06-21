"""
Compatibility shims for crafts_ai blocks and models.

Resolves the old 'crafts_ai.content.*' API paths to the correct
locations in the installed version of crafts_ai.

Block locations (installed version):
  ContactCardBlock  → crafts_ai.blocks.contact.contact_card
  PageLinkBlock     → crafts_ai.blocks.partials.button
  ContactMethodBlock → crafts_ai.blocks.contact.contact_methods
  FAQSectionBlock   → crafts_ai.blocks.partials.faq
  MediaGalleryBlock → crafts_ai.blocks.media.gallery

Model locations:
  DefaultBase       → crafts_ai.models.default
  Organization      → crafts_ai.handlers.models.manage_company
  Contact / Corporate → crafts_ai.contrib.core.models
  Team              → crafts_ai.models.users.team
  Person            → crafts_ai.models.users.users
"""

# ---------------------------------------------------------------------------
# Blocks — import directly from the correct installed paths
# ---------------------------------------------------------------------------
from crafts_ai.blocks.contact.contact_card import ContactCardBlock
from crafts_ai.blocks.contact.contact_methods import ContactMethodBlock
from crafts_ai.blocks.media.gallery import MediaGalleryBlock
from crafts_ai.blocks.partials.button import PageLinkBlock
from crafts_ai.blocks.partials.faq import FAQSectionBlock

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
# Import DefaultBase directly from the submodule to avoid triggering
# crafts_ai.models.__init__ which tries to register EmailSettings
# (a Wagtail GenericSetting) before crafts_ai is in INSTALLED_APPS.
from crafts_ai.models.default import DefaultBase
from crafts_ai.handlers.models.manage_company import Organization

__all__ = [
    "ContactCardBlock",
    "ContactMethodBlock",
    "MediaGalleryBlock",
    "PageLinkBlock",
    "FAQSectionBlock",
    "DefaultBase",
    "Organization",
]
