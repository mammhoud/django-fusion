from __future__ import annotations

from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from apps.learning.management.services.enrollments import EnrollmentService
from apps.learning.models import Course, Enrollment, Lesson, LessonProgress, ModuleProgress

from .common import _hx_or_json, learning_login_required


@learning_login_required
@require_POST
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"), pk=lesson_id, is_active=True
    )
    with transaction.atomic():
        enrollment = get_object_or_404(
            Enrollment.objects.select_for_update(),
            user=request.user,
            course=lesson.module.course,
            status__in=[Enrollment.Status.ACTIVE, Enrollment.Status.COMPLETED],
        )
        if not enrollment.has_verified_payment:
            return HttpResponse("Payment verification required.", status=403)
        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson
        )
        progress.set_completed(not progress.completed)
        enrollment.recalculate_progress()
        enrollment.refresh_from_db()

        # Keep the per-module progress record in sync with lesson completions.
        module_progress, _ = ModuleProgress.objects.get_or_create(
            enrollment=enrollment, module=lesson.module
        )
        module_progress.calculate_progress()

    # Auto-advance: the lesson reader submits ``auto_advance=1`` so completing a
    # lesson moves the learner to the next one (HX-Redirect). The course dossier
    # syllabus toggles submit without it and keeps its inline behavior.
    headers = {}
    if request.POST.get("auto_advance") == "1" and progress.completed:
        # Same flat ordering as the reader's next link (reused helper).
        next_id = EnrollmentService.lesson_neighbors(lesson)[1]
        if next_id:
            headers["HX-Redirect"] = reverse(
                "learning:course_watch_lesson",
                kwargs={"slug": lesson.module.course.slug, "lesson_id": next_id},
            )
        else:
            # Last lesson of the course — land back on the dossier.
            headers["HX-Redirect"] = lesson.module.course.get_absolute_url()

    return _hx_or_json(
        request,
        "learning/fragments/lesson_progress.html",
        {"lesson": lesson, "progress": progress, "enrollment": enrollment},
        {
            "completed": progress.completed,
            "progress": enrollment.progress,
            "course": enrollment.course.slug,
        },
        redirect_to=enrollment.course.get_absolute_url(),
        headers=headers,
    )


@learning_login_required
@require_GET
def course_watch(request, slug, lesson_id=None):
    """The lesson reader — a focused page for one lesson of an enrolled course."""
    course = get_object_or_404(Course.objects.published(), slug=slug)
    enrollment = EnrollmentService.verified_enrollment(request.user, course)
    if enrollment is None or not enrollment.has_verified_payment:
        return HttpResponseRedirect(course.get_absolute_url())

    lessons = list(
        Lesson.objects.filter(module__course=course, is_active=True)
        .select_related("module")
        .order_by("module__order", "order")
    )
    if not lessons:
        return HttpResponseRedirect(course.get_absolute_url())

    if lesson_id is not None:
        lesson = next((item for item in lessons if item.pk == lesson_id), None)
        if lesson is None:
            raise Http404("No lesson with that id in this course.")
    else:
        completed_ids = set(
            enrollment.lesson_progress.filter(completed=True).values_list(
                "lesson_id", flat=True
            )
        )
        lesson = next(
            (item for item in lessons if item.pk not in completed_ids), lessons[0]
        )

    progress, _ = LessonProgress.objects.get_or_create(
        enrollment=enrollment, lesson=lesson
    )
    index = next(i for i, item in enumerate(lessons) if item.pk == lesson.pk)
    prev_lesson = lessons[index - 1] if index > 0 else None
    next_lesson = lessons[index + 1] if index < len(lessons) - 1 else None

    # Per-module progress for the reader panel: derive stats once and only
    # persist when the module record is stale (no write on plain page views).
    module = lesson.module
    module_progress, _ = ModuleProgress.objects.get_or_create(
        enrollment=enrollment, module=module
    )
    module_stats = module_progress.get_lesson_progress_stats()
    if module_stats["progress_percentage"] != module_progress.progress_percentage:
        module_progress.calculate_progress()
    module_lessons = list(
        Lesson.objects.filter(module=module, is_active=True).order_by("order")
    )
    module_completed_ids = set(
        enrollment.lesson_progress.filter(
            lesson__in=module_lessons, completed=True
        ).values_list("lesson_id", flat=True)
    )

    return render(
        request,
        "learning/lesson.html",
        {
            "course": course,
            "lesson": lesson,
            "module": module,
            "module_progress": module_progress,
            "module_lessons": module_lessons,
            "module_completed_ids": module_completed_ids,
            "module_stats": module_stats,
            "enrollment": enrollment,
            "progress": progress,
            "completed": progress.completed,
            "prev_lesson": prev_lesson,
            "next_lesson": next_lesson,
            "lesson_index": index + 1,
            "lesson_total": len(lessons),
        },
    )


@learning_login_required
@require_GET
def course_continue(request, slug):
    """Resume a course at the first incomplete lesson (Precis-style route)."""
    course = get_object_or_404(Course.objects.published(), slug=slug)
    enrollment = EnrollmentService.verified_enrollment(request.user, course)
    if enrollment is None or not enrollment.has_verified_payment:
        return HttpResponseRedirect(course.get_absolute_url())

    lesson = EnrollmentService.first_incomplete_lesson(enrollment, course)
    if lesson is None:
        return HttpResponseRedirect(course.get_absolute_url())
    return HttpResponseRedirect(
        reverse(
            "learning:course_watch_lesson",
            kwargs={"slug": course.slug, "lesson_id": lesson.pk},
        )
    )


@learning_login_required
@require_GET
def lesson_navigate(request, lesson_id):
    """Prev/next lesson pointers for the lesson reader navigation."""
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"), pk=lesson_id, is_active=True
    )
    prev_id, next_id = EnrollmentService.lesson_neighbors(lesson)
    payload = {
        "lesson_id": lesson.pk,
        "course": lesson.module.course.slug,
        "prev_id": prev_id,
        "next_id": next_id,
        "prev_url": (
            reverse(
                "learning:course_watch_lesson",
                kwargs={"slug": lesson.module.course.slug, "lesson_id": prev_id},
            )
            if prev_id
            else None
        ),
        "next_url": (
            reverse(
                "learning:course_watch_lesson",
                kwargs={"slug": lesson.module.course.slug, "lesson_id": next_id},
            )
            if next_id
            else None
        ),
    }
    return JsonResponse(payload)
