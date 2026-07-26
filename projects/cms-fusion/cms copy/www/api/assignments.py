"""
Assignments API — CRUD for assignments, submissions, and instructor grading.

Endpoints:
    Assignment CRUD:
        GET    /apis/assignments/               — List assignments (instructor: course assignments; student: published)
        POST   /apis/assignments/create/         — Create assignment (instructor only)
        GET    /apis/assignments/<pk>/           — Assignment detail with submissions count
        PATCH  /apis/assignments/<pk>/update/    — Update assignment (instructor only)
        DELETE /apis/assignments/<pk>/delete/    — Delete assignment (instructor only)

    File Upload:
        POST   /apis/assignments/upload/         — Upload a file for an assignment submission

    Student Submission:
        POST   /apis/assignments/<pk>/submit/    — Submit assignment (student)
        GET    /apis/assignments/<pk>/submissions/ — List all submissions for grading (instructor)

    My Submissions:
        GET    /apis/submissions/                — List my submissions (student)

    Instructor Grading:
        PATCH  /apis/submissions/<pk>/grade/     — Grade a submission (instructor)
"""

import logging
import mimetypes
import os
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from plugins.lms.models import Assignment, AssignmentSubmission, Course
from www.api.data_adapter import (
    bolt_view,
    login_required,
    paginate_queryset,
    parse_body,
    paginated_response,
)

# ── File Upload ──

ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.txt', '.csv', '.zip', '.rar', '.7z',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp',
    '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.scss',
    '.json', '.xml', '.yaml', '.yml', '.md', '.rst',
}

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB


def _get_media_subdir() -> str:
    """Get the subdirectory for assignment uploads under MEDIA_ROOT."""
    return "assignments"


def _validate_file_extension(filename: str) -> bool:
    """Check if the file extension is allowed."""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def _generate_unique_filename(original: str) -> str:
    """Generate a unique filename preserving the extension."""
    ext = Path(original).suffix
    stem = Path(original).stem[:50]  # Truncate original stem
    unique = uuid.uuid4().hex[:12]
    safe_stem = "".join(c for c in stem if c.isalnum() or c in " _-.").strip()[:50]
    return f"{safe_stem}_{unique}{ext}" if safe_stem else f"file_{unique}{ext}"


@csrf_exempt
@login_required
def assignment_upload(request):
    """
    POST /apis/assignments/upload/ — Upload a file for an assignment submission.

    Accepts multipart/form-data with a single 'file' field.
    Returns the file URL and file name on success.

    Example:
        curl -X POST http://localhost:5071/apis/assignments/upload/ \
          -H "Authorization: Token ..." \
          -F "file=@my_homework.pdf"

    Returns:
        {
            "status": "success",
            "data": {
                "file_url": "/media/assignments/my_homework_abc123.pdf",
                "file_name": "my_homework.pdf"
            }
        }
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
    if not _validate_file_extension(original_name):
        ext = Path(original_name).suffix
        return JsonResponse({
            "status": "error",
            "message": f"File type '{ext}' is not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        }, status=400)

    # Validate size
    if uploaded_file.size > MAX_UPLOAD_SIZE:
        max_mb = MAX_UPLOAD_SIZE // (1024 * 1024)
        return JsonResponse({
            "status": "error",
            "message": f"File too large. Maximum size is {max_mb} MB.",
        }, status=400)

    # Generate unique filename
    unique_name = _generate_unique_filename(original_name)
    subdir = _get_media_subdir()
    relative_path = f"{subdir}/{unique_name}"

    # Ensure media subdirectory exists
    media_root = Path(settings.MEDIA_ROOT)
    upload_dir = media_root / subdir
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    saved_path = default_storage.save(relative_path, uploaded_file)
    file_url = f"{settings.MEDIA_URL}{saved_path}"

    logger.info(f"File uploaded: {original_name} → {file_url} by user {request.user.id}")

    return JsonResponse({
        "status": "success",
        "data": {
            "file_url": file_url,
            "file_name": original_name,
        }
    })

logger = logging.getLogger(__name__)


def _serialize_assignment(a: Assignment) -> dict:
    """Serialize an assignment for the frontend."""
    return {
        "id": a.id,
        "course": a.course_id,
        "course_title": a.course.title,
        "title": a.title,
        "description": a.description,
        "instructions": a.instructions,
        "due_date": a.due_date.isoformat() if a.due_date else None,
        "max_score": a.max_score,
        "is_published": a.is_published,
        "sort_order": a.sort_order,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "updated_at": a.updated_at.isoformat() if a.updated_at else None,
        "submissions_count": a.submissions.count(),
    }


def _serialize_submission(s: AssignmentSubmission) -> dict:
    """Serialize a submission for the frontend."""
    return {
        "id": s.id,
        "assignment": s.assignment_id,
        "assignment_title": s.assignment.title,
        "course": s.assignment.course_id,
        "course_title": s.assignment.course.title,
        "student": s.student_id,
        "student_name": s.student.get_full_name() or s.student.username,
        "text_submission": s.text_submission,
        "file_url": s.file_url or "",
        "file_name": s.file_name or "",
        "status": s.status,
        "score": s.score,
        "max_score": s.assignment.max_score,
        "feedback": s.feedback or "",
        "graded_by": s.graded_by_id,
        "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
        "graded_at": s.graded_at.isoformat() if s.graded_at else None,
        "is_late": (
            s.submitted_at > s.assignment.due_date
            if s.submitted_at and s.assignment.due_date
            else False
        ),
    }


# ── Assignment CRUD ──


@bolt_view
@login_required
def assignment_list(request):
    """GET /apis/assignments/ — List assignments.

    Instructors see assignments for their courses.
    Students see published assignments for courses they're enrolled in.
    """
    user = request.user
    is_instructor = user.groups.filter(name="Instructors").exists()
    is_staff = user.is_staff

    qs = Assignment.objects.all()

    if is_staff:
        pass  # Staff sees all
    elif is_instructor:
        qs = qs.filter(course__instructor=user)
    else:
        # Students see published assignments for their enrolled courses
        enrolled_course_ids = (
            user.enrollment_set.filter(is_active=True)
            .values_list("course_id", flat=True)
        )
        qs = qs.filter(course_id__in=enrolled_course_ids, is_published=True)

    # Optional filters
    course_id = request.GET.get("course")
    if course_id:
        qs = qs.filter(course_id=course_id)

    qs = qs.order_by("course", "sort_order", "-created_at")
    items, pagination = paginate_queryset(qs, request)
    return paginated_response(
        items, pagination, request, [_serialize_assignment(a) for a in items]
    )


@bolt_view
@login_required
def assignment_create(request):
    """POST /apis/assignments/create/ — Create a new assignment (instructor only)."""
    if not request.user.groups.filter(name="Instructors").exists() and not request.user.is_staff:
        return {"status": "error", "message": "Only instructors can create assignments"}, 403

    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    title = body.get("title", "").strip()
    course_id = body.get("course_id")
    if not title or not course_id:
        return {"status": "error", "message": "Title and course are required"}, 400

    course = get_object_or_404(Course, pk=course_id)
    if course.instructor_id != request.user.id and not request.user.is_staff:
        return {"status": "error", "message": "You don't own this course"}, 403

    assignment = Assignment.objects.create(
        course=course,
        title=title,
        description=body.get("description", ""),
        instructions=body.get("instructions", ""),
        due_date=(
            timezone.datetime.fromisoformat(body["due_date"])
            if body.get("due_date") else None
        ),
        max_score=body.get("max_score", 100),
        is_published=body.get("is_published", True),
        sort_order=body.get("sort_order", 0),
    )

    return {"status": "success", "data": _serialize_assignment(assignment)}, 201


@bolt_view
@login_required
def assignment_detail(request, pk):
    """GET /apis/assignments/<pk>/ — Assignment detail with submission info."""
    assignment = get_object_or_404(Assignment, pk=pk)
    data = _serialize_assignment(assignment)
    return {"status": "success", "data": data}


@bolt_view
@login_required
def assignment_update(request, pk):
    """PATCH /apis/assignments/<pk>/update/ — Update an assignment (instructor only)."""
    assignment = get_object_or_404(Assignment, pk=pk)
    if assignment.course.instructor_id != request.user.id and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403

    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    editable = ["title", "description", "instructions", "max_score", "is_published", "sort_order"]
    for field in editable:
        if field in body:
            setattr(assignment, field, body[field])

    if "due_date" in body:
        assignment.due_date = (
            timezone.datetime.fromisoformat(body["due_date"])
            if body["due_date"] else None
        )

    assignment.save()
    return {"status": "success", "data": _serialize_assignment(assignment)}


@bolt_view
@login_required
def assignment_delete(request, pk):
    """DELETE /apis/assignments/<pk>/delete/ — Delete an assignment."""
    assignment = get_object_or_404(Assignment, pk=pk)
    if assignment.course.instructor_id != request.user.id and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403
    assignment.delete()
    return {"status": "success", "message": "Assignment deleted"}


# ── Student Submission ──


@bolt_view
@login_required
def assignment_submit(request, pk):
    """POST /apis/assignments/<pk>/submit/ — Submit assignment (student)."""
    assignment = get_object_or_404(Assignment, pk=pk)

    if not assignment.is_published:
        return {"status": "error", "message": "This assignment is not open for submissions"}, 404

    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    text_submission = body.get("text_submission", "").strip()
    file_url = body.get("file_url", "").strip()
    file_name = body.get("file_name", "").strip()

    if not text_submission and not file_url:
        return {"status": "error", "message": "Submission must include text or a file"}, 400

    # Check for existing submission
    existing = AssignmentSubmission.objects.filter(
        assignment=assignment, student=request.user
    ).first()
    if existing:
        # Update existing submission
        if text_submission:
            existing.text_submission = text_submission
        if file_url:
            existing.file_url = file_url
            existing.file_name = file_name
        existing.status = "submitted"
        existing.submitted_at = timezone.now()
        existing.score = None
        existing.feedback = ""
        existing.graded_by = None
        existing.graded_at = None
        existing.save()
        return {"status": "success", "data": _serialize_submission(existing)}

    submission = AssignmentSubmission.objects.create(
        assignment=assignment,
        student=request.user,
        text_submission=text_submission,
        file_url=file_url,
        file_name=file_name,
    )
    return {"status": "success", "data": _serialize_submission(submission)}, 201


@bolt_view
@login_required
def assignment_submissions(request, pk):
    """GET /apis/assignments/<pk>/submissions/ — List submissions for grading (instructor)."""
    assignment = get_object_or_404(Assignment, pk=pk)
    if assignment.course.instructor_id != request.user.id and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403

    qs = AssignmentSubmission.objects.filter(assignment=assignment).order_by("-submitted_at")
    items, pagination = paginate_queryset(qs, request)
    return paginated_response(
        items, pagination, request, [_serialize_submission(s) for s in items]
    )


# ── My Submissions ──


@bolt_view
@login_required
def my_submissions(request):
    """GET /apis/submissions/ — List current user's submissions."""
    qs = AssignmentSubmission.objects.filter(student=request.user).order_by("-submitted_at")
    items, pagination = paginate_queryset(qs, request)
    return paginated_response(
        items, pagination, request, [_serialize_submission(s) for s in items]
    )


# ── Instructor Grading ──


@bolt_view
@login_required
def submission_grade(request, pk):
    """PATCH /apis/submissions/<pk>/grade/ — Grade a submission (instructor)."""
    submission = get_object_or_404(AssignmentSubmission, pk=pk)
    assignment = submission.assignment

    if assignment.course.instructor_id != request.user.id and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403

    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    score = body.get("score")
    if score is not None:
        if not isinstance(score, (int, float)) or score < 0 or score > assignment.max_score:
            return {
                "status": "error",
                "message": f"Score must be between 0 and {assignment.max_score}",
            }, 400
        submission.score = int(score)
        submission.status = "graded"
        submission.graded_by = request.user

    if "feedback" in body:
        submission.feedback = body.get("feedback", "")

    submission.save()
    return {"status": "success", "data": _serialize_submission(submission)}
