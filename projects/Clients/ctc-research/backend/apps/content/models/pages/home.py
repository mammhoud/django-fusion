from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.domain.blocks.contact.contact_card import ContactCardBlock
from apps.domain.blocks.partials.button import PageLinkBlock
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.blocks import PageChooserBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from .base import BaseFormPage


class HomePage(BaseFormPage):
    """
    🏠 Enhanced HomePage with dynamic sections:
    - Hero sliders
    - About and Features
    - Integrated Contact Form (via BaseFormPage)
    """

    page_title = _("Home Page")

    template = "base_page.html"
    template_name = "home/main.html"
    fragment_name = "home.main"

    # === HEADER SECTION ===
    head = StreamField(
        [
            (
                "slider",
                blocks.StreamBlock(
                    [
                        (
                            "slide",
                            blocks.StructBlock(
                                [
                                    (
                                        "background_image",
                                        SimpleImageBlock(
                                            template="blocks/media/image_lite.html",
                                            label=_("Background Image"),
                                        ),
                                    ),                                        (
                                            "subtitle",
                                            blocks.CharBlock(
                                                required=True,
                                                max_length=100,
                                                label=_("Subtitle"),
                                            ),
                                        ),
                                        (
                                            "title",
                                            blocks.CharBlock(
                                                required=True,
                                                max_length=200,
                                                label=_("Title"),
                                            ),
                                        ),
                                        (
                                            "description",
                                            blocks.TextBlock(
                                                required=False,
                                                max_length=400,
                                                label=_("Description"),
                                                help_text=_("Optional slide description shown under the title"),
                                            ),
                                        ),
                                        (
                                            "text_alignment",
                                            blocks.ChoiceBlock(
                                                choices=[
                                                    ("left", _("Left")),
                                                    ("center", _("Center")),
                                                    ("right", _("Right")),
                                                ],
                                                default="left",
                                                required=False,
                                                label=_("Text Alignment"),
                                            ),
                                        ),
                                        (
                                            "button_text",
                                            blocks.CharBlock(
                                                required=False,
                                                max_length=50,
                                                label=_("Button Text"),
                                            ),
                                        ),
                                        (
                                            "button_link",
                                            blocks.URLBlock(required=False, label=_("Button Link")),
                                        ),
                                        (
                                            "video_url",
                                            blocks.URLBlock(required=False, label=_("Video URL")),
                                        ),
                                        (
                                            "alt_text",
                                            blocks.CharBlock(
                                                required=False,
                                                max_length=200,
                                                label=_("Alt Text"),
                                                help_text=_("Accessible description of the slide image"),
                                            ),
                                        ),
                                    ],
                                    icon="images",
                                    label=_("Slide"),
                                ),
                        ),
                    ],
                    icon="images",
                    label=_("Slider"),
                ),
            ),
            (
                "features",
                blocks.StreamBlock(
                    [
                        (
                            "feature",
                            blocks.StructBlock(
                                [
                                    (
                                        "icon_class",
                                        blocks.CharBlock(
                                            required=False,
                                            default="flaticon-happy",
                                            max_length=100,
                                            help_text=_("e.g., flaticon-happy"),
                                            label=_("Icon Class"),
                                        ),
                                    ),
                                    (
                                        "image",
                                        SimpleImageBlock(
                                            template="blocks/media/image_lite.html",
                                            label=_("Image"),
                                        ),
                                    ),
                                    (
                                        "title",
                                        blocks.CharBlock(
                                            required=True,
                                            max_length=100,
                                            label=_("Title"),
                                        ),
                                    ),
                                    (
                                        "description",
                                        blocks.TextBlock(required=True, label=_("Description")),
                                    ),
                                ],
                                icon="th-list",
                                label=_("Feature"),
                            ),
                        ),
                    ],
                    icon="th-list",
                    label=_("Features"),
                ),
            ),
        ],
        use_json_field=True,
        blank=False,
        verbose_name=_("Header Section"),
    )

    # === SUMMARY SECTION ===
    summary = StreamField(
        [
            (
                "about",
                blocks.StructBlock(
                    [
                        (
                            "background_image",
                            SimpleImageBlock(
                                template="blocks/media/image_lite.html",
                                label=_("Background Image"),
                            ),
                        ),
                        (
                            "years_experience",
                            blocks.IntegerBlock(default=20, label=_("Years of Experience")),
                        ),
                        (
                            "welcome_text",
                            blocks.CharBlock(max_length=100, label=_("Welcome Text")),
                        ),
                        (
                            "main_title",
                            blocks.CharBlock(max_length=200, label=_("Main Title")),
                        ),
                        (
                            "description",
                            blocks.RichTextBlock(label=_("Description")),
                        ),
                        (
                            "service_items",
                            blocks.StreamBlock(
                                [
                                    (
                                        "service_item",
                                        blocks.StructBlock(
                                            [
                                                (
                                                    "icon_class",
                                                    blocks.CharBlock(
                                                        required=True,
                                                        label=_("Icon Class"),
                                                    ),
                                                ),
                                                (
                                                    "title",
                                                    blocks.CharBlock(
                                                        required=True, label=_("Title")
                                                    ),
                                                ),
                                                (
                                                    "description",
                                                    blocks.TextBlock(
                                                        required=True,
                                                        label=_("Description"),
                                                    ),
                                                ),
                                            ],
                                            label=_("Service Item"),
                                        ),
                                    )
                                ],
                                label=_("Services Items"),
                            ),
                        ),
                    ],
                    icon="info-circle",
                    label=_("About Section"),
                ),
            ),
            (
                "listing_section",
                blocks.StructBlock(
                    [
                        (
                            "subtitle",
                            blocks.CharBlock(max_length=100, required=False, label=_("Subtitle")),
                        ),
                        (
                            "title",
                            blocks.CharBlock(max_length=200, required=True, label=_("Title")),
                        ),
                        (
                            "listing_pages",
                            blocks.StreamBlock(
                                [
                                    (
                                        "listing",
                                        blocks.StructBlock(
                                            [
                                                (
                                                    "index_page",
                                                    PageChooserBlock(
                                                        required=True,
                                                        label=_("Index Page"),
                                                    ),
                                                ),
                                                (
                                                    "icon_class",
                                                    blocks.CharBlock(
                                                        max_length=100,
                                                        required=False,
                                                        label=_("Icon Class"),
                                                    ),
                                                ),
                                                (
                                                    "description",
                                                    blocks.TextBlock(
                                                        required=False,
                                                        label=_("Description"),
                                                    ),
                                                ),
                                            ],
                                            icon="list-ul",
                                            label=_("Listing Item"),
                                        ),
                                    ),
                                ],
                                label=_("Listings"),
                                required=False,
                            ),
                        ),
                    ],
                    icon="list-ul",
                    label=_("Listing Section"),
                ),
            ),
        ],
        use_json_field=True,
        blank=False,
        verbose_name=_("Summary Section"),
    )

    # === CTA SECTION ===
    CTA = StreamField(
        [
            ("contact_section", ContactCardBlock(label=_("Contact Section"))),
            (
                "why_choose_section",
                blocks.StructBlock(
                    [
                        (
                            "subtitle",
                            blocks.CharBlock(required=False, max_length=150, label=_("Subtitle")),
                        ),
                        (
                            "title",
                            blocks.CharBlock(required=True, max_length=200, label=_("Title")),
                        ),
                        (
                            "description",
                            blocks.TextBlock(required=False, label=_("Description")),
                        ),
                        (
                            "highlight_text",
                            blocks.CharBlock(
                                required=False, max_length=100, label=_("Highlight Text")
                            ),
                        ),
                        (
                            "methods",
                            blocks.ListBlock(
                                blocks.CharBlock(max_length=100),
                                required=False,
                                label=_("Methods"),
                            ),
                        ),
                        (
                            "image",
                            SimpleImageBlock(
                                template="blocks/media/image_lite.html",
                                label=_("Image"),
                            ),
                        ),
                        (
                            "button",
                            PageLinkBlock(required=False, label=_("Button")),
                        ),
                    ],
                    icon="check-double",
                    label=_("Why Choose Us"),
                ),
            ),
            (
                "clients",
                blocks.StreamBlock(
                    [
                        (
                            "client",
                            blocks.StructBlock(
                                [
                                    (
                                        "organization",
                                        SnippetChooserBlock(
                                            "handlers.Organization",
                                            label=_("Organization"),
                                        ),
                                    ),
                                ],
                                icon="users",
                                label=_("Client"),
                            ),
                        ),
                    ],
                    icon="users",
                    label=_("Clients Section"),
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("CTA Section"),
    )

    # === HERO COPY (CMS-driven, localized per locale) ===
    hero_heading = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name=_("Hero Heading"),
    )
    hero_subheading = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Hero Subheading"),
    )
    hero_accent = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("Hero Accent"),
        help_text=_("Accented word(s) rendered in the brand color inside the hero heading"),
    )

    # === HOME SECTION CHROME (CMS-driven, localized per locale) ===
    # Section headings/intros the Astro shell previously baked into the
    # frontend locale dictionary: the home slider head, the course slider
    # head, the hero evidence panel (title/text/stats), the learning teaser,
    # and the methods/programs section heads. Editors control every one of
    # these per locale from Wagtail; the frontend only falls back to static
    # copy when a block is empty.

    class _SectionHeadBlock(blocks.StructBlock):
        """Small editor block: eyebrow (label), title, optional intro."""

        eyebrow = blocks.CharBlock(required=False, max_length=100, label=_("Eyebrow"), help_text=_("Small label above the title"))
        title = blocks.CharBlock(required=True, max_length=200, label=_("Title"))
        intro = blocks.TextBlock(required=False, max_length=400, label=_("Intro"), help_text=_("Optional supporting sentence"))

        class Meta:
            label = _("Section Head")

    class _StatBlock(blocks.StructBlock):
        """One evidence-panel metric: a number and its label."""

        value = blocks.CharBlock(required=True, max_length=20, label=_("Value"), help_text=_("e.g. 17+"))
        label = blocks.CharBlock(required=True, max_length=100, label=_("Label"))

        class Meta:
            label = _("Stat")

    home_chrome = StreamField(
        [
            ("slider_head", _SectionHeadBlock(icon="slides", label=_("Research slider heading"))),
            ("course_head", _SectionHeadBlock(icon="list-ul", label=_("Course slider heading"))),
            (
                "evidence_panel",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(required=False, max_length=200, label=_("Title"))),
                        ("text", blocks.TextBlock(required=False, max_length=400, label=_("Text"))),
                        (
                            "stats",
                            blocks.ListBlock(
                                _StatBlock(),
                                required=False,
                                default=[
                                    {"value": "17+", "label": "years of research"},
                                    {"value": "6", "label": "course programs"},
                                    {"value": "7", "label": "languages"},
                                ],
                                label=_("Stats"),
                            ),
                        ),
                    ],
                    icon="clipboard-list",
                    label=_("Hero evidence panel"),
                ),
            ),
            (
                "learning_teaser",
                blocks.StructBlock(
                    [
                        ("marker", blocks.CharBlock(required=False, max_length=60, label=_("Marker"))),
                        ("title", blocks.CharBlock(required=True, max_length=200, label=_("Title"))),
                        ("intro", blocks.TextBlock(required=False, max_length=400, label=_("Intro"))),
                        ("cta_label", blocks.CharBlock(required=False, max_length=60, label=_("CTA Label"))),
                        ("cta_url", blocks.URLBlock(required=False, label=_("CTA URL"))),
                    ],
                    icon="graduation-cap",
                    label=_("Learning teaser"),
                ),
            ),
            (
                "methods_head",
                blocks.StructBlock(
                    [
                        ("eyebrow", blocks.CharBlock(required=False, max_length=100, label=_("Eyebrow"))),
                        ("title", blocks.CharBlock(required=True, max_length=200, label=_("Title"))),
                    ],
                    icon="list-ul",
                    label=_("Methods section head"),
                ),
            ),
            (
                "programs_head",
                blocks.StructBlock(
                    [
                        ("eyebrow", blocks.CharBlock(required=False, max_length=100, label=_("Eyebrow"))),
                        ("title", blocks.CharBlock(required=True, max_length=200, label=_("Title"))),
                        ("side_note", blocks.CharBlock(required=False, max_length=120, label=_("Side Note"))),
                    ],
                    icon="cogs",
                    label=_("Programs heading"),
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("Home Section Headings (CMS)"),
    )

    # === PANELS ===
    content_panels = BaseFormPage.content_panels + [
        FieldPanel("head"),
        FieldPanel("summary"),
        FieldPanel("CTA"),
        MultiFieldPanel(
            [FieldPanel("hero_heading"), FieldPanel("hero_subheading"), FieldPanel("hero_accent")],
            heading=_("Hero"),
        ),
        FieldPanel("home_chrome"),
        MultiFieldPanel(
            [FieldPanel("contact_form")],
            heading=_("Contact Form"),
            classname="collapsible",
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(BaseFormPage.promote_panels, heading=_("Promote")),
            ObjectList(BaseFormPage.form_settings_panels, heading=_("Form Settings")),
            ObjectList(BaseFormPage.settings_panels, heading=_("Settings")),
        ]
    )

    class Meta:
        verbose_name = _("Home Page")
        verbose_name_plural = _("Home Pages")
        db_table = "content_homepage"
