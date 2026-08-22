"""
 team blocks with member profiles and team sections.
"""

from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock


class TeamMemberBlock(BaseBlock):
    """
     team member profile block with contact info and social links.
    """

    # Basic Information
    name = blocks.CharBlock(
        required=True,
        max_length=100,
        label=_("Full Name"),
        help_text=_("Team member's full name."),
    )

    position = blocks.CharBlock(
        required=True,
        max_length=100,
        label=_("Position/Title"),
        help_text=_("Job title or role in the team."),
    )

    department = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Department"),
        help_text=_("Department or team within the organization."),
    )

    # Profile
    photo = ImageChooserBlock(
        required=True,
        label=_("Profile Photo"),
        help_text=_("High-quality headshot of the team member."),
    )

    bio = blocks.RichTextBlock(
        required=False,
        label=_("Biography"),
        features=["bold", "italic", "link", "ul", "ol"],
        help_text=_("Professional background and expertise."),
    )

    expertise = blocks.ListBlock(
        blocks.CharBlock(label=_("Area of Expertise")),
        required=False,
        label=_("Areas of Expertise"),
        help_text=_("List key skills or areas of expertise."),
    )

    # Contact Information
    email = blocks.EmailBlock(
        required=False,
        label=_("Email Address"),
    )

    phone = blocks.CharBlock(
        required=False,
        max_length=20,
        label=_("Phone Number"),
    )

    location = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Location"),
        help_text=_("Office location or timezone."),
    )

    # Social Links
    social_links = blocks.ListBlock(
        blocks.StructBlock(
            [
                (
                    "platform",
                    blocks.ChoiceBlock(
                        required=True,
                        choices=[
                            ("linkedin", _("LinkedIn")),
                            ("twitter", _("Twitter/X")),
                            ("facebook", _("Facebook")),
                            ("instagram", _("Instagram")),
                            ("github", _("GitHub")),
                            ("dribbble", _("Dribbble")),
                            ("behance", _("Behance")),
                            ("website", _("Website")),
                            ("youtube", _("YouTube")),
                            ("tiktok", _("TikTok")),
                            ("slack", _("Slack")),
                            ("discord", _("Discord")),
                        ],
                        label=_("Platform"),
                    ),
                ),
                (
                    "url",
                    blocks.URLBlock(
                        required=True,
                        label=_("Profile URL"),
                    ),
                ),
                (
                    "icon_class",
                    blocks.CharBlock(
                        required=False,
                        max_length=50,
                        label=_("Custom Icon Class"),
                        help_text=_("Override default platform icon."),
                    ),
                ),
                (
                    "display_text",
                    blocks.CharBlock(
                        required=False,
                        max_length=50,
                        label=_("Display Text"),
                        help_text=_("Custom text for the link (defaults to platform name)."),
                    ),
                ),
            ],
            label=_("Social Link"),
            icon="site",
        ),
        required=False,
        label=_("Social Media Links"),
    )

    # Display Options
    featured = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Featured Member"),
        help_text=_("Highlight this team member as featured."),
    )

    show_contact_info = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Contact Info"),
        help_text=_("Display email and phone publicly."),
    )

    show_social_links = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Social Links"),
    )

    layout_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("card", _("Card Layout")),
            ("compact", _("Compact Layout")),
            ("detailed", _("Detailed Layout")),
            ("hover", _("Hover Effect")),
        ],
        default="card",
        label=_("Layout Style"),
    )

    # Metadata
    join_date = blocks.DateBlock(
        required=False,
        label=_("Join Date"),
        help_text=_("Date when member joined the team."),
    )

    languages = blocks.ListBlock(
        blocks.CharBlock(label=_("Language")),
        required=False,
        label=_("Languages Spoken"),
    )

    class Meta:
        icon = "user"
        label = _(" Team Member")
        # template was: blocks/enhanced_team_member.html
        group = _("Team")

    def get_social_icon_class(self, platform):
        """Get icon class for social platform."""
        icon_map = {
            "linkedin": "fab fa-linkedin",
            "twitter": "fab fa-twitter",
            "facebook": "fab fa-facebook",
            "instagram": "fab fa-instagram",
            "github": "fab fa-github",
            "dribbble": "fab fa-dribbble",
            "behance": "fab fa-behance",
            "website": "fas fa-globe",
            "youtube": "fab fa-youtube",
            "tiktok": "fab fa-tiktok",
            "slack": "fab fa-slack",
            "discord": "fab fa-discord",
        }
        return icon_map.get(platform, "fas fa-link")


class TeamSectionBlock(BaseBlock):
    """
     team section with multiple layout options and filtering.
    """

    # Header
    title = blocks.CharBlock(
        required=True,
        max_length=200,
        label=_("Section Title"),
        help_text=_("Main heading for the team section."),
    )

    subtitle = blocks.CharBlock(
        required=False,
        max_length=400,
        label=_("Subtitle"),
        help_text=_("Optional subtitle or tagline."),
    )

    description = blocks.RichTextBlock(
        required=False,
        label=_("Description"),
        features=["bold", "italic", "link"],
        help_text=_("Introduction to the team or department."),
    )

    # Layout
    layout_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("grid", _("Grid Layout")),
            ("carousel", _("Carousel")),
            ("list", _("List Layout")),
            ("masonry", _("Masonry Grid")),
            ("table", _("Table View")),
        ],
        default="grid",
        label=_("Layout Style"),
    )

    columns_desktop = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("1", "1 Column"),
            ("2", "2 Columns"),
            ("3", "3 Columns"),
            ("4", "4 Columns"),
            ("5", "5 Columns"),
            ("6", "6 Columns"),
        ],
        default="3",
        label=_("Desktop Columns"),
    )

    columns_tablet = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("1", "1 Column"),
            ("2", "2 Columns"),
            ("3", "3 Columns"),
        ],
        default="2",
        label=_("Tablet Columns"),
    )

    # Team Members
    team_members = blocks.ListBlock(
        TeamMemberBlock(template="blocks/pages/enhanced_team_member.html"),
        label=_("Team Members"),
        help_text=_("Add team members to display."),
    )

    # Filtering and Sorting
    enable_filtering = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Enable Filtering"),
        help_text=_("Allow users to filter team members by department."),
    )

    enable_search = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Enable Search"),
        help_text=_("Add search functionality to find team members."),
    )

    sort_by = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("name", _("Name (A-Z)")),
            ("position", _("Position")),
            ("department", _("Department")),
            ("featured", _("Featured First")),
            ("join_date", _("Join Date (Newest)")),
            ("custom", _("Custom Order")),
        ],
        default="name",
        label=_("Sort By"),
    )

    # Display Options
    show_departments = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Departments"),
    )

    show_positions = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Positions"),
    )

    show_expertise = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Areas of Expertise"),
    )

    show_bios = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("none", _("No Bios")),
            ("excerpt", _("Short Excerpt")),
            ("full", _("Full Bio on Click")),
            ("always", _("Always Show Full Bio")),
        ],
        default="excerpt",
        label=_("Show Biographies"),
    )

    # Call to Action
    show_cta = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Call to Action"),
    )

    cta_title = blocks.CharBlock(
        required=False,
        default=_("Join Our Team"),
        max_length=200,
        label=_("CTA Title"),
    )

    cta_description = blocks.RichTextBlock(
        required=False,
        label=_("CTA Description"),
    )

    cta_button_text = blocks.CharBlock(
        required=False,
        default=_("View Open Positions"),
        max_length=50,
        label=_("CTA Button Text"),
    )

    cta_button_url = blocks.URLBlock(
        required=False,
        label=_("CTA Button URL"),
    )

    class Meta:
        icon = "group"
        label = _(" Team Section")
        group = _("Team")

    def get_departments(self, value):
        """Extract unique departments from team members."""
        departments = set()
        for member in value.get("team_members", []):
            department = member.value.get("department")
            if department:
                departments.add(department)
        return sorted(list(departments))

    def get_featured_members(self, value):
        """Get featured team members."""
        return [
            member
            for member in value.get("team_members", [])
            if member.value.get("featured", False)
        ]

    def get_regular_members(self, value):
        """Get non-featured team members."""
        return [
            member
            for member in value.get("team_members", [])
            if not member.value.get("featured", False)
        ]
