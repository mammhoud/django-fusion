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
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail.snippets.views.snippets import SnippetViewSet
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.models import Orderable


class Course(ClusterableModel, index.Indexed):
    """A published learning product managed as a Wagtail snippet."""

    title = models.CharField(max_length=200, unique=True, verbose_name=_("Title"))
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_description = models.TextField(blank=True, verbose_name=_("Short description"))
    description = RichTextField(blank=True, verbose_name=_("Description"))
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="learning_courses",
        verbose_name=_("Instructor"),
    )
    language = models.CharField(max_length=10, default="en")
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel(
            [FieldPanel("title"), FieldPanel("slug"), FieldPanel("short_description"), FieldPanel("description")],
            heading=_("Course content"),
        ),
        MultiFieldPanel(
            [FieldPanel("instructor"), FieldPanel("language"), FieldPanel("difficulty"), FieldPanel("duration_hours")],
            heading=_("Learning details"),
        ),
        MultiFieldPanel(
            [FieldPanel("price"), FieldPanel("is_published"), FieldPanel("is_featured"), FieldPanel("has_certificate")],
            heading=_("Commercial settings"),
        ),
        InlinePanel("modules", heading=_("Modules"), label=_("Module")),
    ]
    search_fields = [
        index.SearchField("title", partial_match=True, boost=2),
        index.SearchField("short_description"),
        index.SearchField("description"),
        index.FilterField("is_published"),
        index.FilterField("difficulty"),
        index.FilterField("language"),
    ]

    class Meta:
        ordering = ["-is_featured", "title"]
        indexes = [models.Index(fields=["is_published", "is_featured"])]

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
    def module_count(self):
        return self.modules.count()

    @property
    def lesson_count(self):
        return Lesson.objects.filter(module__course=self, is_active=True).count()


class Module(Orderable, ClusterableModel):
    course = ParentalKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    panels = [FieldPanel("title"), FieldPanel("description"), FieldPanel("order"), InlinePanel("lessons", label=_("Lesson"))]

    class Meta:
        ordering = ["order"]
        constraints = [models.UniqueConstraint(fields=["course", "order"], name="learning_module_order")]

    def __str__(self):
        return self.title


class Lesson(Orderable):
    module = ParentalKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = RichTextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("title"), FieldPanel("description"), FieldPanel("content"),
        FieldPanel("duration_minutes"), FieldPanel("is_preview"), FieldPanel("is_active"), FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order"]
        constraints = [models.UniqueConstraint(fields=["module", "order"], name="learning_lesson_order")]

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """User entitlement for a course; payments can attach later without changing access logic."""

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    progress = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    provider = models.CharField(max_length=40, blank=True, help_text=_("Payment provider reference, when configured."))
    provider_reference = models.CharField(max_length=160, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-enrolled_at"]
        constraints = [models.UniqueConstraint(fields=["user", "course"], name="learning_user_course")]
        indexes = [models.Index(fields=["user", "status"]), models.Index(fields=["course", "status"])]

    def __str__(self):
        return f"{self.user} · {self.course}"

    @property
    def has_verified_payment(self) -> bool:
        """Whether this row carries enough evidence to unlock a paid course."""
        return self.course.is_free or (
            bool(self.provider_reference)
            and self.amount_paid >= self.course.price
        )

    def mark_progress(self, value: int):
        self.progress = max(0, min(100, int(value)))
        self.last_accessed_at = timezone.now()
        if self.progress >= 100:
            self.progress = 100
            self.status = self.Status.COMPLETED
            self.completed_at = self.completed_at or timezone.now()
        elif self.status == self.Status.COMPLETED:
            self.status = self.Status.ACTIVE
            self.completed_at = None
        self.save(update_fields=["progress", "status", "completed_at", "last_accessed_at"])

    def recalculate_progress(self) -> int:
        """Persist lesson-derived progress and keep certificates consistent.

        Views call this explicitly; the signal remains a compatibility safety
        net for admin edits and imports. A certificate is revoked when a
        learner toggles below completion and issued again when they finish.
        """
        total = self.course.lesson_count
        completed = self.lesson_progress.filter(completed=True).count()
        value = round(completed / total * 100) if total else 0
        self.mark_progress(value)
        if self.course.has_certificate:
            if value >= 100:
                Certificate.objects.get_or_create(user=self.user, course=self.course)
            else:
                Certificate.objects.filter(user=self.user, course=self.course).delete()
        return value


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="learner_progress")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["enrollment", "lesson"], name="learning_enrollment_lesson")]

    def set_completed(self, completed: bool = True):
        self.completed = completed
        self.completed_at = timezone.now() if completed else None
        self.save(update_fields=["completed", "completed_at", "updated_at"])


class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_certificates")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="certificates")
    certificate_id = models.CharField(max_length=32, unique=True, editable=False, default="")
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "course"], name="learning_user_course_certificate")]

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    body = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["course", "user"], name="learning_course_user_review")]


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_wishlist")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "course"], name="learning_user_course_wishlist")]


class CourseSnippetViewSet(SnippetViewSet):
    model = Course
    menu_label = _("Courses")
    menu_icon = "book"
    add_to_admin_menu = True
    list_display = ["title", "instructor", "difficulty", "price", "is_published", "updated_at"]
    list_filter = ["is_published", "is_featured", "difficulty", "language"]
    search_fields = ["title", "short_description", "instructor__email"]


