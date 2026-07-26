from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock

from .base import BasePage


class FaqPage(BasePage):
    """
    ❓ FAQ Page — displays frequently asked questions organized by groups.

    Content sourced from STATIC_PAGES but stored as Wagtail StreamFields
    so editors can manage FAQ content directly in Wagtail admin.
    """

    template = "base_page.html"
    template_name = "faq/main.html"
    fragment_name = "faq.main"
    page_title = _("FAQ Page")

    # === HEADER SECTION (Hero) ===
    head = StreamField(
        [
            (
                "page_title",
                blocks.StructBlock(
                    [
                        (
                            "page_title_background",
                            SimpleImageBlock(
                                template="blocks/media/image_lite.html",
                                label=_("Page Title Background"),
                            ),
                        ),
                        (
                            "page_title",
                            blocks.CharBlock(
                                required=True, max_length=200, label=_("Page Title")
                            ),
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

    # === FAQ GROUPS SECTION ===
    faq_groups = StreamField(
        [
            (
                "faq_group",
                blocks.StructBlock(
                    [
                        (
                            "title",
                            blocks.CharBlock(
                                required=True, max_length=200, label=_("Group Title")
                            ),
                        ),
                        (
                            "items",
                            blocks.ListBlock(
                                blocks.StructBlock(
                                    [
                                        (
                                            "question",
                                            blocks.CharBlock(
                                                required=True,
                                                max_length=500,
                                                label=_("Question"),
                                            ),
                                        ),
                                        (
                                            "answer",
                                            blocks.TextBlock(
                                                required=True,
                                                label=_("Answer"),
                                            ),
                                        ),
                                    ],
                                    icon="question-circle",
                                    label=_("FAQ Item"),
                                ),
                                label=_("FAQ Items"),
                            ),
                        ),
                    ],
                    icon="list-ul",
                    label=_("FAQ Group"),
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("FAQ Groups"),
    )

    # === CTA SECTION ===
    cta = StreamField(
        [
            (
                "cta_section",
                blocks.StructBlock(
                    [
                        (
                            "heading",
                            blocks.CharBlock(
                                required=True, max_length=200, label=_("Heading")
                            ),
                        ),
                        (
                            "intro",
                            blocks.TextBlock(
                                required=False, label=_("Intro Text")
                            ),
                        ),
                        (
                            "cta_buttons",
                            blocks.ListBlock(
                                blocks.StructBlock(
                                    [
                                        (
                                            "label",
                                            blocks.CharBlock(
                                                required=True,
                                                max_length=100,
                                                label=_("Button Label"),
                                            ),
                                        ),
                                        (
                                            "href",
                                            blocks.URLBlock(
                                                required=False, label=_("Button Link")
                                            ),
                                        ),
                                    ],
                                    icon="link",
                                    label=_("CTA Button"),
                                ),
                                required=False,
                                label=_("CTA Buttons"),
                            ),
                        ),
                    ],
                    icon="bullhorn",
                    label=_("CTA Section"),
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("Call To Action"),
    )

    # === PANELS ===
    content_panels = BasePage.content_panels + [
        FieldPanel("head"),
        FieldPanel("faq_groups"),
        FieldPanel("cta"),
    ]

    class Meta:
        verbose_name = _("FAQ Page")
        verbose_name_plural = _("FAQ Pages")
        db_table = "content_faqpage"
