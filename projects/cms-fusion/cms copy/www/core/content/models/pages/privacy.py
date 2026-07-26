from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

from .base import BasePage


class PrivacyPage(BasePage):
    """
    🔒 Privacy Policy Page — displays privacy policy content as rich sections.

    Content sourced from STATIC_PAGES but stored as Wagtail StreamFields
    so editors can manage privacy content directly in Wagtail admin.
    """

    template = "base_page.html"
    template_name = "privacy/main.html"
    fragment_name = "privacy.main"
    page_title = _("Privacy Policy Page")

    # === BODY (Rich Sections) ===
    body = StreamField(
        [
            (
                "rich_section",
                blocks.StructBlock(
                    [
                        (
                            "heading",
                            blocks.CharBlock(
                                required=True, max_length=200, label=_("Section Heading")
                            ),
                        ),
                        (
                            "html",
                            blocks.TextBlock(
                                required=True,
                                label=_("Content (HTML)"),
                                help_text=_("HTML content for this section"),
                            ),
                        ),
                    ],
                    icon="doc-full",
                    label=_("Rich Section"),
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("Page Content"),
    )

    # === PANELS ===
    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = _("Privacy Page")
        verbose_name_plural = _("Privacy Pages")
        db_table = "content_privacypage"
