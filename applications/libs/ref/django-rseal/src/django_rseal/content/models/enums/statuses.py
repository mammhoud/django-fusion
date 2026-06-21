from colorfield.fields import ColorField  # Requires django-colorfield package
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_rseal.content.models.default import DefaultBase


class StatusChoice(DefaultBase):
    """
    Comprehensive status model with state machine support and visual customization
    """

    class Category(models.TextChoices):
        LEAD = "LEAD", _("Lead")
        ACTIVITY = "ACT", _("Activity")
        PIPELINE = "PIPE", _("Pipeline")
        TICKET = "TICK", _("Ticket")
        TASK = "TASK", _("Task")
        OPPORTUNITY = "OPP", _("Opportunity")

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Code"),
        help_text=_("Unique machine-readable identifier"),
        validators=[
            RegexValidator(
                regex="^[a-zA-Z0-9_]+$",
                message=_("Code can only contain letters, numbers and underscores"),
            )
        ],
    )
    name = models.CharField(
        max_length=100, verbose_name=_("Display Name"), help_text=_("Human-readable status name")
    )
    category = models.CharField(
        max_length=4,
        choices=Category.choices,
        verbose_name=_("Category"),
        help_text=_("Type of entity this status applies to"),
    )
    is_terminal = models.BooleanField(
        default=False,
        verbose_name=_("Is Terminal"),
        help_text=_("Whether this status represents an end state"),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Is Default"),
        help_text=_("Whether this is the default status for new items"),
    )
    color = ColorField(
        default="#FFFFFF", verbose_name=_("Color"), help_text=_("Display color for this status")
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Icon"),
        help_text=_("Icon class name for this status"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Explanation of when to use this status"),
    )
    next_valid_statuses = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        verbose_name=_("Valid Next Statuses"),
        help_text=_("Statuses that can follow this one in workflow"),
    )
    requires_comment = models.BooleanField(
        default=False,
        verbose_name=_("Requires Comment"),
        help_text=_("Whether changing to this status requires a comment"),
    )

    class Meta:
        verbose_name = _("Status Choice")
        verbose_name_plural = _("Status Choices")
        ordering = ["category", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "is_default"],
                condition=models.Q(is_default=True),
                name="unique_default_status_per_category",
            )
        ]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["is_terminal"]),
            models.Index(fields=["is_default"]),
        ]

    def __str__(self):
        return f"{self.get_category_display()}: {self.name}"  # type: ignore

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.is_default and self.is_terminal:
            raise ValidationError(_("A terminal status cannot be the default status"))

    def get_absolute_url(self):
        return reverse("status-choice-detail", kwargs={"pk": self.pk})

    @property
    def badge_class(self):
        """Returns CSS class for displaying this status as a badge"""
        if self.color == "#FFFFFF":
            return "badge-light"
        return ""


class DerivedStatus(DefaultBase):
    """
    Advanced derived status model with versioning and execution context
    """

    class CalculationLanguage(models.TextChoices):
        PYTHON = "PY", _("Python")
        JAVASCRIPT = "JS", _("JavaScript")
        CUSTOM = "CUS", _("Custom DSL")

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Code"),
        help_text=_("Unique identifier for this derived status"),
        validators=[
            RegexValidator(
                regex="^[a-zA-Z0-9_]+$",
                message=_("Code can only contain letters, numbers and underscores"),
            )
        ],
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("Human-readable name for this derived status"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Explanation of what this derived status represents"),
    )
    calculation_language = models.CharField(
        max_length=3,
        choices=CalculationLanguage.choices,
        default=CalculationLanguage.PYTHON,
        verbose_name=_("Language"),
    )
    calculation_logic = models.TextField(
        verbose_name=_("Calculation Logic"),
        help_text=_("Code that evaluates to determine this status"),
    )
    priority = models.IntegerField(
        default=0,
        verbose_name=_("Priority"),
        help_text=_("Evaluation order when multiple derived statuses apply"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Whether this derived status should be calculated"),
    )
    version = models.PositiveIntegerField(default=1, verbose_name=_("Version"))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))
    applicable_models = models.CharField(
        max_length=200,
        verbose_name=_("Applicable Models"),
        help_text=_("Comma-separated list of model names this applies to"),
    )

    class Meta:
        verbose_name = _("Derived Status")
        verbose_name_plural = _("Derived Statuses")
        ordering = ["priority", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["priority"]),
        ]

    def __str__(self):
        return f"{self.name} (v{self.version})"

    def get_absolute_url(self):
        return reverse("derived-status-detail", kwargs={"pk": self.pk})

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.calculation_language == self.CalculationLanguage.PYTHON:
            try:
                compile(self.calculation_logic, "<string>", "exec")
            except SyntaxError as e:
                raise ValidationError(_("Invalid Python syntax: %(error)s") % {"error": str(e)})
