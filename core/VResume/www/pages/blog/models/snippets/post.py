"""
Blog post and snippet content models.

BlogPost          — reusable blog post snippet (non-page), with TabbedInterface.
BlogSnippet       — reusable content block (testimonial, case study, tip, etc.).
BlogPageSnippet   — through model linking BlogSnippet to BlogPage.
"""
from django.db import models
from django.template.defaultfilters import truncatewords
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel, InlinePanel, MultiFieldPanel,
    TabbedInterface, ObjectList,
)
from wagtail.api import APIField
from wagtail.blocks import RichTextBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable
from wagtail.search import index


# ---------------------------------------------------------------------------
# BlogPost — reusable snippet (non-page), TabbedInterface admin
# ---------------------------------------------------------------------------
class BlogPost(ClusterableModel):
    """
    Reusable blog post snippet — not a Wagtail page.
    Authors linked via BlogSnippetPostAuthor (from author.py).
    Tags linked via simple M2M to BlogTag.
    """
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    subtitle = models.CharField(max_length=255, blank=True, verbose_name=_("Subtitle"))
    introduction = models.TextField(blank=True, verbose_name=_("Introduction"))
    excerpt = RichTextField(blank=True, verbose_name=_("Excerpt"))
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Featured Image"),
    )
    published_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Published Date"))
    body = StreamField(
        [("paragraph", RichTextBlock())],
        verbose_name=_("Body"), blank=True, use_json_field=True,
    )
    tags = models.ManyToManyField(
        "blog.BlogTag",
        blank=True,
        related_name="blog_posts",
        verbose_name=_("Tags"),
    )
    related_posts = models.ManyToManyField(
        "self", blank=True, symmetrical=False,
        verbose_name=_("Related Posts"),
    )
    page_views = models.PositiveIntegerField(default=0, verbose_name=_("Page Views"))
    reading_time = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Reading Time (min)"))
    meta_title = models.CharField(max_length=255, blank=True, verbose_name=_("Meta Title"))
    meta_description = models.TextField(blank=True, verbose_name=_("Meta Description"))
    canonical_url = models.URLField(blank=True, verbose_name=_("Canonical URL"))
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("OG Image"),
    )
    is_published = models.BooleanField(default=False, verbose_name=_("Published"))

    display_order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ── TabbedInterface panels ────────────────────────────────────────────────

    _content_panels = [
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("slug"),
            FieldPanel("subtitle"),
            FieldPanel("introduction"),
            FieldPanel("excerpt"),
            FieldPanel("featured_image"),
            FieldPanel("published_date"),
        ], heading=_("Basic Info")),
        FieldPanel("body"),
        MultiFieldPanel([
            FieldPanel("is_published"),

            FieldPanel("display_order"),
        ], heading=_("Publication")),
    ]

    _authors_panels = [
        InlinePanel("author_relationships", label=_("Author")),
    ]

    _tags_panels = [
        FieldPanel("tags"),
    ]

    _seo_panels = [
        MultiFieldPanel([
            FieldPanel("meta_title"),
            FieldPanel("meta_description"),
            FieldPanel("canonical_url"),
            FieldPanel("og_image"),
        ], heading=_("SEO")),
        MultiFieldPanel([
            FieldPanel("reading_time"),
            FieldPanel("page_views", read_only=True),
        ], heading=_("Analytics")),
    ]

    edit_handler = TabbedInterface([
        ObjectList(_content_panels, heading=_("Content")),
        ObjectList(_authors_panels, heading=_("Authors")),
        ObjectList(_tags_panels, heading=_("Tags")),
        ObjectList(_seo_panels, heading=_("SEO")),
    ])

    search_fields = [
        index.SearchField("title", partial_match=True),
        index.SearchField("subtitle"),
        index.SearchField("introduction"),
        index.SearchField("body"),
        index.FilterField("is_published"),
    ]



    class Meta:
        verbose_name = _("Blog Post (Snippet)")
        verbose_name_plural = _("Blog Posts (Snippets)")
        ordering = ["-published_date", "-created_at"]
        app_label = "blog"

    def __str__(self):
        return self.title

    # ── properties ───────────────────────────────────────────────────────────

    @cached_property
    def authors(self):
        return [r.author for r in self.author_relationships.select_related("author")]

    @property
    def primary_author(self):
        rel = self.author_relationships.filter(is_primary=True).first()
        return rel.author if rel else None

    @cached_property
    def word_count(self):
        return len(str(self.body).split())

    @property
    def short_description(self):
        return truncatewords(self.introduction or self.excerpt or str(self.body), 30)

    # ── methods ──────────────────────────────────────────────────────────────

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        if self.is_published and not self.published_date:
            self.published_date = timezone.now()
        if not self.reading_time and self.word_count:
            self.reading_time = max(1, round(self.word_count / 200))
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = truncatewords(
                self.introduction or self.excerpt or "", 25
            )
        super().save(*args, **kwargs)
