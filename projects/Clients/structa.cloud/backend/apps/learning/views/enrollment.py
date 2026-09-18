from __future__ import annotations

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from apps.learning.forms.enrollment import CourseEnrollmentLeadForm
from apps.learning.management.services.enrollments import EnrollmentService
from apps.learning.models import Course, CourseEnrollmentLead, Enrollment

from .common import _hx_or_json, _is_htmx, learning_login_required


@learning_login_required
@require_POST
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)

    existing = Enrollment.objects.filter(user=request.user, course=course).first()
    if (
        existing
        and existing.status
        in [Enrollment.Status.ACTIVE, Enrollment.Status.COMPLETED]
        and existing.has_verified_payment
    ):
        return _hx_or_json(
            request,
            "learning/fragments/enrollment_status.html",
            {"course": course, "enrollment": existing, "created": False},
            {
                "enrolled": True,
                "created": False,
                "course": course.slug,
                "progress": existing.progress,
            },
            redirect_to=course.get_absolute_url(),
        )

    # A cancelled free enrollment can be resumed without creating a second row.
    if existing and course.is_free:
        existing.status = Enrollment.Status.ACTIVE
        existing.save(update_fields=["status"])
        return _hx_or_json(
            request,
            "learning/fragments/enrollment_status.html",
            {"course": course, "enrollment": existing, "created": False},
            {
                "enrolled": True,
                "created": False,
                "course": course.slug,
                "progress": existing.progress,
            },
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
        {
            "enrolled": True,
            "created": created,
            "course": course.slug,
            "progress": enrollment.progress,
        },
        redirect_to=course.get_absolute_url(),
    )


@learning_login_required
@require_GET
def enrollment_list(request):
    """The learner's verified enrollments as JSON (Precis-style endpoint)."""
    enrollments = EnrollmentService.active_enrollments(request.user)
    payload = {
        "results": [
            {
                "id": e.pk,
                "course": e.course.slug,
                "title": e.course.title,
                "status": e.status,
                "progress": e.progress,
                "enrolled_at": e.enrolled_at.isoformat(),
                "url": e.course.get_absolute_url(),
            }
            for e in enrollments
        ]
    }
    return JsonResponse(payload)


@learning_login_required
@require_POST
def enrollment_status_update(request, enrollment_id):
    """Update the status of one of the user's own enrollments (Precis-style)."""
    enrollment = get_object_or_404(
        Enrollment.objects.select_related("course"),
        pk=enrollment_id,
        user=request.user,
    )
    new_status = request.POST.get("status", "").strip()
    valid = {Enrollment.Status.ACTIVE, Enrollment.Status.COMPLETED, Enrollment.Status.CANCELLED}
    if new_status not in valid:
        return JsonResponse({"error": "invalid status"}, status=400)
    enrollment.status = new_status
    enrollment.save(update_fields=["status"])
    return JsonResponse({"id": enrollment.pk, "status": enrollment.status})


def course_enrollment_form(request, course_id):
    """Enrollment lead capture — renders the modal fragment / stores a lead."""
    if request.method not in {"GET", "POST"}:
        return JsonResponse({"error": "method not allowed"}, status=405)
    course = get_object_or_404(Course.objects.published(), pk=course_id)
    if request.method == "POST":
        form = CourseEnrollmentLeadForm(request.POST)
        if form.is_valid():
            lead, created = CourseEnrollmentLead.objects.get_or_create(
                course=course,
                email=form.cleaned_data["email"].lower(),
                defaults={
                    "full_name": form.cleaned_data["full_name"],
                    "phone": form.cleaned_data.get("phone", ""),
                },
            )
            if request.headers.get("HX-Request", "").lower() in {"true", "1", "yes"}:
                return render(
                    request,
                    "learning/fragments/enrollment_lead_success.html",
                    {"course": course, "lead": lead, "created": created},
                )
            return JsonResponse({"ok": True, "created": created, "course": course.slug})
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    context = {"course": course, "form": CourseEnrollmentLeadForm()}
    return render(request, "learning/fragments/enrollment_form.html", context)
