"""
CertificateServiceBase
======================
Base service for certificate operations.

Canonical import: from crafts_ai.services import CertificateServiceBase

Subclass and set ``certificate_model`` to the concrete Certificate model::

    from crafts_ai.services import CertificateServiceBase
    # Project-specific imports removed - use dependency injection

    class CertificateService(CertificateServiceBase):
        certificate_model = Certificate
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Dict, Tuple

from django.core.cache import cache
from django.db.models.aggregates import Avg, Count
from django.db.models.expressions import F
from django.db.models.query_utils import Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class CertificateServiceBase:
    """Base service for certificate operations.

    The concrete ``Certificate`` model is injected via the ``certificate_model``
    class attribute so this base class has no hard-coded model imports.
    """

    certificate_model: type = None  # set by subclass

    # ------------------------------------------------------------------
    # Issuance
    # ------------------------------------------------------------------

    @classmethod
    def issue_certificate(
        cls,
        content_object,
        name: str,
        issuer: str,
        issue_date: date | None = None,
        expiry_date: date | None = None,
        **kwargs,
    ) -> Tuple[bool, str, Any]:
        """Issue a new certificate.

        Returns:
            ``(True, "Certificate issued successfully", certificate)`` on success,
            ``(False, error_message, None)`` on failure.
        """
        try:
            if not issue_date:
                issue_date = timezone.now().date()

            certificate = cls.certificate_model.objects.create(
                content_object=content_object,
                name=name,
                issuer=issuer,
                issue_date=issue_date,
                expiry_date=expiry_date,
                **kwargs,
            )

            if not certificate.certificate_id:
                certificate.certificate_id = f"CERT-{certificate.id.hex[:8].upper()}"
                certificate.save()

            return True, "Certificate issued successfully", certificate

        except Exception as e:
            logger.error("Error issuing certificate: %s", e)
            return False, str(e), None

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @classmethod
    def validate_certificate(
        cls,
        certificate_id: str,
        issuer: str | None = None,
        recipient_name: str | None = None,
    ) -> Tuple[bool, str, Any]:
        """Validate a certificate by its ID.

        Returns:
            ``(True, "Certificate is valid", certificate_data_dict)`` on success,
            ``(False, reason, None)`` on failure.
        """
        try:
            certificate = cls.certificate_model.objects.get(certificate_id=certificate_id)

            if certificate.status != "valid":
                return False, "Certificate is not valid", None
            if getattr(certificate, "is_expired", False):
                return False, "Certificate has expired", None
            if not certificate.is_verified:
                return False, "Certificate is not verified", None
            if issuer and certificate.issuer != issuer:
                return False, "Issuer does not match", None
            if recipient_name:
                recipient = certificate.content_object
                if hasattr(recipient, "full_name") and recipient.full_name != recipient_name:
                    return False, "Recipient does not match", None

            certificate_data = {
                "id": str(certificate.id),
                "certificate_id": certificate.certificate_id,
                "name": certificate.name,
                "issuer": certificate.issuer,
                "issue_date": certificate.issue_date,
                "expiry_date": certificate.expiry_date,
                "recipient": str(certificate.content_object),
                "status": certificate.status,
                "is_verified": certificate.is_verified,
                "verification_status": certificate.verification_status,
            }
            return True, "Certificate is valid", certificate_data

        except cls.certificate_model.DoesNotExist:
            return False, "Certificate not found", None
        except Exception as e:
            logger.error("Error validating certificate: %s", e)
            return False, str(e), None

    # ------------------------------------------------------------------
    # Profile / dashboard
    # ------------------------------------------------------------------

    @classmethod
    def get_certificate_profile(cls, user) -> Dict[str, Any]:
        """Return a certificate dashboard dict for *user*.

        Results are cached for 5 minutes.
        """
        try:
            cache_key = f"cert_dashboard_{user.id}"
            data = cache.get(cache_key)
            if data is not None:
                return data

            certificates = cls.certificate_model.objects.filter(content_object=user)
            valid_certs = certificates.filter(status="valid")

            by_status: Dict[str, int] = {}
            for status in ("valid", "expired", "pending", "revoked"):
                by_status[status] = certificates.filter(status=status).count()

            by_issuer = list(
                certificates.values("issuer")
                .annotate(count=Count("id"))
                .order_by("-count")[:5]
            )

            data = {
                "summary": {
                    "total": certificates.count(),
                    "valid": valid_certs.count(),
                    "expired": certificates.filter(status="expired").count(),
                },
                "breakdown": {
                    "by_status": by_status,
                    "by_issuer": by_issuer,
                },
                "recent_certificates": list(
                    certificates.order_by("-issue_date")[:5].values()
                ),
            }
            cache.set(cache_key, data, 300)
            return data

        except Exception as e:
            logger.error("Error getting certificate profile: %s", e)
            return {}

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    @classmethod
    def generate_certificate_report(
        cls,
        content_object,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Dict[str, Any]:
        """Generate a certificate report for *content_object*.

        Returns a dict with period, summary, monthly_breakdown, and
        issuer_statistics keys.
        """
        try:
            from django.db.models.functions import TruncMonth

            if not end_date:
                end_date = timezone.now().date()
            if not start_date:
                start_date = end_date - timedelta(days=365)

            certificates = cls.certificate_model.objects.filter(
                content_object=content_object,
                issue_date__range=[start_date, end_date],
            )

            total = certificates.count()
            valid = certificates.filter(status="valid").count()
            expired = certificates.filter(status="expired").count()

            monthly_data = list(
                certificates.annotate(month=TruncMonth("issue_date"))
                .values("month")
                .annotate(
                    count=Count("id"),
                    valid=Count("id", filter=Q(status="valid")),
                    expired=Count("id", filter=Q(status="expired")),
                )
                .order_by("month")
            )

            issuer_stats = list(
                certificates.values("issuer")
                .annotate(
                    count=Count("id"),
                    avg_duration=Avg(F("expiry_date") - F("issue_date")),
                )
                .order_by("-count")[:10]
            )

            return {
                "period": {"start_date": start_date, "end_date": end_date},
                "summary": {
                    "total_certificates": total,
                    "valid_certificates": valid,
                    "expired_certificates": expired,
                    "valid_percentage": round(
                        (valid / total * 100) if total > 0 else 0, 2
                    ),
                },
                "monthly_breakdown": monthly_data,
                "issuer_statistics": issuer_stats,
                "certificate_list": list(
                    certificates.order_by("-issue_date").values(
                        "name", "issuer", "issue_date", "expiry_date", "status"
                    )[:50]
                ),
            }

        except Exception as e:
            logger.error("Error generating certificate report: %s", e)
            return {}
