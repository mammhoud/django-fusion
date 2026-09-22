from __future__ import annotations

from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from apps.learning.management.services.courses import CourseService
from apps.learning.management.services.enrollments import EnrollmentService

from .common import _is_htmx


@require_GET
def catalog(request):
    query = request.GET.get("q", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()
    courses = CourseService.catalog(query=query, difficulty=difficulty)
    context = {"courses": courses, "query": query, "difficulty": difficulty}
    if _is_htmx(request):
        return render(request, "learning/fragments/course_list.html", context)
    return render(request, "learning/catalog.html", context)


@require_GET
def course_detail(request, slug):
    course = get_object_or_404(
        CourseService.course_detail_queryset(),
        slug=slug,
    )
    enrollment = None
    completed_lesson_ids = set()
    if request.user.is_authenticated:
        enrollment = EnrollmentService.verified_enrollment(request.user, course)
        if enrollment and enrollment.has_verified_payment:
            completed_lesson_ids = set(
                enrollment.lesson_progress.filter(completed=True).values_list(
                    "lesson_id", flat=True
                )
            )
        elif enrollment and not enrollment.has_verified_payment:
            enrollment = None
    # Published reviews (surfaced in the dossier) + total resources across the
    # prefetched module tree (query-free once ``course_detail_queryset`` loaded
    # lessons with their resources).
    reviews = course.reviews.published().select_related("user")[:6]
    resources_count = sum(
        len(lesson.resources.all())
        for module in course.modules.all()
        for lesson in module.lessons.all()
    )
    return render(
        request,
        "learning/course_detail.html",
        {
            "course": course,
            "enrollment": enrollment,
            "completed_lesson_ids": completed_lesson_ids,
            "reviews": reviews,
            "resources_count": resources_count,
        },
    )
