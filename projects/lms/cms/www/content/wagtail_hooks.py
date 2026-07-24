"""
Wagtail hooks — register CMS page models for admin panel management.

All content pages (HomePage, AboutPage, FaqPage, PrivacyPage, ContactPage)
are registered here so they appear in the Wagtail admin page tree.
"""

from wagtail import hooks
from wagtail.models import Page

from www.content.models.pages import (
    HomePage,
    AboutPage,
    FaqPage,
    PrivacyPage,
    ContactPage,
)

# All page types that can be created under the root Wagtail page
CMS_PAGE_TYPES = [
    HomePage,
    AboutPage,
    FaqPage,
    PrivacyPage,
    ContactPage,
]


@hooks.register("register_admin_viewset")
def register_cms_pages():
    """Ensure CMS page models are discoverable in Wagtail admin.

    Wagtail auto-discovers Page subclasses from INSTALLED_APPS, so
    these models will appear in the page tree automatically as long
    as ``www.content`` is in ``INSTALLED_APPS``.
    """
    pass  # Auto-discovery via AppConfig — no manual registration needed
