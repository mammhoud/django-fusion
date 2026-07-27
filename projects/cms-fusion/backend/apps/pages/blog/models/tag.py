"""
Blog Tag Model
"""
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class BlogTag(models.Model):
    """
    Tag for labeling blog posts.
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Name"),
    )

    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly version of the name"),
    )

    class Meta:
        app_label = 'blog'
        verbose_name = _("Blog Tag")
        verbose_name_plural = _("Blog Tags")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_post_count(self):
        """Return the number of published posts with this tag."""
        return self.posts.filter(status="published").count()
