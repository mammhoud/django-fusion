"""Precis LMS email background tasks.

Uses ``@task`` from ``django_fusion.tasks`` for broker-agnostic enqueue.
"""

from __future__ import annotations

import logging

from django_fusion.tasks import task

logger = logging.getLogger(__name__)


@task(queue="email", max_retries=5, min_backoff=30_000)
def send_enrollment_confirmation(enrollment_id: int):
    """Send a welcome email and course access instructions.

    Fetches the Enrollment record (with student + course) and dispatches
    a branded confirmation email through the configured email backend.
    """
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        from apps.learning.models import Enrollment  # noqa: PLC0415
        enrollment = (
            Enrollment.objects
            .select_related("student", "course")
            .filter(id=enrollment_id)
            .first()
        )
    except ImportError:
        logger.warning("Enrollment model not available — skipping.")
        return

    if enrollment is None:
        logger.warning("Enrollment %d not found.", enrollment_id)
        return

    user = enrollment.student
    course = enrollment.course

    send_mail(
        subject=f"Welcome to {course.title}!",
        message=(
            f"Hi {user.get_full_name() or user.email},\n\n"
            f"You are now enrolled in {course.title}.\n\n"
            f"Access your course: {settings.WAGTAILADMIN_BASE_URL}/courses/{course.slug}/\n\n"
            f"Happy learning!\n"
            f"— The Precis Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    logger.info("Enrollment confirmation sent to %s for course %s.", user.email, course.slug)


@task(queue="email", max_retries=5)
def send_certificate(certificate_id: int):
    """Generate and email a course completion certificate (PDF).

    Renders the certificate as a PDF (if WeasyPrint or similar is
    available), attaches it to an email, and sends it to the student.
    """
    from django.core.mail import EmailMessage
    from django.conf import settings

    try:
        from apps.learning.models import Certificate  # noqa: PLC0415
        cert = (
            Certificate.objects
            .select_related("student", "course")
            .filter(id=certificate_id)
            .first()
        )
    except ImportError:
        logger.warning("Certificate model not available — skipping.")
        return

    if cert is None:
        logger.warning("Certificate %d not found.", certificate_id)
        return

    user = cert.student
    course = cert.course

    # Attempt PDF generation via WeasyPrint (optional dependency)
    pdf_bytes = None
    try:
        from django.template.loader import render_to_string
        html = render_to_string("emails/certificate.html", {
            "user": user,
            "course": course,
            "completion_date": cert.completed_at,
        })
        from weasyprint import HTML  # noqa: PLC0415
        pdf_bytes = HTML(string=html).write_pdf()
    except ImportError:
        logger.info("WeasyPrint not installed — sending plain-text certificate email.")
    except Exception:
        logger.exception("PDF generation failed for certificate %d", certificate_id)

    email = EmailMessage(
        subject=f"Your Certificate: {course.title}",
        body=(
            f"Congratulations {user.get_full_name() or user.email}!\n\n"
            f"You have completed {course.title}.\n"
            f"Your certificate is attached.\n\n"
            f"— The Precis Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    if pdf_bytes:
        email.attach(
            f"certificate_{course.slug}.pdf",
            pdf_bytes,
            "application/pdf",
        )

    email.send(fail_silently=False)
    logger.info("Certificate sent to %s for course %s.", user.email, course.slug)


@task(queue="email", max_retries=3)
def send_password_reset(user_id: int):
    """Send a password reset email to a user.

    Thin wrapper around Django's built-in password reset forms.
    Typically called from a signal or admin action.
    """
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.contrib.auth.forms import PasswordResetForm
    from django.contrib.auth.tokens import default_token_generator

    User = get_user_model()
    user = User.objects.filter(id=user_id, is_active=True).first()
    if user is None:
        logger.warning("User %d not found or inactive — skipping password reset.", user_id)
        return

    form = PasswordResetForm({"email": user.email})
    if form.is_valid():
        form.save(
            request=None,
            from_email=settings.DEFAULT_FROM_EMAIL,
            email_template_name="registration/password_reset_email.html",
        )
        logger.info("Password reset email sent to %s.", user.email)
    else:
        logger.warning("Invalid email for password reset: %s", user.email)
