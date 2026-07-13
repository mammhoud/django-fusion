"""Course Tag Model - for categorizing courses."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class CourseTag(models.Model):
    """Tag for categorizing courses."""

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text=_("Course tag name (e.g., 'Python', 'Web Development')"),
    )
    slug = models.SlugField(unique=True, db_index=True)

    class Meta:
        app_label = "lms"
        verbose_name = _("Course Tag")
        verbose_name_plural = _("Course Tags")
        ordering = ["name"]

    def __str__(self):
        return self.name
