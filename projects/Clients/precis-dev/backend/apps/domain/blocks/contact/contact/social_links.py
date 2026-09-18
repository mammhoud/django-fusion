import logging

from django.utils.translation import gettext_lazy as _
from wagtail import blocks

logger = logging.getLogger(__name__)

__all__ = ["SocialLinkBlock"]


class SocialLinkBlock(blocks.StructBlock):
    """
    Enhanced block for social media links with auto-generated icons and URLs.
    """

    PLATFORM_CHOICES = [
        ("linkedin", _("LinkedIn")),
        ("twitter", _("Twitter/X")),
        ("facebook", _("Facebook")),
        ("instagram", _("Instagram")),
        ("github", _("GitHub")),
        ("youtube", _("YouTube")),
        ("whatsapp", _("WhatsApp")),
        ("telegram", _("Telegram")),
        ("portfolio", _("Portfolio")),
        ("website", _("Personal Website")),
        ("other", _("Other Platform")),
    ]

    platform = blocks.ChoiceBlock(
        choices=PLATFORM_CHOICES, label=_("Platform"), default="linkedin"
    )

    username = blocks.CharBlock(
        required=False,
        label=_("Username/Handle"),
        help_text=_("Your username on this platform"),
    )

    profile_url = blocks.URLBlock(
        required=False,
        label=_("Profile URL"),
        help_text=_("Full URL to your profile (auto-generated if blank)"),
    )

    custom_platform = blocks.CharBlock(
        max_length=50,
        required=False,
        label=_("Custom Platform Name"),
        help_text=_("If 'Other Platform' is selected, specify the platform name"),
    )

    platform_display = blocks.CharBlock(
        required=False,
        label=_("Platform Display Name"),
        help_text=_("Auto-generated display name"),
    )

    is_primary = blocks.BooleanBlock(
        default=False,
        required=False,
        label=_("Primary Profile"),
        help_text=_("Mark as primary profile for this platform"),
    )

    is_public = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Public Profile"),
        help_text=_("Show this profile publicly"),
    )

    verified = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Verified"),
        help_text=_("Mark as verified if confirmed"),
    )

    icon_class = blocks.CharBlock(
        required=False,
        label=_("Icon CSS Class"),
        help_text=_("Optional CSS class for custom icons (e.g., FontAwesome classes)."),
        default="",
    )

    notes = blocks.TextBlock(
        required=False,
        label=_("Notes"),
        help_text=_("Additional notes about this profile"),
    )

    class Meta:
        label = _("Social Media Profile")
        icon = "site"
        form_classname = "social-link-block"

    def clean(self, value):
        cleaned_data = super().clean(value)

        platform = cleaned_data.get("platform")
        username = cleaned_data.get("username", "")

        # Auto-generate profile URL if not provided and username exists
        if not cleaned_data.get("profile_url") and username:
            url_templates = {
                "linkedin": f"https://linkedin.com/in/{username}",
                "twitter": f"https://twitter.com/{username}",
                "facebook": f"https://facebook.com/{username}",
                "instagram": f"https://instagram.com/{username}",
                "github": f"https://github.com/{username}",
                "youtube": f"https://youtube.com/@{username}",
                "portfolio": f"https://{username}",
                "website": f"https://{username}",
            }

            if platform in url_templates:
                cleaned_data["profile_url"] = url_templates[platform]

        # Set custom platform name
        if platform == "other" and cleaned_data.get("custom_platform"):
            cleaned_data["platform_display"] = cleaned_data["custom_platform"]
        else:
            cleaned_data["platform_display"] = dict(self.PLATFORM_CHOICES).get(
                platform, platform
            )

        # Set default icon class if not provided
        if not cleaned_data.get("icon_class"):
            icon_map = {
                "linkedin": "bi bi-linkedin",
                "twitter": "bi bi-twitter",
                "facebook": "bi bi-facebook",
                "instagram": "bi bi-instagram",
                "github": "bi bi-github",
                "youtube": "bi bi-youtube",
                "portfolio": "bi bi-briefcase",
                "website": "bi bi-globe",
            }
            cleaned_data["icon_class"] = icon_map.get(platform, "bi bi-link")

        return cleaned_data
