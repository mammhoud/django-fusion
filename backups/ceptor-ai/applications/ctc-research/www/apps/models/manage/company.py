from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_fusion.core.models import BaseModel as DefaultBase
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.search import index

from www.apps.models.manage.service import Service


# -------------------------------------------------------------------
# COMPANY MODEL
# -------------------------------------------------------------------
# @register_snippet
class Organization(DefaultBase, ClusterableModel):
    """
    Enhanced Company model supporting clients, suppliers, partners, and educational institutions.
    Unified model replacing separate Company and Partner models.
    """

    class CompanyType(models.TextChoices):
        CLIENT = "client", _("Client")
        SUPPLIER = "supplier", _("Supplier")
        PARTNER = "partner", _("Partner")
        VENDOR = "vendor", _("Vendor")
        COMPETITOR = "competitor", _("Competitor")
        EDUCATIONAL = "educational", _("Educational Institution")
        ACADEMIC = "academic", _("Academic Institution")
        INTERNAL = "internal", _("Internal Organization")
        OTHER = "other", _("Other")

    class CompanySize(models.TextChoices):
        MICRO = "micro", _("Micro (1-10)")
        SMALL = "small", _("Small (11-50)")
        MEDIUM = "medium", _("Medium (51-200)")
        LARGE = "large", _("Large (201-1000)")
        ENTERPRISE = "enterprise", _("Enterprise (1000+)")

    class Industry(models.TextChoices):
        TECHNOLOGY = "technology", _("Technology")
        HEALTHCARE = "healthcare", _("Healthcare")
        EDUCATION = "education", _("Education")
        FINANCE = "finance", _("Finance & Banking")
        RETAIL = "retail", _("Retail & E-commerce")
        MANUFACTURING = "manufacturing", _("Manufacturing")
        CONSULTING = "consulting", _("Consulting")
        NON_PROFIT = "non_profit", _("Non-Profit")
        GOVERNMENT = "government", _("Government")
        OTHER = "other", _("Other")

    # Basic Information
    name = models.CharField(
        max_length=200,
        verbose_name=_("Company Name"),
        help_text=_("Official display name of the company")
    )

    legal_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Legal Name"),
        help_text=_("Official legal name if different from display name")
    )

    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly version of the company name")
    )

    company_type = models.CharField(
        max_length=20,
        choices=CompanyType.choices,
        default=CompanyType.CLIENT,
        verbose_name=_("Company Type"),
        help_text=_("Primary classification of the company relationship")
    )

    # Contact Information
    website = models.URLField(
        blank=True,
        verbose_name=_("Website"),
        help_text=_("Primary company website URL")
    )

    email = models.EmailField(
        blank=True,
        verbose_name=_("General Email"),
        help_text=_("General contact email address")
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Phone Number"),
        help_text=_("Main company phone number")
    )

    address = models.TextField(
        blank=True,
        verbose_name=_("Address"),
        help_text=_("Primary business address")
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Country"),
        help_text=_("Company headquarters country")
    )

    timezone = models.CharField(
        max_length=50,
        blank=True,
        default="UTC",
        verbose_name=_("Timezone"),
        help_text=_("Primary business timezone")
    )

    # Business Details
    industry = models.CharField(
        max_length=20,
        choices=Industry.choices,
        default=Industry.OTHER,
        verbose_name=_("Industry"),
        help_text=_("Primary industry sector")
    )

    company_size = models.CharField(
        max_length=20,
        choices=CompanySize.choices,
        blank=True,
        verbose_name=_("Company Size"),
        help_text=_("Approximate number of employees")
    )

    employee_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Employee Count"),
        help_text=_("Exact number of employees (if known)")
    )

    founded_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Founded Year"),
        help_text=_("Year the company was founded")
    )

    tax_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Tax ID/VAT Number"),
        help_text=_("Business tax identification number")
    )

    registration_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Registration Number"),
        help_text=_("Company registration or business number")
    )

    # Visual Identity
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Company Logo"),
        help_text=_("Official company logo")
    )

    brand_color = models.CharField(
        max_length=7,
        blank=True,
        verbose_name=_("Brand Color"),
        help_text=_("Primary brand color in hex format")
    )

    # Partner & Display Settings
    is_displayed = models.BooleanField(
        default=False,
        verbose_name=_("Display Publicly"),
        help_text=_("Display this company in public directories and partner pages")
    )

    partnership_level = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("strategic", _("Strategic Partner")),
            ("premium", _("Premium Partner")),
            ("standard", _("Standard Partner")),
            ("affiliate", _("Affiliate Partner")),
        ],
        verbose_name=_("Partnership Level"),
        help_text=_("Level of partnership (for partner companies only)")
    )

    partnership_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Partnership Start Date"),
        help_text=_("When the partnership began")
    )

    # Educational Institution Specific
    is_educational = models.BooleanField(
        default=False,
        verbose_name=_("Educational Institution"),
        help_text=_("This company is an educational institution")
    )

    accreditation = models.TextField(
        blank=True,
        verbose_name=_("Accreditations"),
        help_text=_("Educational accreditations and certifications")
    )

    institution_type = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ("university", _("University")),
            ("college", _("College")),
            ("school", _("School")),
            ("training", _("Training Center")),
            ("online", _("Online Institution")),
        ],
        verbose_name=_("Institution Type"),
        help_text=_("Type of educational institution")
    )

    # Financial Information
    annual_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Annual Revenue"),
        help_text=_("Annual revenue in local currency")
    )

    currency = models.CharField(
        max_length=3,
        default="USD",
        verbose_name=_("Currency"),
        help_text=_("Primary currency for financial data")
    )

    # Relationship Management
    parent_company = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subsidiaries',
        verbose_name=_("Parent Company"),
        help_text=_("Parent or holding company")
    )

    relationship_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_companies",
        verbose_name=_("Relationship Manager"),
        help_text=_("Primary contact person within our organization")
    )

    # Status & Settings
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Company is currently active and engaged")
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Verified"),
        help_text=_("Company information has been verified")
    )

    notes = models.TextField(
        blank=True,
        verbose_name=_("Internal Notes"),
        help_text=_("Additional internal notes about the company")
    )

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        db_table = "companies"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["company_type"]),
            models.Index(fields=["industry"]),
            models.Index(fields=["is_displayed"]),
            models.Index(fields=["is_educational"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["parent_company"]),
        ]

    search_fields = [
        index.SearchField("name", boost=2),
        index.SearchField("legal_name", boost=2),
        index.SearchField("website"),
        index.SearchField("email"),
        index.SearchField("tax_id"),
        index.SearchField("notes"),
        index.FilterField("company_type"),
        index.FilterField("industry"),
        index.FilterField("is_displayed"),
        index.FilterField("is_educational"),
        index.FilterField("is_active"),
        # index.RelatedFields('tags', [
        #     index.SearchField('name'),
        # ]),
    ]
    # ------------------------------------------------------------
    # COMPANY MODEL ADMIN PANELS
    # ------------------------------------------------------------
    content_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("name"),
                FieldPanel("legal_name"),
            ]),
            FieldPanel("slug"),
            FieldRowPanel([
                FieldPanel("company_type"),
                FieldPanel("industry"),
            ]),
        ], heading=_("Basic Information")),

        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("website"),
                FieldPanel("email"),
            ]),
            FieldRowPanel([
                FieldPanel("phone"),
                FieldPanel("country"),
            ]),
            FieldPanel("address"),
            FieldPanel("timezone"),
        ], heading=_("Contact Information")),

        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("logo"),
                FieldPanel("brand_color"),
            ]),
        ], heading=_("Visual Identity")),
    ]

    business_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("company_size"),
                FieldPanel("employee_count"),
            ]),
            FieldRowPanel([
                FieldPanel("founded_year"),
                FieldPanel("tax_id"),
                FieldPanel("registration_number"),
            ]),
            FieldRowPanel([
                FieldPanel("annual_revenue"),
                FieldPanel("currency"),
            ]),
        ], heading=_("Business Details")),

        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("parent_company"),
                FieldPanel("relationship_manager"),
            ]),
        ], heading=_("Relationship Management")),
    ]

    settings_panels = [
        # MultiFieldPanel([
        #     # FieldPanel("tags"),
        # ], heading=_("Tagging & Categorization")),

        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("is_displayed"),
                FieldPanel("partnership_level"),
                FieldPanel("partnership_start_date"),
            ]),
        ], heading=_("Partner Settings"), classname="collapsible"),

        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("is_educational"),
                FieldPanel("institution_type"),
            ]),
            FieldPanel("accreditation"),
        ], heading=_("Educational Institution"), classname="collapsible"),

        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("is_active"),
                FieldPanel("is_verified"),
            ]),
            FieldPanel("notes"),
        ], heading=_("Status & Settings")),
    ]


    # ------------------------------------------------------------
    # TABBED EDIT INTERFACE
    # ------------------------------------------------------------
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading=_("Overview")),
        ObjectList(business_panels, heading=_("Business")),
        ObjectList(settings_panels, heading=_("Settings")),
    ])

    # ======================
    # PROPERTIES
    # ======================

    @property
    def display_name(self):
        """Get appropriate display name."""
        return self.legal_name or self.name

    @property
    def is_partner(self):
        """Check if company is a partner."""
        return self.company_type == self.CompanyType.PARTNER

    @property
    def is_client(self):
        """Check if company is a client."""
        return self.company_type == self.CompanyType.CLIENT

    @property
    def is_supplier(self):
        """Check if company is a supplier."""
        return self.company_type == self.CompanyType.SUPPLIER

    @property
    def partnership_duration(self):
        """Calculate partnership duration in years."""
        if self.partnership_start_date:
            return (timezone.now().date() - self.partnership_start_date).days // 365
        return 0

    @property
    def department_count(self):
        """Get number of departments."""
        return self.departments.count()

    @property
    def employee_count_display(self):
        """Get formatted employee count."""
        if self.employee_count:
            return f"{self.employee_count:,}"
        return self.get_company_size_display() if self.company_size else _("Unknown")

    @property
    def primary_contact(self):
        """Get primary contact person."""
        return self.contacts.filter(is_primary=True).first()

    # ======================
    # METHODS
    # ======================

    def clean(self):
        """Validate company data."""
        super().clean()

        # Validate partnership fields
        if self.company_type != self.CompanyType.PARTNER:
            if self.partnership_level:
                raise ValidationError({
                    'partnership_level': _('Partnership level is only applicable to partner companies.')
                })
            if self.partnership_start_date:
                raise ValidationError({
                    'partnership_start_date': _('Partnership start date is only applicable to partner companies.')
                })

        # Validate educational fields
        if not self.is_educational and self.institution_type:
            raise ValidationError({
                'institution_type': _('Institution type is only applicable to educational institutions.')
            })

        # Validate parent company
        if self.parent_company and self.parent_company == self:
            raise ValidationError({
                'parent_company': _('A company cannot be its own parent.')
            })

    def save(self, *args, **kwargs):
        """Auto-generate slug and handle business logic."""
        if not self.slug:
            self.slug = slugify(self.name)

        # Auto-set educational flag based on company type
        if self.company_type in [self.CompanyType.EDUCATIONAL, self.CompanyType.ACADEMIC]:
            self.is_educational = True

        # Auto-set code prefix
        self.code_prefix = "COM"

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get URL for company detail page."""
        return reverse("company-detail", kwargs={"slug": self.slug})

    def get_departments_by_function(self):
        """Get departments grouped by function."""
        from django.db.models import Count
        return self.departments.values('function').annotate(
            count=Count('id')
        ).order_by('-count')

    def get_services(self):
        """Get all services offered by company departments."""
        from django.db.models import Q
        return Service.objects.filter(
            Q(owner_department__company=self) |
            Q(supporting_departments__company=self)
        ).distinct()

    @classmethod
    def get_partners(cls):
        """Get all partner companies."""
        return cls.objects.filter(
            company_type=cls.CompanyType.PARTNER,
            is_displayed=True,
            is_active=True
        )

    @classmethod
    def get_clients(cls):
        """Get all client companies."""
        return cls.objects.filter(
            company_type=cls.CompanyType.CLIENT,
            is_active=True
        )

    @classmethod
    def get_suppliers(cls):
        """Get all supplier companies."""
        return cls.objects.filter(
            company_type=cls.CompanyType.SUPPLIER,
            is_active=True
        )

    @classmethod
    def get_educational_institutions(cls):
        """Get all educational institutions."""
        return cls.objects.filter(
            is_educational=True,
            is_active=True
        )

    def __str__(self):
        return f"{self.name} ({self.get_company_type_display()})"


# -------------------------------------------------------------------
# DEPARTMENT MODEL
# -------------------------------------------------------------------
#@register_snippet
class Department(DefaultBase, ClusterableModel):
    """
    Enhanced Department model within a company with service relationships and team management.
    """

    class DepartmentFunction(models.TextChoices):
        EXECUTIVE = "executive", _("Executive")
        SALES = "sales", _("Sales")
        MARKETING = "marketing", _("Marketing")
        FINANCE = "finance", _("Finance")
        HR = "hr", _("Human Resources")
        IT = "it", _("Information Technology")
        OPERATIONS = "operations", _("Operations")
        PRODUCT = "product", _("Product Development")
        CUSTOMER_SERVICE = "customer_service", _("Customer Service")
        R_D = "r_d", _("Research & Development")
        LEGAL = "legal", _("Legal")
        OTHER = "other", _("Other")

    # Basic Information
    name = models.CharField(
        max_length=100,
        verbose_name=_("Department Name"),
        help_text=_("Official name of the department")
    )

    code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Department Code"),
        help_text=_("Internal department code or abbreviation")
    )

    slug = models.SlugField(
        max_length=100,
        blank=True,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly version of the department name")
    )

    # Organizational Structure
    company = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="departments",
        verbose_name=_("Company"),
        help_text=_("Parent company organization")
    )

    parent_department = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_departments',
        verbose_name=_("Parent Department"),
        help_text=_("Parent department for hierarchical organization")
    )

    function = models.CharField(
        max_length=20,
        choices=DepartmentFunction.choices,
        default=DepartmentFunction.OTHER,
        verbose_name=_("Department Function"),
        help_text=_("Primary business function of the department")
    )

    # Leadership
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"type": "EMP", "is_active": True},
        related_name="managed_departments",
        verbose_name=_("Department Manager"),
        help_text=_("Primary manager responsible for the department")
    )

    deputy_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"type": "EMP", "is_active": True},
        related_name="deputy_managed_departments",
        verbose_name=_("Deputy Manager"),
        help_text=_("Secondary manager supporting the department head")
    )

    # Financial Information
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Annual Budget"),
        help_text=_("Annual operating budget for the department")
    )

    budget_year = models.PositiveIntegerField(
        default=timezone.now().year,
        verbose_name=_("Budget Year"),
        help_text=_("Year for which the budget is allocated")
    )

    # Services and Teams
    services = models.ManyToManyField(
        "handlers.Service",
        related_name="departments",
        blank=True,
        verbose_name=_("Department Services"),
        help_text=_("Services provided or managed by this department")
    )


    # Department Details
    mission = models.TextField(
        blank=True,
        verbose_name=_("Department Mission"),
        help_text=_("Mission statement and primary purpose")
    )

    objectives = models.TextField(
        blank=True,
        verbose_name=_("Key Objectives"),
        help_text=_("Main objectives and goals for the department")
    )

    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Location"),
        help_text=_("Primary physical location of the department")
    )

    color = models.CharField(
        max_length=7,
        blank=True,
        default="#6B7280",
        verbose_name=_("Department Color"),
        help_text=_("Color for visual identification of the department")
    )

    # Analytics
    employee_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Employee Count"),
        help_text=_("Number of employees in this department")
    )

    team_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Team Count"),
        help_text=_("Number of teams in this department")
    )

    service_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Service Count"),
        help_text=_("Number of services managed by this department")
    )

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        db_table = "departments"
        ordering = ["company", "function", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_department_name_per_company"
            )
        ]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["company"]),
            models.Index(fields=["function"]),
            models.Index(fields=["parent_department"]),
        ]

    search_fields = [
        index.SearchField("name", boost=2),
        index.SearchField("code", boost=2),
        index.SearchField("mission"),
        index.SearchField("objectives"),
        index.FilterField("company"),
        index.FilterField("function"),
        index.FilterField("parent_department"),
        index.RelatedFields('services', [
            index.SearchField('name'),
        ]),
    ]

    panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("name"),
                FieldPanel("code"),
            ]),
            FieldPanel("slug"),
            FieldRowPanel([
                FieldPanel("company"),
                FieldPanel("parent_department"),
            ]),
            FieldPanel("function"),
        ], heading=_("Basic Information")),

        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("manager"),
                FieldPanel("deputy_manager"),
            ]),
        ], heading=_("Leadership")),

        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("budget"),
                FieldPanel("budget_year"),
            ]),
        ], heading=_("Financial Information")),

        MultiFieldPanel([
            FieldPanel("mission"),
            FieldPanel("objectives"),
            FieldPanel("location"),
            FieldPanel("color"),
        ], heading=_("Department Details")),

        MultiFieldPanel([
            FieldPanel("services"),
            # FieldPanel("teams"),
        ], heading=_("Services & Teams")),

        # MultiFieldPanel([
        #     # FieldPanel("tags"),
        # ], heading=_("Tagging & Categorization")),

        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("employee_count", read_only=True),
                FieldPanel("team_count", read_only=True),
                FieldPanel("service_count", read_only=True),
            ]),
        ], heading=_("Analytics"), classname="collapsible collapsed"),
    ]

    # ======================
    # PROPERTIES
    # ======================

    @property
    def full_path(self):
        """Get full department path including parent departments."""
        path = [self.name]
        current = self.parent_department
        while current:
            path.insert(0, current.name)
            current = current.parent_department
        path.insert(0, self.company.name)
        return " > ".join(path)

    @property
    def active_teams(self):
        """Get active teams in this department."""
        return self.teams.filter(is_active=True)

    @property
    def active_services(self):
        """Get active services provided by this department."""
        return self.services.filter(is_active=True)

    @property
    def budget_utilization(self):
        """Calculate budget utilization percentage."""
        # This would integrate with actual spending data
        return 0  # Placeholder

    @property
    def is_leaf_department(self):
        """Check if department has no sub-departments."""
        return not self.sub_departments.exists()

    # ======================
    # METHODS
    # ======================

    def clean(self):
        """Validate department data."""
        super().clean()

        # Prevent circular references
        if self.parent_department and self.parent_department == self:
            raise ValidationError({
                'parent_department': _('A department cannot be its own parent.')
            })

        # Check for circular hierarchy
        if self.parent_department:
            current = self.parent_department
            while current:
                if current == self:
                    raise ValidationError({
                        'parent_department': _('Circular department hierarchy detected.')
                    })
                current = current.parent_department

        # Validate company consistency
        if self.parent_department and self.parent_department.company != self.company:
            raise ValidationError({
                'parent_department': _('Parent department must belong to the same company.')
            })

    def save(self, *args, **kwargs):
        """Auto-update counts and handle department logic."""
        # Auto-set code prefix
        self.code_prefix = "DEP"

        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(f"{self.company.slug}-{self.name}")

        # Update counts
        self.employee_count = self.get_employee_count()
        self.team_count = self.teams.count()
        self.service_count = self.services.count()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get URL for department detail page."""
        return reverse("department-detail", kwargs={"slug": self.slug})

    def get_employee_count(self):
        """Calculate actual employee count from team memberships."""
        from plugins.accounts.models import TeamMembership

        # Count unique active employees across all department teams
        return TeamMembership.objects.filter(
            team__in=self.teams.all(),
            status=TeamMembership.MembershipStatus.ACTIVE
        ).values('person').distinct().count()

    def get_hierarchy_tree(self, include_self=True):
        """Get hierarchical tree structure of departments."""
        tree = []
        if include_self:
            tree.append(self)

        for sub_dept in self.sub_departments.all():
            tree.extend(sub_dept.get_hierarchy_tree(include_self=True))

        return tree

    def get_all_services(self):
        """Get all services including those from sub-departments."""
        all_services = set(self.services.all())

        for sub_dept in self.sub_departments.all():
            all_services.update(sub_dept.get_all_services())

        return list(all_services)

    def __str__(self):
        return f"{self.name} ({self.company.name})"
