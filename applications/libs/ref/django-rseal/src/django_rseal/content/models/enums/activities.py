from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_rseal.content.models.default import DefaultBase


class ActivityType(DefaultBase):
    """
    Enhanced activity type model with categorization, validation, and workflow integration
    """

    class Category(models.TextChoices):
        COMMUNICATION = "COM", _("Communication")
        MEETING = "MET", _("Meeting")
        TASK = "TSK", _("Task")
        SYSTEM = "SYS", _("System")
        DOCUMENT = "DOC", _("Document")
        OTHER = "OTH", _("Other")

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Code"),
        help_text=_("Unique identifier for this activity type"),
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
        help_text=_("Human-readable name for this activity type"),
    )
    category = models.CharField(
        max_length=3,
        choices=Category.choices,
        default=Category.COMMUNICATION,
        verbose_name=_("Category"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Detailed explanation of when to use this activity type"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Whether this activity type is available for use"),
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Icon"),
        help_text=_("Icon class name (e.g. 'fa-envelope' for FontAwesome)"),
    )
    default_duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Default Duration (minutes)"),
        help_text=_("Suggested duration for this activity type"),
    )
    workflow_sequence = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Workflow Sequence"),
        help_text=_("Suggested order in workflow processes"),
    )
    requires_comment = models.BooleanField(
        default=False,
        verbose_name=_("Requires Comment"),
        help_text=_("Whether this activity type requires additional comments"),
    )
    allowed_statuses = models.ManyToManyField(
        "StatusChoice",
        blank=True,
        verbose_name=_("Allowed Statuses"),
        help_text=_("Statuses that can be assigned to this activity type"),
    )

    class Meta:  # type: ignore
        verbose_name = _("Activity Type")
        verbose_name_plural = _("Activity Types")
        ordering = ["workflow_sequence", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.get_category_display()}: {self.name}"  # type: ignore

    def get_absolute_url(self):
        return reverse("activity-type-detail", kwargs={"pk": self.pk})

    @property
    def is_system_type(self):
        return self.category == self.Category.SYSTEM

