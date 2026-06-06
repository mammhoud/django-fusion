from __future__ import annotations

import logging
from typing import Any, Dict

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_osoul.models import BaseModel as DefaultBase
from django_rseal.blocks.content.overview import OverviewBlock
from django_rseal.models import ModelCacheMixin
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.embeds.blocks import EmbedBlock as SimpleVideoBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.search import index

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# COURSE MODEL
# -------------------------------------------------------------------
class Course(ClusterableModel, index.Indexed, ModelCacheMixin, DefaultBase):
    """
    A comprehensive course model representing a structured learning resource.

    Each Course may belong to a Specialization and contain multiple Modules.
    Includes pricing, visibility, language, and multimedia support.
    """

    # === Core Metadata ===
    title = models.CharField(max_length=200, unique=True, verbose_name=_("Course Title"))
    slug = models.SlugField(
        unique=True,
        max_length=255,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly identifier for this course."),
    )
    specializations = models.ManyToManyField(
        "Specialization",
        blank=True,
        related_name="courses",
        verbose_name=_("Specializations"),
    )
    categories = models.ManyToManyField(
        "CourseCategory",
        blank=True,
        related_name="courses",
        verbose_name=_("Categories"),
    )
    tags = models.ManyToManyField(
        "CourseTag",
        blank=True,
        related_name="courses",
        verbose_name=_("Tags"),
    )

    # === Visual & Media ===
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='course_images',
        verbose_name=_("Course Image"),
        help_text=_("Main course image/thumbnail")
    )
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='course_header_images',
        verbose_name=_("Header Image"),
        help_text=_("Large header image for course detail page")
    )

    preview_video = StreamField(
        [("preview_video", SimpleVideoBlock(template="django_grep/comp/blocks/media/simple_video.html"))],
        null=True,
        blank=True,
        verbose_name=_("Preview Video"),
        help_text=_("An embedded preview or introduction video."),
        use_json_field=True,
    )

    # === Content & Description ===
    overview = StreamField(
        OverviewBlock(template="django_grep/comp/blocks/content/heading_block.html"),
        blank=True,
        use_json_field=True,
        verbose_name=_("Course Overview"),
        help_text=_("Main course description content."),
    )
    short_description = models.TextField(
        blank=True,
        verbose_name=_("Short Description"),
        help_text=_("Brief description for course cards and previews.")
    )
    description = RichTextField(
        blank=True,
        features=['h2', 'h3', 'bold', 'italic', 'link'],
        verbose_name=_("Full Description"),
        help_text=_("Detailed course description.")
    )

    # === Learning Objectives & Requirements ===
    objectives = models.TextField(
        blank=True,
        verbose_name=_("Learning Objectives"),
        help_text=_("What students will learn (one per line)")
    )
    requirements = models.TextField(
        blank=True,
        verbose_name=_("Requirements"),
        help_text=_("Prerequisites and requirements (one per line)")
    )
    target_audience = models.TextField(
        blank=True,
        verbose_name=_("Target Audience"),
        help_text=_("Who this course is for (one per line)")
    )

    # === Instructor ===
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses_taught",
        verbose_name=_("Instructor"),
        limit_choices_to={'groups__name': 'Instructors'}
    )

    # === Pricing & Enrollment ===
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Base Price"),
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        blank=True,
        verbose_name=_("Original Price"),
        help_text=_("Price before discount for showing strikethrough")
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Discount Percentage"),
    )
    discount_until = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Discount Valid Until"),
    )
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Tax %"),
        help_text=_("Tax percentage applied after discount (e.g. 15 for 15%)."),
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Final Price"),
        help_text=_("Auto-calculated: (price - discount) + tax. Do not edit."),
        editable=False,
    )
    coupon = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Coupon"),
        help_text=_("Optional coupon code attached to this course."),
    )
    enrolled_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Enrolled Students"),
    )

    # === Status & Visibility ===
    is_published = models.BooleanField(default=False, verbose_name=_("Published Status"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured Course"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    publication_date = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Publication Date")
    )

    # === Meta Information ===
    canonical_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Canonical URL"),
        help_text=_("Optional canonical URL for SEO")
    )

    language = models.CharField(
        max_length=100,
        default="en",
        verbose_name=_("Course Language"),
        choices=[
            ("en", _("English")),
            ("ar", _("Arabic")),
            ("es", _("Spanish")),
            ("fr", _("French")),
        ],
    )
    class DifficultyChoices(models.TextChoices):
        BEGINNER = "beginner", _("Beginner")
        INTERMEDIATE = "intermediate", _("Intermediate")
        ADVANCED = "advanced", _("Advanced")

    difficulty_level = models.CharField(
        max_length=20,
        verbose_name=_("Difficulty Level"),
        choices=DifficultyChoices.choices,
        default=DifficultyChoices.BEGINNER,
    )
    duration = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Duration (hours)"),
        help_text=_("Total course duration in hours")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))

    pass_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=70.00,
        verbose_name=_("Passing Percentage"),
        help_text=_("Percentage required to pass the course."),
    )
    has_certificate = models.BooleanField(
        default=False,
        verbose_name=_("Certificate Available"),
        help_text=_("Indicates if the course offers a certificate upon completion."),
    )

    # === Search & Panels ===
    search_fields = [
        index.SearchField("title", partial_match=True, boost=2),
        index.SearchField("overview"),
        index.SearchField("short_description"),
        index.SearchField("description"),
        index.SearchField("objectives"),
        index.FilterField("is_published"),
        index.FilterField("is_active"),
        index.FilterField("language"),
        index.FilterField("difficulty_level"),
        index.FilterField("has_certificate"),
        index.FilterField("is_featured"),
    ]

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("slug"),
                FieldPanel("specializations"),
                FieldPanel("categories"),
                FieldPanel("tags"),
                FieldPanel("instructor"),
                FieldPanel("image"),
                FieldPanel("header_image"),
                FieldPanel("preview_video"),
                FieldPanel("language"),
                FieldPanel("difficulty_level"),
                FieldPanel("duration"),
                FieldPanel("canonical_url"),
            ],
            heading=_("Core Metadata"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("short_description"),
                FieldPanel("description"),
                FieldPanel("overview"),
                FieldPanel("objectives"),
                FieldPanel("requirements"),
                FieldPanel("target_audience"),
            ],
            heading=_("Course Content & Description"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("original_price"),
                FieldPanel("price"),
                FieldPanel("discount_percentage"),
                FieldPanel("discount_until"),
                FieldPanel("tax_percentage"),
                FieldPanel("coupon"),
                FieldPanel("enrolled_count"),
            ],
            heading=_("Pricing & Offers"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("is_published"),
                FieldPanel("is_active"),
                FieldPanel("is_featured"),
                FieldPanel("publication_date"),
                FieldPanel("has_certificate"),
                FieldPanel("pass_percentage"),
            ],
            heading=_("Visibility & Status"),
        ),
        InlinePanel("modules", heading=_("Course Modules"), label=_("Module")),
    ]

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        ordering = ["-publication_date", "-created_at"]
        indexes = [
            models.Index(fields=["slug", "publication_date"]),
            models.Index(fields=["is_published", "is_featured", "is_active"]),
            models.Index(fields=["difficulty_level", "language"]),
            models.Index(fields=["price"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title

    # === Properties for Template Context ===
    @property
    def current_price(self):
        """Calculate discounted price dynamically (without tax)."""
        if self.discount_percentage and (
            not self.discount_until or self.discount_until >= timezone.now().date()
        ):
            discount_amount = self.price * (self.discount_percentage / 100)
            return self.price - discount_amount
        return self.price

    @property
    def tax_amount(self):
        """Calculate tax on the discounted price."""
        return round(self.current_price * (self.tax_percentage / 100), 2) if self.tax_percentage else 0

    @property
    def price_with_tax(self):
        """Current price including tax."""
        return round(self.current_price + self.tax_amount, 2)

    @property
    def discount_percentage_calculated(self):
        """Calculate discount percentage based on original price."""
        if self.original_price and self.original_price > self.current_price:
            return int(((self.original_price - self.current_price) / self.original_price) * 100)
        return self.discount_percentage

    @property
    def url(self):
        """Return the URL for this course."""
        return reverse_lazy("lms:course", kwargs={"slug": self.slug})

    @property
    def total_lessons(self):
        """Get total number of lessons in this course."""
        return sum(module.lessons.count() for module in self.modules.all())

    @property
    def total_duration(self):
        """Calculate total duration from all lessons."""
        total_minutes = sum(
            lesson.duration for module in self.modules.all()
            for lesson in module.lessons.all()
        )
        return round(total_minutes / 60, 1)  # Convert to hours

    @property
    def resources_count(self):
        """Count total resources across all lessons."""
        return sum(
            lesson.resources.count() for module in self.modules.all()
            for lesson in module.lessons.all()
        )

    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        from django.db.models import Avg
        result = self.reviews.aggregate(Avg('rating'))
        return result['rating__avg'] or 0.0

    @property
    def reviews_count(self):
        """Count total reviews."""
        return self.reviews.count()

    @property
    def objectives_list(self):
        """Return objectives as list."""
        return [obj.strip() for obj in self.objectives.split('\n') if obj.strip()]

    @property
    def requirements_list(self):
        """Return requirements as list."""
        return [req.strip() for req in self.requirements.split('\n') if req.strip()]

    @property
    def target_audience_list(self):
        """Return target audience as list."""
        return [audience.strip() for audience in self.target_audience.split('\n') if audience.strip()]

    @property
    def has_preview_lessons(self):
        """Check if course has any preview lessons."""
        return any(
            lesson.is_preview for module in self.modules.all()
            for lesson in module.lessons.all()
        )

    @property
    def is_discounted(self):
        """Check if course is currently discounted."""
        if self.discount_percentage and self.discount_percentage > 0:
            if not self.discount_until or self.discount_until >= timezone.now().date():
                return True
        return False

    @property
    def is_free(self):
        """Check if course is free."""
        return self.price == 0

    # === Caching Methods ===
    @property
    def is_cached(self):
        """Check if course is cached."""
        cache_key = self._generate_cache_key('detail', self.slug)
        return cache.get(cache_key) is not None

    # === Methods ===
    def _compute_final_price(self):
        """Compute final_price = (price - discount) + tax."""
        from decimal import Decimal
        base = self.price or Decimal("0.00")
        discount_pct = self.discount_percentage or Decimal("0.00")
        tax_pct = self.tax_percentage or Decimal("0.00")

        # Apply discount (only if within validity)
        if discount_pct and (
            not self.discount_until or self.discount_until >= timezone.now().date()
        ):
            base = base - (base * discount_pct / 100)

        # Apply tax
        if tax_pct:
            base = base + (base * tax_pct / 100)

        return round(base, 2)

    def save(self, *args, **kwargs):
        """Auto-generate slug, compute final_price, and handle caching."""
        # Generate slug if not provided
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Auto-compute final_price
        self.final_price = self._compute_final_price()

        # Set publication date when publishing
        is_publishing = not self.is_published and kwargs.get('is_published', self.is_published)
        if is_publishing and not self.publication_date:
            self.publication_date = timezone.now()

        # Call parent save
        super().save(*args, **kwargs)

        # Invalidate cache on save
        if self.is_published:
            self.invalidate_all_cache()

    def delete(self, *args, **kwargs):
        """Invalidate cache before deletion."""
        self.invalidate_all_cache()
        super().delete(*args, **kwargs)

    # -----------------------------------------------------------------
    # Helper Methods for Views (Resolution for AttributeErrors)
    # -----------------------------------------------------------------

    @classmethod
    def get_course_details(cls, slug: str) -> Dict[str, Any] | None:
        """
        Get complete course details with related data, optimized for caching.
        Called by FrontCourseDetailView.get_course_context.
        """
        cache_key = f"course_details:{slug}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            # Use Course.get_or_cache for the instance
            course = cls.get_or_cache(slug)
            if not course:
                return None

            details = {
                "course": course,
                "course_description": course.description,
                "course_modules": cls.get_course_modules(course),
                "instructor": getattr(course, "instructor", None),
            }

            # Cache the constructed dict for performance
            cache.set(cache_key, details, 3600)
            return details
        except Exception as e:
            logger.error(f"Error in Course.get_course_details for slug {slug}: {e}")
            return None

    @classmethod
    def get_course_modules(cls, course: Course) -> Any:
        """
        Get modules for a given course instance.
        """
        from plugins.lms.services.lessons import LessonsService

        try:
            return LessonsService().get_course_modules(course)
        except Exception as e:
            logger.error(f"Error in Course.get_course_modules: {e}")
            return []

    @classmethod
    def get_cached_course(cls, identifier: Any) -> Any:
        """
        Wrapper for get_or_cache to satisfy view requirements.
        """
        return cls.get_or_cache(identifier)

    @classmethod
    def get_cached_search_results(
        cls, query=None, filters=None, page=1, per_page=12
    ) -> Dict[str, Any]:
        """
        Get cached search results using CourseService.
        """
        from plugins.lms.services.courses import CourseService

        filters = filters or {}
        if query:
            filters["search"] = query

        try:
            return CourseService().get_published_courses_cached(
                filters=filters, limit=per_page, offset=(int(page) - 1) * per_page
            )
        except Exception as e:
            logger.error(f"Error in Course.get_cached_search_results: {e}")
            return {"courses": [], "total_count": 0}

    def get_average_rating(self) -> float:
        """Method alias for average_rating property."""
        return self.average_rating

    def get_duration_display(self) -> str:
        """Format duration for display."""
        return f"{self.duration} hours"

