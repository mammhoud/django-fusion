from django import forms
from django.utils.translation import gettext_lazy as _
from wagtail import blocks


class ObjectiveBlock(blocks.StructBlock):
    """
    Block for representing course or service objectives.
    """

    text = blocks.RichTextBlock(
        label=_("Objective Description"),
        features=["h2", "h3", "bold", "italic", "link", "ol", "ul", "code"],
        help_text=_("Detailed explanation of this objective."),
    )
    style_class = blocks.ChoiceBlock(
        choices=[
            ("feather-check", _("Checkmark")),
            ("feather-chevron-left", _("Chevron Left")),
            ("feather-chevron-right", _("Chevron Right")),
        ],
        default="feather-check",
        widget=forms.RadioSelect,
        label=_("Icon Style"),
        help_text=_("Choose an icon to visually represent this objective."),
    )

    class Meta:
        icon = "target"
        label = _("Objective")
        help_text = _("Describes a goal, feature, or key outcome.")
