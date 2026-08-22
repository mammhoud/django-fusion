"""
Precis Landing Product snippet — the editor-managed product catalog.

Products are managed as Wagtail snippets (mirroring the Course snippet in
``apps.learning.models.courses.info``) so every product carries the same
language + unified-currency contract as courses. The snippet is the
catalog-of-record for language filtering and pricing; the Wagtail
``ProductPage`` documents remain the rich product detail documents and link
here by slug (``ProductPage.get_product_card`` enriches the card with the
snippet's language + currency + price when a matching record exists).

Serves: GET /apis/products/ (?language=) · /apis/pricing/
"""
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from apps.content.models.languages import SUPPORTED_LANGUAGE_CHOICES


def default_currency() -> str:
    """The unified catalog currency from settings (USD unless overridden)."""
    return str(getattr(settings, "FUSION_DEFAULT_CURRENCY", "USD") or "USD")


class ProductCategoryChoices(models.TextChoices):
    APPLICATION = "application", _("Application")
    PLATFORM = "platform", _("Platform")
    LIBRARY = "library", _("Library")


class Product(index.Indexed, models.Model):
    """One catalog product with language + unified currency pricing.

    Registered as a snippet through ``ProductSnippetViewSet`` below (the
    Course pattern) — never combine the ``@register_snippet`` decorator with
    a ``register_snippet(ViewSet)`` call for the same model.
    """

    title = models.CharField(max_length=200, verbose_name=_("Title"))
    slug = models.SlugField(max_length=220, unique=True, verbose_name=_("Slug"))
    detail_slug = models.SlugField(
        max_length=220,
        blank=True,
        default="",
        verbose_name=_("Detail page slug"),
        help_text=_(
            "Slug of the Wagtail product page this catalog row links to. "
            "Leave empty to use this row's own slug (language variants point "
            "at the canonical page here)."
        ),
    )
    short_description = models.TextField(blank=True, default="", verbose_name=_("Short description"))
    description = RichTextField(
        blank=True,
        default="",
        features=["bold", "italic", "link", "ol", "ul"],
        verbose_name=_("Description"),
    )
    category = models.CharField(
        max_length=20,
        choices=ProductCategoryChoices.choices,
        default=ProductCategoryChoices.APPLICATION,
        verbose_name=_("Category"),
    )
    language = models.CharField(
        max_length=10,
        choices=SUPPORTED_LANGUAGE_CHOICES,
        default="en",
        verbose_name=_("Language"),
        help_text=_("Primary language of this product's catalog copy."),
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Price"),
        help_text=_("Base price in the unified catalog currency (0 = free/open source)."),
    )
    currency = models.CharField(
        max_length=3,
        default=default_currency,
        verbose_name=_("Currency"),
        help_text=_("ISO 4217 code — defaults to FUSION_DEFAULT_CURRENCY."),
    )
    version = models.CharField(max_length=40, blank=True, default="", verbose_name=_("Version"))
    status = models.CharField(
        max_length=20,
        choices=[("live", _("Live / released")), ("development", _("Under development"))],
        default="live",
        verbose_name=_("Status"),
    )
    is_published = models.BooleanField(default=True, db_index=True, verbose_name=_("Published"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("slug"),
                FieldPanel("detail_slug"),
                FieldPanel("short_description"),
                FieldPanel("category"),
            ],
            heading=_("Product identity"),
        ),
        FieldPanel("description"),
        MultiFieldPanel(
            [
                FieldPanel("language"),
                FieldPanel("price"),
                FieldPanel("currency"),
                FieldPanel("version"),
                FieldPanel("status"),
            ],
            heading=_("Language & pricing"),
        ),
        MultiFieldPanel(
            [FieldPanel("is_published"), FieldPanel("is_featured"), FieldPanel("created_at")],
            heading=_("Publishing"),
        ),
    ]

    search_fields = [
        index.SearchField("title", boost=10),
        index.SearchField("short_description", boost=5),
        index.SearchField("description", boost=3),
        index.FilterField("is_published"),
        index.FilterField("language"),
        index.FilterField("category"),
    ]

    class Meta:
        app_label = "content"
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["-is_featured", "title"]
        indexes = [models.Index(fields=["language", "is_published"])]

    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"

    @property
    def is_free(self) -> bool:
        return (self.price or Decimal("0.00")) <= 0

    def as_dict(self) -> dict:
        """Frontend-consumable catalog shape (language + unified currency)."""
        return {
            "id": self.pk,
            "title": self.title,
            "slug": self.slug,
            "detail_slug": self.detail_slug or self.slug,
            "short_description": self.short_description,
            "description": str(self.description or ""),
            "category": self.get_category_display().lower(),
            "language": self.language,
            "price": str(self.price),
            "currency": self.currency or default_currency(),
            "is_free": self.is_free,
            "is_featured": self.is_featured,
            "version": self.version,
            "status": self.status,
            "href": f"/products/{self.detail_slug or self.slug}/",
        }

    @classmethod
    def by_slug(cls):
        """Published products keyed by slug — used to enrich ProductPage cards."""
        return {
            item.slug: item
            for item in cls.objects.filter(is_published=True).select_related()
        }


class ProductSnippetViewSet(SnippetViewSet):
    model = Product
    menu_label = _("Products")
    menu_icon = "box"
    list_display = [
        "title",
        "category",
        "language",
        "price",
        "currency",
        "status",
        "is_published",
    ]
    list_filter = ["language", "category", "status", "is_published"]
    search_fields = ["title", "slug", "short_description"]


register_snippet(ProductSnippetViewSet)
