"""Precis LMS course management background tasks.

Uses ``@task`` from ``django_fusion.tasks`` for broker-agnostic enqueue.
"""

from __future__ import annotations

import csv
import io
import logging

from django_fusion.tasks import task

logger = logging.getLogger(__name__)


@task(queue="courses", max_retries=2, time_limit=600_000)
def generate_course_progress_report(course_id: int, instructor_id: int):
    """Generate a CSV progress report for an instructor.

    Produces a downloadable CSV with student names, email, progress %,
    and last activity timestamp.  Emails it to the instructor.
    """
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.core.mail import EmailMessage

    User = get_user_model()

    try:
        from apps.learning.models import Course, Enrollment  # noqa: PLC0415
        course = Course.objects.filter(id=course_id).first()
    except ImportError:
        logger.warning("Learning models not available — skipping.")
        return

    if course is None:
        logger.warning("Course %d not found.", course_id)
        return

    instructor = User.objects.filter(id=instructor_id, is_active=True).first()
    if instructor is None:
        logger.warning("Instructor %d not found.", instructor_id)
        return

    # Gather enrollment data
    enrollments = Enrollment.objects.filter(course=course).select_related("student")

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Student Name", "Email", "Progress %", "Last Activity"])

    for enrollment in enrollments:
        last_activity = getattr(enrollment, "last_activity_at", None) or ""
        progress = getattr(enrollment, "progress_percent", 0) or 0
        writer.writerow([
            enrollment.student.get_full_name() or enrollment.student.email,
            enrollment.student.email,
            progress,
            last_activity,
        ])

    csv_bytes = buf.getvalue().encode("utf-8")

    email = EmailMessage(
        subject=f"Progress Report: {course.title}",
        body=(
            f"Hi {instructor.get_full_name() or instructor.email},\n\n"
            f"Here is the progress report for {course.title}.\n\n"
            f"— The Precis Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[instructor.email],
    )
    email.attach(
        f"progress_{course.slug}.csv",
        csv_bytes,
        "text/csv",
    )
    email.send(fail_silently=False)
    logger.info(
        "Progress report for course %s sent to %s.", course.slug, instructor.email
    )


@task(queue="courses", schedule="0 */6 * * *")
def sync_course_completion_rates():
    """Update cached completion percentages for all active courses.

    Scheduled to run every 6 hours.  Iterates over all published courses,
    computes the number of completed enrollments vs. total enrollments,
    and stores the cached percentage on the Course model.
    """
    try:
        from apps.learning.models import Course, Enrollment  # noqa: PLC0415
    except ImportError:
        logger.warning("Learning models not available — skipping completion sync.")
        return

    updated = 0
    for course in Course.objects.filter(live=True).iterator():
        total = Enrollment.objects.filter(course=course).count()
        completed = Enrollment.objects.filter(
            course=course, status="completed"
        ).count()
        rate = round(completed / max(total, 1) * 100, 1)

        # Store on the course model if it has a completion_rate field
        if hasattr(course, "completion_rate"):
            course.completion_rate = rate
            course.save(update_fields=["completion_rate"])
            updated += 1

    logger.info("Completion rates synced for %d courses.", updated)


@task(queue="courses", schedule="0 9 * * 1")
def send_weekly_learning_digest():
    """Send a weekly digest email to all enrolled students.

    Scheduled every Monday at 09:00 UTC.  Queries recently updated
    courses and sends a personalised digest to each active student.
    """
    from datetime import timedelta

    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail
    from django.utils import timezone

    User = get_user_model()

    try:
        from apps.learning.models import Course, Enrollment  # noqa: PLC0415
    except ImportError:
        logger.warning("Learning models not available — skipping weekly digest.")
        return

    since = timezone.now() - timedelta(days=7)
    recent_courses = Course.objects.filter(
        live=True,
        first_published_at__gte=since,
    )[:5]

    if not recent_courses:
        logger.info("No new courses this week — skipping digest.")
        return

    course_list = "\n".join(
        f"• {c.title} — {settings.WAGTAILADMIN_BASE_URL}/courses/{c.slug}/"
        for c in recent_courses
    )

    # Send to all users with active enrollments
    active_student_ids = (
        Enrollment.objects
        .filter(status="active")
        .values_list("student_id", flat=True)
        .distinct()
    )

    sent = 0
    for user in User.objects.filter(id__in=active_student_ids, is_active=True).iterator():
        try:
            send_mail(
                subject="Your Weekly Learning Digest",
                message=(
                    f"Hi {user.get_full_name() or user.email},\n\n"
                    f"Here are the latest courses published this week:\n\n"
                    f"{course_list}\n\n"
                    f"Happy learning!\n"
                    f"— The Precis Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            sent += 1
        except Exception:
            logger.exception("Failed to send digest to %s", user.email)

    logger.info("Weekly digest sent to %d students.", sent)
