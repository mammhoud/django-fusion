"""
Compatibility shims for ceptor_ai blocks and models.

Resolves the old 'ceptor_ai.content.*' API paths to the correct
locations in the installed version of ceptor_ai.

Block locations (installed version):
  ContactCardBlock  → ceptor_ai.blocks.contact.contact_card
  PageLinkBlock     → ceptor_ai.blocks.partials.button
  ContactMethodBlock → ceptor_ai.blocks.contact.contact_methods
  FAQSectionBlock   → ceptor_ai.blocks.partials.faq
  MediaGalleryBlock → ceptor_ai.blocks.media.gallery

Model locations:
  DefaultBase       → ceptor_ai.models.default
  Organization      → ceptor_ai.handlers.models.manage_company
  Contact / Corporate → ceptor_ai.contrib.core.models
  Team              → ceptor_ai.models.users.team
  Person            → ceptor_ai.models.users.users
"""

# ---------------------------------------------------------------------------
# Blocks — import directly from the correct installed paths
# ---------------------------------------------------------------------------
from ceptor_ai.blocks.contact.contact_card import ContactCardBlock
from ceptor_ai.blocks.contact.contact_methods import ContactMethodBlock
from ceptor_ai.blocks.media.gallery import MediaGalleryBlock
from ceptor_ai.blocks.partials.button import PageLinkBlock
from ceptor_ai.blocks.partials.faq import FAQSectionBlock

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
# Import DefaultBase directly from the submodule to avoid triggering
# ceptor_ai.models.__init__ which tries to register EmailSettings
# (a Wagtail GenericSetting) before ceptor_ai is in INSTALLED_APPS.
from ceptor_ai.models.default import DefaultBase
from ceptor_ai.handlers.models.manage_company import Organization

__all__ = [
    "ContactCardBlock",
    "ContactMethodBlock",
    "MediaGalleryBlock",
    "PageLinkBlock",
    "FAQSectionBlock",
    "DefaultBase",
    "Organization",
]
