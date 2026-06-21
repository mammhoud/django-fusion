from django.db import models
from django.template.defaultfilters import truncatewords
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import DraftStateMixin, Orderable, Page
from wagtail.search import index

from crafts_ai.content.blocks.stream_blocks import BaseStreamBlock
from crafts_ai.content.models import Person


# ---------------------------------------------------------------------
# BlogAuthor — Through model for blog post authors
# ---------------------------------------------------------------------
class BlogAuthor(Orderable):
    """
    Through model for linking authors to blog posts
    """
    page = ParentalKey(
        'BlogPage',
        on_delete=models.CASCADE,
        related_name='author_relationships'
    )
    author = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name=_("Author")
    )

    # Author role for this specific post
    role = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Role"),
        help_text=_("Author's role for this post (e.g., Main Author, Contributor)")
    )

    is_primary_author = models.BooleanField(
        default=False,
        verbose_name=_("Is Primary Author"),
        help_text=_("Mark as the main author of this post")
    )

    class Meta:
        verbose_name = _("Blog Author")
        verbose_name_plural = _("Blog Authors")
        ordering = ['-is_primary_author', 'sort_order']

    def __str__(self):
        primary = "⭐" if self.is_primary_author else ""
        return f"{self.author.full_name} {primary} - {self.page.title}"


# ---------------------------------------------------------------------
# BlogPage — Main blog page model with enhanced tagging and authors
# ---------------------------------------------------------------------
class BlogPage(Page, DraftStateMixin):
    """
    Main blog page model with enhanced tagging capabilities and author management
    """

    # Basic fields
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Subtitle"),
        help_text=_("Optional subtitle or tagline")
    )

    introduction = models.TextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Intro paragraph for listing and SEO")
    )

    excerpt = RichTextField(
        blank=True,
        verbose_name=_("Excerpt"),
        help_text=_("Brief summary of the blog post")
    )

    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_("Featured Image"),
        help_text=_("Landscape image recommended, between 1000px and 3000px wide.")
    )

    published_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Published Date"),
        help_text=_("Date and time when the post was published")
    )

    # Content
    body = StreamField(
        BaseStreamBlock(),
        verbose_name=_("Page body"),
        blank=True,
        use_json_field=True
    )

    # Enhanced tagging
    tags = ClusterTaggableManager(
        through='blog.BlogPageTag',
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Categorize this blog post with relevant tags")
    )

    # Related content
    # related_posts = models.ManyToManyField(
    #     'self',
    #     blank=True,
    #     verbose_name=_("Related Posts"),
    #     help_text=_("Manually select related posts")
    # )

    # Analytics
    page_views = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Page Views"),
        help_text=_("Total number of page views")
    )

    reading_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Reading Time"),
        help_text=_("Estimated reading time in minutes")
    )

    # SEO fields
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Meta Title"),
        help_text=_("Custom SEO title (optional)")
    )

    meta_description = models.TextField(
        blank=True,
        verbose_name=_("Meta Description"),
        help_text=_("Custom meta description")
    )

    canonical_url = models.URLField(
        blank=True,
        verbose_name=_("Canonical URL"),
        help_text=_("Optional canonical URL for SEO")
    )

    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("OpenGraph Image"),
        help_text=_("Image used when sharing on social platforms."),
    )

    class Meta:
        verbose_name = _("Blog Article")
        verbose_name_plural = _("Blog Articles")
        db_table = "blog_pages"
        ordering = ["-published_date"]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("subtitle"),
            FieldPanel("introduction"),
            FieldPanel("excerpt"),
            FieldPanel("featured_image"),
            FieldPanel("published_date"),
        ], heading=_("Basic Information")),

        FieldPanel("body"),

        MultiFieldPanel([
            InlinePanel("author_relationships", label=_("Authors"),
                       heading=_("Post Authors")),
        ], heading=_("Authorship")),

        MultiFieldPanel([
            FieldPanel("tags"),
            InlinePanel("tagged_items", label=_("Tag Management")),
        ], heading=_("Tagging & Categorization")),

        # MultiFieldPanel([
        #     PageChooserPanel("related_posts", "blog.BlogPage"),
        # ], heading=_("Related Content")),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel("reading_time"),
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([
            FieldPanel("meta_title"),
            FieldPanel("meta_description"),
            FieldPanel("canonical_url"),
            FieldPanel("og_image"),
        ], heading=_("SEO & OpenGraph Settings")),

        MultiFieldPanel([
            FieldPanel("page_views", read_only=True),
        ], heading=_("Analytics")),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("subtitle"),
        index.SearchField("introduction"),
        index.SearchField("excerpt"),
        index.SearchField("body"),
        index.RelatedFields('tags', [
            index.SearchField('name'),
        ]),
        index.RelatedFields('author_relationships__author', [
            index.SearchField('first_name'),
            index.SearchField('last_name'),
        ]),
        index.FilterField("published_date"),
    ]

    api_fields = [
        APIField("subtitle"),
        APIField("introduction"),
        APIField("excerpt"),
        APIField("featured_image"),
        APIField("published_date"),
        APIField("body"),
        APIField("tags"),
        APIField("reading_time"),
        APIField("page_views"),
        APIField("authors"),
    ]

    # ======================
    # PROPERTIES
    # ======================

    @cached_property
    def authors(self):
        """Return live related authors."""
        return [
            rel.author for rel in self.author_relationships.select_related("author")
        ]

    @property
    def primary_author(self):
        """Get the primary author for this blog post"""
        primary_author_rel = self.author_relationships.filter(
            is_primary_author=True
        ).first()
        return primary_author_rel.author if primary_author_rel else None

    @property
    def all_authors(self):
        """Get all authors for this blog post"""
        return self.authors

    @property
    def primary_tag(self):
        """Get the primary tag for this blog post"""
        primary_tag = self.tagged_items.filter(is_primary=True).first()
        return primary_tag.tag if primary_tag else None

    @property
    def sorted_tags(self):
        """Get tags sorted by confidence score and primary status"""
        return self.tagged_items.order_by('-is_primary', '-confidence_score')

    @property
    def auto_generated_tags(self):
        """Get auto-generated tags"""
        return self.tagged_items.filter(is_auto_generated=True)

    @property
    def manual_tags(self):
        """Get manually added tags"""
        return self.tagged_items.filter(is_auto_generated=False)

    @cached_property
    def word_count(self):
        """Calculate word count from body content"""
        return len(str(self.body).split())

    @property
    def is_featured(self):
        """Check if this post is featured (based on page views or manual flag)"""
        return self.page_views > 1000  # Simple heuristic

    @property
    def get_tags(self):
        """Return all tags with their URLs."""
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"
        return tags

    @property
    def short_description(self):
        """Fallback text for summaries."""
        return truncatewords(self.introduction or self.excerpt or str(self.body), 30)

    @property
    def seo_title_final(self):
        return self.meta_title or self.title

    # ======================
    # METHODS
    # ======================

    def add_author(self, person, is_primary=False, role=""):
        """Add an author to this blog post"""
        # If setting as primary, unset existing primary
        if is_primary:
            self.author_relationships.filter(is_primary_author=True).update(
                is_primary_author=False
            )

        author_rel, created = BlogAuthor.objects.get_or_create(
            page=self,
            author=person,
            defaults={
                'is_primary_author': is_primary,
                'role': role
            }
        )

        if not created:
            author_rel.is_primary_author = is_primary
            author_rel.role = role
            author_rel.save()

        return author_rel

    def add_tag_with_metadata(self, tag_name, is_primary=False, confidence=1.0,
                            added_by=None, is_auto_generated=False, notes=""):
        """Add a tag with full metadata"""
        from .tag import BlogPageTag, BlogTag
        tag, created = BlogTag.objects.get_or_create(name=tag_name)

        # If setting as primary, unset existing primary
        if is_primary:
            self.tagged_items.filter(is_primary=True).update(is_primary=False)

        tagged_item, created = BlogPageTag.objects.get_or_create(
            content_object=self,
            tag=tag,
            defaults={
                'is_primary': is_primary,
                'confidence_score': confidence,
                'added_by': added_by,
                'is_auto_generated': is_auto_generated,
                'notes': notes
            }
        )

        return tagged_item

    def set_primary_tag(self, tag_name):
        """Set a tag as primary for this post"""
        from .tag import BlogPageTag, BlogTag
        try:
            tag = BlogTag.objects.get(name=tag_name)
            # Unset current primary
            self.tagged_items.filter(is_primary=True).update(is_primary=False)
            # Set new primary
            tagged_item, created = BlogPageTag.objects.get_or_create(
                content_object=self,
                tag=tag
            )
            tagged_item.is_primary = True
            tagged_item.save()
            return tagged_item
        except BlogTag.DoesNotExist:
            return None

    def get_related_posts(self, limit=5):
        """Get related posts based on shared tags"""
        from django.db.models import Count

        # Get posts with shared tags
        shared_tags = self.tags.values_list('id', flat=True)
        tag_based_posts = BlogPage.objects.filter(
            tagged_items__tag__in=shared_tags,
            live=True
        ).exclude(
            id=self.id
        ).annotate(
            shared_tag_count=Count('tagged_items__tag')
        ).order_by('-shared_tag_count', '-published_date')

        # Combine with manually selected related posts
        # manual_related = self.related_posts.filter(live=True)
        manual_related = []

        # Combine and deduplicate
        all_related = list(manual_related) + list(tag_based_posts)
        seen = set()
        unique_related = []

        for post in all_related:
            if post.id not in seen and post.id != self.id:
                seen.add(post.id)
                unique_related.append(post)

        return unique_related[:limit]

    def increment_page_views(self):
        """Increment page view count"""
        self.page_views += 1
        self.save(update_fields=['page_views'])

    def calculate_reading_time(self):
        """Calculate and update reading time based on content"""
        # Simple calculation: 200 words per minute
        self.reading_time = max(1, round(self.word_count / 200))
        self.save(update_fields=['reading_time'])

    def get_absolute_url(self):
        """Get absolute URL for this blog post"""
        return self.full_url

    def save(self, *args, **kwargs):
        """Auto-set published date and calculate reading time"""
        from django.utils import timezone

        # Set published date when going live
        if self.live and not self.published_date:
            self.published_date = timezone.now()

        # Calculate reading time if not set
        if not self.reading_time:
            self.calculate_reading_time()

        # Set default meta fields if empty
        if not self.meta_title:
            self.meta_title = self.title

        if not self.meta_description:
            if self.excerpt:
                self.meta_description = truncatewords(self.excerpt, 25)
            elif self.introduction:
                self.meta_description = truncatewords(self.introduction, 25)

        super().save(*args, **kwargs)

    # -----------------------
    # CMS / Hierarchy Rules
    # -----------------------
    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []
    template = "blog/blog_page.html"

    def __str__(self):
        return self.title
