"""
Cloud CRM — Django Models for POS Full Edition.

Provides cloud-synced Customer Relationship Management models
running as an independent server alongside the Tauri sidecar.

Contact & Company management, sales pipelines / Deal tracking,
Activities & notes, and cloud synchronization queue.

Related Names: crm, cloud, contacts, companies, deals, pipeline, activities, notes
Tags: #crm #cloud #models #sync #pos-full
"""

from django.db import models


# ---------------------------------------------------------------------------
# CRM CORE MODELS
# ---------------------------------------------------------------------------


class Company(models.Model):
    """Organization / business entity that contacts belong to.

    Enhanced with industry classification, custom fields, and
    direct cloud sync support. Linked to POS Customer via pos_customer_id.

    Use Cases:
      - B2B customer profiles with tax info and industry
      - Vendor / supplier management
      - Multi-branch or franchise hierarchies
    """

    name = models.TextField(help_text="Company legal or trading name")
    website = models.URLField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    state = models.TextField(null=True, blank=True, help_text="State / province / region")
    postal_code = models.TextField(null=True, blank=True)
    country = models.TextField(null=True, blank=True, default="US")
    industry = models.TextField(null=True, blank=True, help_text="Industry sector (e.g. Retail, Hospitality)")
    description = models.TextField(null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    tax_id = models.TextField(null=True, blank=True, help_text="Tax/VAT registration number")
    # Classification
    size = models.TextField(
        null=True, blank=True,
        choices=[("1-10", "1-10"), ("11-50", "11-50"), ("51-200", "51-200"),
                 ("201-1000", "201-1000"), ("1000+", "1000+")],
        help_text="Employee size range"
    )
    source = models.TextField(
        null=True, blank=True,
        choices=[("referral", "Referral"), ("website", "Website"), ("direct", "Direct"),
                 ("social", "Social Media"), ("partner", "Partner"), ("other", "Other")],
        help_text="Lead source"
    )
    custom_fields = models.JSONField(null=True, blank=True, default=dict,
                                     help_text="User-defined custom fields as key-value pairs")
    tags = models.TextField(null=True, blank=True, help_text="Comma-separated tags for categorization")
    # Status
    is_active = models.BooleanField(default=True)
    # Timestamps & sync
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    cloud_id = models.TextField(null=True, blank=True, help_text="Remote cloud CRM entity ID")

    class Meta:
        db_table = "crm_companies"
        managed = True
        ordering = ["name"]
        verbose_name_plural = "companies"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["industry"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["synced_at"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def contact_count(self) -> int:
        """Number of active contacts at this company."""
        return self.contacts.filter(is_active=True).count()

    @property
    def total_deal_value(self) -> float:
        """Sum of active deal values for this company."""
        return sum(
            d.value for d in self.deals.filter(is_active=True, is_closed=False)
        )


class Contact(models.Model):
    """Individual person — linked to a Company and optionally to POS Customer.

    Enhanced with communication preferences, custom fields, tags,
    and direct cloud sync. The pos_customer_id field bridges CRM
    contacts to POS restaurant customers.

    Use Cases:
      - Sales leads and prospect tracking
      - Customer support contacts
      - Supplier / partner contacts
      - Employee directory (minimal)
    """

    SALUTATION_CHOICES = [
        ("mr", "Mr."),
        ("ms", "Ms."),
        ("mrs", "Mrs."),
        ("dr", "Dr."),
        ("prof", "Prof."),
        ("", "None"),
    ]

    salutation = models.TextField(null=True, blank=True, choices=SALUTATION_CHOICES)
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField()
    phone = models.TextField(null=True, blank=True, help_text="Primary phone number")
    mobile = models.TextField(null=True, blank=True, help_text="Mobile / cell number")
    job_title = models.TextField(null=True, blank=True)
    department = models.TextField(null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True,
        db_column="company_id", related_name="contacts"
    )
    # Link to existing POS customer (if they're also a restaurant customer)
    pos_customer_id = models.IntegerField(
        null=True, blank=True,
        help_text="POS customers.id — bridges CRM <> restaurant customers"
    )
    # Communication
    address = models.TextField(null=True, blank=True)
    prefer_contact = models.TextField(
        null=True, blank=True,
        choices=[("email", "Email"), ("phone", "Phone"), ("sms", "SMS")],
        help_text="Preferred contact method"
    )
    source = models.TextField(
        null=True, blank=True,
        choices=[("referral", "Referral"), ("website", "Website"), ("direct", "Direct"),
                 ("social", "Social Media"), ("partner", "Partner"), ("walkin", "Walk-in"),
                 ("other", "Other")],
        help_text="Lead source"
    )
    custom_fields = models.JSONField(null=True, blank=True, default=dict,
                                     help_text="User-defined custom fields as key-value pairs")
    tags = models.TextField(null=True, blank=True, help_text="Comma-separated tags for categorization")
    notes = models.TextField(null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Timestamps & sync
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    cloud_id = models.TextField(null=True, blank=True, help_text="Remote cloud CRM entity ID")

    class Meta:
        db_table = "crm_contacts"
        managed = True
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["company"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["synced_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def formatted_name(self) -> str:
        """Return name with salutation if available."""
        if self.salutation:
            return f"{self.get_salutation_display()} {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def open_deal_count(self) -> int:
        """Number of active (unclosed) deals for this contact."""
        return self.deals.filter(is_active=True, is_closed=False).count()


class Pipeline(models.Model):
    """Sales pipeline — a sequence of stages that Deals flow through.

    Multiple pipelines can exist (e.g. Sales, Onboarding, Support),
    with one marked as default.

    Use Cases:
      - Standard sales pipeline (Lead → Qualified → Proposal → Won/Lost)
      - Customer onboarding pipeline
      - Support ticket pipeline
      - Recruitment pipeline
    """

    name = models.TextField(unique=True)
    description = models.TextField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    cloud_id = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "crm_pipelines"
        managed = True
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_default"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def stage_count(self) -> int:
        return self.stages.filter(is_active=True).count()


class Stage(models.Model):
    """A step within a Pipeline (e.g. 'Qualified', 'Proposal', 'Closed Won').

    Each stage has a win probability (0.0–100.0) and optional color for UI display.
    The unique_together constraint prevents duplicate display orders within a pipeline.

    Use Cases:
      - Pipeline visualization (kanban board)
      - Deal stage tracking
      - Win probability analysis
    """

    pipeline = models.ForeignKey(
        Pipeline, on_delete=models.CASCADE, db_column="pipeline_id",
        related_name="stages"
    )
    name = models.TextField()
    display_order = models.IntegerField(default=0)
    probability = models.FloatField(
        default=0.0, help_text="Win probability as percentage (0.0–100.0)"
    )
    color = models.TextField(null=True, blank=True, help_text="Hex color for UI display (e.g. #3b82f6)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crm_stages"
        managed = True
        ordering = ["pipeline", "display_order"]
        unique_together = [("pipeline", "display_order")]
        indexes = [
            models.Index(fields=["pipeline", "display_order"]),
        ]

    def __str__(self) -> str:
        return f"{self.pipeline.name} → {self.name}"


class Deal(models.Model):
    """Sales opportunity tracked through a Pipeline and its Stages.

    Enhanced with discount tracking, product line items, and POS
    sale conversion tracking (pos_sale_id).

    Use Cases:
      - Sales pipeline tracking (opportunity management)
      - Quote-to-order conversion
      - Revenue forecasting by pipeline stage
      - POS sale cross-reference (offline → online)
    """

    CURRENCY_CHOICES = [
        ("USD", "USD"),
        ("EUR", "EUR"),
        ("GBP", "GBP"),
        ("CAD", "CAD"),
        ("AUD", "AUD"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    title = models.TextField(help_text="Deal / opportunity title")
    description = models.TextField(null=True, blank=True)
    value = models.FloatField(default=0.0)
    currency = models.TextField(default="USD", choices=CURRENCY_CHOICES)
    discount_percent = models.FloatField(default=0.0, help_text="Discount percentage applied")
    priority = models.TextField(default="medium", choices=PRIORITY_CHOICES)
    pipeline = models.ForeignKey(
        Pipeline, on_delete=models.CASCADE, db_column="pipeline_id",
        related_name="deals"
    )
    stage = models.ForeignKey(
        Stage, on_delete=models.CASCADE, db_column="stage_id"
    )
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True,
        db_column="contact_id", related_name="deals"
    )
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True,
        db_column="company_id", related_name="deals"
    )
    # Link to POS sale if deal converted
    pos_sale_id = models.IntegerField(
        null=True, blank=True,
        help_text="POS sales.id if deal was converted to a sale"
    )
    # Dates
    expected_close_date = models.DateTimeField(null=True, blank=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    # Status
    is_closed = models.BooleanField(default=False)
    is_won = models.BooleanField(default=False)
    lost_reason = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # Timestamps & sync
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    cloud_id = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "crm_deals"
        managed = True
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["stage"]),
            models.Index(fields=["contact"]),
            models.Index(fields=["company"]),
            models.Index(fields=["is_closed", "is_won"]),
            models.Index(fields=["expected_close_date"]),
            models.Index(fields=["priority"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.value} {self.currency}"

    @property
    def net_value(self) -> float:
        """Value after discount."""
        return self.value * (1 - self.discount_percent / 100)

    @property
    def stage_name(self) -> str:
        return self.stage.name if self.stage else "No Stage"

    @property
    def pipeline_name(self) -> str:
        return self.pipeline.name if self.pipeline else "No Pipeline"


class Activity(models.Model):
    """Logged interactions: meetings, calls, emails, tasks, reminders.

    Enhanced with duration tracking, outcome logging, and
    links to multiple CRM entities simultaneously.

    Use Cases:
      - Sales call logging
      - Meeting scheduling and notes
      - Task assignment and tracking
      - Email thread tracking
      - Reminder system
    """

    ACTIVITY_TYPES = [
        ("meeting", "Meeting"),
        ("call", "Phone Call"),
        ("email", "Email"),
        ("task", "Task"),
        ("reminder", "Reminder"),
        ("note", "Note"),
        ("lunch", "Lunch / Meal"),
        ("demo", "Product Demo"),
        ("followup", "Follow-up"),
        ("other", "Other"),
    ]

    activity_type = models.TextField(choices=ACTIVITY_TYPES)
    subject = models.TextField(help_text="Short summary of the activity")
    description = models.TextField(null=True, blank=True, help_text="Detailed notes or transcript")
    outcome = models.TextField(null=True, blank=True, help_text="Result / outcome (e.g. 'Interested', 'Not now')")
    duration_minutes = models.IntegerField(null=True, blank=True, help_text="Duration in minutes")
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, null=True, blank=True,
        db_column="contact_id", related_name="activities"
    )
    deal = models.ForeignKey(
        Deal, on_delete=models.CASCADE, null=True, blank=True,
        db_column="deal_id", related_name="activities"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True,
        db_column="company_id", related_name="activities"
    )
    # Scheduling
    due_date = models.DateTimeField(null=True, blank=True, help_text="Scheduled date/time")
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    # Status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    cloud_id = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "crm_activities"
        managed = True
        ordering = ["-created_at"]
        verbose_name_plural = "activities"
        indexes = [
            models.Index(fields=["activity_type"]),
            models.Index(fields=["contact"]),
            models.Index(fields=["deal"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["is_completed"]),
        ]

    def __str__(self) -> str:
        return f"[{self.get_activity_type_display()}] {self.subject}"


class CRMNote(models.Model):
    """Generic notes that can be attached to any CRM entity.

    Supports multiple entity links simultaneously:
    a note can reference a contact, deal, and company at once.

    Use Cases:
      - Call notes attached to a contact
      - Deal negotiation notes
      - General company notes
      - Internal reminders
    """

    content = models.TextField(help_text="Note body (Markdown supported)")
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, null=True, blank=True,
        db_column="contact_id", related_name="notes"
    )
    deal = models.ForeignKey(
        Deal, on_delete=models.CASCADE, null=True, blank=True,
        db_column="deal_id", related_name="notes"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True,
        db_column="company_id", related_name="notes"
    )
    is_pinned = models.BooleanField(default=False, help_text="Pinned notes appear at top of lists")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    cloud_id = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "crm_notes"
        managed = True
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["contact"]),
            models.Index(fields=["deal"]),
            models.Index(fields=["company"]),
            models.Index(fields=["is_pinned"]),
        ]

    def __str__(self) -> str:
        return self.content[:80]
