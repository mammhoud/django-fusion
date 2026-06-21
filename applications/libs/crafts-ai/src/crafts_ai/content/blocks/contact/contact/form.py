from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock


class FormFieldBlock(blocks.StructBlock):
    """
    Individual form field configuration with enhanced styling options.
    """

    field_type = blocks.ChoiceBlock(
        choices=[
            ("text", _("Text")),
            ("email", _("Email")),
            ("tel", _("Phone")),
            ("textarea", _("Text Area")),
            ("select", _("Dropdown")),
            ("checkbox", _("Checkbox")),
            ("radio", _("Radio Buttons")),
            ("date", _("Date")),
            ("time", _("Time")),
            ("datetime", _("Date & Time")),
            ("number", _("Number")),
            ("url", _("URL")),
            ("file", _("File Upload")),
            ("hidden", _("Hidden Field")),
        ],
        default="text",
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
        help_text=_("HTML name attribute (no spaces, lowercase)"),
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
        default=False,
        label=_("Required"),
    )
    default_value = blocks.CharBlock(
        max_length=200,
        required=False,
        label=_("Default Value"),
    )

    # Field width for layout control
    field_width = blocks.ChoiceBlock(
        choices=[
            ("full", _("Full Width")),
            ("half", _("Half Width")),
            ("third", _("One Third")),
            ("two-thirds", _("Two Thirds")),
        ],
        default="full",
        required=False,
        label=_("Field Width"),
        help_text=_("Control field width in multi-column layouts"),
    )

    # Icon configuration
    icon = blocks.CharBlock(
        max_length=50,
        required=False,
        label=_("Field Icon"),
        help_text=_("FontAwesome icon class (e.g., 'user', 'envelope')"),
    )

    # Options for select/radio fields
    choices = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("value", blocks.CharBlock(max_length=100, label=_("Value"))),
                ("label", blocks.CharBlock(max_length=100, label=_("Display Label"))),
            ]
        ),
        required=False,
        label=_("Options"),
        help_text=_("For dropdown or radio buttons"),
    )

    # Validation
    min_length = blocks.IntegerBlock(
        required=False,
        min_value=0,
        label=_("Minimum Length"),
    )
    max_length = blocks.IntegerBlock(
        required=False,
        min_value=1,
        label=_("Maximum Length"),
    )
    min_value = blocks.IntegerBlock(
        required=False,
        label=_("Minimum Value"),
        help_text=_("For number fields"),
    )
    max_value = blocks.IntegerBlock(
        required=False,
        label=_("Maximum Value"),
        help_text=_("For number fields"),
    )
    pattern = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Validation Pattern"),
        help_text=_("Regular expression pattern"),
    )
    error_message = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Custom Error Message"),
    )

    # Conditional display
    conditional_field = blocks.CharBlock(
        required=False,
        max_length=50,
        label=_("Conditional Field"),
        help_text=_("Show this field only when another field has a specific value"),
    )
    conditional_value = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Conditional Value"),
        help_text=_("Value that triggers this field to show"),
    )

    class Meta:
        icon = "form"
        label = _("Form Field")

    def clean(self, value):
        cleaned = super().clean(value)
        # Ensure name is valid for HTML
        if cleaned.get("name"):
            cleaned["name"] = cleaned["name"].lower().replace(" ", "_")
        return cleaned


class ContactFormBlock(blocks.StructBlock):
    """
    Enhanced reusable contact form block with dynamic fields.
    """

    # Basic settings
    form_id = blocks.CharBlock(
        max_length=50,
        default="contact-form",
        label=_("Form ID"),
        help_text=_("Unique ID for this form"),
    )

    # Form fields configuration
    fields = blocks.ListBlock(
        FormFieldBlock(),
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
    )

    # Layout options
    layout = blocks.ChoiceBlock(
        choices=[
            ("single", _("Single Column")),
            ("two-column", _("Two Columns")),
            ("split", _("Split Layout")),
        ],
        default="single",
        label=_("Form Layout"),
    )
    show_labels = blocks.BooleanBlock(
        default=True,
        label=_("Show Labels"),
    )
    show_placeholders = blocks.BooleanBlock(
        default=True,
        label=_("Show Placeholders"),
    )

    # Icons
    show_icons = blocks.BooleanBlock(
        default=True,
        label=_("Show Field Icons"),
    )
    icon_style = blocks.ChoiceBlock(
        choices=[
            ("inside", _("Inside Field")),
            ("outside", _("Outside Field")),
        ],
        default="inside",
        label=_("Icon Position"),
    )

    # Privacy/Compliance
    show_privacy_notice = blocks.BooleanBlock(
        default=True,
        label=_("Show Privacy Notice"),
    )
    privacy_notice_text = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic", "link"],
        default=_("I agree to the privacy policy and terms of service."),
        label=_("Privacy Notice Text"),
    )
    require_consent = blocks.BooleanBlock(
        default=True,
        label=_("Require Consent"),
    )

    # Button settings
    button_text = blocks.CharBlock(
        max_length=50,
        default=_("Send Message"),
        label=_("Submit Button Text"),
    )
    button_position = blocks.ChoiceBlock(
        choices=[
            ("left", _("Left")),
            ("center", _("Center")),
            ("right", _("Right")),
        ],
        default="left",
        label=_("Button Position"),
    )

    # Success/Error handling
    success_message = blocks.RichTextBlock(
        default=_("Thank you for your message! We'll get back to you within 24 hours."),
        label=_("Success Message"),
        features=["bold", "italic", "link"],
    )
    error_message = blocks.RichTextBlock(
        default=_(
            "There was an error submitting your message. Please try again or contact us directly."
        ),
        label=_("Error Message"),
        features=["bold", "italic", "link"],
    )

    # Advanced features
    enable_ajax = blocks.BooleanBlock(
        default=True,
        label=_("Enable AJAX Submission"),
    )
    enable_recaptcha = blocks.BooleanBlock(
        default=False,
        label=_("Enable reCAPTCHA"),
    )

    # HTMX settings
    htmx_swap = blocks.ChoiceBlock(
        choices=[
            ("innerHTML", _("Replace Inner HTML")),
            ("outerHTML", _("Replace Outer HTML")),
            ("beforebegin", _("Insert Before Begin")),
            ("afterbegin", _("Insert After Begin")),
            ("beforeend", _("Insert Before End")),
            ("afterend", _("Insert After End")),
        ],
        default="innerHTML",
        label=_("HTMX Swap Method"),
        help_text=_("How to swap the response content"),
    )

    class Meta:
        icon = "form"
        label = _("Contact Form")
        group = _("Forms")
