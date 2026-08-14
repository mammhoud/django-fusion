"""
Blog Category Model
"""
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class BlogCategory(models.Model):
    """
    Category for organizing blog posts.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Name"),
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly version of the name"),
    )

    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
    )

    class Meta:
        app_label = 'blog'
        verbose_name = _("Blog Category")
        verbose_name_plural = _("Blog Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_post_count(self):
        """Return the number of published posts in this category."""
        return self.posts.filter(status="published").count()
