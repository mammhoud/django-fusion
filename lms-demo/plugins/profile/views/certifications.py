import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_osoul.site import NotificationMixin, PageHandler

from plugins.accounts.management.services import CertificateService

logger = logging.getLogger(__name__)

User = get_user_model()



class CertificationsView(PageHandler, NotificationMixin):
    """
    Certificates management view.
    """

    page_title = "Certifications"
    template_name = "base_profile.html"
    fragment_name = "profile.certifications"
    layout_path = "profile/skeleton.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get context data for certificates page.
        """
        self.request = request
        context = super().get_context_data(**kwargs)

        if request.user.is_authenticated:
            try:
                # Get certificate dashboard
                dashboard = CertificateService.get_certificate_profile(request.user)

                # Get valid certificates
                from plugins.accounts.models import Certificate

                valid_certificates = Certificate.objects.get_valid_certificates(request.user)

                # Get expiring certificates
                expiring_certificates = Certificate.objects.get_expiring_soon(request.user, 30)

                context.update(
                    {
                        "dashboard": dashboard,
                        "valid_certificates": valid_certificates,
                        "expiring_certificates": expiring_certificates,
                        "issuers": self._get_user_issuers(request.user),
                    }
                )

            except Exception as e:
                logger.error(f"Error getting certificates context: {e}")
                self.show_notification(
                    message="Error loading certificates",
                    level="error",
                    title="Error",
                    duration=5000,
                    request=request,
                )

        return context

    def _get_user_issuers(self, user):
        """Get unique issuers for user's certificates."""
        from plugins.accounts.models import Certificate

        return (
            Certificate.objects.filter(content_object=user)
            .values_list("issuer", flat=True)
            .distinct()
            .order_by("issuer")
        )

    @require_POST
    @csrf_exempt
    @login_required
    def upload_certificate(self, request: HttpRequest) -> JsonResponse:
        """
        Upload a new certificate.
        """
        try:
            data = request.POST
            files = request.FILES

            success, message, certificate = CertificateService.issue_certificate(
                content_object=request.user,
                name=data.get("name", ""),
                issuer=data.get("issuer", ""),
                issue_date=data.get("issue_date") or timezone.now().date(),
                expiry_date=data.get("expiry_date"),
                description=data.get("description", ""),
            )

            if success and files.get("certificate_file"):
                certificate.certificate_file = files["certificate_file"]
                certificate.save()

            if success:
                self.show_notification(
                    message=message,
                    level="success",
                    title="Certificate Uploaded",
                    duration=3000,
                    request=request,
                )

                return JsonResponse(
                    {
                        "status": "success",
                        "message": message,
                        "certificate": {
                            "id": str(certificate.id),
                            "name": certificate.name,
                            "issuer": certificate.issuer,
                            "issue_date": certificate.issue_date.isoformat(),
                            "status": certificate.status,
                        },
                    }
                )
            else:
                self.show_notification(
                    message=message, level="error", title="Error", duration=5000, request=request
                )

                return JsonResponse({"status": "error", "message": message}, status=400)

        except Exception as e:
            logger.error(f"Error uploading certificate: {e}")
            return JsonResponse(
                {"status": "error", "message": f"Error uploading certificate: {str(e)}"}, status=500
            )
