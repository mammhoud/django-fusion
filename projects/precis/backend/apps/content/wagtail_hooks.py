"""
Wagtail Hooks for Fusion CMS Project

This file registers page models with Wagtail so they can be edited
in the Wagtail admin and rendered with their custom templates.
"""
from django.utils.module_loading import autodiscover_modules


def ready():
    """Register all page models with Wagtail."""
    # Import the models to ensure they're registered with Wagtail
    from apps.content.models.pages.home import HomePage  # noqa: F401
    from apps.content.models.pages.about import AboutPage  # noqa: F401
    from apps.content.models.pages.contact import ContactPage  # noqa: F401
    from apps.content.models.pages.events import EventPage  # noqa: F401 (EventPage not EventsPage)
    from apps.content.models.pages.services import ServicesPage  # noqa: F401
    from apps.content.models.pages.team import TeamPage  # noqa: F401

    # ── Dynamic CMS pages (from merged cms www.content.models) ──
    from apps.content.models.pages.dynamic import (  # noqa: F401
        DynamicHomePage,
        DynamicAboutPage,
        DynamicFaqPage,
        DynamicPrivacyPage,
        DynamicContactPage,
        DynamicDashboardPage,
    )


# Call ready() when the app is ready
ready()
