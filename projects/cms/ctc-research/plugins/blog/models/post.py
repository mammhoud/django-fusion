"""
Blog Post Model
"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from wagtail.fields import RichTextField

from .category import BlogCategory
from .tag import BlogTag


class BlogPost(models.Model):
    """
    Blog post with full content management.
    """

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("published", _("Published")),
        ("archived", _("Archived")),
    ]

    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_("Slug"),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
        verbose_name=_("Author"),
    )

    content = RichTextField(
        verbose_name=_("Content"),
        help_text=_("Main content of the blog post"),
    )

    excerpt = models.TextField(
        max_length=500,
        blank=True,
        default="",
        verbose_name=_("Excerpt"),
        help_text=_("Short summary for listings (max 500 chars)"),
    )

    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Featured Image"),
    )

    categories = models.ManyToManyField(
        BlogCategory,
        blank=True,
        related_name="posts",
        verbose_name=_("Categories"),
    )

    tags = models.ManyToManyField(
        BlogTag,
        blank=True,
        related_name="posts",
        verbose_name=_("Tags"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status"),
        db_index=True,
    )

    published_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Published Date"),
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )

    likes_count = models.IntegerField(
        default=0,
        verbose_name=_("Likes"),
        help_text=_("Number of likes this post has received"),
    )

    # SEO fields
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        default="",
        verbose_name=_("Meta Description"),
    )

    class Meta:
        app_label = 'blog'
        verbose_name = _("Blog Post")
        verbose_name_plural = _("Blog Posts")
        ordering = ["-published_date", "-created_at"]
        indexes = [
            models.Index(fields=["status", "published_date"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-set published_date when status changes to published
        if self.status == "published" and not self.published_date:
            self.published_date = timezone.now()

        super().save(*args, **kwargs)

    def get_reading_time(self) -> int:
        """
        Calculate estimated reading time in minutes.
        Assumes average reading speed of 200 words per minute.
        """
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))

    def get_related_posts(self, limit: int = 3):
        """
        Get related posts based on shared categories or tags.

        Args:
            limit: Maximum number of related posts to return

        Returns:
            QuerySet of related BlogPost instances
        """
        # Get posts that share categories or tags
        category_ids = self.categories.values_list("id", flat=True)
        tag_ids = self.tags.values_list("id", flat=True)

        related = BlogPost.objects.filter(
            status="published"
        ).exclude(
            id=self.id
        ).filter(
            models.Q(categories__id__in=category_ids) |
            models.Q(tags__id__in=tag_ids)
        ).distinct()

        # Order by number of shared categories/tags
        return related[:limit]

    @property
    def is_published(self) -> bool:
        """Check if post is published."""
        return self.status == "published"

    def publish(self):
        """Publish the post."""
        self.status = "published"
        if not self.published_date:
            self.published_date = timezone.now()
        self.save()

    def archive(self):
        """Archive the post."""
        self.status = "archived"
        self.save()
