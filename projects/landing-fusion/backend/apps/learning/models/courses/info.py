from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.content.models.languages import SUPPORTED_LANGUAGE_CHOICES

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail.snippets.views.snippets import SnippetViewSet

from modelcluster.models import ClusterableModel

from apps.learning.managers.course import CourseQuerySet


class Course(ClusterableModel, index.Indexed):
    """A published learning product managed as a Wagtail snippet."""

    title = models.CharField(max_length=200, unique=True, verbose_name=_("Title"))
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_description = models.TextField(blank=True, verbose_name=_("Short description"))
    description = RichTextField(blank=True, verbose_name=_("Description"))

    # === Learning content (mirrors Precis apps/learning course metadata) ===
    objectives = models.TextField(
        blank=True,
        verbose_name=_("Learning objectives"),
        help_text=_("What students will learn — one per line."),
    )
    requirements = models.TextField(
        blank=True,
        verbose_name=_("Requirements"),
        help_text=_("Prerequisites and requirements — one per line."),
    )
    target_audience = models.TextField(
        blank=True,
        verbose_name=_("Target audience"),
        help_text=_("Who this course is for — one per line."),
    )
    specializations = models.ManyToManyField(
        "Specialization",
        blank=True,
        related_name="courses",
        verbose_name=_("Specializations"),
    )
    tags = models.ManyToManyField(
        "CourseTag",
        blank=True,
        related_name="courses",
        verbose_name=_("Tags"),
    )

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="learning_courses",
        verbose_name=_("Instructor"),
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="learning_course_images",
        verbose_name=_("Course image"),
        help_text=_("Main course image/thumbnail (Precis parity)."),
    )
    language = models.CharField(
        max_length=10,
        choices=SUPPORTED_LANGUAGE_CHOICES,
        default="en",
        verbose_name=_("Language"),
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("beginner", _("Beginner")),
            ("intermediate", _("Intermediate")),
            ("advanced", _("Advanced")),
        ],
        default="beginner",
    )
    duration_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_published = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=False)
    has_certificate = models.BooleanField(default=False)
    youtube_channel_url = models.URLField(blank=True, verbose_name=_("YouTube channel"))
    youtube_channel_name = models.CharField(
        max_length=120, blank=True, verbose_name=_("YouTube channel name")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("slug"),
                FieldPanel("short_description"),
                FieldPanel("description"),
            ],
            heading=_("Course content"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("objectives"),
                FieldPanel("requirements"),
                FieldPanel("target_audience"),
            ],
            heading=_("Learning objectives & audience"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("specializations"),
                FieldPanel("tags"),
                FieldPanel("instructor"),
                FieldPanel("language"),
                FieldPanel("difficulty"),
                FieldPanel("duration_hours"),
            ],
            heading=_("Learning details"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("price"),
                FieldPanel("is_published"),
                FieldPanel("is_featured"),
                FieldPanel("has_certificate"),
            ],
            heading=_("Commercial settings"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("youtube_channel_name"),
                FieldPanel("youtube_channel_url"),
            ],
            heading=_("Instructor channel"),
        ),
        InlinePanel("modules", heading=_("Modules"), label=_("Module")),
    ]
    search_fields = [
        index.SearchField("title", partial_match=True, boost=2),
        index.SearchField("short_description"),
        index.SearchField("description"),
        index.SearchField("objectives"),
        index.SearchField("target_audience"),
        index.FilterField("is_published"),
        index.FilterField("difficulty"),
        index.FilterField("language"),
    ]

    class Meta:
        ordering = ["-is_featured", "title"]
        indexes = [models.Index(fields=["is_published", "is_featured"])]

    objects = CourseQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("learning:course", kwargs={"slug": self.slug})

    @property
    def is_free(self):
        return self.price <= 0

    @property
    def average_rating(self) -> float:
        """Average rating from published reviews only (Precis parity).

        Uses the ``_avg_rating`` annotation when present (catalog/detail
        querysets) so listing pages avoid a per-row aggregate.
        """
        annotated = getattr(self, "_avg_rating", None)
        if annotated is not None:
            return float(annotated or 0.0)
        from django.db.models import Avg

        result = self.reviews.published().aggregate(Avg("rating"))
        return float(result["rating__avg"] or 0.0)

    @property
    def reviews_count(self) -> int:
        """Count of published reviews (Precis parity)."""
        annotated = getattr(self, "_reviews_count", None)
        if annotated is not None:
            return annotated
        return self.reviews.published().count()

    @property
    def rating_stars(self) -> str:
        """Star glyphs derived from the (published) average rating, for UI."""
        stars = int(self.average_rating + 0.5)
        stars = max(0, min(5, stars))
        return "★" * stars + "☆" * (5 - stars)

    @property
    def enrolled_count(self) -> int:
        """Count of active/completed enrollments (surfaces in catalog JSON)."""
        annotated = getattr(self, "_enrolled_count", None)
        if annotated is not None:
            return annotated
        return self.enrollments.exclude(status="cancelled").count()

    @property
    def image_url(self):
        """Absolute media URL for the course thumbnail, if set."""
        if not self.image_id:
            return None
        try:
            return self.image.file.url
        except Exception:
            return None

    @property
    def module_count(self):
        annotated = getattr(self, "_module_count", None)
        return annotated if annotated is not None else self.modules.count()

    @property
    def lesson_count(self):
        annotated = getattr(self, "_lesson_count", None)
        if annotated is not None:
            return annotated
        # Lazy import avoids a circular dependency: specification.py imports
        # Module from detail.py, which imports Course from this module.
        from .specification import Lesson

        return Lesson.objects.filter(module__course=self, is_active=True).count()


class CourseSnippetViewSet(SnippetViewSet):
    model = Course
    menu_label = _("Courses")
    menu_icon = "book"
    add_to_admin_menu = True
    list_display = ["title", "instructor", "difficulty", "price", "is_published", "updated_at"]
    list_filter = ["is_published", "is_featured", "difficulty", "language", "specializations"]
    search_fields = ["title", "short_description", "objectives", "instructor__email"]
