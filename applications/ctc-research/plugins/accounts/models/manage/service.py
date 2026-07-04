from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_osoul.core.models import BaseModel as DefaultBase
from ceptor_ai.blocks.pages.services import ServicesSectionBlock
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import StreamField


# ---------------------------------------------------------------------
# 💼 SERVICE MODEL
# ---------------------------------------------------------------------
class Service(DefaultBase):
    """
    Represents a reusable service snippet with overview, pricing, and rich content sections.
    """

    class ServiceCategory(models.TextChoices):
        LMS = "lms", _("Learning Management System (LMS)")
        CRM = "crm", _("Customer Relationship Management (CRM)")
        THERAPY = "therapy", _("Therapy & Counselling")
        CONSULTING = "consulting", _("Consulting Services")
        SUPPORT = "support", _("Customer Support")
        OTHER = "other", _("Other")

    # -------------------------------
    # Core fields
    # -------------------------------
    name = models.CharField(_("Service Name"), max_length=200)
    overview = models.CharField(
        _("Overview"),
        max_length=300,
        blank=True,
        help_text=_("A short tagline or one-sentence summary for the service."),
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Detailed description of the service and its purpose."),
    )
    category = models.CharField(
        _("Category"),
        choices=ServiceCategory.choices,
        max_length=50,
        default=ServiceCategory.OTHER,
    )
    icon = models.CharField(
        _("Icon"),
        max_length=100,
        blank=True,
        help_text=_("Optional icon class (e.g., 'fa-solid fa-laptop')."),
    )

    # -------------------------------
    # Pricing
    # -------------------------------
    price = models.DecimalField(
        _("Base Price"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Base price for this service."),
    )
    pricing_notes = models.TextField(
        _("Pricing Details"),
        blank=True,
        help_text=_("Optional notes about pricing or subscription tiers."),
    )

    # -------------------------------
    # Dynamic section content
    # -------------------------------
    title = models.CharField(
        _("Section Title"),
        max_length=200,
        blank=True,
        help_text=_("Optional title for the content section."),
    )
    content = StreamField(
        [
            ("rich_text", blocks.RichTextBlock()),
            ("services_section", ServicesSectionBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name=_("Content"),
        help_text=_("Dynamic content sections for the service."),
    )

    is_visible = models.BooleanField(
        _("Is Visible"),
        default=True,
        help_text=_("Controls whether this section appears on the frontend."),
    )

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Image"),
    )
    # -------------------------------
    # Meta and visibility
    # -------------------------------
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Determines whether this service is currently available."),
    )

    # -------------------------------
    # Panels
    # -------------------------------
    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("overview"),
                FieldPanel("description"),
                FieldPanel("image"),
                FieldPanel("category"),
                FieldPanel("icon"),
            ],
            heading=_("Basic Information"),
        ),
    ]

    pricing_panels = [
        MultiFieldPanel(
            [
                FieldPanel("price"),
                FieldPanel("pricing_notes"),
            ],
            heading=_("Pricing Information"),
        ),
    ]

    section_panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("content"),
                FieldPanel("is_visible"),
            ],
            heading=_("Service Content"),
        ),
    ]

    settings_panels = [
        FieldPanel("is_active"),
    ]

    # -------------------------------
    # Wagtail Tabbed Edit Interface
    # -------------------------------
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(pricing_panels, heading=_("Pricing")),
            ObjectList(section_panels, heading=_("Sections")),
            ObjectList(settings_panels, heading=_("Settings")),
        ]
    )

    # -------------------------------
    # Meta and Utility Methods
    # -------------------------------
    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        db_table = "handlers_services" if "handlers" in __name__ else "accounts_services" if "accounts" in __name__ else "services"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def get_absolute_url(self):
        return reverse("service-detail", kwargs={"pk": self.pk})

    # -------------------------------
    # Computed properties
    # -------------------------------
    @property
    def short_description(self):
        if self.description and len(self.description) > 80:
            return f"{self.description[:77]}..."
        return self.description or _("No description provided.")

    @property
    def formatted_price(self):
        if self.price is None:
            return _("Contact for pricing")
        return f"${self.price:,.2f}"

