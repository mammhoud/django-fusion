from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.fields import StreamField

from django_osoul.comp.blocks import ContactMethodBlock
from django_osoul.comp.blocks.partials.faq import FAQSectionBlock
from .base import BaseFormPage

class ContactPage(BaseFormPage):
    """
    📞 Enhanced Contact Page
    Contains specialized contact fields (Info, Details, Map, FAQ)
    in addition to the core form inherited from BaseFormPage.
    """
    template = "base_page.html"
    fragment_name = "contact.main"
    page_title = _("Contact Page")

    # -------------------------------------------------------------------------
    # PAGE HEADER
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # CONTACT INFORMATION (Specific to Contact Page layout)
    # -------------------------------------------------------------------------
    contact_info = StreamField(
        [
            (
                "contact_info",
                blocks.StructBlock(
                    [
                        (
                            "subtitle",
                            blocks.CharBlock(
                                max_length=100,
                                default=_("Reach Out to Us"),
                                label=_("Subtitle"),
                            ),
                        ),
                        (
                            "title",
                            blocks.CharBlock(
                                max_length=200,
                                default=_(
                                    "Where Questions Find Answers, And Conversations Begin"
                                ),
                                label=_("Title"),
                            ),
                        ),
                        (
                            "description",
                            blocks.TextBlock(
                                default=_(
                                    "In every message sent,\n"
                                    "A bridge is built between us.\n"
                                    "Your words, our compass—\n"
                                    "Guiding us to serve you better.\n"
                                    "Together we craft solutions,\n"
                                    "Where vision meets dedication."
                                ),
                                label=_("Description"),
                            ),
                        ),
                    ],
                    icon="info-circle",
                    label=_("Contact Info Summary"),
                ),
            )
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("Contact Info Section"),
    )

    contact_details = StreamField(
        [
            (
                "address",
                blocks.StructBlock(
                    [
                        (
                            "icon_class",
                            blocks.CharBlock(
                                default="flaticon-house", max_length=50, label=_("Icon Class")
                            ),
                        ),
                        (
                            "title",
                            blocks.CharBlock(
                                default=_("Our Home"), max_length=100, label=_("Title")
                            ),
                        ),
                        (
                            "lines",
                            blocks.ListBlock(
                                blocks.CharBlock(max_length=200),
                                default=[
                                    _("Where innovation anchors deep Pip"),
                                    _("And dreams find their address."),
                                ],
                                label=_("Address Lines"),
                            ),
                        ),
                    ],
                    icon="map-marker-alt",
                    label=_("Address Detail"),
                ),
            ),
            (
                "phone",
                blocks.StructBlock(
                    [
                        (
                            "icon_class",
                            blocks.CharBlock(
                                default="flaticon-support-1", max_length=50, label=_("Icon Class")
                            ),
                        ),
                        (
                            "title",
                            blocks.CharBlock(
                                default=_("Voices Connect"), max_length=100, label=_("Title")
                            ),
                        ),
                        (
                            "lines",
                            blocks.ListBlock(
                                blocks.CharBlock(max_length=50),
                                default=[
                                    _("Every ring, a new possibility"),
                                    _("Every call, a step closer"),
                                ],
                                label=_("Phone Lines"),
                            ),
                        ),
                    ],
                    icon="phone-alt",
                    label=_("Phone Detail"),
                ),
            ),
            (
                "email",
                blocks.StructBlock(
                    [
                        (
                            "icon_class",
                            blocks.CharBlock(
                                default="flaticon-email", max_length=50, label=_("Icon Class")
                            ),
                        ),
                        (
                            "title",
                            blocks.CharBlock(
                                default=_("Digital Doorway"),
                                max_length=100,
                                label=_("Title"),
                            ),
                        ),
                        (
                            "lines",
                            blocks.ListBlock(
                                blocks.CharBlock(max_length=100),
                                default=[
                                    _("hello@example.com"),
                                    _("support@example.com"),
                                ],
                                label=_("Email Lines"),
                            ),
                        ),
                    ],
                    icon="envelope",
                    label=_("Email Detail"),
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("Contact Details"),
    )

    map = StreamField(
        [
            (
                "map",
                blocks.StructBlock(
                    [
                        (
                            "map_embed_url",
                            blocks.URLBlock(
                                default="https://maps.google.com/maps?hl=en&amp;q=Dhaka&amp;t=&amp;z=10&amp;iwloc=B&amp;output=embed",
                                help_text=_("Google Maps embed URL."),
                                label=_("Map Embed URL"),
                            ),
                        ),
                        (
                            "map_height",
                            blocks.CharBlock(
                                default="500px",
                                max_length=20,
                                help_text=_("Map height in pixels (e.g., 500px)."),
                                label=_("Map Height"),
                            ),
                        ),
                    ],
                    icon="map-marked-alt",
                    label=_("Map Section"),
                ),
            )
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("Map"),
    )


    faq = StreamField(
        [
            ("faq", FAQSectionBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("FAQ Section"),
    )

    # -------------------------------------------------------------------------
    # PANELS
    # -------------------------------------------------------------------------
    content_panels = BaseFormPage.content_panels + [
        FieldPanel("head"),
        MultiFieldPanel(
            [
                FieldPanel("contact_info"),
                FieldPanel("contact_form"),
            ],
            heading=_("Contact Form Section"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_details"),
                FieldPanel("map"),
            ],
            heading=_("Contact Details & Map"),
        ),
        FieldPanel("faq"),
    ]

    # Tabs for clean administration
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading=_("Content")),
        ObjectList(BaseFormPage.promote_panels, heading=_("Promote")),
        ObjectList(BaseFormPage.form_settings_panels, heading=_("Form Settings")),
        ObjectList(BaseFormPage.settings_panels, heading=_("Settings")),
    ])

    class Meta:
        verbose_name = _("Contact Page")
        verbose_name_plural = _("Contact Pages")
