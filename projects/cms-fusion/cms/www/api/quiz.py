"""
Quiz API — CRUD for quizzes, questions, attempts, and grading (bolt-pattern).

All endpoints require authentication (token or session).
"""

from __future__ import annotations

import json
import logging
from datetime import timedelta

from django.db import models, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from www.api.data_adapter import bolt_view, login_required
from www.api.data.helpers import paginate_queryset, paginated_response, parse_body

from www.api.notifications import create_notification

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# Quiz CRUD
# ═══════════════════════════════════════════════════════════════════════


@bolt_view
@login_required
def quiz_list(request):
    """GET /apis/quizzes/ — List quizzes (instructor sees all, student sees active)."""
    from plugins.lms.models import Quiz

    if request.user.groups.filter(name="Instructors").exists() or request.user.is_staff:
        qs = Quiz.objects.all()
    else:
        qs = Quiz.objects.filter(is_active=True)

    qs = qs.select_related("lesson__module__course").order_by("-created_at")

    search = request.GET.get("search", "")
    if search:
        qs = qs.filter(title__icontains=search)

    course_id = request.GET.get("course_id")
    if course_id:
        qs = qs.filter(lesson__module__course_id=course_id)

    items, pagination = paginate_queryset(qs, request, default_per_page=20)
    serialized = [_serialize_quiz(q, request.user) for q in items]
    return paginated_response(items, pagination, request, serialized)


@bolt_view
@login_required
def quiz_detail(request, pk):
    """GET /apis/quizzes/<pk>/ — Get quiz with all questions and choices."""
    from plugins.lms.models import Quiz

    quiz = get_object_or_404(Quiz, pk=pk)
    data = _serialize_quiz(quiz, request.user, include_questions=True)
    return {"status": "success", "data": data}


@bolt_view
@login_required
def quiz_create(request):
    """POST /apis/quizzes/ — Create a new quiz."""
    from plugins.lms.models import Quiz

    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    if not request.user.groups.filter(name="Instructors").exists() and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403

    quiz = Quiz.objects.create(
        lesson_id=body.get("lesson_id"),
        title=body.get("title", "Untitled Quiz"),
        description=body.get("description", ""),
        passing_score=body.get("passing_score", 70),
        time_limit=body.get("time_limit", 0),
        max_attempts=body.get("max_attempts", 0),
        shuffle_questions=body.get("shuffle_questions", False),
        show_correct_answers=body.get("show_correct_answers", True),
        is_active=body.get("is_active", True),
    )
    return {"status": "success", "data": _serialize_quiz(quiz, request.user)}, 201


@bolt_view
@login_required
def quiz_update(request, pk):
    """PATCH /apis/quizzes/<pk>/ — Update quiz settings."""
    from plugins.lms.models import Quiz

    quiz = get_object_or_404(Quiz, pk=pk)
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    updatable_fields = [
        "title", "description", "passing_score", "time_limit",
        "max_attempts", "shuffle_questions", "show_correct_answers", "is_active",
        "lesson_id",
    ]
    for field in updatable_fields:
        if field in body:
            setattr(quiz, field, body[field])
    quiz.save()

    return {"status": "success", "data": _serialize_quiz(quiz, request.user)}


@bolt_view
@login_required
def quiz_delete(request, pk):
    """DELETE /apis/quizzes/<pk>/ — Delete a quiz."""
    from plugins.lms.models import Quiz

    quiz = get_object_or_404(Quiz, pk=pk)
    quiz.delete()
    return {"status": "success", "message": "Quiz deleted"}


# ═══════════════════════════════════════════════════════════════════════
# Questions CRUD
# ═══════════════════════════════════════════════════════════════════════


@bolt_view
@login_required
def question_create(request, quiz_pk):
    """POST /apis/quizzes/<quiz_pk>/questions/ — Add a question to a quiz."""
    from plugins.lms.models import Quiz, QuizQuestion

    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    max_order = QuizQuestion.objects.filter(quiz=quiz).aggregate(
        m=models.Max("order")
    )["m"] or 0

    question = QuizQuestion.objects.create(
        quiz=quiz,
        question_type=body.get("question_type", "multiple_choice"),
        question_text=body.get("question_text", ""),
        explanation=body.get("explanation", ""),
        points=body.get("points", 1),
        order=max_order + 1,
    )

    # Handle choices (for multiple_choice and true_false)
    choices_data = body.get("choices", [])
    for i, choice_data in enumerate(choices_data):
        QuizChoice.objects.create(
            question=question,
            choice_text=choice_data.get("text", ""),
            is_correct=choice_data.get("is_correct", False),
            order=i,
        )

    return {"status": "success", "data": _serialize_question(question)}, 201


@bolt_view
@login_required
def question_update(request, pk):
    """PATCH /apis/quizzes/questions/<pk>/ — Update a question."""
    from plugins.lms.models import QuizChoice, QuizQuestion

    question = get_object_or_404(QuizQuestion, pk=pk)
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    updatable_fields = [
        "question_type", "question_text", "explanation", "points", "order", "is_active",
    ]
    for field in updatable_fields:
        if field in body:
            setattr(question, field, body[field])
    question.save()

    # Update or recreate choices
    if "choices" in body:
        question.choices.all().delete()
        for i, choice_data in enumerate(body["choices"]):
            QuizChoice.objects.create(
                question=question,
                choice_text=choice_data.get("text", ""),
                is_correct=choice_data.get("is_correct", False),
                order=i,
            )

    return {"status": "success", "data": _serialize_question(question)}


@bolt_view
@login_required
def question_delete(request, pk):
    """DELETE /apis/quizzes/questions/<pk>/ — Delete a question."""
    from plugins.lms.models import QuizQuestion

    question = get_object_or_404(QuizQuestion, pk=pk)
    question.delete()
    return {"status": "success", "message": "Question deleted"}


# ═══════════════════════════════════════════════════════════════════════
# File Upload (for short answer/essay submissions)
# ═══════════════════════════════════════════════════════════════════════

ALLOWED_QUIZ_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.txt', '.rtf',
    '.png', '.jpg', '.jpeg', '.gif', '.webp',
    '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.scss',
    '.json', '.xml', '.yaml', '.yml', '.md', '.rst',
    '.zip', '.rar', '.7z',
}

MAX_QUIZ_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB

import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def _generate_quiz_filename(original: str) -> str:
    """Generate a unique filename for quiz uploads."""
    ext = Path(original).suffix
    stem = Path(original).stem[:50]
    unique = uuid.uuid4().hex[:12]
    safe_stem = "".join(c for c in stem if c.isalnum() or c in " _-.").strip()[:50]
    return f"quiz_{safe_stem}_{unique}{ext}" if safe_stem else f"quiz_file_{unique}{ext}"


@csrf_exempt
@bolt_view
def quiz_upload(request):
    """
    POST /apis/quizzes/upload/ — Upload a file for a quiz answer (short answer/essay).

    Accepts multipart/form-data with a single 'file' field.
    Returns the file URL and file name on success.

    Example:
        curl -X POST http://localhost:5071/apis/quizzes/upload/ \
          -H "Authorization: Bearer ..." \
          -F "file=@my_essay.pdf"
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)

    if 'file' not in request.FILES:
        return JsonResponse({"status": "error", "message": "No file provided. Use form field 'file'."}, status=400)

    uploaded_file = request.FILES['file']
    original_name = uploaded_file.name

    # Validate extension
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_QUIZ_EXTENSIONS:
        return JsonResponse({
            "status": "error",
            "message": f"File type '{ext}' is not allowed.",
        }, status=400)

    # Validate size
    if uploaded_file.size > MAX_QUIZ_UPLOAD_SIZE:
        max_mb = MAX_QUIZ_UPLOAD_SIZE // (1024 * 1024)
        return JsonResponse({
            "status": "error",
            "message": f"File too large. Maximum size is {max_mb} MB.",
        }, status=400)

    # Generate unique filename
    unique_name = _generate_quiz_filename(original_name)
    relative_path = f"quiz_uploads/{unique_name}"

    # Ensure media subdirectory exists
    media_root = Path(settings.MEDIA_ROOT)
    upload_dir = media_root / "quiz_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    saved_path = default_storage.save(relative_path, uploaded_file)
    file_url = f"{settings.MEDIA_URL}{saved_path}"

    logger.info(f"Quiz file uploaded: {original_name} -> {file_url} by user {request.user.id}")

    return JsonResponse({
        "status": "success",
        "data": {
            "file_url": file_url,
            "file_name": original_name,
        }
    })


# ═══════════════════════════════════════════════════════════════════════
# Question Reordering
# ═══════════════════════════════════════════════════════════════════════


@bolt_view
@login_required
def quiz_questions_reorder(request, quiz_pk):
    """
    POST /apis/quizzes/<quiz_pk>/questions/reorder/

    Batch-update question order for drag-to-reorder in the editor.

    Request body:
        {
            "questions": [
                {"id": 1, "order": 1},
                {"id": 2, "order": 2},
                {"id": 3, "order": 3},
            ]
        }

    All questions must belong to the specified quiz.
    """
    from plugins.lms.models import Quiz, QuizQuestion

    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    questions_data = body.get("questions", [])
    if not questions_data:
        return {"status": "error", "message": "No questions provided"}, 400

    # Validate all IDs belong to this quiz
    q_ids = [q["id"] for q in questions_data]
    existing = set(
        QuizQuestion.objects.filter(quiz=quiz, id__in=q_ids).values_list("id", flat=True)
    )

    for q_data in questions_data:
        qid = q_data.get("id")
        if qid not in existing:
            return {
                "status": "error",
                "message": f"Question {qid} does not belong to this quiz",
            }, 400

    # Update all question orders
    updated = []
    for q_data in questions_data:
        QuizQuestion.objects.filter(id=q_data["id"]).update(order=q_data["order"])
        updated.append({"id": q_data["id"], "order": q_data["order"]})

    return {"status": "success", "data": {"questions": updated}}


# ═══════════════════════════════════════════════════════════════════════
# Attempts
# ═══════════════════════════════════════════════════════════════════════


@bolt_view
@login_required
def attempt_start(request, quiz_pk):
    """POST /apis/quizzes/<quiz_pk>/attempts/ — Start a new quiz attempt."""
    from plugins.lms.models import Quiz, QuizAttempt

    quiz = get_object_or_404(Quiz, pk=quiz_pk)

    # Check max attempts
    if quiz.max_attempts > 0:
        prev_attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
        if prev_attempts >= quiz.max_attempts:
            return {"status": "error", "message": "Maximum attempts reached"}, 403

    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
    )

    return {"status": "success", "data": _serialize_attempt(attempt, include_questions=True)}, 201


@bolt_view
@login_required
def attempt_submit(request, pk):
    """POST /apis/attempts/<pk>/submit/ — Submit answers for a quiz attempt."""
    from plugins.lms.models import QuizAnswer, QuizAttempt, QuizChoice, QuizQuestion

    attempt = get_object_or_404(QuizAttempt, pk=pk, user=request.user)

    if attempt.status != QuizAttempt.Status.IN_PROGRESS:
        return {"status": "error", "message": "Attempt is not in progress"}, 400

    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    answers_data = body.get("answers", [])

    points_earned = 0
    points_possible = 0

    with transaction.atomic():
        for ans_data in answers_data:
            question = get_object_or_404(QuizQuestion, pk=ans_data["question_id"])
            points_possible += question.points

            answer = QuizAnswer.objects.create(
                attempt=attempt,
                question=question,
            )

            if question.question_type in [
                QuizQuestion.QuestionType.MULTIPLE_CHOICE,
                QuizQuestion.QuestionType.TRUE_FALSE,
            ]:
                choice_id = ans_data.get("selected_choice_id")
                if choice_id:
                    choice = QuizChoice.objects.get(pk=choice_id, question=question)
                    answer.selected_choices.add(choice)
                answer.evaluate()
                if answer.is_correct:
                    points_earned += answer.points_awarded

            elif question.question_type == QuizQuestion.QuestionType.MULTIPLE_SELECT:
                choice_ids = ans_data.get("selected_choice_ids", [])
                for cid in choice_ids:
                    choice = QuizChoice.objects.get(pk=cid, question=question)
                    answer.selected_choices.add(choice)
                answer.evaluate()
                if answer.is_correct:
                    points_earned += answer.points_awarded

            else:  # short_answer
                answer.text_answer = ans_data.get("text_answer", "")
                answer.file_url = ans_data.get("file_url", "")
                answer.file_name = ans_data.get("file_name", "")
                answer.save()
                # Short answers need manual grading

        # Update attempt
        attempt.points_earned = points_earned
        attempt.points_possible = points_possible
        attempt.complete()

    # Send notification for auto-graded results
    if attempt.passed is not None:
        create_notification(
            user=request.user,
            notification_type="quiz",
            title=f"Quiz Result: {attempt.quiz.title}",
            message=f"You scored {attempt.score:.0f}%",
            link="/dashboard/attempts",
        )

    return {"status": "success", "data": _serialize_attempt(attempt)}


@bolt_view
@login_required
def attempt_list(request):
    """GET /apis/attempts/ — List attempts for current user."""
    from plugins.lms.models import QuizAttempt

    qs = QuizAttempt.objects.filter(user=request.user).select_related("quiz").order_by("-started_at")

    items, pagination = paginate_queryset(qs, request, default_per_page=20)
    serialized = [_serialize_attempt(a) for a in items]
    return paginated_response(items, pagination, request, serialized)


@bolt_view
@login_required
def attempt_detail(request, pk):
    """GET /apis/attempts/<pk>/ — Get attempt detail with answers."""
    from plugins.lms.models import QuizAttempt

    attempt = get_object_or_404(QuizAttempt, pk=pk)

    if attempt.user != request.user and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403

    return {"status": "success", "data": _serialize_attempt(attempt, include_answers=True)}


@bolt_view
@login_required
def quiz_attempts(request, quiz_pk):
    """GET /apis/quizzes/<quiz_pk>/attempts/ — List attempts for a quiz (instructor)."""
    from plugins.lms.models import QuizAttempt

    if not request.user.groups.filter(name="Instructors").exists() and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403

    qs = QuizAttempt.objects.filter(quiz_id=quiz_pk).select_related("user", "quiz").order_by("-started_at")

    items, pagination = paginate_queryset(qs, request, default_per_page=50)
    serialized = [_serialize_attempt(a) for a in items]
    return paginated_response(items, pagination, request, serialized)


@bolt_view
@login_required
def attempt_grade(request, pk):
    """PATCH /apis/attempts/<pk>/grade/ — Grade short answer questions (instructor)."""
    from plugins.lms.models import QuizAnswer, QuizAttempt

    if not request.user.groups.filter(name="Instructors").exists() and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403

    attempt = get_object_or_404(QuizAttempt, pk=pk)
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    # Update manually graded answers
    graded = body.get("graded_answers", [])
    total_points = 0

    for grade_data in graded:
        answer = get_object_or_404(QuizAnswer, pk=grade_data["answer_id"], attempt=attempt)
        answer.is_correct = grade_data.get("is_correct", False)
        answer.points_awarded = grade_data.get("points_awarded", 0)
        answer.save()

    # Recalculate attempt score
    attempt.points_earned = attempt.answers.aggregate(
        total=models.Sum("points_awarded")
    )["total"] or 0
    attempt.points_possible = attempt.answers.aggregate(
        total=models.Sum("question__points")
    )["total"] or 0
    attempt.complete()

    return {"status": "success", "data": _serialize_attempt(attempt, include_answers=True)}


# ═══════════════════════════════════════════════════════════════════════
# Serializers
# ═══════════════════════════════════════════════════════════════════════


def _serialize_quiz(quiz, user=None, include_questions=False) -> dict:
    """Serialize a quiz to the frontend contract."""
    from plugins.lms.models import QuizAttempt

    data = {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "passing_score": quiz.passing_score,
        "time_limit": quiz.time_limit,
        "max_attempts": quiz.max_attempts,
        "shuffle_questions": quiz.shuffle_questions,
        "show_correct_answers": quiz.show_correct_answers,
        "is_active": quiz.is_active,
        "question_count": quiz.questions.filter(is_active=True).count(),
        "total_points": sum(
            q.points for q in quiz.questions.filter(is_active=True)
        ),
        "created_at": quiz.created_at.isoformat() if quiz.created_at else None,
        "updated_at": quiz.updated_at.isoformat() if quiz.updated_at else None,
    }

    # Course info
    lesson = getattr(quiz, "lesson", None)
    if lesson:
        data["course_id"] = lesson.module.course_id if lesson.module else None
        data["course_title"] = lesson.module.course.title if lesson.module and lesson.module.course else ""
        data["module_title"] = lesson.module.title if lesson.module else ""
        data["lesson_title"] = lesson.title

    if include_questions:
        questions = quiz.get_questions() if hasattr(quiz, "get_questions") else quiz.questions.filter(is_active=True)
        data["questions"] = [_serialize_question(q, show_answers=True) for q in questions]

    # User's attempts count
    if user and user.is_authenticated:
        data["user_attempts"] = QuizAttempt.objects.filter(user=user, quiz=quiz).count()
        best = (
            QuizAttempt.objects.filter(user=user, quiz=quiz, status=QuizAttempt.Status.COMPLETED)
            .order_by("-score")
            .first()
        )
        data["best_score"] = float(best.score) if best and best.score else None
    else:
        data["user_attempts"] = 0
        data["best_score"] = None

    return data


def _serialize_question(question, show_answers=False) -> dict:
    """Serialize a quiz question."""
    data = {
        "id": question.id,
        "quiz_id": question.quiz_id,
        "question_type": question.question_type,
        "question_text": question.question_text,
        "explanation": question.explanation,
        "points": question.points,
        "order": question.order,
        "is_active": question.is_active,
    }

    choices = question.choices.order_by("order")
    data["choices"] = [
        {
            "id": c.id,
            "text": c.choice_text,
            "is_correct": c.is_correct if show_answers else None,
            "order": c.order,
        }
        for c in choices
    ]

    return data


def _serialize_attempt(attempt, include_questions=False, include_answers=False) -> dict:
    """Serialize a quiz attempt."""
    data = {
        "id": attempt.id,
        "attempt_id": attempt.attempt_id,
        "user_id": attempt.user_id,
        "username": attempt.user.username if hasattr(attempt, "user") and attempt.user else "",
        "quiz_id": attempt.quiz_id,
        "quiz_title": attempt.quiz.title if hasattr(attempt, "quiz") and attempt.quiz else "",
        "status": attempt.status,
        "score": float(attempt.score) if attempt.score else None,
        "points_earned": attempt.points_earned,
        "points_possible": attempt.points_possible,
        "passed": attempt.passed,
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        "time_spent": attempt.time_spent,
    }

    if include_questions:
        questions = attempt.quiz.get_questions() if hasattr(attempt.quiz, "get_questions") else attempt.quiz.questions.filter(is_active=True)
        data["questions"] = [_serialize_question(q, show_answers=True) for q in questions]

    if include_answers:
        answers = attempt.answers.select_related("question").prefetch_related("selected_choices")
        data["answers"] = [
            {
                "id": a.id,
                "question_id": a.question_id,
                "question_text": a.question.question_text if a.question else "",
                "question_type": a.question.question_type if a.question else "",
                "selected_choice_ids": list(a.selected_choices.values_list("id", flat=True)),
                "text_answer": a.text_answer,
                "file_url": a.file_url or "",
                "file_name": a.file_name or "",
                "is_correct": a.is_correct,
                "points_awarded": a.points_awarded,
                "points_possible": a.question.points if a.question else 0,
            }
            for a in answers
        ]

    return data
