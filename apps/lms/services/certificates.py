"""
Certificate Generation Service for LMS.
"""
import io
import logging
from datetime import date
from typing import Optional

from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


class CertificateService:
    """
    Service for generating and managing course completion certificates.
    """

    @classmethod
    def create_certificate(cls, user, course, completion_date: Optional[date] = None):
        """
        Create a certificate for a user who completed a course.

        Args:
            user: The user who completed the course
            course: The completed course
            completion_date: Optional completion date (defaults to today)

        Returns:
            Certificate instance
        """
        from django.utils import timezone

        from apps.lms.models.certificate import Certificate

        if completion_date is None:
            completion_date = timezone.now().date()

        # Get user's display name
        user_name = cls._get_user_display_name(user)

        # Create certificate
        certificate = Certificate.objects.create(
            user=user,
            course=course,
            course_title=course.title,
            user_name=user_name,
            completion_date=completion_date,
        )

        # Generate PDF
        try:
            cls.generate_pdf(certificate)
        except Exception as e:
            logger.error(f"Failed to generate PDF for certificate {certificate.certificate_id}: {e}")

        return certificate

    @classmethod
    def _get_user_display_name(cls, user) -> str:
        """Get user's display name for certificate."""
        if hasattr(user, "get_full_name"):
            full_name = user.get_full_name()
            if full_name:
                return full_name

        if hasattr(user, "first_name") and hasattr(user, "last_name"):
            if user.first_name and user.last_name:
                return f"{user.first_name} {user.last_name}"

        return user.username if hasattr(user, "username") else str(user)

    @classmethod
    def generate_pdf(cls, certificate) -> str:
        """
        Generate PDF certificate.

        Args:
            certificate: Certificate instance

        Returns:
            Path to generated PDF file
        """
        try:
            # Try to use reportlab for PDF generation
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.pdfgen import canvas

            buffer = io.BytesIO()

            # Create PDF with landscape orientation
            c = canvas.Canvas(buffer, pagesize=landscape(A4))
            width, height = landscape(A4)

            # Add certificate content
            cls._draw_certificate_content(c, certificate, width, height)

            c.save()
            buffer.seek(0)

            # Save to certificate
            filename = f"{certificate.certificate_id}.pdf"
            certificate.pdf_file.save(filename, ContentFile(buffer.read()), save=True)

            logger.info(f"Generated PDF for certificate {certificate.certificate_id}")
            return certificate.pdf_file.path

        except ImportError:
            logger.warning("reportlab not installed, skipping PDF generation")
            return ""
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise

    @classmethod
    def _draw_certificate_content(cls, canvas, certificate, width, height):
        """Draw certificate content on canvas."""
        from reportlab.lib.colors import HexColor

        # Colors
        primary_color = HexColor("#3A7CA5")
        text_color = HexColor("#333333")

        # Border
        canvas.setStrokeColor(primary_color)
        canvas.setLineWidth(3)
        canvas.rect(30, 30, width - 60, height - 60)

        # Inner border
        canvas.setLineWidth(1)
        canvas.rect(40, 40, width - 80, height - 80)

        # Title
        canvas.setFillColor(primary_color)
        canvas.setFont("Helvetica-Bold", 36)
        canvas.drawCentredString(width / 2, height - 100, "Certificate of Completion")

        # Subtitle
        canvas.setFillColor(text_color)
        canvas.setFont("Helvetica", 16)
        canvas.drawCentredString(width / 2, height - 140, "This is to certify that")

        # User name
        canvas.setFont("Helvetica-Bold", 28)
        canvas.drawCentredString(width / 2, height - 190, certificate.user_name)

        # Course completion text
        canvas.setFont("Helvetica", 16)
        canvas.drawCentredString(width / 2, height - 240, "has successfully completed the course")

        # Course title
        canvas.setFillColor(primary_color)
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawCentredString(width / 2, height - 290, certificate.course_title)

        # Date
        canvas.setFillColor(text_color)
        canvas.setFont("Helvetica", 14)
        date_str = certificate.completion_date.strftime("%B %d, %Y")
        canvas.drawCentredString(width / 2, height - 350, f"Completed on {date_str}")

        # Certificate ID
        canvas.setFont("Helvetica", 10)
        canvas.drawCentredString(width / 2, 60, f"Certificate ID: {certificate.certificate_id}")

    @classmethod
    def verify_certificate(cls, certificate_id: str) -> Optional[dict]:
        """
        Verify a certificate by its ID.

        Args:
            certificate_id: The certificate ID to verify

        Returns:
            Certificate details if valid, None otherwise
        """
        from apps.lms.models.certificate import Certificate

        try:
            cert = Certificate.objects.select_related("user", "course").get(
                certificate_id=certificate_id
            )
            return {
                "valid": True,
                "certificate_id": cert.certificate_id,
                "user_name": cert.user_name,
                "course_title": cert.course_title,
                "completion_date": cert.completion_date,
                "issued_at": cert.issued_at,
            }
        except Certificate.DoesNotExist:
            return None

    @classmethod
    def get_user_certificates(cls, user):
        """Get all certificates for a user."""
        from apps.lms.models.certificate import Certificate
        return Certificate.objects.filter(user=user).select_related("course")
