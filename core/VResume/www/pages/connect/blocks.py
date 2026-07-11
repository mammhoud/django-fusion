"""
Connect app blocks — ContactFormBlock for the contact page form.
"""
from django.utils.translation import gettext_lazy as _
from wagtail import blocks


class ContactFormBlock(blocks.StructBlock):
    show_name = blocks.BooleanBlock(default=True, required=False, label=_("Show Name Field"))
    show_phone = blocks.BooleanBlock(default=False, required=False, label=_("Show Phone Field"))
    show_subject = blocks.BooleanBlock(default=True, required=False, label=_("Show Subject Field"))
    button_text = blocks.CharBlock(
        default=_("Send Message"), max_length=50, label=_("Submit Button Text"),
    )

    class Meta:
        template = "connect/blocks/contact_form.html"
        icon = "form"
        label = _("Contact Form")
