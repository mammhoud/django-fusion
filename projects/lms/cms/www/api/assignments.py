"""
Assignments API — CRUD for assignments, submissions, and instructor grading.

Endpoints:
    Assignment CRUD:
        GET    /apis/assignments/               — List assignments (instructor: course assignments; student: published)
        POST   /apis/assignments/create/         — Create assignment (instructor only)
        GET    /apis/assignments/<pk>/           — Assignment detail with submissions count
        PATCH  /apis/assignments/<pk>/update/    — Update assignment (instructor only)
        DELETE /apis/assignments/<pk>/delete/    — Delete assignment (instructor only)

    Student Submission:
        POST   /apis/assignments/<pk>/submit/    — Submit assignment (student)
        GET    /apis/assignments/<pk>/submissions/ — List all submissions for grading (instructor)

    My Submissions:
        GET    /apis/submissions/                — List my submissions (student)

    Instructor Grading:
        PATCH  /apis/submissions/<pk>/grade/     — Grade a submission (instructor)
"""

import logging

from django.shortcuts import get_object_or_404
from django.utils import timezone

from plugins.lms.models import Assignment, AssignmentSubmission, Course
from www.api.data_adapter import (
    bolt_view,
    login_required,
    paginate_queryset,
    parse_body,
    paginated_response,
)

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
