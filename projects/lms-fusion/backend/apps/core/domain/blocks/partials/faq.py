from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.blocks import CharBlock, ChoiceBlock, ListBlock, RichTextBlock, StructBlock


class FAQItemBlock(StructBlock):
    """Single FAQ item block"""

    question = CharBlock(
        required=True, max_length=200, help_text=_("Enter the frequently asked question")
    )
    answer = RichTextBlock(
        required=True,
        features=["bold", "italic", "link", "ol", "ul"],
        help_text=_("Provide a detailed answer"),
    )

    class Meta:
        icon = "question-circle"
        label = _("FAQ Item")


class FAQSectionBlock(StructBlock):
    """FAQ section with category"""

    section_title = CharBlock(
        required=True,
        max_length=100,
        default=_("Frequently Asked Questions"),
        help_text=_("Title for the FAQ section"),
    )
    section_description = RichTextBlock(
        required=False,
        features=["bold", "italic"],
        help_text=_("Optional description for the FAQ section"),
    )
    category = ChoiceBlock(
        required=True,
        choices=[
            ("general", _("General Questions")),
            ("ai_training", _("AI Training & Tools")),
            ("medical_research", _("Medical Research Hub")),
            ("technical", _("Technical Support")),
            ("account", _("Account & Access")),
            ("data", _("Data & Privacy")),
        ],
        default="general",
        help_text=_("Select FAQ category"),
    )
    faq_items = ListBlock(FAQItemBlock(), help_text=_("Add FAQ items to this section"), min_num=1)
    show_contact_prompt = blocks.BooleanBlock(
        required=False, default=True, help_text=_("Show contact prompt after FAQ section")
    )

    class Meta:
        icon = "list-ul"
        label = _("FAQ Section")
