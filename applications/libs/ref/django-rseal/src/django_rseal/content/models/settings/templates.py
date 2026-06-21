"""
Email template model for django_rseal.

EmailTemplate has been moved to django_rseal.email.models.EmailTemplate.
TemplateVariable is a standalone model for reusable template variables.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, FieldRowPanel
from wagtail.models import Orderable


class TemplateVariable(Orderable):
    """
    Reusable variables/placeholders for email templates.
    Defines the variables that can be used in template content.
    """

    name = models.CharField(
        max_length=50,
        verbose_name=_("Variable Name"),
        help_text=_("Name used in templates as {{ variable_name }}"),
    )

    description = models.CharField(
        max_length=200,
        verbose_name=_("Description"),
        help_text=_("What this variable represents"),
    )

    default_value = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Default Value"),
        help_text=_("Default value if not provided in context"),
    )

    is_required = models.BooleanField(
        default=False,
        verbose_name=_("Required"),
        help_text=_("This variable must be provided in context"),
    )

    variable_type = models.CharField(
        max_length=20,
        choices=[
            ("text", _("Text")),
            ("url", _("URL")),
            ("email", _("Email")),
            ("date", _("Date")),
            ("number", _("Number")),
            ("boolean", _("Boolean")),
            ("color", _("Color")),
            ("image", _("Image")),
            ("file", _("File")),
        ],
        default="text",
        verbose_name=_("Type"),
    )

    validation_regex = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Validation Regex"),
        help_text=_("Regular expression for validating this variable (optional)"),
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("default_value"),
        FieldRowPanel(
            [
                FieldPanel("is_required"),
                FieldPanel("variable_type"),
            ]
        ),
        FieldPanel("validation_regex"),
    ]

    class Meta:
        verbose_name = _("Template Variable")
        verbose_name_plural = _("Template Variables")
        ordering = ["name"]

    def __str__(self):
        return f"{{{{ {self.name} }}}}"

    def validate_value(self, value):
        """Validate a value against this variable's constraints."""
        if self.is_required and not value:
            return False, _("This field is required")

        if self.validation_regex and value:
            import re
            if not re.match(self.validation_regex, str(value)):
                return False, _("Value does not match required format")

        return True, None


__all__ = ["TemplateVariable"]
