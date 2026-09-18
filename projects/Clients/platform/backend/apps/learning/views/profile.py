from __future__ import annotations

from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.learning.management.services.enrollments import EnrollmentService
from apps.learning.models import Certificate, LessonProgress, Wishlist

from .common import learning_login_required


@learning_login_required
@require_GET
def dashboard(request):
    enrollments = EnrollmentService.active_enrollments(request.user)
    return render(request, "learning/dashboard.html", {"enrollments": enrollments})


@learning_login_required
@require_GET
def profile_dashboard(request):
    """Profile surface shared by auth users; no duplicate Person model.

    One page, three lenses: the learner's enrollments (active + completed),
    saved courses, and issued certificates — plus a lean recent-activity
    stream derived from lesson progress timestamps.
    """
    enrollments = EnrollmentService.active_enrollments(request.user)
    wishlist = Wishlist.objects.filter(user=request.user).select_related("course")
    certificates = (
        Certificate.objects.filter(user=request.user)
        .select_related("course")
        .order_by("-issued_at")
    )
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
