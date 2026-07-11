from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from embed_video.fields import EmbedVideoField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.embeds.blocks import EmbedBlock as SimpleVideoBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock
from wagtail.models import Orderable


# -------------------------------------------------------------------
# LESSON MODEL
# -------------------------------------------------------------------
class Lesson(Orderable, ClusterableModel):
    """Individual lesson within a module."""

    module = ParentalKey(
        "Module",
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name=_("Parent Module"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Lesson Order"))
    title = models.CharField(max_length=200, verbose_name=_("Lesson Title"))
    slug = models.SlugField(
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("Unique identifier for URL structure."),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Brief description of this lesson"),
    )
    objectives = models.TextField(
        blank=True,
        verbose_name=_("Learning Objectives"),
        help_text=_("Enter each objective on a new line"),
    )

    # Content
    content = StreamField(
        [
            (
                "rich_text",
                blocks.RichTextBlock(
                    features=["bold", "italic", "link", "ol", "ul"],
                    label=_("Rich Text"),
                ),
            ),
            ("video", SimpleVideoBlock(template="blocks/media/video_lite.html")),
            ("image", SimpleImageBlock(template="blocks/media/image_lite.html")),
            (
                "code",
                blocks.TextBlock(
                    label=_("Code Snippet"),
                    help_text=_("Add code with syntax highlighting"),
                ),
            ),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Lesson Content"),
    )

    # Media
    video_url = EmbedVideoField(
        blank=True,
        verbose_name=_("Video URL"),
        help_text=_("YouTube, Vimeo, or other embed video URL"),
    )
    video_file = models.FileField(
        upload_to="lesson_videos/", blank=True, null=True, verbose_name=_("Video File")
    )
    thumbnail = models.ImageField(
        upload_to="lesson_thumbnails/",
        verbose_name=_("Thumbnail"),
        help_text=_("Preview image for the lesson"),
        blank=True,
        null=True,
    )

    # Meta
    duration = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Duration (minutes)"),
        help_text=_("Lesson duration in minutes"),
    )
    is_preview = models.BooleanField(
        default=False,
        verbose_name=_("Preview Lesson"),
        help_text=_("Make this lesson available for free preview"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    has_quiz = models.BooleanField(
        default=False,
        verbose_name=_("Includes Quiz"),
        help_text=_("Check if this lesson contains an assessment"),
    )
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0, verbose_name=_("Average Rating")
    )
    num_reviews = models.PositiveIntegerField(default=0, verbose_name=_("Review Count"))
    additional_resources = models.FileField(
        upload_to="lesson_resources/%Y/%m/%d/",
        verbose_name=_("Additional Resources"),
        help_text=_("Supplementary materials for download"),
        blank=True,
        null=True,
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("slug"),
                FieldPanel("description"),
                FieldPanel("objectives"),
                FieldPanel("order"),
                FieldPanel("duration"),
                FieldPanel("is_preview"),
                FieldPanel("is_active"),
                FieldPanel("has_quiz"),
            ],
            heading=_("Lesson Information"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("video_url"),
                FieldPanel("video_file"),
                FieldPanel("thumbnail"),
                FieldPanel("additional_resources"),
            ],
            heading=_("Media Content"),
        ),
        FieldPanel("content"),
        InlinePanel("resources", heading=_("Lesson Resources"), label=_("Resource")),
    ]

    class Meta:
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "module"], name="unique_lesson_order_per_module"
            ),
            models.UniqueConstraint(
                fields=["slug", "module"], name="unique_slug_per_module"
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.module.title}"

    @property
    def course(self):
        """Get the parent course."""
        return self.module.course

    @property
    def objectives_list(self):
        """Return objectives as a list."""
        if not self.objectives:
            return []
        return [obj.strip() for obj in self.objectives.split("\n") if obj.strip()]

    @property
    def url(self):
        """Get lesson URL."""
        return reverse_lazy("lms:lesson_watch", kwargs={"lesson_id": self.id})

    @property
    def duration_minutes(self):
        """Get duration in minutes for display."""
        return self.duration

    @property
    def duration_seconds(self):
        """Get duration in seconds for video players."""
        return self.duration * 60

    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        from django.utils.text import slugify

        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Lesson.objects.filter(slug=slug, module=self.module).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


# -------------------------------------------------------------------
# LESSON RESOURCE MODEL
# -------------------------------------------------------------------
class LessonResource(Orderable):
    """Downloadable resources for lessons."""

    lesson = ParentalKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="resources",
        verbose_name=_("Parent Lesson"),
    )
    title = models.CharField(max_length=200, verbose_name=_("Resource Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    file = models.FileField(upload_to="lesson_resources/", verbose_name=_("File"))
    resource_type = models.CharField(
        max_length=50,
        choices=[
            ("slides", _("Slides")),
            ("code", _("Code Files")),
            ("document", _("Document")),
            ("exercise", _("Exercise")),
            ("other", _("Other")),
        ],
        default="document",
        verbose_name=_("Resource Type"),
    )
    is_free = models.BooleanField(
        default=False,
        verbose_name=_("Free Resource"),
        help_text=_("Available without enrollment"),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("file"),
        FieldPanel("resource_type"),
        FieldPanel("is_free"),
    ]

    class Meta:
        verbose_name = _("Lesson Resource")
        verbose_name_plural = _("Lesson Resources")
        # ordering = ["order"]

    def __str__(self):
        return f"{self.title} - {self.lesson.title}"

    @property
    def file_size(self):
        """Get human-readable file size."""
        if self.file:
            return self.file.size
        return 0

    def get_file_size_display(self):
        """Display file size in human-readable format."""
        size = self.file_size
        if size == 0:
            return "0 Bytes"

        for unit in ["Bytes", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


# # =====================
# # QUIZ MODELS
# # =====================
# class QuizQuestion(ClusterableModel, models.Model):
#     """Base question model for all question types"""

#     QUESTION_TYPES = (
#         ("multiple_choice", _("Multiple Choice")),
#         ("true_false", _("True/False")),
#         ("short_answer", _("Short Answer")),
#         ("file_upload", _("File Upload")),
#     )

#     question_type = models.CharField(
#         max_length=20, choices=QUESTION_TYPES, verbose_name=_("Question Type")
#     )
#     question_text = models.TextField(verbose_name=_("Question Text"))
#     points = models.PositiveIntegerField(default=1, verbose_name=_("Points"))
#     document = models.ForeignKey(
#         Document,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         verbose_name=_("Supporting Document"),
#     )
#     explanation = RichTextField(blank=True, verbose_name=_("Explanation"))
#     # multiple_choice_options = models.ManyToManyField(
#     #     "MultipleChoiceOption", blank=True, verbose_name=_("Multiple Choice Options")
#     # )

#     panels = [
#         FieldPanel("question_type"),
#         FieldPanel("question_text"),
#         FieldPanel("points"),
#         FieldPanel("document"),
#         FieldPanel("explanation"),
#         InlinePanel("multiple_choice_options"),
#     ]

#     def __str__(self):
#         return f"{self.get_question_type_display()}: {self.question_text[:50]}..."

#     class Meta:
#         verbose_name = _("Question")
#         verbose_name_plural = _("Questions")


# class MultipleChoiceOption(Orderable):
#     """Options for multiple choice questions"""

#     option_text = models.CharField(max_length=500, verbose_name=_("Option Text"))
#     is_correct = models.BooleanField(default=False, verbose_name=_("Is Correct"))
#     question = ParentalKey(
#         QuizQuestion,
#         related_name="multiple_choice_options",
#         on_delete=models.CASCADE,
#         verbose_name=_("Question"),
#     )

#     panels = [
#         FieldPanel("option_text"),
#         FieldPanel("is_correct"),
#     ]

#     def __str__(self):
#         return self.option_text


# class Quiz(ClusterableModel, DefaultBase):
#     """Quiz model with form generation capability"""

#     COURSE_LEVELS = (
#         ("course", _("Course")),
#         ("module", _("Module")),
#         ("lesson", _("Lesson")),
#     )

#     title = models.CharField(max_length=255)
#     slug = models.SlugField(unique=True)
#     description = RichTextField(blank=True)
#     level = models.CharField(
#         max_length=10, choices=COURSE_LEVELS, verbose_name=_("Course Level")
#     )
#     parent_page = models.ForeignKey(
#         Page,
#         on_delete=models.CASCADE,
#         related_name="quizzes",
#         verbose_name=_("Parent Page"),
#     )
#     course = models.ForeignKey(
#         "Course",
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="quizzes",
#         verbose_name=_("Course"),
#     )
#     passing_score = models.PositiveIntegerField(default=70)
#     max_attempts = models.PositiveIntegerField(default=3)
#     questions = models.ManyToManyField(
#         QuizQuestion, through="QuizQuestionOrder", verbose_name=_("Questions")
#     )
#     required_documents = models.ManyToManyField(
#         Document, blank=True, verbose_name=_("Required Documents")
#     )

#     panels = [
#         FieldPanel("title"),
#         FieldPanel("slug"),
#         FieldPanel("description"),
#         FieldPanel("level"),
#         PageChooserPanel("parent_page"),
#         FieldPanel("passing_score"),
#         FieldPanel("max_attempts"),
#         InlinePanel("question_orders", heading="Questions"),
#         FieldPanel("required_documents"),
#     ]

#     def has_quiz(self):
#         return self.questions.exists()

#     def get_quiz_form(self):
#         """Generate a dynamic form based on questions"""

#         class QuizForm(forms.Form):
#             def __init__(self, *args, **kwargs):
#                 super().__init__(*args, **kwargs)
#                 for order in self.instance.question_orders.all():
#                     question = order.question
#                     field_name = f"question_{question.id}"

#                     if (
#                         question.question_type == "multiple_choice"
#                         and question.multiple_choice_options.exists()
#                     ):
#                         choices = [
#                             (opt.id, opt.option_text)
#                             for opt in question.multiple_choice_options.all()
#                         ]
#                         self.fields[field_name] = forms.ChoiceField(
#                             label=question.question_text,
#                             choices=choices,
#                             widget=forms.RadioSelect,
#                             required=True,
#                         )
#                     elif question.question_type == "true_false":
#                         self.fields[field_name] = forms.BooleanField(
#                             label=question.question_text,
#                             required=False,
#                             widget=forms.CheckboxInput,
#                         )
#                     elif question.question_type == "short_answer":
#                         self.fields[field_name] = forms.CharField(
#                             label=question.question_text,
#                             widget=forms.Textarea(attrs={"rows": 3}),
#                             required=True,
#                         )
#                     elif question.question_type == "file_upload":
#                         self.fields[field_name] = forms.FileField(
#                             label=question.question_text, required=True
#                         )

#         form = QuizForm()
#         form.instance = self
#         return form

#     def __str__(self):
#         return self.title

#     class Meta:
#         verbose_name = _("Quiz")
#         verbose_name_plural = _("Quizzes")


# class QuizQuestionOrder(Orderable):
#     """Ordering of questions within a quiz"""

#     quiz = ParentalKey(Quiz, related_name="question_orders", on_delete=models.CASCADE)
#     question = models.ForeignKey(
#         QuizQuestion, on_delete=models.CASCADE, verbose_name=_("Question")
#     )

#     panels = [
#         FieldPanel("question"),
#     ]

#     def __str__(self):
#         return f"{self.quiz.title} - {self.question.question_text[:50]}..."
