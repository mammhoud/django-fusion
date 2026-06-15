from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock
from wagtail.models import Page

from .base import BasePage


class TeamPage(BasePage):
    template = "base_page.html"
    template_name = "team/main.html"
    fragment_name = "team.main"
    page_title = _("Team Page")

    # Page Title Section
    head = StreamField(
        [
            (
                "page_title",
                blocks.StructBlock(
                    [
                        (
                            "page_title_background",
                            SimpleImageBlock(
                                template="django_grep/comp/blocks/media/simple_image.html",
                                label=_("Page Title Background"),
                            ),
                        ),
                        (
                            "page_title",
                            blocks.CharBlock(required=True, max_length=200, label=_("Page Title")),
                        ),
                        (
                            "breadcrumb_home_text",
                            blocks.CharBlock(
                                default="Home", max_length=50, label=_("Breadcrumb Home Text")
                            ),
                        ),
                    ],
                    icon="address-card",
                    label=_("Page Title Section"),
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
        max_length=1,
        verbose_name=_("Header Section"),
    )

    # Team Section
    body = StreamField(
        [
            (
                "team_section",
                blocks.StructBlock(
                    [
                        (
                            "title",
                            blocks.CharBlock(
                                max_length=200,
                                required=False,
                                help_text=_("Section title"),
                                label=_("Title"),
                            ),
                        ),
                        (
                            "subtitle",
                            blocks.CharBlock(
                                max_length=300,
                                required=False,
                                help_text=_("Section subtitle"),
                                label=_("Subtitle"),
                            ),
                        ),
                        (
                            "team_members",
                            blocks.ListBlock(
                                blocks.StructBlock(
                                    [
                                        (
                                            "photo",
                                            SimpleImageBlock(
                                                template="django_grep/comp/blocks/media/simple_image.html",
                                                label=_("Photo"),
                                            ),
                                        ),
                                        (
                                            "name",
                                            blocks.CharBlock(
                                                max_length=100,
                                                required=True,
                                                help_text=_("Full name"),
                                                label=_("Name"),
                                            ),
                                        ),
                                        (
                                            "position",
                                            blocks.CharBlock(
                                                max_length=100,
                                                required=True,
                                                help_text=_("Job position/role"),
                                                label=_("Position"),
                                            ),
                                        ),
                                        (
                                            "facebook",
                                            blocks.URLBlock(
                                                required=False,
                                                help_text=_("Facebook profile URL"),
                                                label=_("Facebook URL"),
                                            ),
                                        ),
                                        (
                                            "twitter",
                                            blocks.URLBlock(
                                                required=False,
                                                help_text=_("Twitter/X profile URL"),
                                                label=_("Twitter URL"),
                                            ),
                                        ),
                                        (
                                            "linkedin",
                                            blocks.URLBlock(
                                                required=False,
                                                help_text=_("LinkedIn profile URL"),
                                                label=_("LinkedIn URL"),
                                            ),
                                        ),
                                        (
                                            "email",
                                            blocks.EmailBlock(
                                                required=False,
                                                help_text=_("Email address"),
                                                label=_("Email"),
                                            ),
                                        ),
                                        (
                                            "phone",
                                            blocks.CharBlock(
                                                max_length=20,
                                                required=False,
                                                help_text=_("Phone number"),
                                                label=_("Phone"),
                                            ),
                                        ),
                                        (
                                            "bio",
                                            blocks.TextBlock(
                                                required=False,
                                                max_length=500,
                                                help_text=_("Short biography"),
                                                label=_("Bio"),
                                            ),
                                        ),
                                        (
                                            "skills",
                                            blocks.ListBlock(
                                                blocks.StructBlock(
                                                    [
                                                        (
                                                            "name",
                                                            blocks.CharBlock(
                                                                required=True,
                                                                label=_("Skill Name"),
                                                            ),
                                                        ),
                                                        (
                                                            "percentage",
                                                            blocks.IntegerBlock(
                                                                required=True,
                                                                min_value=0,
                                                                max_value=100,
                                                                label=_("Percentage"),
                                                            ),
                                                        ),
                                                    ],
                                                    label=_("Skill"),
                                                ),
                                                required=False,
                                                label=_("Skills"),
                                                help_text=_("Add skills for this team member"),
                                            ),
                                        ),
                                        (
                                            "order",
                                            blocks.IntegerBlock(
                                                required=False,
                                                default=1,
                                                help_text=_("Display order (lower numbers first)"),
                                                label=_("Order"),
                                            ),
                                        ),
                                    ],
                                    label=_("Team Member"),
                                    icon="user-tie",
                                ),
                                required=False,
                                help_text=_("Add team members"),
                                label=_("Team Members"),
                            ),
                        ),
                    ],
                    icon="users",
                    label=_("Team Section"),
                    template="blocks/team_section.html",
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("Page Content"),
        help_text=_("Add team sections to the page"),
    )

    # === Panels ===
    content_panels = BasePage.content_panels + [
        FieldPanel("head"),
        MultiFieldPanel(
            [
                FieldPanel("body"),
            ],
            heading=_("Team Content"),
        ),
    ]

    class Meta:
        verbose_name = _("Team Page")
        verbose_name_plural = _("Team Pages")

    def get_listed_data(self, request=None):
        data = super().get_listed_data(request)
        team_count = 0
        for block in self.body:
            if block.block_type == "team_section":
                team_count += len(block.value.get("team_members", []))

        data.update(
            {
                "team_members_count": team_count,
            }
        )
        return data

    def get_sorted_team_members(self, block_value):
        if not block_value.get("team_members"):
            return []

        members = list(block_value["team_members"])
        return sorted(members, key=lambda x: x.get("order", 0))
