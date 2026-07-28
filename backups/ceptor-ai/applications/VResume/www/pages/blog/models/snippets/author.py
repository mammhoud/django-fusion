"""
Blog author models.

BlogAuthor         — standalone author profile snippet.
BlogPageAuthorRel  — through model: BlogPage ↔ BlogAuthor  (ParentalKey).
BlogPostAuthorRel  — through model: BlogPost ↔ BlogAuthor  (ParentalKey).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Orderable
from wagtail.search import index


class BlogAuthor(models.Model):
    """
    Standalone author profile — not linked to VResumeSettings.
    Any person can be an author.
    """
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    slug = models.SlugField(
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("Used in author archive URLs"),
    )
    role = models.CharField(
        max_length=100, blank=True,
        verbose_name=_("Role / Title"),
        help_text=_("e.g. Lead Developer, Designer, Contributor"),
    )
    bio = models.TextField(blank=True, verbose_name=_("Bio"))
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Photo"),
    )
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website = models.URLField(blank=True, verbose_name=_("Website"))
    twitter = models.CharField(max_length=100, blank=True, verbose_name=_("Twitter"))
    linkedin = models.URLField(blank=True, verbose_name=_("LinkedIn URL"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    display_order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel([
            FieldPanel("name"),
            FieldPanel("slug"),
            FieldPanel("role"),
            FieldPanel("photo"),
        ], heading=_("Identity")),
        FieldPanel("bio"),
        MultiFieldPanel([
            FieldPanel("email"),
            FieldPanel("website"),
            FieldPanel("twitter"),
            FieldPanel("linkedin"),
        ], heading=_("Contact & Social")),
        MultiFieldPanel([
            FieldPanel("is_active"),
            FieldPanel("display_order"),
        ], heading=_("Settings")),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
        index.SearchField("role"),
        index.SearchField("bio"),
    ]

    class Meta:
        verbose_name = _("Blog Author")
        verbose_name_plural = _("Blog Authors")
        ordering = ["display_order", "name"]
        app_label = "blog"

    def __str__(self):
        return f"{self.name} — {self.role}" if self.role else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPageAuthorRel(Orderable):
    """Through model: BlogPage (Wagtail page) ↔ BlogAuthor."""
    page = ParentalKey(
        "blog.BlogPage",
        on_delete=models.CASCADE,
        related_name="author_relationships",
    )
    author = models.ForeignKey(
        BlogAuthor,
        on_delete=models.CASCADE,
        related_name="page_relationships",
        verbose_name=_("Author"),
    )
    is_primary = models.BooleanField(default=False, verbose_name=_("Primary"))

    panels = [FieldPanel("author"), FieldPanel("is_primary")]

    class Meta:
        verbose_name = _("Page Author")
        ordering = ["-is_primary", "sort_order"]
        unique_together = [["page", "author"]]
        app_label = "blog"

    def __str__(self):
        return f"{self.author.name} → {self.page.title}"


class BlogPostAuthorRel(Orderable):
    """Through model: BlogPost (snippet) ↔ BlogAuthor."""
    post = ParentalKey(
        "blog.BlogPost",
        on_delete=models.CASCADE,
        related_name="author_relationships",
    )
    author = models.ForeignKey(
        BlogAuthor,
        on_delete=models.CASCADE,
        related_name="post_relationships",
        verbose_name=_("Author"),
    )
    is_primary = models.BooleanField(default=False, verbose_name=_("Primary"))

    panels = [FieldPanel("author"), FieldPanel("is_primary")]

    class Meta:
        verbose_name = _("Post Author")
        ordering = ["-is_primary", "sort_order"]
        unique_together = [["post", "author"]]
        app_label = "blog"

    def __str__(self):
        return f"{self.author.name} → {self.post.title}"
