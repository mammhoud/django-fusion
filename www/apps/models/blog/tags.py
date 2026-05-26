
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_rseal.workflows.pipelines.models import BaseTag, BaseTagCategory
from modelcluster.fields import ParentalKey
from taggit.models import ItemBase
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    PublishingPanel,
)
from wagtail.models import Orderable
from wagtail.search import index


# ---------------------------------------------------------------------
# Blog Tag Category
# ---------------------------------------------------------------------
class BlogTagCategory(BaseTagCategory):
    """Category for organizing blog tags"""

    class Meta:
        verbose_name = _("Blog Tag Category")
        verbose_name_plural = _("Blog Tag Categories")
        db_table = "blog_tag_categories"

    panels = BaseTagCategory.panels if hasattr(BaseTagCategory, "panels") else [
        MultiFieldPanel([
            FieldPanel("name"),
            FieldPanel("slug"),
            FieldPanel("description"),
            FieldPanel("color"),
            FieldPanel("icon"),
            FieldPanel("is_public"),
            FieldPanel("display_order"),
        ], heading=_("Basic Information")),
        PublishingPanel(),
    ]

    @property
    def tag_count(self):
        return self.blog_tags.count()

    @property
    def published_tag_count(self):
        return self.blog_tags.filter(live=True).count()

    def get_absolute_url(self):
        return reverse("blog-tag-category-detail", kwargs={"slug": self.slug})


# ---------------------------------------------------------------------
# Blog Tag
# ---------------------------------------------------------------------
class BlogTag(BaseTag):
    """Enhanced Tag model specifically for blog posts"""
    category = models.ForeignKey(
        BlogTagCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_tags',
        verbose_name=_("Category"),
    )

    class Meta:
        verbose_name = _("Blog Tag")
        verbose_name_plural = _("Blog Tags")
        db_table = "blog_tags"
        indexes = BaseTag.Meta.indexes + [models.Index(fields=["category"])]

    panels = BaseTag.panels + [
        FieldPanel("category"),
    ]

    search_fields = BaseTag.search_fields + [
        index.FilterField("category"),
    ]

    def get_absolute_url(self):
        return reverse("blog-tag-detail", kwargs={"slug": self.slug})

    def update_usage_stats(self):
        recent = self.tagged_blogs.filter(content_object__live=True).order_by("-id").first()
        self.usage_count = self.tagged_blogs.filter(content_object__live=True).count()
        self.last_used = recent.created_at if recent else None
        self.save(update_fields=["usage_count", "last_used"])

    @property
    def published_items_count(self):
        return self.tagged_blogs.filter(content_object__live=True).count()

    def get_related_tags(self, limit=10):
        from django.db.models import Count
        return BlogTag.objects.filter(
            tagged_blogs__content_object__live=True,
            tagged_blogs__content_object__tagged_items__tag__in=[self]
        ).exclude(id=self.id).annotate(common_count=Count("id")).order_by("-common_count")[:limit]


# ---------------------------------------------------------------------
# Blog Page Tag (Through Model)
# ---------------------------------------------------------------------
class BlogPageTag(Orderable, ItemBase):
    """Through model for tagging blog posts"""
    content_object = ParentalKey("BlogPage", related_name="tagged_items", on_delete=models.CASCADE)
    tag = models.ForeignKey(BlogTag, related_name="tagged_blogs", on_delete=models.CASCADE)
    confidence_score = models.FloatField(default=1.0)
    is_primary = models.BooleanField(default=False)
    is_auto_generated = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    click_count = models.PositiveIntegerField(default=0)
    last_clicked = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Blog Page Tag")
        verbose_name_plural = _("Blog Page Tags")
        db_table = "blog_page_tags"
        unique_together = [["content_object", "tag"]]
        ordering = ["-is_primary", "-confidence_score", "tag__name"]

    panels = [
        FieldPanel("tag"),
        MultiFieldPanel([
            FieldRowPanel([FieldPanel("is_primary"), FieldPanel("is_auto_generated")]),
            FieldPanel("confidence_score"),
            FieldPanel("notes"),
        ], heading=_("Tag Metadata")),
    ]

    def __str__(self):
        return f"{self.tag.name} → {self.content_object.title}"

    def clean(self):
        super().clean()
        if not 0 <= self.confidence_score <= 1:
            raise ValidationError({'confidence_score': _('Confidence score must be between 0.0 and 1.0')})
        if self.is_primary:
            existing_primary = BlogPageTag.objects.filter(content_object=self.content_object, is_primary=True).exclude(pk=self.pk)
            if existing_primary.exists():
                raise ValidationError({'is_primary': _('Only one primary tag allowed per blog post')})

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.tag.update_usage_stats()

    def delete(self, *args, **kwargs):
        tag = self.tag
        super().delete(*args, **kwargs)
        tag.update_usage_stats()

    def increment_click_count(self):
        self.click_count += 1
        self.last_clicked = timezone.now()
        self.save(update_fields=["click_count", "last_clicked"])

