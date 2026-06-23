"""
Wagtail Hooks for django-grep pipelines.
"""

from django.utils.translation import gettext_lazy as _
from crafts_ai.content.snippets import (
    BackgroundTaskLogViewSet,
    EmailSettingsViewSet,
    GlobalSettingsViewSet,
    NewsletterSnippetGroup,
    TechBridgesViewSet,
)
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from .snippets.banner import AnnouncementBannerViewSet
from .snippets.certification import CertificationViewSet
from .snippets.coupon import CouponViewSet

# =============================================================================
# SNIPPET GROUP: Brand Settings
# =============================================================================


class TechBridgesSnippetGroup(SnippetViewSetGroup):
    """
    Site-wide configuration and settings.
    """

    menu_label = _("Tech Bridges")
    menu_icon = "cog"
    menu_order = 900
    items = (
        TechBridgesViewSet,
        GlobalSettingsViewSet,
        EmailSettingsViewSet,
        AnnouncementBannerViewSet,
    )


# =============================================================================
# REGISTER SNIPPETS & GROUPS
# =============================================================================

register_snippet(TechBridgesSnippetGroup)
register_snippet(BackgroundTaskLogViewSet)
register_snippet(NewsletterSnippetGroup)
register_snippet(CertificationViewSet)
register_snippet(CouponViewSet)


# =============================================================================
# REGISTER ICONS
# =============================================================================


@hooks.register("register_icons")
def register_icons(icons):
    """
    Register FontAwesome SVG icons.
    """
    return icons + [
        "wagtailfontawesomesvg/solid/suitcase.svg",
        "wagtailfontawesomesvg/solid/utensils.svg",
        "wagtailfontawesomesvg/solid/chart-line.svg",
        "wagtailfontawesomesvg/solid/users.svg",
        "wagtailfontawesomesvg/brands/facebook.svg",
        "wagtailfontawesomesvg/regular/face-laugh.svg",
        "wagtailfontawesomesvg/solid/yin-yang.svg",
        "wagtailfontawesomesvg/solid/address-card.svg",
        "wagtailfontawesomesvg/solid/info-circle.svg",
        "wagtailfontawesomesvg/solid/map-marker-alt.svg",
        "wagtailfontawesomesvg/solid/phone-alt.svg",
        "wagtailfontawesomesvg/solid/envelope.svg",
        "wagtailfontawesomesvg/solid/map-marked-alt.svg",
        "wagtailfontawesomesvg/solid/question-circle.svg",
        "wagtailfontawesomesvg/solid/images.svg",
        "wagtailfontawesomesvg/solid/list-ul.svg",
        "wagtailfontawesomesvg/solid/user-tie.svg",
        "wagtailfontawesomesvg/solid/th-list.svg",
        "wagtailfontawesomesvg/solid/check-double.svg",
        "wagtailfontawesomesvg/solid/users.svg",
        "wagtailfontawesomesvg/solid/briefcase.svg",
        "wagtailfontawesomesvg/solid/paper-plane.svg",
        "wagtailfontawesomesvg/solid/id-card.svg",
        "wagtailfontawesomesvg/solid/bullhorn.svg",
        "wagtailfontawesomesvg/solid/briefcase.svg",
        "wagtailfontawesomesvg/solid/cog.svg",
    ]


# =============================================================================
# MAIN MENU CUSTOMIZATION
# =============================================================================


@hooks.register("construct_main_menu")
def customize_main_menu(request, menu_items):
    # Hide explorer for non‑staff users
    if not request.user.is_staff:
        menu_items[:] = [item for item in menu_items if item.name != "explorer"]

    # Move 'Styleguide' under the 'Help' menu
    styleguide_item = None
    help_item = None
    for item in menu_items:
        if item.name == "styleguide":
            styleguide_item = item
        if item.name == "help":
            help_item = item

    if styleguide_item and help_item:
        menu_items.remove(styleguide_item)
        styleguide_item.parent_name = "help"
        menu_items.append(styleguide_item)

    return menu_items
