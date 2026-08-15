"""Loop-CRM CRM module — Twenty DNA (sales).

Company and Contact are the people/business graph; Pipeline + PipelineStage
model configurable sales stages; Deal links a company to a stage and (crucially)
to a marketing campaign — the attribution glue between marketing and sales.
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import Workspace


class Company(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="companies")
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    employee_count = models.IntegerField(null=True, blank=True)
    custom_attributes = models.JSONField(default=dict)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="owned_companies")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["workspace", "name"])]

    def __str__(self) -> str:
        return self.name


class Contact(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="contacts")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contacts")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(blank=True)
    custom_attributes = models.JSONField(default=dict)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="owned_contacts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [models.Index(fields=["workspace", "email"])]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return self.full_name


class Pipeline(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="pipelines")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return self.name


class PipelineStage(models.Model):
    STAGE_TYPES = [
        ("lead", "Lead"),
        ("qualified", "Qualified"),
        ("proposal", "Proposal"),
        ("negotiation", "Negotiation"),
        ("closed_won", "Closed Won"),
        ("closed_lost", "Closed Lost"),
    ]

    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=100)
    stage_type = models.CharField(max_length=20, choices=STAGE_TYPES, default="lead")
    color = models.CharField(max_length=7, default="#6B7280")
    order = models.IntegerField(default=0)
    probability = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    @property
    def is_won(self) -> bool:
        return self.stage_type == "closed_won"

    @property
    def is_closed(self) -> bool:
        return self.stage_type in {"closed_won", "closed_lost"}

    def __str__(self) -> str:
        return f"{self.pipeline.name} - {self.name}"


class Deal(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="deals")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="deals")
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, related_name="deals")
    name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.SET_NULL, null=True, related_name="deals")
    stage = models.ForeignKey(PipelineStage, on_delete=models.SET_NULL, null=True, related_name="deals")
    expected_close_date = models.DateField()
    actual_close_date = models.DateField(null=True, blank=True)
    # Attribution link — connects marketing to sales in one atomic record.
    campaign = models.ForeignKey(
        "marketing.Campaign", on_delete=models.SET_NULL, null=True, blank=True, related_name="deals"
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="owned_deals")
    custom_attributes = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "stage"]),
            models.Index(fields=["workspace", "company"]),
            models.Index(fields=["workspace", "campaign"]),
        ]

    @property
    def is_won(self) -> bool:
        return bool(self.stage and self.stage.is_won)

    def transition_to_stage(self, stage: PipelineStage, *, save: bool = True) -> None:
        """Move a deal and queue the close workflow when it becomes won."""
        if stage.pipeline_id != self.pipeline_id:
            raise ValueError("The stage must belong to the deal pipeline.")
        was_won = self.is_won
        self.stage = stage
        if stage.is_won and self.actual_close_date is None:
            from django.utils import timezone

            self.actual_close_date = timezone.localdate()
        if save:
            self.save(update_fields=["stage", "actual_close_date", "updated_at"])
            if stage.is_won and not was_won and self.workspace_id:
                from plugins.workers.tasks import trigger_workflow

                trigger_workflow(
                    "deal-won",
                    self.workspace_id,
                    {"deal_id": self.pk, "source": "deal.stage_changed:closed_won"},
                )
                from apps.core.webhooks import dispatch_webhooks

                dispatch_webhooks(
                    self.workspace_id,
                    "deal_won",
                    {"deal_id": self.pk, "value": str(self.value), "company_id": self.company_id},
                )

    def __str__(self) -> str:
        return self.name


class Activity(models.Model):
    ACTIVITY_TYPES = [
        ("call", "Call"),
        ("email", "Email"),
        ("meeting", "Meeting"),
        ("note", "Note"),
        ("task", "Task"),
        ("social", "Social Interaction"),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="activities")
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name="activities")
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, related_name="activities")
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_activities")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "deal"]),
            models.Index(fields=["workspace", "activity_type"]),
        ]


class CustomFieldDefinition(models.Model):
    """Tenant-owned metadata for values stored in domain JSON attributes.

    This deliberately uses composition rather than polymorphic model
    inheritance: field definitions are cheap to query, easy to expose through
    Bolt, and do not create one table per custom field or cross-tenant joins.
    """

    OBJECT_TYPES = [
        ("company", "Company"),
        ("contact", "Contact"),
        ("deal", "Deal"),
        ("campaign", "Campaign"),
        ("post", "Post"),
    ]
    FIELD_TYPES = [
        ("text", "Text"),
        ("textarea", "Long text"),
        ("number", "Number"),
        ("boolean", "Boolean"),
        ("date", "Date"),
        ("url", "URL"),
        ("email", "Email"),
        ("select", "Select"),
        ("multi_select", "Multi-select"),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="custom_field_definitions")
    object_type = models.CharField(max_length=30, choices=OBJECT_TYPES)
    key = models.SlugField(max_length=80)
    label = models.CharField(max_length=120)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    description = models.CharField(max_length=255, blank=True)
    required = models.BooleanField(default=False)
    options = models.JSONField(default=list, blank=True)
    validation = models.JSONField(default=dict, blank=True)
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_custom_fields")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["object_type", "position", "label"]
        constraints = [
            models.UniqueConstraint(fields=["workspace", "object_type", "key"], name="uniq_custom_field_workspace_object_key"),
        ]
        indexes = [
            models.Index(fields=["workspace", "object_type", "is_active"]),
        ]

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        if self.field_type in {"select", "multi_select"} and not isinstance(self.options, list):
            raise ValidationError({"options": "Select options must be a JSON list."})
        if self.field_type not in {"select", "multi_select"} and self.options:
            raise ValidationError({"options": "Only select fields may define options."})

    def __str__(self) -> str:
        return f"{self.workspace} · {self.object_type} · {self.label}"


class CustomObjectDefinition(models.Model):
    """A workspace-defined object type (Twenty-style runtime schema).

    Fields are declarative JSON (key/label/type/required/options) so a
    workspace can add a new record type without a migration. Values live in
    ``CustomObjectRecord.data`` and are validated against this schema at the
    service boundary, never via polymorphic model inheritance.
    """

    FIELD_TYPE_CHOICES = [
        ("text", "Text"),
        ("textarea", "Long text"),
        ("number", "Number"),
        ("boolean", "Boolean"),
        ("date", "Date"),
        ("url", "URL"),
        ("email", "Email"),
        ("select", "Select"),
        ("multi_select", "Multi-select"),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="custom_object_definitions")
    key = models.SlugField(max_length=80)
    name = models.CharField(max_length=120)
    icon = models.CharField(max_length=40, blank=True, default="dataset")
    fields = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_custom_objects")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["workspace", "key"], name="uniq_custom_object_workspace_key"),
        ]
        indexes = [models.Index(fields=["workspace", "is_active"])]

    def __str__(self) -> str:
        return f"{self.name} ({self.key})"


class CustomObjectRecord(models.Model):
    """A single row for a workspace-defined object type."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="custom_object_records")
    definition = models.ForeignKey(CustomObjectDefinition, on_delete=models.CASCADE, related_name="records")
    data = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_custom_object_records")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["workspace", "definition"])]

    def __str__(self) -> str:
        return f"{self.definition.name} #{self.pk}"
