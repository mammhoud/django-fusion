"""POS Cloud — Core models: Organization, Branch, Lead, InventoryReport, BranchReport,
DeviceToken (cloud-side device auth), and Branch Sync models (products, sales,
inventory synced from pos-full nodes)."""

from __future__ import annotations

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


# ══════════════════════════════════════════════════════════════════════
# Organization
# ══════════════════════════════════════════════════════════════════════


class Organization(models.Model):
    """Multi-tenant organization — owns branches and users."""

    name = models.CharField(_("name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)
    description = models.TextField(_("description"), blank=True)
    website = models.URLField(_("website"), blank=True)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone"), max_length=50, blank=True)
    address = models.TextField(_("address"), blank=True)
    logo = models.ImageField(_("logo"), upload_to="orgs/logos/", blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    subscription_plan = models.CharField(
        _("plan"), max_length=50, default="free",
        choices=[("free", "Free"), ("pro", "Pro"), ("enterprise", "Enterprise")],
    )

    # Metadata
    settings = models.JSONField(_("settings"), default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")
        ordering = ["name"]

    def __str__(self):
        return self.name


# ══════════════════════════════════════════════════════════════════════
# Branch
# ══════════════════════════════════════════════════════════════════════


class Branch(models.Model):
    """Physical/virtual store branch within an organization."""

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="branches",
        verbose_name=_("organization"),
    )
    name = models.CharField(_("name"), max_length=200)
    code = models.CharField(_("branch code"), max_length=20, unique=True)
    address = models.TextField(_("address"), blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    country = models.CharField(_("country"), max_length=100, blank=True)
    phone = models.CharField(_("phone"), max_length=50, blank=True)
    email = models.EmailField(_("email"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    is_headquarters = models.BooleanField(_("headquarters"), default=False)

    # POS configuration
    pos_type = models.CharField(
        _("POS type"), max_length=20, default="pos-solo",
        choices=[("pos-solo", "POS Solo"), ("pos-full", "POS Full"), ("pos-mini", "POS Mini")],
    )
    node_id = models.CharField(
        _("node ID"), max_length=100, blank=True,
        help_text="Linked POS node identifier",
    )

    # Sync settings
    sync_enabled = models.BooleanField(_("sync enabled"), default=True)
    sync_interval = models.IntegerField(_("sync interval (s)"), default=300)

    # Metadata
    settings = models.JSONField(_("settings"), default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("branch")
        verbose_name_plural = _("branches")
        ordering = ["organization__name", "name"]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


# ══════════════════════════════════════════════════════════════════════
# Lead
# ══════════════════════════════════════════════════════════════════════


class Lead(models.Model):
    """Sales lead — tracks potential customers through the pipeline."""

    LEAD_STATUS_CHOICES = [
        ("new", _("New")),
        ("contacted", _("Contacted")),
        ("qualified", _("Qualified")),
        ("proposal", _("Proposal Sent")),
        ("negotiation", _("Negotiation")),
        ("won", _("Won")),
        ("lost", _("Lost")),
        ("archived", _("Archived")),
    ]

    LEAD_SOURCE_CHOICES = [
        ("website", _("Website")),
        ("referral", _("Referral")),
        ("social_media", _("Social Media")),
        ("email_campaign", _("Email Campaign")),
        ("phone", _("Phone")),
        ("event", _("Event")),
        ("other", _("Other")),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="leads",
        verbose_name=_("organization"),
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="leads", verbose_name=_("branch"),
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="assigned_leads",
        verbose_name=_("assigned to"),
    )

    first_name = models.CharField(_("first name"), max_length=200)
    last_name = models.CharField(_("last name"), max_length=200)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone"), max_length=50, blank=True)
    company_name = models.CharField(_("company"), max_length=300, blank=True)
    job_title = models.CharField(_("job title"), max_length=200, blank=True)

    status = models.CharField(
        _("status"), max_length=20, choices=LEAD_STATUS_CHOICES, default="new",
    )
    source = models.CharField(
        _("source"), max_length=20, choices=LEAD_SOURCE_CHOICES, default="website",
    )
    interest = models.CharField(_("interest"), max_length=200, blank=True)
    notes = models.TextField(_("notes"), blank=True)
    estimated_value = models.DecimalField(
        _("estimated value"), max_digits=12, decimal_places=2, default=0,
    )
    score = models.IntegerField(_("lead score"), default=0)

    is_active = models.BooleanField(_("active"), default=True)
    first_contacted_at = models.DateTimeField(null=True, blank=True)
    last_contacted_at = models.DateTimeField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("lead")
        verbose_name_plural = _("leads")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["assigned_to"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} [{self.status}]"


# ══════════════════════════════════════════════════════════════════════
# Contact (CRM)
# ══════════════════════════════════════════════════════════════════════


class Contact(models.Model):
    """CRM Contact linked to organization."""

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="contacts",
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacts",
    )
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    mobile = models.CharField(max_length=50, blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ══════════════════════════════════════════════════════════════════════
# Deal (CRM)
# ══════════════════════════════════════════════════════════════════════


class Deal(models.Model):
    """CRM Deal — tracked opportunity."""

    DEAL_STAGES = [
        ("discovery", _("Discovery")),
        ("qualification", _("Qualification")),
        ("proposal", _("Proposal")),
        ("negotiation", _("Negotiation")),
        ("closed_won", _("Closed Won")),
        ("closed_lost", _("Closed Lost")),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="deals",
    )
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals",
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stage = models.CharField(max_length=20, choices=DEAL_STAGES, default="discovery")
    probability = models.IntegerField(default=10)
    expected_close_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("deal")
        verbose_name_plural = _("deals")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# ══════════════════════════════════════════════════════════════════════
# Inventory Report
# ══════════════════════════════════════════════════════════════════════


class InventoryReport(models.Model):
    """Aggregated inventory report across branches."""

    REPORT_TYPES = [
        ("stock_level", _("Stock Level")),
        ("low_stock", _("Low Stock Alert")),
        ("movement", _("Stock Movement")),
        ("valuation", _("Inventory Valuation")),
        ("turnover", _("Inventory Turnover")),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="inventory_reports",
    )
    title = models.CharField(max_length=300)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="generated_reports",
    )

    # Filters used
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    branches = models.ManyToManyField(Branch, blank=True, related_name="inventory_reports")

    # Results
    data = models.JSONField(default=dict, blank=True)
    summary = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("inventory report")
        verbose_name_plural = _("inventory reports")
        ordering = ["-created_at"]


# ══════════════════════════════════════════════════════════════════════
# Branch Report
# ══════════════════════════════════════════════════════════════════════


class BranchReport(models.Model):
    """Per-branch performance and sales report."""

    REPORT_TYPES = [
        ("daily_sales", _("Daily Sales")),
        ("weekly_summary", _("Weekly Summary")),
        ("monthly_summary", _("Monthly Summary")),
        ("product_performance", _("Product Performance")),
        ("employee_performance", _("Employee Performance")),
        ("revenue_trend", _("Revenue Trend")),
        ("profit_loss", _("Profit & Loss")),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="branch_reports",
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="reports",
    )
    title = models.CharField(max_length=300)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)

    # Date range
    date_from = models.DateField()
    date_to = models.DateField()

    # Filters
    category_filter = models.CharField(max_length=100, blank=True)
    employee_filter = models.CharField(max_length=200, blank=True)

    # Results
    data = models.JSONField(default=dict, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    format = models.CharField(
        max_length=10, default="json",
        choices=[("json", "JSON"), ("pdf", "PDF"), ("xlsx", "Excel")],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("branch report")
        verbose_name_plural = _("branch reports")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "branch", "report_type"]),
        ]


# ══════════════════════════════════════════════════════════════════════
# Branch Sync — synced POS data from pos-full nodes
# ══════════════════════════════════════════════════════════════════════


class BranchSyncLog(models.Model):
    """Audit log for branch-to-cloud sync operations."""

    SYNC_STATUS = [
        ("pending", "Pending"), ("received", "Received"),
        ("processed", "Processed"), ("failed", "Failed"),
    ]

    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="sync_logs",
    )
    node_id = models.CharField(max_length=100, db_index=True)
    entity_type = models.CharField(max_length=50)
    entity_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default="received")
    error_message = models.TextField(blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("branch sync log")
        verbose_name_plural = _("branch sync logs")
        ordering = ["-received_at"]
        indexes = [
            models.Index(fields=["branch", "entity_type"]),
            models.Index(fields=["node_id", "received_at"]),
        ]

    def __str__(self):
        return f"[{self.status}] {self.entity_type} x{self.entity_count} from {self.node_id}"


class BranchProduct(models.Model):
    """Synced product catalog entry from a branch node."""

    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="synced_products",
    )
    source_id = models.CharField(max_length=100, help_text="Original product ID from the branch")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=100, blank=True, default="")
    category_name = models.CharField(max_length=200, blank=True, default="")
    stock_quantity = models.IntegerField(default=0)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("branch product")
        verbose_name_plural = _("branch products")
        unique_together = [["branch", "source_id"]]
        ordering = ["branch", "name"]

    def __str__(self):
        return f"{self.name} @ {self.branch.name}"


class BranchSale(models.Model):
    """Synced sale transaction from a branch node."""

    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="synced_sales",
    )
    source_id = models.CharField(max_length=100, help_text="Original sale ID from the branch")
    customer_name = models.CharField(max_length=200, blank=True, default="")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True, default="cash")
    sale_date = models.DateTimeField()
    item_count = models.IntegerField(default=0)
    items = models.JSONField(default=list, blank=True, help_text="Line items from the sale")
    last_synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("branch sale")
        verbose_name_plural = _("branch sales")
        unique_together = [["branch", "source_id"]]
        ordering = ["-sale_date"]
        indexes = [
            models.Index(fields=["branch", "sale_date"]),
        ]

    def __str__(self):
        return f"Sale #{self.source_id} @ {self.branch.name} ({self.total_amount})"


class BranchInventory(models.Model):
    """Synced inventory transaction from a branch node."""

    TX_TYPES = [
        ("addition", "Addition"), ("removal", "Removal"),
        ("adjustment", "Adjustment"), ("transfer", "Transfer"),
    ]

    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="synced_inventory",
    )
    source_id = models.CharField(max_length=100, help_text="Original transaction ID from the branch")
    product_name = models.CharField(max_length=200, blank=True, default="")
    transaction_type = models.CharField(max_length=20, choices=TX_TYPES, default="addition")
    quantity = models.IntegerField()
    notes = models.TextField(blank=True, default="")
    transaction_date = models.DateTimeField()
    last_synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("branch inventory tx")
        verbose_name_plural = _("branch inventory txs")
        unique_together = [["branch", "source_id"]]
        ordering = ["-transaction_date"]
        indexes = [
            models.Index(fields=["branch", "transaction_type"]),
        ]

    def __str__(self):
        return f"{self.transaction_type} x{self.quantity} @ {self.branch.name}"


# ══════════════════════════════════════════════════════════════════════
# Device Token — cloud-side device authentication & sync tracking
# ══════════════════════════════════════════════════════════════════════


class DeviceToken(models.Model):
    """Cloud-side token for POS device authentication and sync tracking.

    Mirrors the sidecar DeviceToken (pos-full/sidecar/models/token.py) on the
    cloud side so the central server can validate tokens, track sync progress
    per device, and revoke access remotely.
    """

    class AppType(models.TextChoices):
        POS_SOLO = "pos-solo", "POS Solo"
        POS_FULL = "pos-full", "POS Full"
        POS_MINI = "pos-mini", "POS Mini"
        CLOUD = "cloud", "Cloud Server"

    class SyncStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SYNCING = "syncing", "Syncing"
        SYNCED = "synced", "Synced"
        FAILED = "failed", "Failed"

    class Role(models.TextChoices):
        ADMIN = "admin", "Administrator"
        MANAGER = "manager", "Manager"
        CASHIER = "cashier", "Cashier"
        VIEWER = "viewer", "Viewer"

    # ── Core identity ──
    device_id = models.CharField(
        _("device ID"), max_length=100, db_index=True,
        help_text="Device identifier. Multiple tokens per device allowed for refresh cycles.",
    )
    token_hash = models.CharField(
        _("token hash"), max_length=128, unique=True,
        help_text="SHA-256 hash of the raw token.",
    )
    token_prefix = models.CharField(
        _("token prefix"), max_length=8,
        help_text="First 8 characters of the raw token (for UI display).",
    )

    # ── Node / branch linkage ──
    node_id_link = models.CharField(
        _("node ID"), max_length=100, blank=True, default="", db_index=True,
        help_text="Node identifier this token belongs to.",
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="device_tokens", verbose_name=_("branch"),
        help_text="Branch this device token is associated with.",
    )

    # ── Role & type ──
    role = models.CharField(
        _("role"), max_length=20, choices=Role.choices, default=Role.VIEWER, db_index=True,
    )
    app_type = models.CharField(
        _("app type"), max_length=20, choices=AppType.choices, default=AppType.POS_SOLO,
        db_index=True, help_text="Application type flag for DataToken sync scoping.",
    )
    node_type = models.CharField(
        _("node type"), max_length=20,
        choices=[("pos-solo", "POS Solo"), ("pos-full", "POS Full"),
                 ("pos-minimal", "POS Minimal"), ("cloud-server", "Cloud Server"),
                 ("external", "External")],
        default="pos-solo",
    )

    # ── Capabilities ──
    capabilities = models.JSONField(_("capabilities"), default=dict, blank=True)
    allowed_entities = models.JSONField(_("allowed entities"), default=list, blank=True)

    # ── Lifecycle ──
    issued_at = models.DateTimeField(_("issued at"), auto_now_add=True)
    expires_at = models.DateTimeField(_("expires at"), help_text="When this token expires.")
    last_used_at = models.DateTimeField(_("last used at"), null=True, blank=True)

    # ── DataToken sync tracking (new fields) ──
    last_synced_at = models.DateTimeField(
        _("last synced at"), null=True, blank=True,
        help_text="When data tagged with this token was last confirmed synced.",
    )
    sync_status = models.CharField(
        _("sync status"), max_length=20, choices=SyncStatus.choices,
        default=SyncStatus.PENDING, db_index=True,
        help_text="Sync status of data tagged with this token.",
    )

    # ── State ──
    is_active = models.BooleanField(_("active"), default=True)
    metadata = models.JSONField(_("metadata"), default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "cloud_device_tokens"
        verbose_name = _("device token")
        verbose_name_plural = _("device tokens")
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["token_hash"]),
            models.Index(fields=["device_id", "is_active"]),
            models.Index(fields=["role"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["sync_status"]),
            models.Index(fields=["app_type", "sync_status"]),
            models.Index(fields=["branch", "is_active"]),
        ]

    def __str__(self):
        return f"[{self.role}] {self.device_id} ({self.token_prefix}...)"

    def is_expired(self) -> bool:
        from django.utils import timezone
        return timezone.now() >= self.expires_at

    def mark_data_synced(self):
        """Mark this token's associated data as synced."""
        from django.utils import timezone
        self.sync_status = self.SyncStatus.SYNCED
        self.last_synced_at = timezone.now()
        self.save(update_fields=["sync_status", "last_synced_at", "updated_at"])
        # Cascade to linked DataTokens
        if self.node_id_link:
            try:
                from django_fusion.core.models import DataToken
                DataToken.objects.filter(
                    node_id=self.node_id_link,
                    sync_status__in=["pending", "syncing"],
                ).update(sync_status="synced", synced_at=timezone.now())
            except ImportError:
                pass

    def mark_data_sync_failed(self):
        """Mark this token's sync as failed."""
        self.sync_status = self.SyncStatus.FAILED
        self.save(update_fields=["sync_status", "updated_at"])
