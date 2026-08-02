import uuid
from typing import Any, Dict

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_fusion.models.default import DefaultBase
from django_fusion.models.tags import TaggedPerson
from taggit.managers import TaggableManager
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    HelpPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import StreamField
from wagtail.search import index

from apps.domain.blocks.profile.stream_blocks import ProfileStreamBlock

# Validators
EMAIL_VALIDATOR = RegexValidator(
    regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    message=_("Enter a valid email address."),
)

PHONE_VALIDATOR = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."),
)


class Person(DefaultBase):
    """
    Comprehensive Profile model that extends Wagtail's user system.
    One-to-one relationship with the Django/Wagtail User model.
    """

    # ==================== IDENTIFIER ====================
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID"),
    )

    # ==================== RELATIONSHIPS ====================
    # One-to-one relationship with Wagtail/Django User model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("User Account"),
        help_text=_("Linked Django/Wagtail user account"),
    )

    # Optional: Link to other profiles if needed
    linked_profile = models.ForeignKey(
        getattr(settings, 'PROFILE_MODEL', 'auth.User'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_profiles",
        verbose_name=_("Linked System Profile"),
        help_text=_("Linked system profile for additional settings"),
    )

    # ==================== PERSONAL INFORMATION ====================
    # Name fields - can sync with user model or keep separate
    first_name = models.CharField(
        max_length=100,
        verbose_name=_("First Name"),
        blank=True,
        null=True,
    )

    last_name = models.CharField(
        max_length=100,
        verbose_name=_("Last Name"),
        blank=True,
        null=True,
    )

    full_name = models.CharField(
        max_length=200,
        verbose_name=_("Full Name"),
        blank=True,
        null=True,
        help_text=_("Automatically generated from first and last name"),
    )

    # Preferred display name (can be different from legal name)
    display_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Display Name"),
        help_text=_("Name to display publicly (can be different from legal name)"),
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date of Birth"),
    )

    gender = models.CharField(
        max_length=20,
        choices=[
            ("MALE", _("Male")),
            ("FEMALE", _("Female")),
            ("OTHER", _("Other")),
            ("PREFER_NOT_TO_SAY", _("Prefer not to say")),
        ],
        blank=True,
        null=True,
        verbose_name=_("Gender"),
    )

    # ==================== CONTACT INFORMATION ====================
    # Primary contact details (can be different from user account email)
    email = models.EmailField(
        verbose_name=_("Profile Email"),
        blank=True,
        null=True,
        help_text=_("Primary email for this profile (can be different from user account email)"),
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Phone Number"),
        help_text=_("Primary phone number for this profile"),
    )

    alternate_email = models.EmailField(
        verbose_name=_("Alternate Email"),
        blank=True,
        null=True,
        help_text=_("Alternate email address"),
    )

    alternate_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Alternate Phone"),
        help_text=_("Alternate phone number"),
    )

    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Primary Address"),
        help_text=_("Full physical address"),
    )

    country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Country"),
    )

    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("City"),
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Postal Code"),
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Location"),
        help_text=_("General location (e.g. City, Country)"),
    )

    # ==================== PRIVACY & VISIBILITY ====================
    public_profile = models.BooleanField(
        default=False,
        verbose_name=_("Public Profile"),
        help_text=_("Make your profile visible to everyone"),
    )

    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ("public", _("Public - Anyone can see your profile")),
            ("members", _("Members Only - Only registered members can see your profile")),
            ("private", _("Private - Only you can see your profile")),
        ],
        default="public",
        verbose_name=_("Profile Visibility"),
    )

    share_usage_data = models.BooleanField(
        default=True,
        verbose_name=_("Share Usage Data"),
        help_text=_("Help us improve by sharing anonymous usage data"),
    )

    allow_search_indexing = models.BooleanField(
        default=True,
        verbose_name=_("Allow Search Indexing"),
        help_text=_("Allow search engines to index your profile"),
    )

    show_online_status = models.BooleanField(
        default=True,
        verbose_name=_("Show Online Status"),
    )

    allow_contact = models.BooleanField(
        default=True,
        verbose_name=_("Allow Contact"),
        help_text=_("Allow other members to contact you"),
    )

    show_email = models.BooleanField(
        default=False,
        verbose_name=_("Show Email"),
        help_text=_("Show your email address on your public profile"),
    )

    # ==================== PROFESSIONAL INFORMATION ====================
    job_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Job Title"),
    )

    company = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Company"),
    )

    department = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Department"),
    )

    position = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Current Position"),
    )

    industry = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Industry"),
    )

    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Biography"),
        help_text=_("Brief professional biography"),
    )

    # ==================== SOCIAL & DIGITAL PRESENCE ====================
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Personal Website"),
    )

    linkedin_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("LinkedIn Profile"),
    )

    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("GitHub Profile"),
    )

    twitter_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Twitter/X Profile"),
    )

    facebook_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Facebook Profile"),
    )

    instagram_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Instagram Profile"),
    )

    # ==================== PROFILE TYPE & STATUS ====================
    class ProfileType(models.TextChoices):
        EMPLOYEE = "EMP", _("Employee")
        STUDENT = "STU", _("Student")
        CUSTOMER = "CUS", _("Customer")
        SUPPLIER_CONTACT = "SUP", _("Supplier Contact")
        PARTNER_CONTACT = "PRT", _("Partner Contact")
        CONTACT = "CON", _("Contact Person")
        GUEST = "GST", _("Guest")
        ADMINISTRATOR = "ADM", _("Administrator")
        OTHER = "OTH", _("Other")

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        INACTIVE = "INACTIVE", _("Inactive")
        SUSPENDED = "SUSPENDED", _("Suspended")
        PENDING = "PENDING", _("Pending Approval")
        INVITED = "INVITED", _("Invited")
        ARCHIVED = "ARCHIVED", _("Archived")

    profile_type = models.CharField(
        max_length=3,
        choices=ProfileType.choices,
        default=ProfileType.CONTACT,
        verbose_name=_("Profile Type"),
        help_text=_("Type of profile/role in the system"),
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status"),
    )

    # ==================== REGISTRATION FLAG ====================
    # IMPORTANT: is_registered indicates if profile has been registered/activated
    # False = profile exists but user hasn't registered yet, True = user has registered
    is_registered = models.BooleanField(
        default=False,
        verbose_name=_("Registered"),
        help_text=_(
            "Designates whether this profile has been registered/activated by a user. "
            "False = profile exists but user hasn't registered yet."
        ),
    )

    registration_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Registration Date"),
        help_text=_("Date when the profile was registered"),
    )

    # ==================== VERIFICATION FIELDS ====================
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name=_("Email Verified"),
        help_text=_("Indicates if the profile email has been verified."),
    )

    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Email Verified At"),
        help_text=_("Timestamp when profile email was verified."),
    )

    is_phone_verified = models.BooleanField(
        default=False,
        verbose_name=_("Phone Verified"),
        help_text=_("Indicates if the profile phone number has been verified."),
    )

    phone_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Phone Verified At"),
        help_text=_("Timestamp when profile phone was verified."),
    )

    # ==================== PREFERENCE FIELDS ====================
    language = models.CharField(
        max_length=10,
        default="en",
        choices=getattr(settings, "LANGUAGES", [("en", "English")]),
        verbose_name=_("Language"),
        help_text=_("Preferred language for this profile."),
    )

    timezone = models.CharField(
        max_length=50,
        default="UTC",
        verbose_name=_("Timezone"),
        help_text=_("Profile's preferred timezone."),
    )

    profile_completion = models.IntegerField(
        default=0,
        verbose_name=_("Profile Completion %"),
        help_text=_("Percentage of profile completion."),
    )

    email_notifications = models.BooleanField(
        _("Email Notifications"),
        default=True,
        help_text=_("Enable email notifications for this profile."),
    )

    newsletter_notifications = models.BooleanField(
        _("Newsletter Notifications"),
        default=True,
        help_text=_("Subscribe to newsletters for this profile."),
    )

    marketing_emails = models.BooleanField(
        _("Marketing Emails"),
        default=False,
        help_text=_("Receive marketing and promotional emails."),
    )

    # Detailed Notifications
    course_updates_notifications = models.BooleanField(
        default=True,
        verbose_name=_("Course Updates"),
        help_text=_("Notifications for course updates and announcements"),
    )

    instructor_messages_notifications = models.BooleanField(
        default=True,
        verbose_name=_("Instructor Messages"),
        help_text=_("Notifications for new messages from instructors"),
    )

    weekly_reports_notifications = models.BooleanField(
        default=True,
        verbose_name=_("Weekly Reports"),
        help_text=_("Receive weekly progress reports"),
    )

    assignment_notifications = models.BooleanField(
        default=True,
        verbose_name=_("Assignment Notifications"),
        help_text=_("Notifications for assignment graded or feedback"),
    )

    forum_activity_notifications = models.BooleanField(
        default=True,
        verbose_name=_("Forum Activity"),
        help_text=_("Notifications for forum mentions and replies"),
    )

    deadline_reminders_notifications = models.BooleanField(
        default=True,
        verbose_name=_("Deadline Reminders"),
        help_text=_("Reminders for upcoming deadlines"),
    )

    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ("instantly", _("Instantly")),
            ("daily", _("Daily Digest")),
            ("weekly", _("Weekly Newsletter")),
        ],
        default="instantly",
        verbose_name=_("Notification Frequency"),
    )

    # ==================== UI PREFERENCES ====================
    dark_mode = models.BooleanField(
        default=True,
        verbose_name=_("Dark Mode"),
    )

    high_contrast = models.BooleanField(
        default=False,
        verbose_name=_("High Contrast"),
    )

    reduce_animations = models.BooleanField(
        default=False,
        verbose_name=_("Reduce Animations"),
    )

    ui_density = models.CharField(
        max_length=20,
        choices=[
            ("compact", _("Compact")),
            ("comfortable", _("Comfortable")),
            ("spacious", _("Spacious")),
        ],
        default="comfortable",
        verbose_name=_("UI Density"),
    )

    date_format = models.CharField(
        max_length=20,
        default="DD/MM/YYYY",
        verbose_name=_("Date Format"),
    )

    time_format = models.CharField(
        max_length=10,
        choices=[
            ("12h", _("12-hour (AM/PM)")),
            ("24h", _("24-hour")),
        ],
        default="24h",
        verbose_name=_("Time Format"),
    )

    # ==================== BILLING & SUBSCRIPTION ====================
    subscription_plan = models.CharField(
        max_length=50,
        choices=[
            ("free", _("Free Plan")),
            ("pro", _("Pro Monthly")),
            ("enterprise", _("Enterprise")),
        ],
        default="free",
        verbose_name=_("Subscription Plan"),
    )

    billing_cycle = models.CharField(
        max_length=20,
        choices=[
            ("monthly", _("Monthly")),
            ("yearly", _("Yearly")),
        ],
        default="monthly",
        verbose_name=_("Billing Cycle"),
    )

    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("card", _("Credit/Debit Card")),
            ("paypal", _("PayPal")),
            ("stripe", _("Stripe")),
        ],
        blank=True,
        null=True,
        verbose_name=_("Payment Method"),
    )

    auto_renew = models.BooleanField(
        default=True,
        verbose_name=_("Auto Renew"),
    )

    billing_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Billing Name"),
    )

    billing_address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Billing Address"),
    )

    tax_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Tax ID"),
    )

    send_invoices = models.BooleanField(
        default=True,
        verbose_name=_("Send Invoices"),
    )

    paperless_billing = models.BooleanField(
        default=True,
        verbose_name=_("Paperless Billing"),
    )

    # ==================== ACTIVITY & USAGE ====================
    last_active = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Active"),
        help_text=_("Last time the profile was actively used"),
    )

    last_profile_update = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Profile Update"),
        help_text=_("Last time profile information was updated"),
    )

    login_count = models.IntegerField(
        default=0,
        verbose_name=_("Login Count"),
        help_text=_("Number of times the user has logged in"),
    )

    # ==================== MEDIA & CONTENT ====================
    profile_image = models.ImageField(
        upload_to="profiles/images/%Y/%m/%d/",
        null=True,
        blank=True,
        verbose_name=_("Profile Image"),
        help_text=_("Profile photo (recommended: 400x400px)"),
    )

    cover_image = models.ImageField(
        upload_to="profiles/covers/%Y/%m/%d/",
        null=True,
        blank=True,
        verbose_name=_("Cover Image"),
        help_text=_("Cover photo (recommended: 1500x500px)"),
    )

    profile_content = StreamField(
        ProfileStreamBlock,
        blank=True,
        verbose_name=_("Additional Profile Content"),
        help_text=_("Add social links, certifications, projects, and more"),
        use_json_field=True,
    )

    # ==================== SLUG FIELD ====================
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly version of the profile"),
    )

    # ==================== ADDITIONAL METADATA ====================
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Metadata"),
        help_text=_("Additional structured data for the profile"),
    )

    # ==================== MODEL CONFIGURATION ====================
    objects = models.Manager()

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ["-created_at", "full_name"]
        db_table = "profiles"
        managed = False
        app_label = "shared"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["email"]),
            models.Index(fields=["is_registered"]),
            models.Index(fields=["status"]),
            models.Index(fields=["profile_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["country", "city"]),
            models.Index(fields=["last_active"]),
            models.Index(fields=["profile_completion"]),
        ]
        permissions = [
            ("view_profile_stats", "Can view profile statistics"),
            ("export_profiles", "Can export profile data"),
            ("can_manage_profiles", "Can manage all profiles"),
            ("can_view_sensitive_data", "Can view sensitive profile data"),
            ("can_invite_profiles", "Can invite new profiles"),
            ("can_share_profiles", "Can share profile data"),
            ("can_impersonate_profile", "Can impersonate profile"),
        ]

    # ==================== SEARCH CONFIGURATION ====================
    search_fields = [
        index.SearchField("full_name", boost=2),
        index.SearchField("display_name", boost=1.8),
        index.SearchField("first_name", boost=1.5),
        index.SearchField("last_name", boost=1.5),
        index.AutocompleteField("email"),
        index.SearchField("phone_number"),
        index.SearchField("job_title", boost=1.2),
        index.SearchField("bio"),
        index.SearchField("company"),
        index.SearchField("department"),
        index.SearchField("address"),
        index.SearchField("city"),
        index.SearchField("country"),
        index.FilterField("is_registered"),
        index.FilterField("status"),
        index.FilterField("profile_type"),
    ]

    # ==================== PROPERTIES ====================
    @property
    def cache_key(self) -> str:
        """Get cache key for this profile."""
        return f"profile:{self.id}"

    @property
    def age(self):
        """Calculate age from birth date."""
        if not self.birth_date:
            return None
        today = timezone.now().date()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @property
    def is_complete(self):
        """Check if profile has minimum required information."""
        required_fields = [
            self.first_name,
            self.last_name,
            self.email or (self.user and self.user.email),
        ]
        return all(required_fields)

    @property
    def profile_completion_details(self) -> Dict[str, Any]:
        """Get detailed breakdown of profile completion."""
        fields_to_check = [
            ("first_name", 10),
            ("last_name", 10),
            ("email", 10),
            ("profile_image", 15),
            ("job_title", 10),
            ("company", 10),
            ("bio", 10),
            ("phone_number", 10),
            ("address", 5),
            ("birth_date", 5),
            ("gender", 5),
        ]

        completed = 0
        for field_name, weight in fields_to_check:
            if getattr(self, field_name, None):
                completed += weight

        # Check if user email can be used as fallback
        if not self.email and self.user and self.user.email:
            completed += 10

        return {
            "percentage": min(completed, 100),
            "breakdown": fields_to_check,
        }

    @property
    def social_links(self):
        """Extract social links from StreamField."""
        links = []
        for block in self.profile_content:
            if block.block_type == "social_link":
                links.append(block.value)
        return links

    @property
    def certifications(self):
        """Extract certifications from StreamField."""
        certs = []
        for block in self.profile_content:
            if block.block_type == "certification":
                certs.append(block.value)
        return certs

    @property
    def projects(self):
        """Extract projects from StreamField."""
        projects = []
        for block in self.profile_content:
            if block.block_type == "project":
                projects.append(block.value)
        return projects

    @property
    def notification_channels(self):
        """Get available notification channels based on preferences and verified methods."""
        channels = []

        if self.email_notifications and (self.email or (self.user and self.user.email)):
            if self.is_email_verified or (self.user and self.user.is_email_verified):
                channels.append("email")

        if self.newsletter_notifications and (self.email or (self.user and self.user.email)):
            channels.append("newsletter")

        if self.marketing_emails and (self.email or (self.user and self.user.email)):
            channels.append("marketing")

        return channels

    @property
    def primary_email(self):
        """Get primary email, falling back to user email."""
        return self.email or (self.user.email if self.user else None)

    @property
    def primary_name(self):
        """Get primary name for display."""
        if self.display_name:
            return self.display_name
        elif self.full_name:
            return self.full_name
        elif self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        elif self.user:
            return self.user.get_full_name() or self.user.username
        return None

    # ==================== SKILLS & GAMIFICATION ====================
    tags = TaggableManager(
        through=TaggedPerson,
        blank=True,
        verbose_name=_("Tags/Skills"),
        help_text=_("Skills and tags associated with this profile"),
    )

    reputation_score = models.IntegerField(
        default=0,
        verbose_name=_("Reputation Score"),
        help_text=_("Gamification score based on activity"),
    )

    level = models.IntegerField(
        default=1,
        verbose_name=_("Level"),
        help_text=_("User level based on reputation"),
    )

    languages_spoken = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Languages Spoken"),
        help_text=_("List of languages spoken (ISO codes)"),
    )

    # ==================== AVAILABILITY & ONBOARDING ====================
    is_available_for_hire = models.BooleanField(
        default=False,
        verbose_name=_("Available for Hire"),
    )

    is_available_for_mentoring = models.BooleanField(
        default=False,
        verbose_name=_("Available for Mentoring"),
    )

    onboarding_status = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Onboarding Status"),
        help_text=_("Tracking of onboarding steps completed"),
    )

    # ==================== DATA PRIVACY ====================
    data_export_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Data Export Requested At"),
    )

    account_deletion_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Account Deletion Requested At"),
    )

    # ==================== METHODS ====================

    def __str__(self):
        name = self.primary_name
        if name:
            return f"{name} ({self.email or (self.user.email if self.user else 'No email')})"
        return self.email or (self.user.email if self.user else str(self.id))

    def get_absolute_url(self):
        if self.slug:
            return reverse("profile-detail-slug", kwargs={"slug": self.slug})
        return reverse("profile-detail", kwargs={"pk": self.pk})

    def get_share_url(self):
        """Get shareable URL for this profile."""
        # Implementation depends on your sharing service
        if self.slug:
            return f"{settings.SITE_URL}/profile/{self.slug}/"
        return f"{settings.SITE_URL}/profile/{self.id}/"

    def update_last_active(self):
        """Update last active timestamp."""
        self.last_active = timezone.now()
        self.save(update_fields=["last_active"])

    def update_profile_usage(self):
        """Update profile usage statistics."""
        self.login_count += 1
        self.last_active = timezone.now()
        self.save(update_fields=["login_count", "last_active"])

    def verify_email(self):
        """Mark profile email as verified."""
        self.is_email_verified = True
        self.email_verified_at = timezone.now()
        self.save(update_fields=["is_email_verified", "email_verified_at"])

    def verify_phone(self):
        """Mark profile phone as verified."""
        self.is_phone_verified = True
        self.phone_verified_at = timezone.now()
        self.save(update_fields=["is_phone_verified", "phone_verified_at"])

    def register(self, user=None):
        """
        Register this profile with a user account.
        Sets is_registered=True and status=ACTIVE.
        """
        if user:
            self.user = user
            self.status = self.Status.ACTIVE
            self.is_registered = True
            self.registration_date = timezone.now()

            # Sync basic information if not set
            if not self.email and user.email:
                self.email = user.email
            if not self.first_name and user.first_name:
                self.first_name = user.first_name
            if not self.last_name and user.last_name:
                self.last_name = user.last_name

            self.save(
                update_fields=[
                    "user",
                    "status",
                    "is_registered",
                    "registration_date",
                    "email",
                    "first_name",
                    "last_name",
                ]
            )
        else:
            self.status = self.Status.ACTIVE
            self.is_registered = True
            self.registration_date = timezone.now()
            self.save(update_fields=["status", "is_registered", "registration_date"])

    def invite(self, email: str, first_name: str = "", last_name: str = ""):
        """
        Create an invitation for a new profile.
        """
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.is_registered = False
        self.status = self.Status.INVITED
        self.save()
        # Send invitation email logic here
        return self

    def activate(self):
        """Activate the profile."""
        self.status = self.Status.ACTIVE
        self.save(update_fields=["status"])

    def deactivate(self):
        """Deactivate the profile."""
        self.status = self.Status.INACTIVE
        self.save(update_fields=["status"])

    def archive(self):
        """Archive the profile."""
        self.status = self.Status.ARCHIVED
        self.save(update_fields=["status"])

    def sync_with_user(self):
        """Sync profile data with associated user account."""
        if not self.user:
            return

        # Sync basic information
        if not self.email and self.user.email:
            self.email = self.user.email
        if not self.first_name and self.user.first_name:
            self.first_name = self.user.first_name
        if not self.last_name and self.user.last_name:
            self.last_name = self.user.last_name

        # Sync verification status
        if self.user.is_email_verified and not self.is_email_verified:
            self.is_email_verified = True
            self.email_verified_at = self.user.email_verified_at or timezone.now()

        self.save()

    # ==================== VALIDATION ====================
    def clean(self):
        """Perform validation."""
        super().clean()

        # Validate phone formats
        if self.phone_number:
            try:
                PHONE_VALIDATOR(self.phone_number)
            except ValidationError:
                raise ValidationError({"phone_number": _("Please enter a valid phone number.")})

        # Validate email format if provided
        if self.email:
            try:
                EMAIL_VALIDATOR(self.email)
            except ValidationError:
                raise ValidationError({"email": _("Please enter a valid email address.")})

        if self.alternate_email:
            try:
                EMAIL_VALIDATOR(self.alternate_email)
            except ValidationError:
                raise ValidationError({"alternate_email": _("Please enter a valid email address.")})

        # Validate birth date is not in future
        if self.birth_date and self.birth_date > timezone.now().date():
            raise ValidationError({"birth_date": _("Birth date cannot be in the future.")})

        # Ensure at least one email is provided
        if not self.email and not (self.user and self.user.email):
            raise ValidationError(_("Either profile email or user email must be provided."))

    # ==================== SAVE LOGIC ====================
    def save(self, *args, **kwargs):
        """Custom save logic."""
        # Normalize emails to lowercase
        if self.email:
            self.email = self.email.lower().strip()
        if self.alternate_email:
            self.alternate_email = self.alternate_email.lower().strip()

        # Normalize URLs
        urls_to_normalize = [
            "website",
            "linkedin_url",
            "github_url",
            "twitter_url",
            "facebook_url",
            "instagram_url",
        ]

        for url_field in urls_to_normalize:
            url = getattr(self, url_field, None)
            if url and not url.startswith(("http://", "https://")):
                setattr(self, url_field, f"https://{url}")

        # Auto-generate full name if not set
        if not self.full_name and self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}".strip()
        elif not self.full_name and self.first_name:
            self.full_name = self.first_name
        elif not self.full_name and self.last_name:
            self.full_name = self.last_name

        # Auto-generate display name if not set
        if not self.display_name and self.full_name:
            self.display_name = self.full_name

        # Auto-generate slug if not set
        if not self.slug and self.display_name:
            base_slug = slugify(self.display_name)
            slug = base_slug
            counter = 1
            while self.__class__.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Update profile completion percentage
        completion_details = self.profile_completion_details
        self.profile_completion = completion_details["percentage"]

        # Update last profile update timestamp
        if self.pk:
            self.last_profile_update = timezone.now()

        super().save(*args, **kwargs)

    # ==================== CLASS METHODS ====================

    @classmethod
    def create_for_user(cls, user, **kwargs):
        """Create a profile for an existing user."""
        profile = cls(user=user, **kwargs)

        # Set default values from user
        if not profile.email and user.email:
            profile.email = user.email
        if not profile.first_name and user.first_name:
            profile.first_name = user.first_name
        if not profile.last_name and user.last_name:
            profile.last_name = user.last_name

        # Auto-register if user already exists
        if user.pk:
            profile.is_registered = True
            profile.status = cls.Status.ACTIVE
            profile.registration_date = timezone.now()

        profile.save()
        return profile

    @classmethod
    def create_invitation(cls, email, first_name="", last_name="", **kwargs):
        """Create a profile invitation."""
        profile = cls(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_registered=False,
            status=cls.Status.INVITED,
            **kwargs,
        )
        profile.save()
        return profile

    # ==================== WAGTAIL PANEL CONFIGURATION ====================

    # Basic Information Panels
    basic_info_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("first_name"),
                        FieldPanel("last_name"),
                    ]
                ),
                FieldPanel("display_name"),
                FieldPanel("full_name", read_only=True),
                FieldPanel("email"),
                FieldPanel("alternate_email"),
                FieldPanel("phone_number"),
                FieldPanel("alternate_phone"),
                FieldPanel("location"),
                HelpPanel(content=_("Enter the basic contact information.")),
            ],
            heading=_("Basic Information"),
        ),
    ]

    # Personal Information Panels
    personal_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("birth_date"),
                        FieldPanel("gender"),
                    ]
                ),
                FieldPanel("address"),
                FieldRowPanel(
                    [
                        FieldPanel("city"),
                        FieldPanel("country"),
                        FieldPanel("postal_code"),
                    ]
                ),
                FieldPanel("languages_spoken"),
                HelpPanel(content=_("Personal and location information.")),
            ],
            heading=_("Personal Details"),
        ),
    ]

    # Professional Information Panels
    professional_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("job_title"),
                        FieldPanel("company"),
                    ]
                ),
                FieldPanel("department"),
                FieldPanel("position"),
                FieldPanel("industry"),
                FieldPanel("bio"),
                FieldPanel("tags"),
                FieldRowPanel(
                    [
                        FieldPanel("is_available_for_hire"),
                        FieldPanel("is_available_for_mentoring"),
                    ]
                ),
                HelpPanel(content=_("Professional information and biography.")),
            ],
            heading=_("Professional Information"),
        ),
    ]

    # Social & Media Panels
    social_media_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("website"),
                        FieldPanel("linkedin_url"),
                        FieldPanel("github_url"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("twitter_url"),
                        FieldPanel("facebook_url"),
                        FieldPanel("instagram_url"),
                    ]
                ),
                FieldPanel("profile_image"),
                FieldPanel("cover_image"),
                FieldPanel("profile_content"),
                HelpPanel(content=_("Social media profiles and additional content.")),
            ],
            heading=_("Social & Media"),
        ),
    ]

    # Settings & Status Panels
    settings_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("profile_type"),
                        FieldPanel("status"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("is_registered"),
                        FieldPanel("registration_date"),
                        FieldPanel("is_email_verified"),
                        FieldPanel("is_phone_verified"),
                    ]
                ),
                FieldPanel("language"),
                FieldPanel("timezone"),
                FieldPanel("profile_completion", read_only=True),
                FieldPanel("onboarding_status"),
                HelpPanel(content=_("Profile settings and status.")),
            ],
            heading=_("Status & Core Settings"),
        ),
    ]

    # Privacy Panels
    privacy_panels = [
        MultiFieldPanel(
            [
                FieldPanel("public_profile"),
                FieldPanel("profile_visibility"),
                FieldPanel("share_usage_data"),
                FieldPanel("allow_search_indexing"),
                FieldPanel("show_online_status"),
                FieldPanel("allow_contact"),
                FieldPanel("show_email"),
                FieldPanel("data_export_requested_at", read_only=True),
                FieldPanel("account_deletion_requested_at", read_only=True),
            ],
            heading=_("Privacy & Visibility"),
        ),
    ]

    # Notification Panels
    notification_panels = [
        MultiFieldPanel(
            [
                FieldPanel("email_notifications"),
                FieldPanel("newsletter_notifications"),
                FieldPanel("marketing_emails"),
                FieldPanel("course_updates_notifications"),
                FieldPanel("instructor_messages_notifications"),
                FieldPanel("weekly_reports_notifications"),
                FieldPanel("assignment_notifications"),
                FieldPanel("forum_activity_notifications"),
                FieldPanel("deadline_reminders_notifications"),
                FieldPanel("notification_frequency"),
            ],
            heading=_("Notifications"),
        ),
    ]

    # Preference Panels
    preference_panels = [
        MultiFieldPanel(
            [
                FieldPanel("dark_mode"),
                FieldPanel("high_contrast"),
                FieldPanel("reduce_animations"),
                FieldPanel("ui_density"),
                FieldPanel("date_format"),
                FieldPanel("time_format"),
            ],
            heading=_("UI Preferences"),
        ),
    ]

    # Billing Panels
    billing_panels = [
        MultiFieldPanel(
            [
                FieldPanel("subscription_plan"),
                FieldPanel("billing_cycle"),
                FieldPanel("payment_method"),
                FieldPanel("auto_renew"),
                FieldPanel("billing_name"),
                FieldPanel("billing_address"),
                FieldPanel("tax_id"),
                FieldPanel("send_invoices"),
                FieldPanel("paperless_billing"),
            ],
            heading=_("Billing & Subscription"),
        ),
    ]

    # Activity & Relationships Panels
    activity_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("last_active", read_only=True),
                        FieldPanel("last_profile_update", read_only=True),
                        FieldPanel("login_count", read_only=True),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("reputation_score", read_only=True),
                        FieldPanel("level", read_only=True),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("user"),
                        FieldPanel("linked_profile"),
                    ]
                ),
                HelpPanel(content=_("Activity tracking and relationships.")),
            ],
            heading=_("Activity & Relationships"),
        ),
    ]

    # Tabbed Interface Configuration
    @classmethod
    def get_profile_edit_handler(cls, user=None):
        """Return a dynamic tabbed Wagtail edit interface."""

        is_admin = False
        if user:
            is_admin = (
                user.is_superuser
                or user.groups.filter(name__in=["Admin", "Administrators", "Editors"]).exists()
            )

        # Start with always-visible tabs
        tabs = [
            ObjectList(cls.basic_info_panels, heading=_("Basic Info")),
            ObjectList(cls.personal_panels, heading=_("Personal")),
            ObjectList(cls.professional_panels, heading=_("Professional")),
        ]

        # Add social tab
        tabs.append(ObjectList(cls.social_media_panels, heading=_("Social & Media")))

        # Add settings tabs
        tabs.extend(
            [
                ObjectList(cls.privacy_panels, heading=_("Privacy")),
                ObjectList(cls.notification_panels, heading=_("Notifications")),
                ObjectList(cls.preference_panels, heading=_("Preferences")),
                ObjectList(cls.billing_panels, heading=_("Billing")),
            ]
        )

        # Add admin-only tabs
        if is_admin:
            tabs.extend(
                [
                    ObjectList(cls.settings_panels, heading=_("System Status")),
                    ObjectList(cls.activity_panels, heading=_("Activity")),
                ]
            )

        return TabbedInterface(tabs)

    # Edit handler property
    @classmethod
    def get_edit_handler(cls, request=None):
        """Return the proper Wagtail edit handler for this model."""
        user = getattr(request, "user", None)
        return cls.get_profile_edit_handler(user)

    # Default edit handler
    edit_handler = TabbedInterface(
        [
            ObjectList(basic_info_panels, heading=_("Basic Info")),
            ObjectList(personal_panels, heading=_("Personal")),
            ObjectList(professional_panels, heading=_("Professional")),
            ObjectList(social_media_panels, heading=_("Social & Media")),
            ObjectList(privacy_panels, heading=_("Privacy")),
            ObjectList(notification_panels, heading=_("Notifications")),
            ObjectList(preference_panels, heading=_("Preferences")),
            ObjectList(billing_panels, heading=_("Billing")),
            ObjectList(settings_panels, heading=_("System Status")),
            ObjectList(activity_panels, heading=_("Activity")),
        ]
    )
