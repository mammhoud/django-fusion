from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock

from apps.core.domain.blocks.media.gallery import MediaGalleryBlock

from .base import BasePage


class AboutPage(BasePage):
    template = "base_page.html"
    # Use a concrete inner template for this page instead of a dynamic fragment
    # to avoid recursive `{% comp %}` resolution when components are not
    # located under the component directories. This will make `base_page.html`
    # include `template_name` directly.
    template_name = "about/main.html"
    fragment_name = "about.main"
    page_title = _("About Page")
    # ✅ Wrap your title section fields in a StructBlock inside a StreamField
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

    facts = StreamField(
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
                            "welcome_text",
                            blocks.CharBlock(max_length=100, label=_("Welcome Text")),
                        ),
                        (
                            "main_title",
                            blocks.CharBlock(max_length=200, label=_("Main Title")),
                        ),
                        ("description", blocks.TextBlock(label=_("Description"))),
                        (
                            "years_experience",
                            blocks.IntegerBlock(default=20, label=_("Years of Experience")),
                        ),
                        (
                            "experience_description",
                            blocks.RichTextBlock(label=_("Experience Description")),
                        ),
                        (
                            "video_link",
                            blocks.URLBlock(
                                required=False,
                                help_text=_("YouTube or Vimeo link"),
                                label=_("Video Link"),
                            ),
                        ),
                        (
                            "gallery",
                            MediaGalleryBlock(
                                required=False,
                                label=_("Team / Media Gallery"),
                                template="blocks/media/gallery.html",
                            ),
                        ),
                        (
                            "counters",
                            blocks.StreamBlock(
                                [
                                    (
                                        "counter",
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
                                                    "number",
                                                    blocks.IntegerBlock(
                                                        required=True,
                                                        label=_("Number"),
                                                    ),
                                                ),
                                                (
                                                    "label",
                                                    blocks.CharBlock(
                                                        max_length=100,
                                                        label=_("Label"),
                                                    ),
                                                ),
                                            ],
                                            label=_("Counter"),
                                        ),
                                    )
                                ],
                                label=_("Counters"),
                                required=False,
                            ),
                        ),
                    ],
                    icon="info-circle",
                    label=_("About Section with Counters"),
                ),
            ),
            (
                "testimonials",
                blocks.StructBlock(
                    [
                        (
                            "subtitle",
                            blocks.CharBlock(max_length=100, label=_("Subtitle")),
                        ),
                        (
                            "title",
                            blocks.CharBlock(max_length=200, label=_("Title")),
                        ),
                        (
                            "background_image",
                            SimpleImageBlock(
                                template="blocks/media/image_lite.html",
                                label=_("Background Image"),
                            ),
                        ),
                        (
                            "video_url",
                            blocks.URLBlock(required=False, label=_("Video URL")),
                        ),
                        (
                            "testimonials",
                            blocks.StreamBlock(
                                [
                                    (
                                        "testimonial",
                                        blocks.StructBlock(
                                            [
                                                (
                                                    "content",
                                                    blocks.RichTextBlock(
                                                        required=True,
                                                        features=[
                                                            "bold",
                                                            "italic",
                                                            "link",
                                                        ],
                                                        help_text=_(
                                                            "The testimonial text provided by the client."
                                                        ),
                                                        label=_("Content"),
                                                    ),
                                                ),
                                                (
                                                    "client_photo",
                                                    SimpleImageBlock(
                                                        template="blocks/media/image_lite.html",
                                                        label=_("Client Photo"),
                                                    ),
                                                ),
                                                (
                                                    "client_name",
                                                    blocks.CharBlock(
                                                        max_length=100,
                                                        help_text=_("Full name of the client."),
                                                        label=_("Client Name"),
                                                    ),
                                                ),
                                                (
                                                    "client_position",
                                                    blocks.CharBlock(
                                                        max_length=100,
                                                        help_text=_(
                                                            "Client’s job title or position."
                                                        ),
                                                        label=_("Client Position"),
                                                    ),
                                                ),
                                            ],
                                            label=_("Testimonial"),
                                        ),
                                    )
                                ],
                                label=_("Testimonials"),
                                required=True,
                            ),
                        ),
                    ],
                    icon="openquote",
                    label=_("Testimonials Section"),
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
        null=True,
        blank=True,
        verbose_name=_("Facts & Testimonials"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("head"),
        FieldPanel("facts"),
    ]

    class Meta:
        verbose_name = _("About Page")
        verbose_name_plural = _("About Pages")
        db_table = "content_aboutpage"
