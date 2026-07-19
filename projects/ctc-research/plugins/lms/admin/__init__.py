"""
Full LMS admin with Unfold for all LMS models.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin as BaseImportExportModelAdmin
from unfold.admin import ModelAdmin, StackedInline, TabularInline


class ImportExportModelAdmin(BaseImportExportModelAdmin, ModelAdmin):
    """Combines django-import-export with Unfold styling."""
    pass


from ..models import Certificate, Classes, Enrollment, Quiz, Schedule, Wishlist
from ..models.courses import Course, Module
from ..models.quiz import QuizChoice, QuizQuestion
from ..models.review import Review

# ─────────────────────────────────────────────
# COURSE INLINES
# ─────────────────────────────────────────────

class ModuleInline(StackedInline):
    model = Module
    extra = 0
    fields = ("title", "order", "description", "has_quiz", "is_preview")
    show_change_link = True
    verbose_name = _("Module")
    verbose_name_plural = _("Modules")


class EnrollmentInline(TabularInline):
    model = Enrollment
    extra = 0
    fields = ("student", "status", "progress", "payment_status", "enrolled_at")
    readonly_fields = ("enrolled_at",)
    show_change_link = True
    verbose_name = _("Enrollment")
    verbose_name_plural = _("Enrollments")


class ReviewInline(TabularInline):
    model = Review
    extra = 0
    fields = ("profile", "rating", "is_displayed", "created_at")
    readonly_fields = ("created_at",)
    show_change_link = True
    verbose_name = _("Review")
    verbose_name_plural = _("Reviews")


# ─────────────────────────────────────────────
# MODULE INLINES
# ─────────────────────────────────────────────

class LessonInline(TabularInline):
    """Inline for lessons within a module."""
    verbose_name = _("Lesson")
    verbose_name_plural = _("Lessons")
    extra = 0
    show_change_link = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    # Dynamically set model to avoid import errors if Lesson doesn't exist
    @classmethod
    def _get_model(cls):
        try:
            from ..models.courses.specification import Lesson
            return Lesson
        except ImportError:
            return None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

try:
    from ..models.courses.specification import Lesson

    class LessonInline(TabularInline):  # type: ignore[no-redef]
        model = Lesson
        extra = 0
        fields = ("title", "order", "duration", "is_preview", "is_active")
        show_change_link = True
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")

except ImportError:
    pass


# ─────────────────────────────────────────────
# QUIZ INLINES
# ─────────────────────────────────────────────

class QuizChoiceInline(TabularInline):
    model = QuizChoice
    extra = 2
    fields = ("choice_text", "is_correct", "order")
    verbose_name = _("Choice")
    verbose_name_plural = _("Choices")


class QuizQuestionInline(StackedInline):
    model = QuizQuestion
    extra = 0
    fields = ("question_type", "question_text", "points", "order", "is_active")
    show_change_link = True
    verbose_name = _("Question")
    verbose_name_plural = _("Questions")


# ─────────────────────────────────────────────
# COURSE ADMIN
# ─────────────────────────────────────────────

@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True

    list_display = (
        "title", "instructor", "difficulty_level",
        "price", "is_published", "is_featured", "enrolled_count",
    )
    list_filter = (
        "is_published", "is_featured", "difficulty_level",
        "language", "has_certificate",
    )
    search_fields = ("title", "instructor__username", "instructor__email")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "final_price", "enrolled_count")
    inlines = [ModuleInline, EnrollmentInline, ReviewInline]

    fieldsets = (
        (_("Core Information"), {
            "fields": (
                "title", "slug", "instructor", "specializations",
                "language", "difficulty_level", "duration",
            )
        }),
        (_("Media"), {
            "fields": ("image", "header_image"),
            "classes": ("collapse",)
        }),
        (_("Content"), {
            "fields": (
                "short_description", "description",
                "objectives", "requirements", "target_audience",
            ),
            "classes": ("collapse",)
        }),
        (_("Pricing"), {
            "fields": (
                "price", "original_price", "discount_percentage",
                "discount_until", "tax_percentage", "final_price", "coupon",
            ),
            "classes": ("collapse",)
        }),
        (_("Status & Visibility"), {
            "fields": (
                "is_published", "is_active", "is_featured",
                "publication_date", "has_certificate", "pass_percentage",
            )
        }),
        (_("Statistics"), {
            "fields": ("enrolled_count", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


# ─────────────────────────────────────────────
# MODULE ADMIN
# ─────────────────────────────────────────────

@admin.register(Module)
class ModuleAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True

    list_display = ("title", "course", "order", "lessons_count", "has_quiz")
    list_filter = ("course", "has_quiz", "is_preview")
    search_fields = ("title", "course__title")
    readonly_fields = ("lessons_count",)

    fieldsets = (
        (_("Module Information"), {
            "fields": ("course", "title", "order", "description")
        }),
        (_("Settings"), {
            "fields": ("is_preview", "is_extra", "has_quiz", "has_assignment")
        }),
        (_("Statistics"), {
            "fields": ("lessons_count",),
            "classes": ("collapse",)
        }),
    )

    def get_inlines(self, request, obj=None):
        try:
            from ..models.courses.specification import Lesson
            return [LessonInline]
        except ImportError:
            return []


# ─────────────────────────────────────────────
# ENROLLMENT ADMIN
# ─────────────────────────────────────────────

@admin.register(Enrollment)
class EnrollmentAdmin(ImportExportModelAdmin):
    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True

    list_display = (
        "student", "course", "status", "progress",
        "payment_status", "enrolled_at",
    )
    list_filter = ("status", "payment_status", "is_active")
    search_fields = (
        "student__username", "student__email",
        "course__title",
    )
    readonly_fields = ("enrolled_at", "last_accessed_at")

    fieldsets = (
        (_("Enrollment"), {
            "fields": ("student", "course", "is_active")
        }),
        (_("Progress"), {
            "fields": ("status", "progress", "completed_at")
        }),
        (_("Payment"), {
            "fields": (
                "payment_status", "payment_id",
                "amount_paid", "payment_reference", "transaction_date",
            ),
            "classes": ("collapse",)
        }),
        (_("Timestamps"), {
            "fields": ("enrolled_at", "last_accessed_at", "end_date"),
            "classes": ("collapse",)
        }),
    )


# ─────────────────────────────────────────────
# REVIEW ADMIN
# ─────────────────────────────────────────────

@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True

    list_display = ("course", "profile", "rating", "is_displayed", "created_at")
    list_filter = ("rating", "is_displayed")
    search_fields = ("course__title", "profile__username", "comment")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (_("Review"), {
            "fields": ("course", "profile", "rating", "comment", "is_displayed")
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


# ─────────────────────────────────────────────
# CERTIFICATE ADMIN
# ─────────────────────────────────────────────

@admin.register(Certificate)
class CertificateAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True

    list_display = (
        "certificate_id", "user_name", "course_title",
        "completion_date", "issued_at",
    )
    list_filter = ("completion_date", "issued_at")
    search_fields = (
        "certificate_id", "user_name", "course_title",
        "user__username", "course__title",
    )
    readonly_fields = ("certificate_id", "issued_at")

    fieldsets = (
        (_("Certificate"), {
            "fields": (
                "certificate_id", "user", "course",
                "user_name", "course_title", "completion_date",
            )
        }),
        (_("File"), {
            "fields": ("pdf_file",),
            "classes": ("collapse",)
        }),
        (_("Timestamps"), {
            "fields": ("issued_at",),
            "classes": ("collapse",)
        }),
    )


# ─────────────────────────────────────────────
# CLASSES ADMIN
# ─────────────────────────────────────────────

@admin.register(Classes)
class ClassesAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True

    list_display = (
        "title", "course", "class_type", "status", "primary_instructor",
    )
    list_filter = ("status", "class_type", "course")
    search_fields = (
        "title", "course__title",
        "primary_instructor__username",
    )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (_("Class Information"), {
            "fields": (
                "course", "module", "class_type", "status", "sequence",
            )
        }),
        (_("Instructors"), {
            "fields": ("primary_instructor", "co_instructors")
        }),
        (_("Schedule"), {
            "fields": ("schedule",)
        }),
        (_("Content"), {
            "fields": ("objectives", "materials"),
            "classes": ("collapse",)
        }),
        (_("Settings"), {
            "fields": (
                "max_students", "is_mandatory",
                "requires_registration", "prerequisites",
            ),
            "classes": ("collapse",)
        }),
    )


# ─────────────────────────────────────────────
# SCHEDULE ADMIN
# ─────────────────────────────────────────────

@admin.register(Schedule)
class ScheduleAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True

    list_display = (
        "title", "start_date", "start_time",
        "schedule_type", "meeting_platform", "is_active",
    )
    list_filter = ("schedule_type", "meeting_platform", "is_active", "is_online")
    search_fields = ("title", "meeting_id", "location")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (_("Basic Information"), {
            "fields": ("title", "schedule_type", "is_active")
        }),
        (_("Date & Time"), {
            "fields": (
                "start_date", "end_date",
                "start_time", "end_time",
            )
        }),
        (_("Recurrence"), {
            "fields": ("recurrence_days", "recurrence_interval"),
            "classes": ("collapse",)
        }),
        (_("Meeting Details"), {
            "fields": (
                "meeting_platform", "meeting_link",
                "meeting_id", "meeting_passcode",
                "is_online", "is_hybrid", "location",
            )
        }),
        (_("Session Settings"), {
            "fields": (
                "max_participants", "is_recorded", "recording_link",
            ),
            "classes": ("collapse",)
        }),
    )


# ─────────────────────────────────────────────
# QUIZ ADMIN
# ─────────────────────────────────────────────

@admin.register(Quiz)
class QuizAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True

    list_display = (
        "title", "lesson", "passing_score",
        "time_limit", "max_attempts", "is_active",
    )
    list_filter = ("is_active", "shuffle_questions", "show_correct_answers")
    search_fields = ("title", "description", "lesson__title")
    readonly_fields = ("created_at", "updated_at")
    inlines = [QuizQuestionInline]

    fieldsets = (
        (_("Quiz Information"), {
            "fields": ("lesson", "title", "description", "is_active")
        }),
        (_("Settings"), {
            "fields": (
                "passing_score", "time_limit", "max_attempts",
                "shuffle_questions", "show_correct_answers",
            )
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


# ─────────────────────────────────────────────
# WISHLIST ADMIN
# ─────────────────────────────────────────────

@admin.register(Wishlist)
class WishlistAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True

    list_display = ("user", "course", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "course__title")
    readonly_fields = ("created_at",)

    fieldsets = (
        (_("Wishlist Item"), {
            "fields": ("user", "course", "notes")
        }),
        (_("Timestamps"), {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
