"""
Quiz System Models for LMS.
"""
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Quiz(models.Model):
    """
    Quiz associated with a lesson.

    Attributes:
        lesson: The lesson this quiz belongs to
        title: Quiz title
        description: Quiz description
        passing_score: Minimum score to pass (percentage)
        time_limit: Time limit in minutes (0 = no limit)
        max_attempts: Maximum attempts allowed (0 = unlimited)
        shuffle_questions: Whether to randomize question order
        show_correct_answers: Whether to show correct answers after completion
    """

    lesson = models.ForeignKey(
        "lms.Lesson",
        on_delete=models.CASCADE,
        related_name="quizzes",
        verbose_name=_("Lesson"),
        null=True,
        blank=True,
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
    )

    passing_score = models.PositiveIntegerField(
        default=70,
        verbose_name=_("Passing Score (%)"),
        help_text=_("Minimum percentage to pass"),
    )

    time_limit = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Time Limit (minutes)"),
        help_text=_("0 for no time limit"),
    )

    max_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Max Attempts"),
        help_text=_("0 for unlimited attempts"),
    )

    shuffle_questions = models.BooleanField(
        default=False,
        verbose_name=_("Shuffle Questions"),
    )

    show_correct_answers = models.BooleanField(
        default=True,
        verbose_name=_("Show Correct Answers"),
        help_text=_("Show correct answers after quiz completion"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Quiz")
        verbose_name_plural = _("Quizzes")
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_questions(self):
        """Get all questions, optionally shuffled."""
        questions = self.questions.filter(is_active=True)
        if self.shuffle_questions:
            return questions.order_by("?")
        return questions.order_by("order")

    @property
    def question_count(self):
        return self.questions.filter(is_active=True).count()


class QuizQuestion(models.Model):
    """
    Individual quiz question.
    """

    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = "multiple_choice", _("Multiple Choice")
        TRUE_FALSE = "true_false", _("True/False")
        SHORT_ANSWER = "short_answer", _("Short Answer")
        MULTIPLE_SELECT = "multiple_select", _("Multiple Select")

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("Quiz"),
    )

    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
        verbose_name=_("Question Type"),
    )

    question_text = models.TextField(
        verbose_name=_("Question"),
    )

    explanation = models.TextField(
        blank=True,
        verbose_name=_("Explanation"),
        help_text=_("Explanation shown after answering"),
    )

    points = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Points"),
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
    )

    class Meta:
        verbose_name = _("Quiz Question")
        verbose_name_plural = _("Quiz Questions")
        ordering = ["order"]

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order + 1}"

    def get_choices(self):
        """Get answer choices for this question."""
        return self.choices.all().order_by("order")


class QuizChoice(models.Model):
    """
    Answer choice for a quiz question.
    """

    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name=_("Question"),
    )

    choice_text = models.CharField(
        max_length=500,
        verbose_name=_("Choice Text"),
    )

    is_correct = models.BooleanField(
        default=False,
        verbose_name=_("Is Correct"),
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
    )

    class Meta:
        verbose_name = _("Quiz Choice")
        verbose_name_plural = _("Quiz Choices")
        ordering = ["order"]

    def __str__(self):
        return self.choice_text[:50]


class QuizAttempt(models.Model):
    """
    User's quiz attempt tracking.
    """

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", _("In Progress")
        COMPLETED = "completed", _("Completed")
        TIMED_OUT = "timed_out", _("Timed Out")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
        verbose_name=_("User"),
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name=_("Quiz"),
    )

    attempt_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        verbose_name=_("Status"),
    )

    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Score (%)"),
    )

    points_earned = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Points Earned"),
    )

    points_possible = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Points Possible"),
    )

    passed = models.BooleanField(
        null=True,
        blank=True,
        verbose_name=_("Passed"),
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Started At"),
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Completed At"),
    )

    time_spent = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Time Spent (seconds)"),
    )

    class Meta:
        verbose_name = _("Quiz Attempt")
        verbose_name_plural = _("Quiz Attempts")
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "quiz"]),
            models.Index(fields=["attempt_id"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.quiz.title} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.attempt_id:
            self.attempt_id = f"ATT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def complete(self):
        """Mark attempt as completed and calculate score."""
        from django.utils import timezone

        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()

        # Calculate time spent
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.time_spent = int(delta.total_seconds())

        # Calculate score
        if self.points_possible > 0:
            self.score = (self.points_earned / self.points_possible) * 100
            self.passed = self.score >= self.quiz.passing_score

        self.save()


class QuizAnswer(models.Model):
    """
    User's answer to a quiz question.
    """

    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("Attempt"),
    )

    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name="user_answers",
        verbose_name=_("Question"),
    )

    selected_choices = models.ManyToManyField(
        QuizChoice,
        blank=True,
        related_name="selected_in_answers",
        verbose_name=_("Selected Choices"),
    )

    text_answer = models.TextField(
        blank=True,
        verbose_name=_("Text Answer"),
        help_text=_("For short answer questions"),
    )

    is_correct = models.BooleanField(
        null=True,
        blank=True,
        verbose_name=_("Is Correct"),
    )

    points_awarded = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Points Awarded"),
    )

    answered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Answered At"),
    )

    class Meta:
        verbose_name = _("Quiz Answer")
        verbose_name_plural = _("Quiz Answers")
        unique_together = [["attempt", "question"]]

    def __str__(self):
        return f"{self.attempt} - Q{self.question.order + 1}"

    def evaluate(self):
        """Evaluate the answer and award points."""
        question = self.question

        if question.question_type in [
            QuizQuestion.QuestionType.MULTIPLE_CHOICE,
            QuizQuestion.QuestionType.TRUE_FALSE,
        ]:
            # Single correct answer
            correct_choice = question.choices.filter(is_correct=True).first()
            selected = self.selected_choices.first()
            self.is_correct = selected == correct_choice if correct_choice else False

        elif question.question_type == QuizQuestion.QuestionType.MULTIPLE_SELECT:
            # Multiple correct answers
            correct_ids = set(question.choices.filter(is_correct=True).values_list("id", flat=True))
            selected_ids = set(self.selected_choices.values_list("id", flat=True))
            self.is_correct = correct_ids == selected_ids

        else:
            # Short answer - needs manual grading
            self.is_correct = None

        if self.is_correct:
            self.points_awarded = question.points
        else:
            self.points_awarded = 0

        self.save()
        return self.is_correct
