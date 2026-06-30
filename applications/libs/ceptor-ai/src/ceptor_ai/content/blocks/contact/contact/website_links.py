import logging
import uuid
from typing import Any, Dict, Optional

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock

logger = logging.getLogger(__name__)

__all__ = [
    "ContactProfileBlock",
    "ContactProfileStreamBlock",
    "SiteContactSettingsBlock",
]


# =============================================================================
# UNIFIED CONTACT PROFILE BLOCK
# =============================================================================


class ContactProfileBlock(BaseBlock):
    """
    Universal block for managing all types of contact profiles:
    - Social media profiles
    - Website links
    - Contact methods
    - Professional profiles

    Supports auto-generation of URLs, icons, and structured data.
    """

    # === Profile Type Definitions ===
    PROFILE_TYPE_CHOICES = [
        ("social", _("Social Media Profile")),
        ("website", _("Website/Blog")),
        ("professional", _("Professional Profile")),
        ("portfolio", _("Portfolio/Showcase")),
        ("business", _("Business/Company")),
        ("contact", _("Contact Method")),
        ("other", _("Other")),
    ]

    # === Platform Definitions (used when type='social') ===
    SOCIAL_PLATFORM_CHOICES = [
        ("linkedin", _("LinkedIn")),
        ("twitter", _("Twitter/X")),
        ("facebook", _("Facebook")),
        ("instagram", _("Instagram")),
        ("github", _("GitHub")),
        ("youtube", _("YouTube")),
        ("whatsapp", _("WhatsApp Business")),
        ("telegram", _("Telegram")),
        ("discord", _("Discord")),
        ("slack", _("Slack")),
        ("tiktok", _("TikTok")),
        ("pinterest", _("Pinterest")),
        ("reddit", _("Reddit")),
        ("medium", _("Medium")),
        ("behance", _("Behance")),
        ("dribbble", _("Dribbble")),
        ("stackoverflow", _("Stack Overflow")),
        ("gitlab", _("GitLab")),
        ("bitbucket", _("Bitbucket")),
        ("mastodon", _("Mastodon")),
        ("threads", _("Threads")),
        ("snapchat", _("Snapchat")),
        ("twitch", _("Twitch")),
        ("spotify", _("Spotify")),
        ("soundcloud", _("SoundCloud")),
        ("other", _("Other Social Platform")),
    ]

    # === Website Type Definitions (used when type='website') ===
    WEBSITE_TYPE_CHOICES = [
        ("personal", _("Personal Website")),
        ("portfolio", _("Portfolio")),
        ("blog", _("Blog/Newsletter")),
        ("company", _("Company Website")),
        ("project", _("Project Site")),
        ("ecommerce", _("E-commerce Store")),
        ("educational", _("Educational")),
        ("documentation", _("Documentation")),
        ("forum", _("Forum/Community")),
        ("wiki", _("Wiki/KB")),
        ("dashboard", _("Dashboard/Admin")),
        ("landing", _("Landing Page")),
        ("saas", _("SaaS Application")),
        ("api", _("API/Docs")),
        ("other_website", _("Other Website Type")),
    ]

    # === Professional Profile Types ===
    PROFESSIONAL_TYPE_CHOICES = [
        ("upwork", _("Upwork/Freelancer")),
        ("fiverr", _("Fiverr")),
        ("toptal", _("Toptal")),
        ("angel", _("AngelList")),
        ("crunchbase", _("Crunchbase")),
        ("producthunt", _("Product Hunt")),
        ("indiehackers", _("Indie Hackers")),
        ("clutch", _("Clutch")),
        ("glassdoor", _("Glassdoor")),
        ("resume", _("Resume/CV")),
        ("calendly", _("Calendly/Booking")),
        ("other_professional", _("Other Professional")),
    ]

    # === Contact Method Types ===
    CONTACT_TYPE_CHOICES = [
        ("email", _("Email Address")),
        ("phone", _("Phone Number")),
        ("whatsapp", _("WhatsApp")),
        ("signal", _("Signal")),
        ("telegram", _("Telegram")),
        ("skype", _("Skype")),
        ("zoom", _("Zoom")),
        ("meet", _("Google Meet")),
        ("teams", _("Microsoft Teams")),
        ("address", _("Physical Address")),
        ("other_contact", _("Other Contact Method")),
    ]

    # === Core Fields (Common to All Types) ===
    profile_type = blocks.ChoiceBlock(
        choices=PROFILE_TYPE_CHOICES,
        default="social",
        label=_("Profile Type"),
        help_text=_("Category of this profile/link"),
        required=True,
    )

    title = blocks.CharBlock(
        max_length=150,
        required=True,
        label=_("Display Title"),
        help_text=_("How this profile should be displayed"),
    )

    # === Type-Specific Platform/Subtype Selection ===
    social_platform = blocks.ChoiceBlock(
        choices=SOCIAL_PLATFORM_CHOICES,
        default="linkedin",
        label=_("Social Platform"),
        help_text=_("Social media platform"),
        required=False,
    )

    website_type = blocks.ChoiceBlock(
        choices=WEBSITE_TYPE_CHOICES,
        default="personal",
        label=_("Website Type"),
        help_text=_("Type of website"),
        required=False,
    )

    professional_type = blocks.ChoiceBlock(
        choices=PROFESSIONAL_TYPE_CHOICES,
        default="resume",
        label=_("Professional Platform"),
        help_text=_("Professional platform type"),
        required=False,
    )

    contact_type = blocks.ChoiceBlock(
        choices=CONTACT_TYPE_CHOICES,
        default="email",
        label=_("Contact Method"),
        help_text=_("Type of contact method"),
        required=False,
    )

    custom_type = blocks.CharBlock(
        max_length=100,
        required=False,
        label=_("Custom Type"),
        help_text=_("Custom type name for 'Other' selections"),
    )

    # === URL/Value Fields ===
    url = blocks.URLBlock(
        required=False,
        label=_("Profile URL"),
        help_text=_("Full URL to the profile/website"),
    )

    username = blocks.CharBlock(
        required=False,
        label=_("Username/Handle/ID"),
        help_text=_("Username, handle, or identifier for the profile"),
    )

    value = blocks.CharBlock(
        required=False,
        label=_("Value"),
        help_text=_("Value (email, phone number, etc.)"),
    )

    # === Display & UX Fields ===
    description = blocks.TextBlock(
        required=False,
        label=_("Description"),
        help_text=_("Brief description or purpose"),
    )

    thumbnail = ImageChooserBlock(
        required=False,
        label=_("Thumbnail/Logo"),
        help_text=_("Profile picture, logo, or screenshot"),
    )

    icon_class = blocks.CharBlock(
        required=False,
        label=_("Icon CSS Class"),
        help_text=_("CSS classes for icon (e.g., 'fab fa-linkedin')"),
        default="",
    )

    color = blocks.CharBlock(
        required=False,
        max_length=7,
        label=_("Brand Color"),
        help_text=_("Hex color code (e.g., #0077B5 for LinkedIn)"),
    )

    # === Flags & Metadata ===
    is_primary = blocks.BooleanBlock(
        default=False,
        required=False,
        label=_("Primary Profile"),
        help_text=_("Main/default profile for this type"),
    )

    is_public = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Public"),
        help_text=_("Show this profile publicly"),
    )

    verified = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Verified"),
        help_text=_("Mark as verified/confirmed"),
    )

    open_in_new_tab = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Open in New Tab"),
        help_text=_("Open link in new browser tab"),
    )

    priority = blocks.IntegerBlock(
        required=False,
        default=0,
        label=_("Display Priority"),
        help_text=_("Higher numbers appear first (0 = default)"),
        min_value=-10,
        max_value=10,
    )

    # === Metadata ===
    last_verified = blocks.DateTimeBlock(
        required=False,
        label=_("Last Verified"),
        help_text=_("When this profile was last confirmed"),
    )

    notes = blocks.TextBlock(
        required=False,
        label=_("Internal Notes"),
        help_text=_("Private notes for editors"),
    )

    # === Advanced Fields (Conditional) ===
    # embed_code = blocks.RawHTMLBlock(
    #     required=False,
    #     label=_("Embed Code"),
    #     help_text=_("Custom embed/iframe code"),
    # )

    # api_key = blocks.CharBlock(
    #     required=False,
    #     label=_("API Key/Token"),
    #     help_text=_("For integrations (stored securely)"),
    # )

    # metadata = blocks.JSONBlock(
    #     required=False,
    #     default=dict,
    #     label=_("Metadata"),
    #     help_text=_("Additional structured data"),
    # )

    class Meta:
        label = _("Contact Profile")
        icon = "user"
        form_classname = "contact-profile-block"
        # template was: blocks/contact_profile.html
        group = _("Contact")

    # === URL Generation Templates ===
    URL_TEMPLATES = {
        "social": {
            "linkedin": "https://linkedin.com/in/{username}",
            "twitter": "https://twitter.com/{username}",
            "facebook": "https://facebook.com/{username}",
            "instagram": "https://instagram.com/{username}",
            "github": "https://github.com/{username}",
            "youtube": "https://youtube.com/@{username}",
            "whatsapp": "https://wa.me/{username}",
            "telegram": "https://t.me/{username}",
            "discord": "https://discord.gg/{username}",
            "tiktok": "https://tiktok.com/@{username}",
            "pinterest": "https://pinterest.com/{username}",
            "reddit": "https://reddit.com/user/{username}",
            "medium": "https://medium.com/@{username}",
            "behance": "https://behance.net/{username}",
            "dribbble": "https://dribbble.com/{username}",
            "stackoverflow": "https://stackoverflow.com/users/{username}",
            "gitlab": "https://gitlab.com/{username}",
            "bitbucket": "https://bitbucket.org/{username}",
            "mastodon": "https://{instance}/@{username}",
            "threads": "https://threads.net/@{username}",
            "snapchat": "https://snapchat.com/add/{username}",
            "twitch": "https://twitch.tv/{username}",
            "spotify": "https://open.spotify.com/user/{username}",
            "soundcloud": "https://soundcloud.com/{username}",
        },
        "contact": {
            "email": "mailto:{value}",
            "phone": "tel:{value}",
            "whatsapp": "https://wa.me/{value}",
            "signal": "https://signal.me/#p/{value}",
            "telegram": "https://t.me/{value}",
            "skype": "skype:{value}?call",
            "zoom": "https://zoom.us/j/{value}",
            "meet": "https://meet.google.com/{value}",
            "teams": "https://teams.microsoft.com/l/meetup-join/{value}",
        },
        "professional": {
            "upwork": "https://upwork.com/freelancers/{username}",
            "fiverr": "https://fiverr.com/{username}",
            "toptal": "https://toptal.com/{username}",
            "angel": "https://angel.co/u/{username}",
            "crunchbase": "https://crunchbase.com/person/{username}",
            "producthunt": "https://producthunt.com/@{username}",
            "indiehackers": "https://indiehackers.com/{username}",
            "clutch": "https://clutch.co/profile/{username}",
            "glassdoor": "https://glassdoor.com/Overview/{username}",
        },
    }

    # === Icon Mappings ===
    ICON_CLASSES = {
        "social": {
            "linkedin": "bi bi-linkedin",
            "twitter": "bi bi-twitter-x",
            "facebook": "bi bi-facebook",
            "instagram": "bi bi-instagram",
            "github": "bi bi-github",
            "youtube": "bi bi-youtube",
            "whatsapp": "bi bi-whatsapp",
            "telegram": "bi bi-telegram",
            "discord": "bi bi-discord",
            "tiktok": "bi bi-tiktok",
            "pinterest": "bi bi-pinterest",
            "reddit": "bi bi-reddit",
            "medium": "bi bi-medium",
            "behance": "bi bi-behance",
            "dribbble": "bi bi-dribbble",
            "stackoverflow": "bi bi-stack-overflow",
            "gitlab": "bi bi-gitlab",
            "bitbucket": "bi bi-bitbucket",
            "mastodon": "bi bi-mastodon",
            "threads": "bi bi-threads",
            "snapchat": "bi bi-snapchat",
            "twitch": "bi bi-twitch",
            "spotify": "bi bi-spotify",
            "soundcloud": "bi bi-soundcloud",
        },
        "website": {
            "personal": "bi bi-person-badge",
            "portfolio": "bi bi-briefcase",
            "blog": "bi bi-pencil-square",
            "company": "bi bi-building",
            "project": "bi bi-code-square",
            "ecommerce": "bi bi-cart",
            "educational": "bi bi-mortarboard",
            "documentation": "bi bi-file-text",
            "forum": "bi bi-people",
            "wiki": "bi bi-journal-text",
            "dashboard": "bi bi-speedometer2",
            "landing": "bi bi-window",
            "saas": "bi bi-cloud",
            "api": "bi bi-plug",
        },
        "professional": {
            "upwork": "bi bi-briefcase",
            "fiverr": "bi bi-currency-dollar",
            "toptal": "bi bi-star",
            "angel": "bi bi-gem",
            "crunchbase": "bi bi-graph-up",
            "producthunt": "bi bi-rocket",
            "indiehackers": "bi bi-lightning",
            "clutch": "bi bi-award",
            "glassdoor": "bi bi-building",
            "resume": "bi bi-file-earmark-person",
            "calendly": "bi bi-calendar-check",
        },
        "contact": {
            "email": "bi bi-envelope",
            "phone": "bi bi-telephone",
            "whatsapp": "bi bi-whatsapp",
            "signal": "bi bi-shield-check",
            "telegram": "bi bi-telegram",
            "skype": "bi bi-skype",
            "zoom": "bi bi-camera-video",
            "meet": "bi bi-google",
            "teams": "bi bi-microsoft",
            "address": "bi bi-geo-alt",
        },
    }

    # === Brand Colors ===
    BRAND_COLORS = {
        "linkedin": "#0077B5",
        "twitter": "#1DA1F2",
        "facebook": "#1877F2",
        "instagram": "#E4405F",
        "github": "#181717",
        "youtube": "#FF0000",
        "whatsapp": "#25D366",
        "telegram": "#26A5E4",
        "discord": "#5865F2",
        "tiktok": "#000000",
        "pinterest": "#E60023",
        "reddit": "#FF4500",
        "medium": "#000000",
        "behance": "#0057FF",
        "dribbble": "#EA4C89",
        "stackoverflow": "#F48024",
        "gitlab": "#FC6D26",
        "bitbucket": "#0052CC",
        "mastodon": "#6364FF",
        "threads": "#000000",
        "snapchat": "#FFFC00",
        "twitch": "#9146FF",
        "spotify": "#1DB954",
        "soundcloud": "#FF3300",
    }

    def clean(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and auto-generate data based on profile type.
        """
        cleaned_data = super().clean(value)
        profile_type = cleaned_data.get("profile_type", "social")

        # Get appropriate subtype based on profile_type
        subtype = self._get_subtype(cleaned_data, profile_type)
        username = cleaned_data.get("username", "")
        value_data = cleaned_data.get("value", "")

        # Auto-generate URL if not provided
        if not cleaned_data.get("url"):
            generated_url = self._generate_url(profile_type, subtype, username, value_data)
            if generated_url:
                cleaned_data["url"] = generated_url

        # Auto-set icon class if not provided
        if not cleaned_data.get("icon_class"):
            cleaned_data["icon_class"] = self._get_icon_class(profile_type, subtype)

        # Auto-set brand color if not provided
        if not cleaned_data.get("color") and profile_type == "social":
            cleaned_data["color"] = self.BRAND_COLORS.get(subtype, "#6c757d")

        # Set display type
        cleaned_data["display_type"] = self._get_display_type(profile_type, subtype, cleaned_data)

        # Generate display title if not set
        if not cleaned_data.get("title"):
            cleaned_data["title"] = self._generate_title(
                profile_type, subtype, username, value_data
            )

        # Generate a unique ID for tracking
        cleaned_data["profile_id"] = str(uuid.uuid4())[:8]

        # # Add metadata
        # cleaned_data["metadata"] = cleaned_data.get("metadata", {})
        # cleaned_data["metadata"].update(
        #     {
        #         "profile_type": profile_type,
        #         "subtype": subtype,
        #         "generated_at": "auto",
        #         "has_thumbnail": bool(cleaned_data.get("thumbnail")),
        #     }
        # )

        logger.debug(
            f"Cleaned contact profile: {cleaned_data.get('profile_id')} - {cleaned_data.get('title')}"
        )

        return cleaned_data

    def _get_subtype(self, data: Dict[str, Any], profile_type: str) -> str:
        """Get the subtype based on profile type."""
        subtype_map = {
            "social": data.get("social_platform", "linkedin"),
            "website": data.get("website_type", "personal"),
            "professional": data.get("professional_type", "resume"),
            "contact": data.get("contact_type", "email"),
        }

        subtype = subtype_map.get(profile_type, "other")

        # Handle custom types
        if subtype == "other" and data.get("custom_type"):
            return data["custom_type"]

        return subtype

    def _generate_url(
        self, profile_type: str, subtype: str, username: str, value: str
    ) -> Optional[str]:
        """Generate URL based on profile type and subtype."""
        templates = self.URL_TEMPLATES.get(profile_type, {})
        template = templates.get(subtype, "")

        if not template:
            return None

        # Use value for contact methods, username for others
        if profile_type == "contact" and value:
            return template.format(value=value.strip().lstrip("+").replace(" ", ""))
        elif username:
            # Handle Mastodon special case
            if subtype == "mastodon" and "@" in username:
                instance, username_only = username.split("@", 1)
                return template.format(instance=instance, username=username_only)
            return template.format(username=username.strip())

        return None

    def _get_icon_class(self, profile_type: str, subtype: str) -> str:
        """Get icon class based on profile type and subtype."""
        icon_map = self.ICON_CLASSES.get(profile_type, {})
        return icon_map.get(subtype, "bi bi-link")

    def _get_display_type(self, profile_type: str, subtype: str, data: Dict[str, Any]) -> str:
        """Get human-readable display type."""
        if profile_type == "social":
            for key, label in self.SOCIAL_PLATFORM_CHOICES:
                if key == subtype:
                    return str(label)
        elif profile_type == "website":
            for key, label in self.WEBSITE_TYPE_CHOICES:
                if key == subtype:
                    return str(label)
        elif profile_type == "professional":
            for key, label in self.PROFESSIONAL_TYPE_CHOICES:
                if key == subtype:
                    return str(label)
        elif profile_type == "contact":
            for key, label in self.CONTACT_TYPE_CHOICES:
                if key == subtype:
                    return str(label)

        return data.get("custom_type", str(_("Other")))

    def _generate_title(self, profile_type: str, subtype: str, username: str, value: str) -> str:
        """Generate a display title."""
        if profile_type == "contact":
            if subtype == "email" and value:
                return value
            elif subtype == "phone" and value:
                return value
            elif value:
                return value

        if username:
            if "@" in username and profile_type == "social":
                return username.split("@")[0]
            return username

        display_type = self._get_display_type(profile_type, subtype, {})
        return str(_(display_type))

    def get_context(
        self, value: Dict[str, Any], parent_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Get template context."""
        context = super().get_context(value, parent_context)

        # Add computed values
        value["is_social"] = value.get("profile_type") == "social"
        value["is_website"] = value.get("profile_type") == "website"
        value["is_professional"] = value.get("profile_type") == "professional"
        value["is_contact"] = value.get("profile_type") == "contact"

        # Determine if it's clickable
        value["is_clickable"] = bool(value.get("url")) or (
            value.get("profile_type") == "contact" and value.get("value")
        )

        # Generate hover text
        value["hover_text"] = self._get_hover_text(value)

        # Determine link target
        value["link_target"] = "_blank" if value.get("open_in_new_tab", True) else "_self"

        # Add CSS classes for styling
        css_classes = ["contact-profile"]
        css_classes.append(f"profile-type-{value.get('profile_type', 'other')}")
        css_classes.append(
            f"subtype-{self._get_subtype(value, value.get('profile_type', 'social'))}"
        )

        if value.get("is_primary"):
            css_classes.append("is-primary")
        if value.get("verified"):
            css_classes.append("is-verified")

        value["css_classes"] = " ".join(css_classes)

        return context

    def _get_hover_text(self, value: Dict[str, Any]) -> str:
        """Generate hover text for the profile."""
        parts = []

        title = value.get("title", "")
        if title:
            parts.append(title)

        description = value.get("description", "")
        if description:
            # Truncate long descriptions
            if len(description) > 100:
                parts.append(description[:97] + "...")
            else:
                parts.append(description)

        if value.get("verified"):
            parts.append(str(_("✓ Verified")))

        return " | ".join(parts)

    def get_searchable_content(self, value: Dict[str, Any]) -> list:
        """Get content for search indexing."""
        content = []

        if value.get("title"):
            content.append(value["title"])

        if value.get("username"):
            content.append(value["username"])

        if value.get("description"):
            content.append(value["description"])

        if value.get("url"):
            content.append(value["url"])

        return content

    def render(self, value: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Custom render method."""
        from django.template.loader import render_to_string

        if context is None:
            context = {}

        context["value"] = value
        context["block"] = self

        return render_to_string(self.meta.template, context)


# =============================================================================
# HELPER BLOCKS
# =============================================================================


class ContactProfileStreamBlock(blocks.StreamBlock):
    """
    Container stream block for multiple contact profiles.
    """

    profile = ContactProfileBlock(template="blocks/contact/contact_profile.html")

    class Meta:
        label = _("Contact Profiles")
        icon = "group"
        max_num = 50

    def get_profile_by_type(self, value, profile_type=None, subtype=None, is_primary=False):
        """Helper to filter profiles by type and subtype."""
        profiles = []

        for child in value:
            if child.block_type == "profile":
                profile_data = child.value

                if profile_type and profile_data.get("profile_type") != profile_type:
                    continue

                if subtype:
                    actual_subtype = child.block._get_subtype(
                        profile_data, profile_data.get("profile_type", "social")
                    )
                    if actual_subtype != subtype:
                        continue

                if is_primary and not profile_data.get("is_primary"):
                    continue

                profiles.append(profile_data)

        # Sort by priority (higher first), then alphabetically
        return sorted(profiles, key=lambda x: (-x.get("priority", 0), x.get("title", "").lower()))

    def get_social_profiles(self, value):
        """Get all social media profiles."""
        return self.get_profile_by_type(value, profile_type="social")

    def get_websites(self, value):
        """Get all website links."""
        return self.get_profile_by_type(value, profile_type="website")

    def get_contact_methods(self, value):
        """Get all contact methods."""
        return self.get_profile_by_type(value, profile_type="contact")

    def get_primary_profiles(self, value):
        """Get all primary profiles."""
        return self.get_profile_by_type(value, is_primary=True)


# =============================================================================
# SETTINGS INTEGRATION BLOCK
# =============================================================================


class SiteContactSettingsBlock(blocks.StructBlock):
    """
    Block specifically designed for site-wide contact settings.
    """

    title = blocks.CharBlock(
        max_length=100,
        default=_("Contact Information"),
        label=_("Section Title"),
    )

    description = blocks.TextBlock(
        required=False,
        label=_("Description"),
        help_text=_("Introduction text for contact section"),
    )

    contact_profiles = ContactProfileStreamBlock(required=False,
        label=_("Contact Profiles & Methods"), template="blocks/contact/site_contact_settings.html",
        help_text=_("Add all contact methods, social profiles, and websites"),
    )

    display_mode = blocks.ChoiceBlock(
        choices=[
            ("list", _("Simple List")),
            ("cards", _("Profile Cards")),
            ("compact", _("Compact Icons")),
            ("detailed", _("Detailed View")),
        ],
        default="list",
        label=_("Display Mode"),
    )

    show_section_title = blocks.BooleanBlock(
        default=True,
        label=_("Show Section Title"),
    )

    columns = blocks.ChoiceBlock(
        choices=[
            ("1", _("1 Column")),
            ("2", _("2 Columns")),
            ("3", _("3 Columns")),
            ("4", _("4 Columns")),
            ("auto", _("Auto Fit")),
        ],
        default="3",
        label=_("Layout Columns"),
    )

    class Meta:
        label = _("Contact Settings Block")
        icon = "cog"
        # template was: blocks/site_contact_settings.html
        group = _("Settings")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        # Organize profiles by type for easy templating
        if value.get("contact_profiles"):
            stream_block = ContactProfileStreamBlock(template="blocks/contact/site_contact_settings.html")
            profiles = value["contact_profiles"]

            context.update(
                {
                    "social_profiles": stream_block.get_social_profiles(profiles),
                    "websites": stream_block.get_websites(profiles),
                    "contact_methods": stream_block.get_contact_methods(profiles),
                    "primary_profiles": stream_block.get_primary_profiles(profiles),
                    "all_profiles": [child.value for child in profiles],
                }
            )

        return context

# =============================================================================
# FORM MEDIA (for admin interface)
# =============================================================================


class Media:
    css = {"all": ("css/contact-profile-admin.css",)}
    js = ("js/contact-profile-admin.js",)
