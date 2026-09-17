from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class CourseTag(models.Model):
    """Tag for categorizing courses (Precis parity)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text=_("Course tag name (e.g., 'Django', 'HTMX')"),
    )
    slug = models.SlugField(unique=True, db_index=True)

    class Meta:
        verbose_name = _("Course tag")
        verbose_name_plural = _("Course tags")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
