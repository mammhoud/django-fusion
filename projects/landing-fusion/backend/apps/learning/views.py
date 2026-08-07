from __future__ import annotations

import json
from functools import wraps

from django.conf import settings
from django.db import models, transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from .models import Certificate, Course, Enrollment, Lesson, LessonProgress, Wishlist


def _is_htmx(request) -> bool:
    """Use django-htmx's parsed request flag with a header fallback.

    The fallback keeps these endpoints useful in isolated tests and when a
    caller mounts the app without the Fusion middleware stack.
    """
    return bool(getattr(request, "htmx", False) or request.headers.get("HX-Request"))


def _hx_or_json(
    request,
    template: str,
    context: dict,
    payload: dict,
    status: int = 200,
    redirect_to: str | None = None,
):
    if _is_htmx(request):
        return render(request, template, context, status=status)
    if redirect_to and status < 400:
        return HttpResponseRedirect(redirect_to)
    return JsonResponse(payload, status=status)


def _verified_enrollments(user):
    """Return only entitlements that are valid for the course's price."""
    return Enrollment.objects.filter(user=user).filter(
        models.Q(course__price__lte=0)
        | models.Q(
            provider_reference__gt="",
            amount_paid__gte=models.F("course__price"),
        )
    )


def _login_response(request):
    if _is_htmx(request):
        response = HttpResponse(status=401)
        response["HX-Trigger"] = json.dumps({"fusion:open-login": {}})
        return response
    return HttpResponseRedirect("/accounts/login/?next=/learning/")


def learning_login_required(view):
    """Protect learner views while keeping HTMX requests in the current page."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _login_response(request)
        return view(request, *args, **kwargs)

    return wrapped


@require_GET
def catalog(request):
    courses = Course.objects.filter(is_published=True).select_related("instructor")
    query = request.GET.get("q", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()
    if query:
        courses = courses.filter(title__icontains=query)
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    context = {"courses": courses, "query": query, "difficulty": difficulty}
    if _is_htmx(request):
        return render(request, "learning/fragments/course_list.html", context)
    return render(request, "learning/catalog.html", context)


@require_GET
def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.filter(is_published=True).select_related("instructor"), slug=slug
    )
    enrollment = None
    completed_lesson_ids = set()
    if request.user.is_authenticated:
        enrollment = _verified_enrollments(request.user).filter(
            course=course,
            status__in=[Enrollment.Status.ACTIVE, Enrollment.Status.COMPLETED],
        ).first()
        if enrollment and enrollment.has_verified_payment:
            completed_lesson_ids = set(
                enrollment.lesson_progress.filter(completed=True).values_list("lesson_id", flat=True)
            )
        elif enrollment and not enrollment.has_verified_payment:
            enrollment = None
    return render(
        request,
        "learning/course_detail.html",
        {"course": course, "enrollment": enrollment, "completed_lesson_ids": completed_lesson_ids},
    )


@learning_login_required
def dashboard(request):
    enrollments = _verified_enrollments(request.user).filter(
        status__in=[Enrollment.Status.ACTIVE, Enrollment.Status.COMPLETED],
    ).select_related("course")
    return render(request, "learning/dashboard.html", {"enrollments": enrollments})


@learning_login_required
@require_POST
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)

    existing = Enrollment.objects.filter(
        user=request.user,
        course=course,
        status__in=[Enrollment.Status.ACTIVE, Enrollment.Status.COMPLETED],
    ).first()
    if existing and existing.has_verified_payment:
        return _hx_or_json(
            request,
            "learning/fragments/enrollment_status.html",
            {"course": course, "enrollment": existing, "created": False},
            {"enrolled": True, "created": False, "course": course.slug, "progress": existing.progress},
            redirect_to=course.get_absolute_url(),
        )

    # Never create an active entitlement for a paid course without a verified
    # checkout callback. A provider name alone is not a payment integration.
    if not course.is_free:
        provider = getattr(settings, "LEARNING_PAYMENT_PROVIDER", "")
        payment_enabled = bool(getattr(settings, "LEARNING_PAYMENT_ENABLED", False))
        payload = {
            "enrolled": False,
            "course": course.slug,
            "checkout": "provider_not_connected" if provider and payment_enabled else "disabled",
            "detail": (
                "Checkout is not connected for this course yet."
                if provider and payment_enabled
                else "This course requires checkout, which is disabled in this environment."
            ),
        }
        return _hx_or_json(
            request,
            "learning/fragments/payment_required.html",
            {"course": course, "payment_provider": provider if payment_enabled else ""},
            payload,
            status=200 if _is_htmx(request) else (402 if not payment_enabled else 409),
        )

    with transaction.atomic():
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={"amount_paid": 0},
        )
    context = {"course": course, "enrollment": enrollment, "created": created}
    return _hx_or_json(
        request,
        "learning/fragments/enrollment_status.html",
        context,
        {"enrolled": True, "created": created, "course": course.slug, "progress": enrollment.progress},
        redirect_to=course.get_absolute_url(),
    )


@learning_login_required
@require_POST
def toggle_wishlist(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    with transaction.atomic():
        item, created = Wishlist.objects.get_or_create(user=request.user, course=course)
        if not created:
            item.delete()
    return _hx_or_json(
        request,
        "learning/fragments/wishlist_button.html",
        {"course": course, "wishlisted": created},
        {"wishlisted": created, "course": course.slug},
        redirect_to=course.get_absolute_url(),
    )


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
        progress, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
        progress.set_completed(not progress.completed)
        enrollment.recalculate_progress()
        enrollment.refresh_from_db()

    return _hx_or_json(
        request,
        "learning/fragments/lesson_progress.html",
        {"lesson": lesson, "progress": progress, "enrollment": enrollment},
        {"completed": progress.completed, "progress": enrollment.progress, "course": enrollment.course.slug},
        redirect_to=enrollment.course.get_absolute_url(),
    )


@learning_login_required
@require_GET
def profile_dashboard(request):
    """Profile surface shared by auth users; no duplicate Person model.

    One page, three lenses: the learner's enrollments (active + completed),
    saved courses, and issued certificates — plus a lean recent-activity
    stream derived from lesson progress timestamps.
    """
    enrollments = _verified_enrollments(request.user).filter(
        status__in=[Enrollment.Status.ACTIVE, Enrollment.Status.COMPLETED],
    ).select_related("course")
    wishlist = Wishlist.objects.filter(user=request.user).select_related("course")
    certificates = Certificate.objects.filter(user=request.user).select_related("course").order_by("-issued_at")
    # Recent activity: the 6 most recently touched lessons across enrollments.
    recent = (
        LessonProgress.objects.filter(enrollment__user=request.user, completed=True)
        .select_related("lesson__module__course", "enrollment")
        .order_by("-completed_at")[:6]
    )
    return render(
        request,
        "learning/profile.html",
        {
            "enrollments": enrollments,
            "wishlist": wishlist,
            "certificates": certificates,
            "recent": recent,
        },
    )
