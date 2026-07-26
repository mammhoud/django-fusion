from django.utils.translation import gettext_lazy as _
from wagtail import blocks


class SimpleFormFieldBlock(blocks.StructBlock):
    """
    Simplified form field block with only essential configuration.
    Advanced features (validation, conditional logic, error messages)
    are configured at the page level in Settings panel.
    """

    # Essential Field Configuration
    field_type = blocks.ChoiceBlock(
        choices=[
            ("text", _("Text")),
            ("email", _("Email")),
            ("tel", _("Phone")),
            ("textarea", _("Text Area")),
            ("select", _("Dropdown")),
            ("checkbox", _("Checkbox")),
            ("number", _("Number")),
            ("date", _("Date")),
        ],
        label=_("Field Type"),
    )

    label = blocks.CharBlock(
        max_length=100,
        label=_("Field Label"),
        help_text=_("Display label for the field"),
    )

    name = blocks.CharBlock(
        max_length=50,
        label=_("Field Name"),
        help_text=_("HTML name attribute (lowercase, no spaces)"),
    )

    placeholder = blocks.CharBlock(
        max_length=100,
        required=False,
        label=_("Placeholder Text"),
    )

    help_text = blocks.CharBlock(
        max_length=200,
        required=False,
        label=_("Help Text"),
    )

    required = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Required Field"),
    )

    # For dropdown/select fields only
    choices = blocks.ListBlock(
        blocks.StructBlock([
            ("value", blocks.CharBlock(max_length=100, label=_("Value"))),
            ("label", blocks.CharBlock(max_length=100, label=_("Display Label"))),
        ]),
        required=False,
        label=_("Options"),
        help_text=_("For dropdown fields only"),
    )

    class Meta:
        app_label = "lms"
        icon = "th-list"
        label = _("Form Field")


class MinimalContactFormBlock(blocks.StructBlock):
    """
    Simplified contact form block.
    Only contains essential form structure (ID and fields).
    All styling, messages, validation, and configuration are in page Settings panel.
    """

    form_id = blocks.CharBlock(
        max_length=50,
        default="contact-form",
        label=_("Form ID"),
        help_text=_("Unique ID for this form (used for DOM identification)"),
    )

    fields = blocks.ListBlock(
        SimpleFormFieldBlock(),
        default=[
            {
                "field_type": "text",
                "label": _("Full Name"),
                "name": "name",
                "required": True,
                "placeholder": _("Enter your full name"),
            },
            {
                "field_type": "email",
                "label": _("Email Address"),
                "name": "email",
                "required": True,
                "placeholder": _("Enter your email address"),
            },
            {
                "field_type": "textarea",
                "label": _("Message"),
                "name": "message",
                "required": True,
                "placeholder": _("How can we help you?"),
            },
        ],
        label=_("Form Fields"),
        help_text=_("Add, remove, or reorder form fields"),
    )

    class Meta:
        app_label = "lms"
        icon = "paper-plane"
        label = _("Contact Form")
        template = "blocks/minimal_contact_form.html"
