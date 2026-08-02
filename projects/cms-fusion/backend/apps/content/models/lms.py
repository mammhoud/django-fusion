"""
LMS site data models — Features, Instructors, FAQ, Dashboard, Products, Menu.

These models replace the static TS data files in next-lms/src/data/ and are
served via django-bolt API endpoints in apis.py.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet


@register_snippet
class Feature(models.Model):
    """Feature card displayed on home pages."""

    page = models.CharField(max_length=50, default="home_1",
        help_text="Which home page version this feature belongs to")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    icon = models.ForeignKey(
        get_image_model_string(), on_delete=models.SET_NULL, null=True, blank=True,
    )
    icon_class = models.CharField(max_length=100, blank=True, default="")
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    panels = [FieldPanel("page"), FieldPanel("title"), FieldPanel("description"),
              FieldPanel("icon"), FieldPanel("icon_class"), FieldPanel("sort_order")]

    class Meta:
        app_label = "content"
        ordering = ["page", "sort_order"]
        verbose_name = _("feature")
        verbose_name_plural = _("features")

    def __str__(self):
        return self.title


@register_snippet
class Instructor(models.Model):
    """Instructor profile."""

    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    avatar = models.ForeignKey(
        get_image_model_string(), on_delete=models.SET_NULL, null=True, blank=True,
    )
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    course_count = models.IntegerField(default=0)
    student_count = models.IntegerField(default=0)
    social_links = models.JSONField(default=dict, blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    panels = [FieldPanel("name"), FieldPanel("designation"), FieldPanel("bio"),
              FieldPanel("avatar"), FieldPanel("rating"), FieldPanel("sort_order")]

    class Meta:
        app_label = "content"
        ordering = ["sort_order"]
        verbose_name = _("instructor")
        verbose_name_plural = _("instructors")

    def __str__(self):
        return self.name


@register_snippet
class Faq(models.Model):
    """Frequently Asked Question."""

    page = models.CharField(max_length=50, default="home_1",
        help_text="Which home page version this FAQ belongs to")
    question = models.TextField()
    answer = models.TextField()
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    panels = [FieldPanel("page"), FieldPanel("question"), FieldPanel("answer"),
              FieldPanel("sort_order")]

    class Meta:
        app_label = "content"
        ordering = ["page", "sort_order"]
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")

    def __str__(self):
        return self.question[:80]


@register_snippet
class DashboardCounter(models.Model):
    """Dashboard stat counter (e.g., '5 Enrolled Courses')."""

    label = models.CharField(max_length=200)
    value = models.IntegerField(default=0)
    icon_class = models.CharField(max_length=100, blank=True, default="")
    prefix = models.CharField(max_length=20, blank=True, default="")
    suffix = models.CharField(max_length=20, blank=True, default="")
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    panels = [FieldPanel("label"), FieldPanel("value"), FieldPanel("icon_class"),
              FieldPanel("prefix"), FieldPanel("suffix"), FieldPanel("sort_order")]

    class Meta:
        app_label = "content"
        ordering = ["sort_order"]
        verbose_name = _("dashboard counter")
        verbose_name_plural = _("dashboard counters")

    def __str__(self):
        return f"{self.label}: {self.value}"


@register_snippet
class ShopProduct(models.Model):
    """Shop product for the LMS store."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ForeignKey(
        get_image_model_string(), on_delete=models.SET_NULL, null=True, blank=True,
    )
    category = models.CharField(max_length=100, blank=True, default="")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    stock_status = models.CharField(max_length=20, default="in_stock",
        choices=[("in_stock", "In Stock"), ("out_of_stock", "Out of Stock"), ("coming_soon", "Coming Soon")])
    is_active = models.BooleanField(default=True)

    panels = [FieldPanel("title"), FieldPanel("slug"), FieldPanel("description"),
              FieldPanel("price"), FieldPanel("sale_price"), FieldPanel("image"),
              FieldPanel("category"), FieldPanel("stock_status")]

    class Meta:
        app_label = "content"
        ordering = ["title"]
        verbose_name = _("shop product")
        verbose_name_plural = _("shop products")

    def __str__(self):
        return self.title


@register_snippet
class MenuItem(models.Model):
    """Navigation menu item (flat hierarchy via parent_id)."""

    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True,
        related_name="children", help_text="Parent menu item for nested menus",
    )
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=500, blank=True, default="#")
    menu_class = models.CharField(max_length=100, blank=True, default="",
        help_text="CSS class for mega-menu container")
    badge = models.CharField(max_length=100, blank=True, default="",
        help_text="Badge text like 'Hot' or 'New'")
    badge_class = models.CharField(max_length=100, blank=True, default="",
        help_text="Badge color variant like 'tg-badge'")
    icon = models.CharField(max_length=100, blank=True, default="")
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    panels = [FieldPanel("parent"), FieldPanel("title"), FieldPanel("link"),
              FieldPanel("menu_class"), FieldPanel("badge"), FieldPanel("badge_class"),
              FieldPanel("icon"), FieldPanel("sort_order")]

    class Meta:
        app_label = "content"
        ordering = ["sort_order"]
        verbose_name = _("menu item")
        verbose_name_plural = _("menu items")

    def __str__(self):
        return self.title
