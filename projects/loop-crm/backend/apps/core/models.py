"""Loop-CRM core module — shared foundation (Twenty DNA, tenant-scoped).

Workspace is the multi-tenant boundary every domain record scopes to.
Django's ``auth.User`` remains the account (django-fusion's models reference it
directly, so AUTH_USER_MODEL is intentionally NOT swapped); role/workspace live
on ``UserProfile``. AuditLog is the write-once trail shared across the CRM and
marketing apps.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class Workspace(models.Model):
    """Multi-tenant workspace — the tenancy root for all Loop-CRM data."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    timezone = models.CharField(max_length=50, default="UTC")
    currency = models.CharField(max_length=3, default="USD")
    # Machine-to-machine correlation: the Formint POS org/branch reference that
    # maps to this workspace during ingest. Null for tenant-created workspaces.
    external_ref = models.CharField(max_length=120, null=True, blank=True, unique=True)
    source = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class UserProfile(models.Model):
    """Role + workspace + preferences attached to a Django ``auth.User``.

    The seven RBAC personas (super_admin, sales_manager, sales_rep,
    marketing_manager, marketing_specialist, revops_manager, viewer) live here
    so django-fusion's ``auth.User`` relations stay intact.
    """

    ROLE_CHOICES = [
        ("super_admin", "Super Admin"),
        ("sales_manager", "Sales Manager"),
        ("sales_rep", "Sales Rep"),
        ("marketing_manager", "Marketing Manager"),
        ("marketing_specialist", "Marketing Specialist"),
        ("revops_manager", "RevOps Manager"),
        ("viewer", "Viewer"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="members", null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="viewer")
    avatar = models.URLField(blank=True)
    title = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    preferences = models.JSONField(default=dict)

    @property
    def is_sales_user(self) -> bool:
        return self.role in {"super_admin", "sales_manager", "sales_rep"}

    @property
    def is_marketing_user(self) -> bool:
        return self.role in {"super_admin", "marketing_manager", "marketing_specialist"}

    def __str__(self) -> str:
        return f"{self.user} ({self.get_role_display()})"


class AuditLog(models.Model):
    """Append-only audit trail — every mutation in the workspace is recorded."""

    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("view", "View"),
        ("login", "Login"),
        ("logout", "Logout"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="audit_logs"
    )
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="audit_logs"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "created_at"]),
            models.Index(fields=["model_name", "object_id"]),
        ]


class WorkflowDefinition(models.Model):
    """Persisted, workspace-aware automation definition.

    The action list is declarative JSON so CRM, marketing, and attribution can
    share one workflow contract without hard-coding provider calls in forms.
    ``workspace=None`` represents a global template shipped by the product.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("paused", "Paused"),
        ("archived", "Archived"),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="workflow_definitions",
        null=True,
        blank=True,
    )
    slug = models.SlugField(max_length=120)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=40, default="workspace")
    trigger = models.CharField(max_length=120)
    trigger_config = models.JSONField(default=dict, blank=True)
    actions = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_workflows",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "slug"],
                name="uniq_workflow_workspace_slug",
            ),
        ]
        indexes = [models.Index(fields=["workspace", "status"])]

    @property
    def is_enabled(self) -> bool:
        return self.status == "active"

    @property
    def action_count(self) -> int:
        return len(self.actions or [])

    def __str__(self) -> str:
        return self.name


class WorkflowRun(models.Model):
    """An auditable execution record for a workflow definition."""

    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("running", "Running"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    definition = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name="runs",
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="workflow_runs",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    trigger_payload = models.JSONField(default=dict, blank=True)
    result = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)
    queued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-queued_at"]
        indexes = [
            models.Index(fields=["workspace", "status"]),
            models.Index(fields=["definition", "queued_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.definition.name} · {self.status}"


class TaskExecution(models.Model):
    """Website-local mirror of the shared ``BackgroundTaskLog`` audit record.

    The shared worker writes ``django_fusion.models.tasks.BackgroundTaskLog``;
    the Task Center page mirrors those rows into this product-owned table so
    each website can query its own task history without reaching the shared
    infra database. Populated idempotently (on ``job_id``) by
    ``django_fusion.tasks.views.sync_website_record`` / the
    ``sync_task_history`` management command.
    """

    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("started", "Started"),
        ("finished", "Finished"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("retrying", "Retrying"),
    ]

    job_id = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    task_name = models.CharField(max_length=255, db_index=True)
    queue_name = models.CharField(max_length=100, default="default")
    site_name = models.CharField(max_length=100, db_index=True, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["site_name", "-created_at"]),
            models.Index(fields=["task_name", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.task_name} [{self.status}]"


class SavedView(models.Model):
    """A member's persisted list/kanban view configuration for one resource.

    ``config`` carries a safe, declarative shape: ``columns`` (read-field
    projection), ``sort`` (one allowlisted ordering), ``filters`` (field →
    substring), and ``group_by`` (kanban grouping field). Views are scoped to
    the owning member AND workspace so one user's board never leaks to another.
    """

    VIEW_TYPES = [
        ("list", "List"),
        ("kanban", "Kanban"),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="saved_views")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_views")
    resource = models.CharField(max_length=60)
    name = models.CharField(max_length=120)
    view_type = models.CharField(max_length=20, choices=VIEW_TYPES, default="list")
    config = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["resource", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "user", "resource", "name"],
                name="uniq_saved_view_member_name",
            ),
        ]
        indexes = [models.Index(fields=["workspace", "user", "resource"])]

    def __str__(self) -> str:
        return f"{self.user} · {self.resource} · {self.name}"


class Webhook(models.Model):
    """Workspace-configured outbound webhook subscription.

    Each webhook listens for one or more domain events (or all events when
    ``events`` is empty) and is delivered HMAC-signed by the ``deliver_webhook``
    Dramatiq actor with retry backoff and a dead-letter terminal state.
    """

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="webhooks")
    url = models.URLField()
    # Shared signing secret; never returned by the API resource projection.
    secret = models.CharField(max_length=255, blank=True)
    events = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_webhooks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["workspace", "is_active"])]

    def __str__(self) -> str:
        return f"{self.url} ({', '.join(self.events) or 'all'})"


class WebhookDelivery(models.Model):
    """One delivery attempt (or dead-letter terminal state) for a webhook."""

    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("dead", "Dead letter"),
    ]

    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name="deliveries")
    event = models.CharField(max_length=120)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    attempt_count = models.PositiveIntegerField(default=0)
    response_status = models.PositiveIntegerField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["webhook", "status"]),
            models.Index(fields=["webhook", "event"]),
        ]

    def __str__(self) -> str:
        return f"{self.webhook.url} · {self.event} · {self.status}"
